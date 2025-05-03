#define _DEFAULT_SOURCE // Or _POSIX_C_SOURCE >= 200809L for barriers, rand_r
#define _GNU_SOURCE
#include "ep2.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <errno.h>
#include <limits.h> // For INT_MAX

// --- Global Variable Definitions ---
int d;
int k;
char concurrency_mode;
bool debug_mode = false;

int **pista = NULL;
CyclistInfo *cyclists = NULL;
ResultInfo *final_results = NULL;

int num_active_cyclists;
int num_finished_cyclists = 0;
unsigned long long simulation_time_ms = 0;
bool race_over = false;
int current_lap_leader = 0; // Tracks the maximum lap number completed by any cyclist

// Synchronization primitives
pthread_mutex_t global_lock;
pthread_mutex_t *track_mutexes = NULL;
pthread_mutex_t print_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_t results_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_barrier_t step_barrier_start;
pthread_barrier_t step_barrier_end;


pthread_mutex_t track_lock;  // Single mutex for small tracks

volatile bool cleanup_requested = false;  // Flag to signal threads to exit

// --- Helper Functions ---

// Thread-safe random integer between min and max (inclusive)
int get_random_int(int min, int max, unsigned int *seedp) {
    if (min > max) return min; // Basic error check
    return min + rand_r(seedp) % (max - min + 1);
}

// Thread-safe random double between 0.0 and 1.0
double get_random_double(unsigned int *seedp) {
    return (double)rand_r(seedp) / RAND_MAX;
}

// Comparison function for sorting lap ranks by time (ascending)
int compare_lap_ranks(const void *a, const void *b) {
    LapRankEntry *entryA = (LapRankEntry *)a;
    LapRankEntry *entryB = (LapRankEntry *)b;
    if (entryA->crossing_time < entryB->crossing_time) return -1;
    if (entryA->crossing_time > entryB->crossing_time) return 1;
    return 0; // Should ideally not happen with ulonglong times, but handle anyway
}

// Comparison function for sorting final results
int compare_final_ranks(const void *a, const void *b) {
    ResultInfo *resA = (ResultInfo *)a;
    ResultInfo *resB = (ResultInfo *)b;

    // Broken cyclists come last
    if (resA->final_state == BROKEN && resB->final_state != BROKEN) return 1;
    if (resA->final_state != BROKEN && resB->final_state == BROKEN) return -1;
    if (resA->final_state == BROKEN && resB->final_state == BROKEN) {
         // Sort broken by lap number descending (broke later = better)
        if (resA->broken_lap > resB->broken_lap) return -1;
        if (resA->broken_lap < resB->broken_lap) return 1;
        return 0;
    }

     // Eliminated cyclists come after finished but before broken
    if (resA->final_state == ELIMINATED && resB->final_state == FINISHED) return 1;
    if (resA->final_state == FINISHED && resB->final_state == ELIMINATED) return -1;
    if (resA->final_state == ELIMINATED && resB->final_state == ELIMINATED) {
         // Sort eliminated by laps completed descending
        if (resA->completed_laps > resB->completed_laps) return -1;
        if (resA->completed_laps < resB->completed_laps) return 1;
         // If same laps, sort by finish time ascending (eliminated earlier is worse)
        if (resA->finish_time_ms < resB->finish_time_ms) return -1;
        if (resA->finish_time_ms > resB->finish_time_ms) return 1;
        return 0;
    }

    // Finished cyclists sorted by rank (which is based on finish time)
    if (resA->rank < resB->rank) return -1;
    if (resA->rank > resB->rank) return 1;
    return 0;
}

// --- Initialization ---

void initialize_simulation(int argc, char *argv[]) {
    // 1. Parse Arguments
    if (argc < 4 || argc > 5) {
        fprintf(stderr, "Usage: %s <d> <k> <i|e> [-debug]\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    d = atoi(argv[1]);
    k = atoi(argv[2]);
    concurrency_mode = argv[3][0];

    if ((d < 100 || d > 2500) || (k < 5 || k > 5 * d) || (concurrency_mode != 'i' && concurrency_mode != 'e')) {
        fprintf(stderr, "Invalid arguments:\n");
        fprintf(stderr, "  100 <= d <= 2500\n");
        fprintf(stderr, "  5 <= k <= 5*d\n");
        fprintf(stderr, "  mode must be 'i' or 'e'\n");
        exit(EXIT_FAILURE);
    }

    if (argc == 5 && strcmp(argv[4], "-debug") == 0) {
        debug_mode = true;
    }

    num_active_cyclists     = k;
    num_finished_cyclists   = 0;
    simulation_time_ms      = 0;
    race_over               = false;
    current_lap_leader      = 0;

    // Seed the main random number generator (for initial placement, tie-breaks)
    srand(time(NULL));

    // 3. Allocate Memory
    pista = (int **)malloc(d * sizeof(int *));
    if (!pista) { perror("Failed to allocate pista rows"); exit(EXIT_FAILURE); }
    for (int i = 0; i < d; ++i) {
        pista[i] = (int *)malloc(MAX_LANES * sizeof(int));
        if (!pista[i]) { perror("Failed to allocate pista columns"); exit(EXIT_FAILURE); }
        for (int j = 0; j < MAX_LANES; ++j) {
            pista[i][j] = -1; // Initialize track as empty
        }
    }

    cyclists = (CyclistInfo *)malloc(k * sizeof(CyclistInfo));
    if (!cyclists) { perror("Failed to allocate cyclists"); exit(EXIT_FAILURE); }

    final_results = (ResultInfo *)malloc(k * sizeof(ResultInfo));
     if (!final_results) { perror("Failed to allocate final_results"); exit(EXIT_FAILURE); }


    // 4. Initialize Synchronization Primitives
    if (pthread_mutex_init(&global_lock, NULL) != 0) {
        perror("Mutex init failed (global_lock)"); exit(EXIT_FAILURE);
    }
    if (pthread_mutex_init(&print_mutex, NULL) != 0) {
        perror("Mutex init failed (print_mutex)"); exit(EXIT_FAILURE);
    }
     if (pthread_mutex_init(&results_mutex, NULL) != 0) {
        perror("Mutex init failed (results_mutex)"); exit(EXIT_FAILURE);
    }

    if (concurrency_mode == 'e') {
        if (d < SMALL_TRACK_THRESHOLD) {
            if (pthread_mutex_init(&track_lock, NULL) != 0) {
                perror("Mutex init failed (track_lock)"); exit(EXIT_FAILURE);
            }
        } else {
            track_mutexes = (pthread_mutex_t *)malloc(d * sizeof(pthread_mutex_t));
            if (!track_mutexes) { perror("Failed to allocate track mutexes"); exit(EXIT_FAILURE); }
            for (int i = 0; i < d; ++i) {
                if (pthread_mutex_init(&track_mutexes[i], NULL) != 0) {
                    perror("Mutex init failed (track_mutexes)"); exit(EXIT_FAILURE);
                }
            }
        }
    }

    // Initialize barriers (k cyclists + 1 main thread)
    // All cyclist threads participate in barriers regardless of state (running or ghosted)
    if (pthread_barrier_init(&step_barrier_start, NULL, k + 1) != 0) {
         perror("Barrier init failed (step_barrier_start)"); exit(EXIT_FAILURE);
    }
    if (pthread_barrier_init(&step_barrier_end, NULL, k + 1) != 0) {
        perror("Barrier init failed (step_barrier_end)"); exit(EXIT_FAILURE);
    }


    // 5. Initialize Cyclists
    for (int i = 0; i < k; ++i) {
        cyclists[i].id = i;
        cyclists[i].state = RUNNING;
        cyclists[i].current_speed = BASE_SPEED; // Start at 30km/h for lap 1
        cyclists[i].effective_speed = BASE_SPEED;
        cyclists[i].current_meter = -1; // Will be set by initialize_cyclist_positions
        cyclists[i].current_lane = -1;
        cyclists[i].laps_completed = 0;
        cyclists[i].time_to_move_ms = METER_TIME_SLOW_MS; // Time for first meter at 30km/h
        cyclists[i].last_crossing_time = 0;
        cyclists[i].lap_rank = 0;
        cyclists[i].needs_main_update = false;
        cyclists[i].rand_seed = time(NULL) ^ (i << 16); // Simple unique seed per thread
        cyclists[i].broken_lap = -1;
    }

    initialize_cyclist_positions();

    printf("Simulation Started: d=%d, k=%d, mode=%c, debug=%s\n",
           d, k, concurrency_mode, debug_mode ? "true" : "false");
}

// Place cyclists randomly at the start line (meter 0)
// Max 5 wide, potentially spilling back to meter d-1, d-2 etc. if needed
void initialize_cyclist_positions() {
    int *start_order = malloc(k * sizeof(int));
    if (!start_order) { perror("Failed to allocate start_order"); exit(EXIT_FAILURE); }
    for(int i=0; i<k; ++i) start_order[i] = i;

    // Shuffle the starting order
    for (int i = k - 1; i > 0; --i) {
        int j = rand() % (i + 1);
        int temp = start_order[i];
        start_order[i] = start_order[j];
        start_order[j] = temp;
    }

    int current_meter = 0;
    int current_row = 0; // Row within the starting block (0 = front)
    int lane_in_row = 0; // Position within the row (0-4)

    for (int i = 0; i < k; ++i) {
        int cyclist_id = start_order[i];

        // Find the specific meter and lane for this starting position
        int place_meter = (d + current_meter - current_row) % d; // Start at meter 0, go backwards
        int place_lane = lane_in_row;

        cyclists[cyclist_id].current_meter = place_meter;
        cyclists[cyclist_id].current_lane = place_lane;
        pista[place_meter][place_lane] = cyclist_id; // Place on track

        // Move to next starting slot
        lane_in_row++;
        if (lane_in_row >= 5) { // Max 5 wide
            lane_in_row = 0;
            current_row++;
        }
    }
    free(start_order);
     printf("Initial positions assigned.\n");
     if (debug_mode) print_track_state(); // Show initial state if debugging
}


// --- Cyclist Thread ---

void *ciclista_func(void *arg) {
    int id = *(int *)arg;
    CyclistInfo *me = &cyclists[id];
    unsigned int *my_seed = &me->rand_seed;

    while (!race_over && !cleanup_requested) {
        // Use timed barrier wait instead
        struct timespec timeout;
        clock_gettime(CLOCK_REALTIME, &timeout);
        timeout.tv_sec += BARRIER_TIMEOUT_SEC;
        
        int barrier_result = pthread_barrier_wait(&step_barrier_start);
        if (barrier_result != 0 && barrier_result != PTHREAD_BARRIER_SERIAL_THREAD) {
            fprintf(stderr, "Warning: Cyclist %d barrier wait error (start)\n", id);
            me->state = BROKEN;
            me->needs_main_update = true;
            break;
        }

        // Check if race ended while waiting or cleanup requested
        if (race_over || cleanup_requested) {
            // Wait for end barrier before exiting
            pthread_barrier_wait(&step_barrier_end);
            break;
        }

        // --- Simulation Logic for one time step (only if RUNNING) ---
        if (me->state == RUNNING) {
            me->time_to_move_ms -= TIME_STEP_MS;

            if (me->time_to_move_ms <= 0) {
                // Time to attempt moving 1 meter
                int current_m = me->current_meter;
                int current_l = me->current_lane;
                int target_m = (current_m - 1 + d) % d;  // Move backward by 1 meter, with wrap-around
                int target_l = current_l; // Assume same lane initially

                bool can_move = false;
                me->effective_speed = me->current_speed; // Assume target speed initially

                // --- Acquire Locks (Naive or Efficient) ---
                if (concurrency_mode == 'i') {
                    pthread_mutex_lock(&global_lock);
                } else { // Efficient mode
                    if (d < SMALL_TRACK_THRESHOLD) {
                        pthread_mutex_lock(&track_lock);
                    } else {
                        // For larger tracks, use a more sophisticated locking strategy
                        int lock1_idx = current_m;
                        int lock2_idx = target_m;
                        
                        // Always lock in ascending order to prevent deadlocks
                        if (lock1_idx > lock2_idx) {
                            int temp = lock1_idx;
                            lock1_idx = lock2_idx;
                            lock2_idx = temp;
                        }
                        
                        // Use trylock with timeout to prevent deadlocks
                        struct timespec timeout;
                        clock_gettime(CLOCK_REALTIME, &timeout);
                        timeout.tv_sec += 1; // 1 second timeout
                        
                        if (pthread_mutex_timedlock(&track_mutexes[lock1_idx], &timeout) != 0) {
                            // Failed to acquire first lock, skip this move
                            me->time_to_move_ms = METER_TIME_SLOW_MS;
                            continue;
                        }
                        
                        if (lock1_idx != lock2_idx) {
                            if (pthread_mutex_timedlock(&track_mutexes[lock2_idx], &timeout) != 0) {
                                // Failed to acquire second lock, release first and skip move
                                pthread_mutex_unlock(&track_mutexes[lock1_idx]);
                                me->time_to_move_ms = METER_TIME_SLOW_MS;
                                continue;
                            }
                        }
                    }
                }

                // --- Check for Blocking and Overtaking ---
                bool target_occupied = false;
                int blocking_cyclist_id = -1;
                bool blocked_by_slow_cyclist = false;

                // Check target lane first
                if (pista[target_m][target_l] != -1) {
                    target_occupied = true;
                    blocking_cyclist_id = pista[target_m][target_l];
                    // Check if blocker is going at 30km/h
                    if (cyclists[blocking_cyclist_id].current_speed == BASE_SPEED) {
                        blocked_by_slow_cyclist = true;
                    }
                }

                if (!target_occupied) {
                    can_move = true;
                } else {
                    // Target lane occupied, try to overtake using outer lanes
                    for (int check_lane = target_l + 1; check_lane < MAX_LANES; ++check_lane) {
                        if (pista[target_m][check_lane] == -1) {
                            // Found a free outer lane
                            target_l = check_lane; // Update target lane
                            can_move = true;
                            break;
                        }
                    }

                    // If still can't move, we are blocked
                    if (!can_move) {
                        // If blocked by a slow cyclist, must slow down
                        if (blocked_by_slow_cyclist) {
                            me->effective_speed = BASE_SPEED;
                        }
                        // If blocked by a fast cyclist, maintain current speed
                        // (no need to change effective_speed)
                    }
                }


                // --- Update Position if Moved ---
                if (can_move) {
                    pista[current_m][current_l] = -1; // Leave old spot
                    pista[target_m][target_l] = id;   // Enter new spot
                    me->current_meter = target_m;
                    me->current_lane = target_l;
                    me->needs_main_update = true; // Signal main thread

                    // --- Lap Completion Logic ---
                    if (target_m == 0) { // Crossed the finish line
                        me->laps_completed++;
                        me->last_crossing_time = simulation_time_ms; // Record time

                        // Decide speed for NEXT lap (after completing this one)
                        double chance_60;
                        if (me->current_speed == BASE_SPEED) {
                            chance_60 = 0.75;
                        } else { // Was 60km/h
                            chance_60 = 0.45;
                        }
                        if (get_random_double(my_seed) < chance_60) {
                            me->current_speed = FAST_SPEED;
                        } else {
                            me->current_speed = BASE_SPEED;
                        }

                        // --- Breaking Check ---
                        if (me->laps_completed > 0 && (me->laps_completed % BREAK_CHECK_LAPS == 0)) {
                            if (get_random_double(my_seed) < BREAK_PROBABILITY) {
                                me->state = BROKEN;
                                me->broken_lap = me->laps_completed;
                                me->needs_main_update = true;
                                
                                // Remove self from track (already have lock)
                                pista[target_m][target_l] = -1;
                                
                                // Don't exit thread, just signal main thread and continue as ghost
                                pthread_mutex_lock(&print_mutex);
                                printf(">>> Cyclist %d BROKE on lap %d at time %llu ms <<<\n",
                                       id, me->laps_completed, simulation_time_ms);
                                pthread_mutex_unlock(&print_mutex);
                            }
                        }
                    } // End lap completion

                    // Reset timer for next meter based on CHOSEN speed for next lap
                     // Add back any "negative" time from the previous step
                    long long remaining_time = me->time_to_move_ms; // This is <= 0
                    me->time_to_move_ms = (me->current_speed == FAST_SPEED) ? METER_TIME_FAST_MS : METER_TIME_SLOW_MS;
                    me->time_to_move_ms += remaining_time; // Adjust for overshoot


                } else { // Could not move (blocked)
                     // Reset timer based on EFFECTIVE speed (forced 30km/h)
                     long long remaining_time = me->time_to_move_ms; // This is <= 0
                     me->time_to_move_ms = METER_TIME_SLOW_MS; // Blocked, so takes 120ms for this meter
                     me->time_to_move_ms += remaining_time;
                }


                // --- Release Locks ---
                if (concurrency_mode == 'i') {
                    pthread_mutex_unlock(&global_lock);
                } else { // Efficient mode
                    if (d < SMALL_TRACK_THRESHOLD) {
                        pthread_mutex_unlock(&track_lock);
                    } else {
                        int lock1_idx = current_m;
                        int lock2_idx = target_m;
                        if (lock1_idx > lock2_idx) {
                            int temp = lock1_idx;
                            lock1_idx = lock2_idx;
                            lock2_idx = temp;
                        }
                        pthread_mutex_unlock(&track_mutexes[lock2_idx]);
                        if (lock1_idx != lock2_idx) {
                            pthread_mutex_unlock(&track_mutexes[lock1_idx]);
                        }
                    }
                }

            } // End if (time_to_move_ms <= 0)
        } // End if (state == RUNNING)

        // --- Wait for end of time step (ALL threads, regardless of state) ---
        barrier_result = pthread_barrier_wait(&step_barrier_end);
        if (barrier_result != 0 && barrier_result != PTHREAD_BARRIER_SERIAL_THREAD) {
            fprintf(stderr, "Warning: Cyclist %d barrier wait error (end)\n", id);
            if (me->state == RUNNING) {
                me->state = BROKEN;
                me->needs_main_update = true;
            }
            break;
        }
    }

    // If thread is exiting due to an error, make sure we update the state
    if (me->state == RUNNING) {
        me->needs_main_update = true;
    }

    return NULL;
}

// --- Main Simulation Loop ---

void run_simulation() {
    // Create cyclist threads
    int **thread_args = malloc(k * sizeof(int*));
    if (!thread_args) { perror("Failed to allocate thread args"); exit(EXIT_FAILURE); }
    
    int barrier_result; // Variable to store barrier wait results
    
    for (int i = 0; i < k; ++i) {
        // Allocate memory for each thread's argument
        thread_args[i] = malloc(sizeof(int));
        if (!thread_args[i]) { 
            perror("Failed to allocate thread arg"); 
            // Clean up previous allocations
            for (int j = 0; j < i; j++) {
                free(thread_args[j]);
            }
            free(thread_args);
            exit(EXIT_FAILURE); 
        }
        
        // Set the thread argument value
        *thread_args[i] = i;
        
        // Create the thread with its own argument
        if (pthread_create(&cyclists[i].thread_id, NULL, ciclista_func, thread_args[i]) != 0) {
            perror("Failed to create cyclist thread");
            // Clean up allocations
            for (int j = 0; j <= i; j++) {
                free(thread_args[j]);
            }
            free(thread_args);
            exit(EXIT_FAILURE);
        }
    }

    int last_reported_lap = -1; // Track when lap reports were printed
    int active_cyclists_local = k; // Local count for loop condition

    while (active_cyclists_local > 1 && !race_over && !cleanup_requested) {
        // --- Start Barrier ---
        barrier_result = pthread_barrier_wait(&step_barrier_start);
        if (barrier_result != 0 && barrier_result != PTHREAD_BARRIER_SERIAL_THREAD) {
            fprintf(stderr, "Warning: Main thread barrier wait error (start)\n");
            race_over = true;
            break;
        }

        // --- Advance Time ---
        simulation_time_ms += TIME_STEP_MS;

        // --- End Barrier (Wait for cyclists to finish their step) ---
        barrier_result = pthread_barrier_wait(&step_barrier_end);
        if (barrier_result != 0 && barrier_result != PTHREAD_BARRIER_SERIAL_THREAD) {
            fprintf(stderr, "Warning: Main thread barrier wait error (end)\n");
            race_over = true;
            break;
        }

        // --- Main Thread Processing (Post-Step) ---
        if (race_over) break; // Exit if error occurred

        int max_lap_this_step = 0;
        bool lap_completed_this_step = false;
        active_cyclists_local = 0; // Recount active cyclists

        // Lock results mutex for updating final results and counts
        pthread_mutex_lock(&results_mutex);

        for (int i = 0; i < k; ++i) {
            if (cyclists[i].needs_main_update) {
                 // Check if cyclist broke or was eliminated/finished externally
                if (cyclists[i].state != RUNNING && cyclists[i].state != FINISHED) { // FINISHED state is handled below
                    // Record result if not already done
                    bool found = false;
                    for(int j=0; j<num_finished_cyclists; ++j) {
                        if (final_results[j].id == i) {
                            found = true;
                            break;
                        }
                    }
                    if (!found) {
                         record_final_result(i, cyclists[i].state, -1, cyclists[i].last_crossing_time, cyclists[i].laps_completed, cyclists[i].broken_lap);
                    }
                }
                cyclists[i].needs_main_update = false; // Reset flag
            }

             // Update leader lap count and check if anyone is still running
            if (cyclists[i].state == RUNNING) {
                active_cyclists_local++;
                if (cyclists[i].laps_completed > max_lap_this_step) {
                    max_lap_this_step = cyclists[i].laps_completed;
                }
                 // Check if the leader completed a new lap THIS step
                if (cyclists[i].laps_completed > current_lap_leader && cyclists[i].current_meter == 0 && cyclists[i].last_crossing_time == simulation_time_ms) {
                     lap_completed_this_step = true; // A lap finished now
                }
            }
        }
         // Unlock results mutex after processing updates
        pthread_mutex_unlock(&results_mutex);


        // Update global leader lap if necessary
        if (max_lap_this_step > current_lap_leader) {
            current_lap_leader = max_lap_this_step;
        }

        // --- Elimination Logic ---
        // Check only if a lap was completed this step AND it's an elimination lap
        if (lap_completed_this_step && current_lap_leader > 0 && (current_lap_leader % 2 == 0)) {
             // Check if this lap hasn't been processed for elimination yet
             // (Requires tracking which laps had eliminations)
             // SIMPLIFICATION: Assume we process elimination once when leader hits lap X*2
             if (current_lap_leader > last_reported_lap) { // Only eliminate once per even lap
                 handle_eliminations(current_lap_leader);
                 // Recalculate active cyclists after potential elimination
                 active_cyclists_local = 0;
                 
                 // Use a try-finally pattern to ensure mutex is released
                 pthread_mutex_lock(&results_mutex);
                 for(int i=0; i<k; ++i) {
                     if (cyclists[i].state == RUNNING) active_cyclists_local++;
                 }
                 pthread_mutex_unlock(&results_mutex);
             }
        }


        // --- Reporting ---
        if (debug_mode) {
            print_track_state();  // Only print track state to stderr in debug mode
        } else if (current_lap_leader > last_reported_lap && lap_completed_this_step) {
            // Print lap report only in non-debug mode
            print_lap_report();
            last_reported_lap = current_lap_leader;
        }

        // --- Check Race End Condition ---
        if (active_cyclists_local <= 1) {
            race_over = true;
            pthread_mutex_lock(&results_mutex); // Lock for final update
            // Find the winner (the single remaining RUNNING cyclist)
            for (int i = 0; i < k; i++) {
                if (cyclists[i].state == RUNNING) {
                    cyclists[i].state = FINISHED; // Mark as winner
                    record_final_result(i, FINISHED, 1, cyclists[i].last_crossing_time, cyclists[i].laps_completed, -1);
                    break; // Should only be one
                }
            }
             pthread_mutex_unlock(&results_mutex);
        }

        // Small sleep to prevent busy-waiting if simulation is very fast
        // usleep(1000); // 1ms - Adjust as needed, or remove if barriers handle timing well

    } // End while loop

    // --- Race Finished ---
    race_over = true;
    cleanup_requested = true;

    // Force one more barrier cycle to let threads exit cleanly
    barrier_result = pthread_barrier_wait(&step_barrier_start);
    barrier_result = pthread_barrier_wait(&step_barrier_end);

    // Join any remaining threads with timeout
    struct timespec timeout;
    clock_gettime(CLOCK_REALTIME, &timeout);
    timeout.tv_sec += 2; // 2 second timeout for thread joining

    for (int i = 0; i < k; ++i) {
        if (pthread_timedjoin_np(cyclists[i].thread_id, NULL, &timeout) != 0) {
            fprintf(stderr, "Warning: Failed to join cyclist thread %d\n", i);
            pthread_cancel(cyclists[i].thread_id); // Force thread termination if it won't join
        }
        free(thread_args[i]); // Free the thread argument
    }
    free(thread_args); // Free the array of arguments

    // Always print final report to stdout, regardless of debug mode
    print_final_report();
}

// --- Elimination Handling ---
void handle_eliminations(int lap_num) {
    pthread_mutex_lock(&print_mutex);
    printf("\n--- Handling Eliminations for Lap %d ---\n", lap_num);
    pthread_mutex_unlock(&print_mutex);

    LapRankEntry *lap_ranks = malloc(k * sizeof(LapRankEntry));
    if (!lap_ranks) { perror("Failed to allocate lap_ranks"); return; }

    int runners_in_lap = 0;
    unsigned long long max_time_in_lap = 0;

    pthread_mutex_lock(&results_mutex);
    for (int i = 0; i < k; ++i) {
        // Consider only cyclists who completed the target lap and are still running
        if (cyclists[i].state == RUNNING && cyclists[i].laps_completed >= lap_num) {
            lap_ranks[runners_in_lap].id = i;
            lap_ranks[runners_in_lap].crossing_time = cyclists[i].last_crossing_time;

            if (cyclists[i].last_crossing_time > max_time_in_lap) {
                max_time_in_lap = cyclists[i].last_crossing_time;
            }
            runners_in_lap++;
        }
    }

    if (runners_in_lap <= 1) {
        pthread_mutex_unlock(&results_mutex);
        free(lap_ranks);
        pthread_mutex_lock(&print_mutex);
        printf("   Not enough runners (%d) to eliminate.\n", runners_in_lap);
        pthread_mutex_unlock(&print_mutex);
        return;
    }

    // Find the cyclist(s) with the maximum crossing time (last place)
    int *last_place_ids = malloc(runners_in_lap * sizeof(int));
    if (!last_place_ids) {
        perror("Failed to allocate last_place_ids");
        pthread_mutex_unlock(&results_mutex);
        free(lap_ranks);
        return;
    }
    int num_last_place = 0;

    for (int i = 0; i < runners_in_lap; ++i) {
        if (lap_ranks[i].crossing_time == max_time_in_lap) {
            last_place_ids[num_last_place++] = lap_ranks[i].id;
        }
    }

    // Eliminate one cyclist
    int eliminated_id = -1;
    if (num_last_place == 1) {
        eliminated_id = last_place_ids[0];
    } else if (num_last_place > 1) {
        // Tie-breaker: randomly choose one among the last place finishers
        eliminated_id = last_place_ids[rand() % num_last_place];
        pthread_mutex_lock(&print_mutex);
        printf("   Tie break among %d cyclists for last place. Randomly choosing %d.\n", 
               num_last_place, eliminated_id);
        pthread_mutex_unlock(&print_mutex);
    }

    if (eliminated_id != -1) {
        // Ensure the cyclist is still running before eliminating
        if (cyclists[eliminated_id].state == RUNNING) {
            // Remove this cyclist from the track (using appropriate lock)
            int cyclist_meter = cyclists[eliminated_id].current_meter;
            int cyclist_lane = cyclists[eliminated_id].current_lane;
            
            // Acquire appropriate lock before modifying the track
            if (concurrency_mode == 'i') {
                pthread_mutex_lock(&global_lock);
            } else if (d < SMALL_TRACK_THRESHOLD) {
                pthread_mutex_lock(&track_lock);
            } else {
                pthread_mutex_lock(&track_mutexes[cyclist_meter]);
            }
            
            // Remove cyclist from track
            if (pista[cyclist_meter][cyclist_lane] == eliminated_id) {
                pista[cyclist_meter][cyclist_lane] = -1;
            }
            
            // Release lock
            if (concurrency_mode == 'i') {
                pthread_mutex_unlock(&global_lock);
            } else if (d < SMALL_TRACK_THRESHOLD) {
                pthread_mutex_unlock(&track_lock);
            } else {
                pthread_mutex_unlock(&track_mutexes[cyclist_meter]);
            }
            
            // Update cyclist state
            cyclists[eliminated_id].state = ELIMINATED;
            cyclists[eliminated_id].needs_main_update = true;
            record_final_result(eliminated_id, ELIMINATED, -1, 
                              cyclists[eliminated_id].last_crossing_time, lap_num, -1);

            pthread_mutex_lock(&print_mutex);
            printf(">>> Cyclist %d ELIMINATED after lap %d at time %llu ms <<<\n",
                   eliminated_id, lap_num, cyclists[eliminated_id].last_crossing_time);
            pthread_mutex_unlock(&print_mutex);
        }
    }

    pthread_mutex_unlock(&results_mutex);
    free(last_place_ids);
    free(lap_ranks);
}

void print_track_state() {
    pthread_mutex_lock(&print_mutex);
    fprintf(stderr, "\n--- Time: %llu ms ---\n", simulation_time_ms);
    // Print track (adjust formatting for readability)
    // Example: Print chunks of the track or transpose lanes/meters
    int print_width = 100; // How many meters to print per line
    for (int start_meter = 0; start_meter < d; start_meter += print_width) {
        fprintf(stderr, "Meters %d to %d:\n", start_meter, (start_meter + print_width - 1 < d) ? start_meter + print_width - 1 : d-1);
        for (int lane = 0; lane < MAX_LANES; ++lane) {
            fprintf(stderr, "Lane %d: ", lane);
            for (int meter = start_meter; meter < d && meter < start_meter + print_width; ++meter) {
                int cyclist_id = pista[meter][lane];
                 // Print cyclist ID right-aligned in a 3-char space, or ' . ' if empty
                 if (cyclist_id != -1) {
                     fprintf(stderr, "%3d ", cyclist_id);
                 } else {
                     fprintf(stderr, " . ");
                 }
            }
            fprintf(stderr, "\n");
        }
         fprintf(stderr,"\n");
    }
    pthread_mutex_unlock(&print_mutex);
}

void print_lap_report() {
    pthread_mutex_lock(&print_mutex);
    pthread_mutex_lock(&results_mutex);

    printf("\n--- Lap %d Completed (Leader) at %llu ms ---\n", current_lap_leader, simulation_time_ms);

    // Create temporary structure for ranking cyclists in this lap
    LapRankEntry *lap_ranks = malloc(k * sizeof(LapRankEntry));
    if (!lap_ranks) {
        perror("Failed malloc lap_ranks");
        pthread_mutex_unlock(&results_mutex);
        pthread_mutex_unlock(&print_mutex);
        return;
    }

    int ranked_count = 0;
    for (int i = 0; i < k; ++i) {
        if (cyclists[i].state == RUNNING && cyclists[i].laps_completed >= current_lap_leader) {
            lap_ranks[ranked_count].id = i;
            lap_ranks[ranked_count].crossing_time = cyclists[i].last_crossing_time;
            ranked_count++;
        }
    }

    // Sort by crossing time
    qsort(lap_ranks, ranked_count, sizeof(LapRankEntry), compare_lap_ranks);

    printf("Rank | ID | Lap Time (ms) | Position (m, l) | Speed (km/h)\n");
    printf("--------------------------------------------------------------\n");
    for (int i = 0; i < ranked_count; ++i) {
        int id = lap_ranks[i].id;
        printf("%4d | %2d | %13llu | (%4d, %d) | %11d\n",
               i + 1, id, lap_ranks[i].crossing_time,
               cyclists[id].current_meter, cyclists[id].current_lane,
               cyclists[id].current_speed);
    }

    // List non-running cyclists
    printf("Others:\n");
    for(int i=0; i<k; ++i) {
        bool listed = false;
        for(int j=0; j<ranked_count; ++j) if (lap_ranks[j].id == i) listed = true;

        if (!listed) {
            const char* status_str;
            switch(cyclists[i].state) {
                case RUNNING: status_str = "RUNNING"; break;
                case BROKEN: status_str = "BROKEN"; break;
                case ELIMINATED: status_str = "ELIMINATED"; break;
                case FINISHED: status_str = "FINISHED"; break;
                default: status_str = "UNKNOWN"; break;
            }
            printf("     | %2d | %-10s | (%4d, %d) | %11s\n",
                   i, status_str, cyclists[i].current_meter, 
                   cyclists[i].current_lane, "-");
        }
    }

    free(lap_ranks);
    pthread_mutex_unlock(&results_mutex);
    pthread_mutex_unlock(&print_mutex);
}

// Records the final result for a cyclist
void record_final_result(int cyclist_id, CyclistState state, int rank, unsigned long long time, int laps, int broken_lap) {
    // Use a single mutex for the entire results structure
    pthread_mutex_lock(&results_mutex);

    // Check for duplicate entries atomically
    bool found = false;
    for(int i=0; i<num_finished_cyclists; ++i) {
        if (final_results[i].id == cyclist_id) {
            found = true;
            break;
        }
    }

    if (!found && num_finished_cyclists < k) {
        final_results[num_finished_cyclists].id = cyclist_id;
        final_results[num_finished_cyclists].final_state = state;
        final_results[num_finished_cyclists].rank = rank;
        final_results[num_finished_cyclists].finish_time_ms = time;
        final_results[num_finished_cyclists].completed_laps = laps;
        final_results[num_finished_cyclists].broken_lap = broken_lap;
        num_finished_cyclists++;
    } else if (!found) {
        fprintf(stderr, "Warning: Tried to record more results than cyclists (%d).\n", cyclist_id);
    }

    pthread_mutex_unlock(&results_mutex);
}


void print_final_report() {
    pthread_mutex_lock(&print_mutex);
    pthread_mutex_lock(&results_mutex);

    printf("\n=============== RACE FINISHED ===============\n");
    printf("Total Simulation Time: %llu ms\n", simulation_time_ms);

    pthread_mutex_lock(&results_mutex); // Lock for final calculation/sorting

    // Ensure all cyclists have a result recorded
    if (num_finished_cyclists != k) {
        printf("Warning: Mismatch in final results count (%d) vs k (%d)\n", num_finished_cyclists, k);
         // Attempt to record any missing runners as DNF based on their last state
        for(int i=0; i<k; ++i) {
            bool found = false;
            for(int j=0; j<num_finished_cyclists; ++j) {
                if (final_results[j].id == i) {
                    found = true;
                    break;
                }
            }
            if (!found) {
                 // Record based on last known state
                 record_final_result(i, cyclists[i].state, -1, cyclists[i].last_crossing_time, cyclists[i].laps_completed, cyclists[i].broken_lap);
            }
        }
    }

    // Assign ranks to finished cyclists based on time
    // Create temporary array to sort only FINISHED cyclists by time
    ResultInfo *finished_sorted = malloc(num_finished_cyclists * sizeof(ResultInfo));
    int finished_count = 0;
    if (finished_sorted) {
        for(int i=0; i<num_finished_cyclists; ++i) {
            if (final_results[i].final_state == FINISHED) {
                finished_sorted[finished_count++] = final_results[i];
            }
        }
        // Sort finished cyclists by time (ascending)
        qsort(finished_sorted, finished_count, sizeof(ResultInfo), compare_final_ranks); // Use compare_final_ranks, it handles FINISHED state

        // Assign ranks based on sorted order
        for(int i=0; i<finished_count; ++i) {
            for(int j=0; j<num_finished_cyclists; ++j) {
                if (final_results[j].id == finished_sorted[i].id) {
                    final_results[j].rank = i + 1; // Rank is 1-based index
                    break;
                }
            }
        }
        free(finished_sorted);
    } else {
        perror("Failed to allocate for rank sorting");
        // Ranks might be incorrect if allocation fails
    }

    // Sort the entire final_results array for printing
    qsort(final_results, num_finished_cyclists, sizeof(ResultInfo), compare_final_ranks);

    printf("\n--- Final Rankings ---\n");
    printf("Rank | ID | Status     | Laps | Finish Time (ms) | Broken Lap\n");
    printf("------------------------------------------------------------------\n");

    for (int i = 0; i < num_finished_cyclists; ++i) {
        ResultInfo res = final_results[i];
        const char *status_str;
        char rank_str[10];

        switch (res.final_state) {
            case FINISHED:
                status_str = "FINISHED";
                snprintf(rank_str, 10, "%d", res.rank);
                break;
            case ELIMINATED:
                status_str = "ELIMINATED";
                snprintf(rank_str, 10, "DNF");
                break;
            case BROKEN:
                status_str = "BROKEN";
                snprintf(rank_str, 10, "DNF");
                break;
            default: // Should not happen
                status_str = "UNKNOWN";
                 snprintf(rank_str, 10, "DNF");
                break;
        }

        printf("%4s | %2d | %-10s | %4d | %16llu | %s\n",
               rank_str,
               res.id,
               status_str,
               res.completed_laps,
               (res.final_state == FINISHED || res.final_state == ELIMINATED) ? res.finish_time_ms : 0, // Show time only if finished/eliminated normally
               (res.final_state == BROKEN) ? (sprintf(rank_str, "%d", res.broken_lap), rank_str) : "-"); // Show broken lap#
    }

    pthread_mutex_unlock(&results_mutex); // Unlock after reading/sorting
    pthread_mutex_unlock(&print_mutex);
}


// --- Cleanup ---

void cleanup_simulation() {
    cleanup_requested = true;
    pthread_mutex_destroy(&global_lock);
    pthread_mutex_destroy(&print_mutex);
    pthread_mutex_destroy(&results_mutex);
    if (concurrency_mode == 'e') {
        if (d < SMALL_TRACK_THRESHOLD) {
            pthread_mutex_destroy(&track_lock);
        } else if (track_mutexes != NULL) {
            for (int i = 0; i < d; ++i) {
                pthread_mutex_destroy(&track_mutexes[i]);
            }
            free(track_mutexes);
        }
    }
    pthread_barrier_destroy(&step_barrier_start);
    pthread_barrier_destroy(&step_barrier_end);
    if (pista != NULL) {
        for (int i = 0; i < d; ++i) {
            free(pista[i]);
        }
        free(pista);
    }
    free(cyclists);
    free(final_results);
    printf("Simulation cleanup complete.\n");
}


// --- Main Function ---

int main(int argc, char *argv[]) {
    initialize_simulation(argc, argv);
    run_simulation();
    cleanup_simulation();
    return EXIT_SUCCESS;
}