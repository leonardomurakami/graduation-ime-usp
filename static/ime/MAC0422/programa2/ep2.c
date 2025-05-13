#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <pthread.h>
#include <stdbool.h>
#include <string.h>
#include <limits.h>

#include "ep2.h"

// Global race struct
Race race;

// Random number generator between min and max (inclusive)
int random_between(int min, int max) {
    return min + rand() % (max - min + 1);
}

// Initialize the race with the given parameters
void initialize_race(Race *race, int d, int k, bool efficient, bool debug) {
    race->d = d;
    race->k = k;
    race->efficient = efficient;
    race->debug = debug;
    race->clock = 0;
    race->lap_leader = 0;
    race->cyclists_in_race = k;
    
    // Initialize elimination state variables
    race->current_elimination_lap = 2; // The first even lap
    race->lap_completions = (LapCompletion *)malloc(LAP_COMPLETION_BUFFER_SIZE * sizeof(LapCompletion));
    race->completion_head = 0;
    race->completion_tail = 0;
    race->num_completions = 0;
    
    // Initialize mutexes and condition variables
    pthread_mutex_init(&race->global_mutex, NULL);
    pthread_mutex_init(&race->clock_mutex, NULL);
    pthread_mutex_init(&race->leader_mutex, NULL);
    pthread_mutex_init(&race->completion_mutex, NULL);
    pthread_cond_init(&race->clock_cond, NULL);
    
    // Initialize lap completion mutexes
    for (int i = 0; i < LAP_COMPLETION_BUFFER_SIZE; i++) {
        pthread_mutex_init(&race->lap_completions[i].mutex, NULL);
    }
    
    // Allocate memory for cyclists
    race->cyclists = (Cyclist *)malloc(k * sizeof(Cyclist));
    
    // Initialize cyclist mutexes
    for (int i = 0; i < k; i++) {
        pthread_mutex_init(&race->cyclists[i].mutex, NULL);
    }
    
    // Allocate memory for track
    race->track = (int **)malloc(d * sizeof(int *));
    for (int i = 0; i < d; i++) {
        race->track[i] = (int *)malloc(MAX_SIDE_BY_SIDE * sizeof(int));
        // Initialize all positions as empty (-1)
        for (int j = 0; j < MAX_SIDE_BY_SIDE; j++) {
            race->track[i][j] = -1;
        }
    }
    
    // Initialize track mutexes
    if (efficient) {
        // For efficient approach, one mutex per track position
        race->track_mutex = (pthread_mutex_t *)malloc(d * sizeof(pthread_mutex_t));
        for (int i = 0; i < d; i++) {
            pthread_mutex_init(&race->track_mutex[i], NULL);
        }
    } else {
        // For naive approach, one mutex for the entire track
        race->track_mutex = (pthread_mutex_t *)malloc(sizeof(pthread_mutex_t));
        pthread_mutex_init(&race->track_mutex[0], NULL);
    }
    
    // Initialize cyclists
    for (int i = 0; i < k; i++) {
        race->cyclists[i].id = i + 1;
        race->cyclists[i].lap = 0;
        race->cyclists[i].last_lap_time = 0;
        race->cyclists[i].last_speed = 30; // All cyclists start at 30 km/h
        race->cyclists[i].current_speed = 30;
        race->cyclists[i].eliminated = false;
        race->cyclists[i].broken = false;
        race->cyclists[i].broken_lap = -1;
        race->cyclists[i].final_position = -1;
        race->cyclists[i].final_time = -1;
    }
    
    // Place cyclists at the starting line
    // Randomly determine starting positions, with max 5 cyclists side by side
    int position = 0;
    int cyclists_placed = 0;
    
    // Shuffle cyclists order for random starting positions
    int *order = (int *)malloc(k * sizeof(int));
    for (int i = 0; i < k; i++) {
        order[i] = i;
    }
    
    // Fisher-Yates shuffle
    for (int i = k - 1; i > 0; i--) {
        int j = random_between(0, i);
        int temp = order[i];
        order[i] = order[j];
        order[j] = temp;
    }
    
    // Place cyclists on starting grid
    while (cyclists_placed < k) {
        int max_side = (cyclists_placed + 5 <= k) ? 5 : (k - cyclists_placed);
        
        for (int i = 0; i < max_side; i++) {
            int cyclist_idx = order[cyclists_placed];
            race->cyclists[cyclist_idx].position = position;
            race->cyclists[cyclist_idx].lane = i;
            race->track[position][i] = race->cyclists[cyclist_idx].id;
            cyclists_placed++;
        }
        
        position++; // Move to next position for remaining cyclists
    }
    
    free(order);
    
    // Seed random number generator
    srand(time(NULL));
}

// Clean up resources used by the race
void cleanup_race(Race *race) {
    // Destroy mutexes and condition variables
    pthread_mutex_destroy(&race->global_mutex);
    pthread_mutex_destroy(&race->clock_mutex);
    pthread_mutex_destroy(&race->leader_mutex);
    pthread_mutex_destroy(&race->completion_mutex);
    pthread_cond_destroy(&race->clock_cond);
    
    // Destroy lap completion mutexes
    for (int i = 0; i < LAP_COMPLETION_BUFFER_SIZE; i++) {
        pthread_mutex_destroy(&race->lap_completions[i].mutex);
    }
    
    // Destroy cyclist mutexes
    for (int i = 0; i < race->k; i++) {
        pthread_mutex_destroy(&race->cyclists[i].mutex);
    }
    
    // Free track mutexes
    if (race->efficient) {
        for (int i = 0; i < race->d; i++) {
            pthread_mutex_destroy(&race->track_mutex[i]);
        }
    } else {
        pthread_mutex_destroy(&race->track_mutex[0]);
    }
    free(race->track_mutex);
    
    // Free track
    for (int i = 0; i < race->d; i++) {
        free(race->track[i]);
    }
    free(race->track);
    
    // Free cyclists
    free(race->cyclists);
    
    // Free lap completions array
    free(race->lap_completions);
}

// Update cyclist speed based on rules
void update_cyclist_speed(Cyclist *cyclist) {
    int prob;
    
    // First lap is always at 30 km/h
    if (cyclist->lap == 0) {
        cyclist->current_speed = 30;
        return;
    }
    
    if (cyclist->last_speed == 30) {
        // 75% chance of choosing 60 km/h
        prob = random_between(1, 100);
        cyclist->current_speed = (prob <= 75) ? 60 : 30;
    } else { // last_speed == 60
        // 45% chance of choosing 60 km/h
        prob = random_between(1, 100);
        cyclist->current_speed = (prob <= 45) ? 60 : 30;
    }
}

// Check if cyclist breaks down
bool check_cyclist_breakdown(Cyclist *cyclist) {
    // Check for breakdown every 5 laps
    if (cyclist->lap > 0 && cyclist->lap % 5 == 0) {
        // 10% chance of breaking down
        int prob = random_between(1, 100);
        return (prob <= 10);
    }
    return false;
}

// Check if cyclist can overtake at a target position
bool can_overtake(Race *race, Cyclist *cyclist, int target_position) {
    // Calculate target position with wraparound
    int pos = (target_position + race->d) % race->d;
    
    // Look for an empty lane to the outside
    for (int lane = cyclist->lane + 1; lane < MAX_SIDE_BY_SIDE; lane++) {
        if (race->track[pos][lane] == -1) {
            return true;
        }
    }
    
    return false;
}

// Try to move cyclist forward
bool try_move_cyclist(Race *race, Cyclist *cyclist) {
    // Lock cyclist state
    pthread_mutex_lock(&cyclist->mutex);
    if (cyclist->eliminated || cyclist->broken) {
        pthread_mutex_unlock(&cyclist->mutex);
        return false;
    }
    pthread_mutex_unlock(&cyclist->mutex);
    
    // Calculate distance to move based on speed
    // 30 km/h = 30,000 m/3,600,000 ms = 1/120 m/ms
    // 60 km/h = 60,000 m/3,600,000 ms = 1/60 m/ms
    // With 60ms clock ticks:
    // 30 km/h = 0.5 positions per tick
    // 60 km/h = 1 position per tick
    
    // At 30 km/h, move one position every 120ms (every other tick)
    // At 60 km/h, move one position every 60ms (every tick)
    if ((cyclist->current_speed == 30 && race->clock % 120 != 0) ||
        (cyclist->current_speed == 60 && race->clock % 60 != 0)) {
        // Not time to move yet based on speed
        return false;
    }
    
    // Calculate target position with wraparound
    int current_pos = cyclist->position;
    int next_pos = (current_pos + 1) % race->d;
    int current_lane = cyclist->lane;
    int lap_just_completed = -1;
    
    // Lock the appropriate mutex(es)
    if (race->efficient) {
        pthread_mutex_lock(&race->track_mutex[current_pos]);
        if (next_pos != current_pos) pthread_mutex_lock(&race->track_mutex[next_pos]);
    } else {
        pthread_mutex_lock(&race->track_mutex[0]);
    }
    
    bool moved = false;
    
    // Check if there's a cyclist directly in front in the same lane
    int blocking_cyclist_id = race->track[next_pos][current_lane];
    if (blocking_cyclist_id != -1 && blocking_cyclist_id != cyclist->id) { // Check if the position is actually occupied by another cyclist
        // Check if overtaking is possible
        bool can_overtake = false;
        int overtake_lane = -1;
        for (int lane = current_lane + 1; lane < MAX_SIDE_BY_SIDE; lane++) {
            if (race->track[next_pos][lane] == -1) {
                can_overtake = true;
                overtake_lane = lane;
                break;
            }
        }

        if (can_overtake) {
            // Move to the outside lane to overtake
            race->track[current_pos][current_lane] = -1;
            race->track[next_pos][overtake_lane] = cyclist->id;
            cyclist->position = next_pos;
            cyclist->lane = overtake_lane;
            moved = true;
        } else {
            // Cannot overtake, must slow down if trying to go 60km/h
            if (cyclist->current_speed == 60) {
                 // Speed adjustment doesn't happen here directly, 
                 // the cyclist simply doesn't move this 60ms tick.
                 // Speed update logic is handled elsewhere (when lap completes or based on probability)
                 moved = false; 
            } else { 
                 // If already going 30km/h, they also don't move this tick 
                 // as the space is blocked.
                 moved = false;
            }
        }
    } else {
        // No cyclist blocking, or it's the cyclist itself (should not happen with proper locking)
        // Proceed normally
        race->track[current_pos][current_lane] = -1;
        race->track[next_pos][current_lane] = cyclist->id;
        cyclist->position = next_pos;
        moved = true;
    }
    
    // Unlock the mutex(es)
    if (race->efficient) {
        if (next_pos != current_pos) pthread_mutex_unlock(&race->track_mutex[next_pos]);
        pthread_mutex_unlock(&race->track_mutex[current_pos]);
    } else {
        pthread_mutex_unlock(&race->track_mutex[0]);
    }
    
    if (moved && next_pos == 0) { // Cyclist crossed the finish line
        lap_just_completed = cyclist->lap + 1;
        
        // Lock cyclist for state update
        pthread_mutex_lock(&cyclist->mutex);
        cyclist->lap++;
        cyclist->last_lap_time = race->clock;
        pthread_mutex_unlock(&cyclist->mutex);
        
        // Update race leader if needed
        pthread_mutex_lock(&race->leader_mutex);
        if (cyclist->lap > race->lap_leader) {
            race->lap_leader = cyclist->lap;
        }
        pthread_mutex_unlock(&race->leader_mutex);
        
        // Check elimination logic
        if (race->cyclists_in_race > 1) {
            if (lap_just_completed % 2 == 0) {
                // Lock completion buffer for update
                pthread_mutex_lock(&race->completion_mutex);
                
                // Add new completion to circular buffer
                int completion_idx = race->completion_tail;
                pthread_mutex_lock(&race->lap_completions[completion_idx].mutex);
                race->lap_completions[completion_idx].cyclist_id = cyclist->id;
                race->lap_completions[completion_idx].lap_number = lap_just_completed;
                race->lap_completions[completion_idx].completion_time = race->clock;
                pthread_mutex_unlock(&race->lap_completions[completion_idx].mutex);
                
                // Update buffer state
                race->completion_tail = (race->completion_tail + 1) % LAP_COMPLETION_BUFFER_SIZE;
                if (race->num_completions < LAP_COMPLETION_BUFFER_SIZE) {
                    race->num_completions++;
                } else {
                    race->completion_head = (race->completion_head + 1) % LAP_COMPLETION_BUFFER_SIZE;
                }
                
                // Count completions for current elimination lap
                int active_cyclists_completed = 0;
                int current_elimination_lap = lap_just_completed;
                
                for (int i = 0; i < race->num_completions; i++) {
                    int idx = (race->completion_head + i) % LAP_COMPLETION_BUFFER_SIZE;
                    pthread_mutex_lock(&race->lap_completions[idx].mutex);
                    if (race->lap_completions[idx].lap_number == current_elimination_lap) {
                        active_cyclists_completed++;
                    }
                    pthread_mutex_unlock(&race->lap_completions[idx].mutex);
                }
                
                pthread_mutex_unlock(&race->completion_mutex);
                
                // Check if elimination is needed
                if ((active_cyclists_completed == race->cyclists_in_race) || 
                    (race->cyclists_in_race == 2 && cyclist->lap == race->lap_leader)) {
                    
                    // Lock global mutex for elimination
                    pthread_mutex_lock(&race->global_mutex);
                    
                    // Find the last cyclist to complete this lap
                    int last_cyclist_id = -1;
                    int last_completion_time = -1;
                    
                    if (race->cyclists_in_race == 2 && cyclist->lap == race->lap_leader) {
                        // Find the other active cyclist
                        for (int i = 0; i < race->k; i++) {
                            pthread_mutex_lock(&race->cyclists[i].mutex);
                            if (!race->cyclists[i].eliminated && !race->cyclists[i].broken && 
                                race->cyclists[i].id != cyclist->id) {
                                last_cyclist_id = race->cyclists[i].id;
                                last_completion_time = race->clock;
                            }
                            pthread_mutex_unlock(&race->cyclists[i].mutex);
                        }
                    } else {
                        // Find the slowest cyclist
                        pthread_mutex_lock(&race->completion_mutex);
                        for (int i = 0; i < race->num_completions; i++) {
                            int idx = (race->completion_head + i) % LAP_COMPLETION_BUFFER_SIZE;
                            pthread_mutex_lock(&race->lap_completions[idx].mutex);
                            if (race->lap_completions[idx].lap_number == current_elimination_lap) {
                                if (race->lap_completions[idx].completion_time >= last_completion_time) {
                                    last_cyclist_id = race->lap_completions[idx].cyclist_id;
                                    last_completion_time = race->lap_completions[idx].completion_time;
                                }
                            }
                            pthread_mutex_unlock(&race->lap_completions[idx].mutex);
                        }
                        pthread_mutex_unlock(&race->completion_mutex);
                    }
                    
                    // Eliminate the last cyclist
                    if (last_cyclist_id != -1) {
                        for (int i = 0; i < race->k; i++) {
                            pthread_mutex_lock(&race->cyclists[i].mutex);
                            if (race->cyclists[i].id == last_cyclist_id && 
                                !race->cyclists[i].eliminated && 
                                !race->cyclists[i].broken) {
                                race->cyclists[i].eliminated = true;
                                race->cyclists[i].final_time = last_completion_time;
                                race->cyclists_in_race--;
                                
                                fprintf(stdout, "Cyclist %d eliminated at lap %d\n", 
                                        race->cyclists[i].id, current_elimination_lap);
                            }
                            pthread_mutex_unlock(&race->cyclists[i].mutex);
                        }
                        
                        race->current_elimination_lap = current_elimination_lap + 2;
                    }
                    
                    pthread_mutex_unlock(&race->global_mutex);
                }
            }
        }
        
        // Update speed for next lap
        pthread_mutex_lock(&cyclist->mutex);
        cyclist->last_speed = cyclist->current_speed;
        update_cyclist_speed(cyclist);
        
        // Check for breakdown
        if (check_cyclist_breakdown(cyclist)) {
            cyclist->broken = true;
            cyclist->broken_lap = cyclist->lap;
            fprintf(stdout, "Cyclist %d broke down at lap %d\n", cyclist->id, cyclist->lap);
            
            pthread_mutex_lock(&race->global_mutex);
            race->cyclists_in_race--;
            pthread_mutex_unlock(&race->global_mutex);
            
            // Update elimination records if needed
            if (lap_just_completed % 2 == 0) {
                pthread_mutex_lock(&race->completion_mutex);
                for (int i = 0; i < race->num_completions; i++) {
                    int idx = (race->completion_head + i) % LAP_COMPLETION_BUFFER_SIZE;
                    pthread_mutex_lock(&race->lap_completions[idx].mutex);
                    if (race->lap_completions[idx].cyclist_id == cyclist->id && 
                        race->lap_completions[idx].lap_number == lap_just_completed) {
                        race->lap_completions[idx].cyclist_id = -1;
                    }
                    pthread_mutex_unlock(&race->lap_completions[idx].mutex);
                }
                pthread_mutex_unlock(&race->completion_mutex);
            }
        }
        pthread_mutex_unlock(&cyclist->mutex);
    }
    
    return moved;
}

// Sort active cyclists by current race progress
void sort_cyclists_by_position(Race *race) {
    // Create temporary array with indices of active cyclists
    int active_count = 0;
    int *active_indices = (int *)malloc(race->k * sizeof(int));
    for (int i = 0; i < race->k; i++) {
        if (!race->cyclists[i].broken && !race->cyclists[i].eliminated) {
            active_indices[active_count++] = i;
        }
        // Reset final position for recalculation
        race->cyclists[i].final_position = -1; 
    }

    if (active_count == 0) {
        free(active_indices);
        return; 
    }

    // Quicksort helper function to compare cyclists
    int compare_cyclists(const void *a, const void *b) {
        int idx1 = *(const int *)a;
        int idx2 = *(const int *)b;
        
        // Primary sort key: Lap (higher is better)
        if (race->cyclists[idx1].lap != race->cyclists[idx2].lap) {
            return race->cyclists[idx2].lap - race->cyclists[idx1].lap; // Descending order
        }
        
        // Secondary sort key: Position (higher is better - further along)
        if (race->cyclists[idx1].position != race->cyclists[idx2].position) {
            return race->cyclists[idx2].position - race->cyclists[idx1].position; // Descending order
        }
        
        // Tertiary sort key: Lane (lower is better - inner lane)
        return race->cyclists[idx1].lane - race->cyclists[idx2].lane; // Ascending order
    }

    // Sort active cyclists using qsort
    qsort(active_indices, active_count, sizeof(int), compare_cyclists);

    // Assign current rank (1st, 2nd, etc.) to active cyclists
    for (int i = 0; i < active_count; i++) {
        race->cyclists[active_indices[i]].final_position = i + 1;
    }

    free(active_indices);
}

// Check if the race is finished
bool is_race_finished(Race *race) {
    // Race is finished when only one cyclist remains active
    return race->cyclists_in_race <= 1;
}

// Print track debug information
void print_track_debug(Race *race) {
    fprintf(stderr, "\n");
    
    // Print track state
    for (int lane = 0; lane < MAX_SIDE_BY_SIDE; lane++) {
        for (int pos = 0; pos < race->d; pos++) {
            if (race->track[pos][lane] == -1) {
                fprintf(stderr, ". ");
            } else {
                fprintf(stderr, "%d ", race->track[pos][lane]);
            }
        }
        fprintf(stderr, "\n");
    }
    fprintf(stderr, "\n");
}

// Print lap report with cyclists positions
void print_lap_report(Race *race) {
    if (race->debug) {
        return;  // Skip lap report in debug mode
    }
    
    fprintf(stdout, "\n--- Lap %d Report (Time: %d ms) ---\n", race->lap_leader, race->clock);
    
    // Sort cyclists by position
    sort_cyclists_by_position(race);
    
    // Print cyclist positions for all cyclists still in the race
    for (int i = 0; i < race->k; i++) {
        if (!race->cyclists[i].broken && !race->cyclists[i].eliminated) {
            fprintf(stdout, "Position %2d: Cyclist %2d (Lap: %d, Speed: %d km/h)\n", 
                    race->cyclists[i].final_position, 
                    race->cyclists[i].id, 
                    race->cyclists[i].lap, 
                    race->cyclists[i].current_speed);
        }
    }
    fprintf(stdout, "\n");
}

// Print final race report
void print_final_report(Race *race) {
    fprintf(stdout, "\n--- Final Race Report ---\n");

    // Create temporary array for sorting final ranks
    typedef struct {
        int index;
        int status; // 0: active/winner, 1: eliminated, 2: broken
        int lap; // The lap number they reached
        int final_time; // Time when eliminated or race ended
    } FinalRankCyclist;

    FinalRankCyclist *rankings = (FinalRankCyclist *)malloc(race->k * sizeof(FinalRankCyclist));
    int rank_count = 0;

    // Gather information about all cyclists
    for (int i = 0; i < race->k; i++) {
        rankings[rank_count].index = i;
        if (race->cyclists[i].broken) {
            rankings[rank_count].status = 2;
            rankings[rank_count].lap = race->cyclists[i].broken_lap;
            rankings[rank_count].final_time = 0; // Not using time for broken cyclists
        } else if (race->cyclists[i].eliminated) {
            rankings[rank_count].status = 1;
            rankings[rank_count].lap = race->cyclists[i].lap;
            rankings[rank_count].final_time = race->cyclists[i].final_time;
        } else { // Winner
            rankings[rank_count].status = 0;
            rankings[rank_count].lap = race->cyclists[i].lap;
            rankings[rank_count].final_time = race->clock;
        }
        rank_count++;
    }

    // Sort based on lap count (higher is better), then by status as tiebreaker
    for (int i = 0; i < rank_count - 1; i++) {
        for (int j = 0; j < rank_count - i - 1; j++) {
            bool swap = false;
            
            // Primary sort key: lap count (higher is better)
            if (rankings[j].lap < rankings[j + 1].lap) {
                swap = true;
            } 
            // If same lap count, sort by status (winner > eliminated > broken)
            else if (rankings[j].lap == rankings[j + 1].lap) {
                if (rankings[j].status > rankings[j + 1].status) {
                    swap = true;
                }
                // If same status and both eliminated, higher time is better (eliminated later)
                else if (rankings[j].status == rankings[j + 1].status && 
                        rankings[j].status == 1 && 
                        rankings[j].final_time < rankings[j + 1].final_time) {
                    swap = true;
                }
            }

            if (swap) {
                FinalRankCyclist tmp = rankings[j];
                rankings[j] = rankings[j + 1];
                rankings[j + 1] = tmp;
            }
        }
    }

    // Print final rankings
    int place = 1;
    for (int i = 0; i < rank_count; i++) {
        int idx = rankings[i].index;
        Cyclist *c = &race->cyclists[idx];

        if (c->broken) {
            fprintf(stdout, "Rank %2d: Cyclist %2d - Broke down at lap %d\n",
                    place++, c->id, c->broken_lap);
        } else if (c->eliminated) {
            fprintf(stdout, "Rank %2d: Cyclist %2d - Eliminated at lap %d (Time: %d ms)\n",
                    place++, c->id, c->lap, c->final_time);
        } else { // Winner
            fprintf(stdout, "Rank %2d: Cyclist %2d - WINNER! (Time: %d ms, Laps: %d)\n",
                    place++, c->id, race->clock, c->lap);
        }
    }

    free(rankings);
}

// Check if all cyclists are ready to proceed to next clock tick
bool all_cyclists_ready(Race *race) {
    // With the new approach, cyclists are ready when they've had a chance to process each tick
    // We don't need to check specific speed conditions anymore as that's handled in try_move_cyclist
    return true;
}

// Thread function for each cyclist
void *cyclist_thread(void *arg) {
    int cyclist_idx = *((int *)arg);
    free(arg);
    
    Cyclist *cyclist = &race.cyclists[cyclist_idx];
    
    while (!cyclist->eliminated && !cyclist->broken) {
        // Wait for clock tick
        pthread_mutex_lock(&race.clock_mutex);
        // Just wait for the next clock tick without checking speed
        pthread_cond_wait(&race.clock_cond, &race.clock_mutex);
        pthread_mutex_unlock(&race.clock_mutex);
        
        // Try to move forward - speed checks are now inside try_move_cyclist
        try_move_cyclist(&race, cyclist);
        
        // Signal that cyclist has processed this tick
        pthread_mutex_lock(&race.clock_mutex);
        pthread_cond_broadcast(&race.clock_cond);
        pthread_mutex_unlock(&race.clock_mutex);
    }
    
    return NULL;
}

// Start the race simulation
void start_race(Race *race) {
    // Create threads for cyclists
    for (int i = 0; i < race->k; i++) {
        int *arg = malloc(sizeof(int));
        *arg = i;
        pthread_create(&race->cyclists[i].thread, NULL, cyclist_thread, arg);
    }
    
    int previous_leader_lap = 0;
    
    // Main simulation loop
    while (!is_race_finished(race)) {
        // Advance the clock by 60ms
        pthread_mutex_lock(&race->clock_mutex);
        race->clock += 60;
        pthread_cond_broadcast(&race->clock_cond);
        pthread_mutex_unlock(&race->clock_mutex);
        
        // Wait for all cyclists to finish their moves for this clock tick
        bool all_ready = false;
        while (!all_ready) {
            pthread_mutex_lock(&race->clock_mutex);
            all_ready = all_cyclists_ready(race);
            if (!all_ready) {
                pthread_cond_wait(&race->clock_cond, &race->clock_mutex);
            }
            pthread_mutex_unlock(&race->clock_mutex);
        }
        
        // Print debug information if requested
        if (race->debug) {
            print_track_debug(race);
        } else if (race->lap_leader > previous_leader_lap) {
            // Print lap report when leader completes a new lap
            print_lap_report(race);
            previous_leader_lap = race->lap_leader;
        }
    }
    
    // Determine the winner and final positions
    pthread_mutex_lock(&race->global_mutex);
    sort_cyclists_by_position(race);
    pthread_mutex_unlock(&race->global_mutex);
    
    // Print final report
    print_final_report(race);
    
    // Wait for all threads to finish
    for (int i = 0; i < race->k; i++) {
        if (!race->cyclists[i].broken && !race->cyclists[i].eliminated) {
            pthread_cancel(race->cyclists[i].thread);
        }
        pthread_join(race->cyclists[i].thread, NULL);
    }
}

int main(int argc, char *argv[]) {
    // Check command line arguments
    if (argc < 4 || argc > 5) {
        fprintf(stderr, "Usage: %s d k <i|e> [-debug]\n", argv[0]);
        fprintf(stderr, "  d: track length in meters (100 <= d <= 2500)\n");
        fprintf(stderr, "  k: number of cyclists (5 <= k <= 5*d)\n");
        fprintf(stderr, "  i: use naive approach for synchronization\n");
        fprintf(stderr, "  e: use efficient approach for synchronization\n");
        fprintf(stderr, "  -debug: print debug information\n");
        return 1;
    }
    
    int d = atoi(argv[1]);
    int k = atoi(argv[2]);
    
    // Validate d and k
    if (d < 100 || d > 2500) {
        fprintf(stderr, "Error: track length must be between 100 and 2500 meters\n");
        return 1;
    }
    
    if (k < 5 || k > 5 * d) {
        fprintf(stderr, "Error: number of cyclists must be between 5 and 5*d\n");
        return 1;
    }
    
    // Parse synchronization approach
    bool efficient = false;
    if (strcmp(argv[3], "e") == 0) {
        efficient = true;
    } else if (strcmp(argv[3], "i") == 0) {
        efficient = false;
    } else {
        fprintf(stderr, "Error: synchronization approach must be 'i' (naive) or 'e' (efficient)\n");
        return 1;
    }
    
    // Parse debug flag
    bool debug = false;
    if (argc == 5 && strcmp(argv[4], "-debug") == 0) {
        debug = true;
    }
    
    // Initialize race
    initialize_race(&race, d, k, efficient, debug);
    
    // Start simulation
    start_race(&race);
    
    // Clean up
    cleanup_race(&race);
    
    return 0;
}
