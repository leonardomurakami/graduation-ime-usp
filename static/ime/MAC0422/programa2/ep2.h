#ifndef EP2_H
#define EP2_H

#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h> // For usleep
#include <string.h>
#include <time.h>   // For seeding rand_r
#include <math.h>   // For ceil

// --- Constants ---
#define MAX_LANES 10                // Max cyclists side-by-side per meter
#define BASE_SPEED 30               // km/h
#define FAST_SPEED 60               // km/h
#define TIME_STEP_MS 60             // Simulation time granularity
#define METER_TIME_FAST_MS 60       // Time to cross 1m at 60km/h
#define METER_TIME_SLOW_MS 120      // Time to cross 1m at 30km/h
#define BREAK_CHECK_LAPS 5          // Check for breaking every 5 laps
#define BREAK_PROBABILITY 0.10      // 10% chance of breaking
#define SMALL_TRACK_THRESHOLD 1000  // Use single mutex for tracks smaller than this
#define MUTEX_TIMEOUT_SEC 1         // Timeout for mutex operations in seconds
#define BARRIER_TIMEOUT_SEC 2       // Timeout for barrier operations in seconds

// --- Data Structures ---
// Cyclist state enum
typedef enum {
    RUNNING,    // Actively racing
    BROKEN,     // Quit due to mechanical failure/fatigue
    ELIMINATED, // Removed due to race rules
    FINISHED    // Completed the race (includes winner)
} CyclistState;

// Structure to hold information about each cyclist
typedef struct {
    int id;                                 // Unique identifier (0 to k-1)
    pthread_t thread_id;                    // POSIX thread ID
    CyclistState state;                     // Current state of the cyclist
    int current_speed;                      // Current target speed (30 or 60 km/h)
    int effective_speed;                    // Actual speed considering blocking (30 or 60 km/h)
    int current_meter;                      // Current position on the track (0 to d-1)
    int current_lane;                       // Current lane (0 to MAX_LANES-1)
    int laps_completed;                     // Number of laps completed
    unsigned long long time_to_move_ms;     // Time remaining to move to the next meter
    unsigned long long last_crossing_time;  // Simulation time when last crossing finish line
    int lap_rank;                           // Rank within the current lap (updated by main thread)
    bool needs_main_update;                 // Flag for main thread to check state changes
    unsigned int rand_seed;                 // Seed for thread-safe random number generation
    int broken_lap;                         // Lap number when the cyclist broke (-1 if not broken)
} CyclistInfo;

// Structure to hold final results
typedef struct {
    int id;
    CyclistState final_state;
    int rank;                           // Final position (1st, 2nd, ...) or -1 if DNF
    unsigned long long finish_time_ms;  // Time of final lap completion
    int completed_laps;                 // Laps completed
    int broken_lap;                     // Lap when broken, or -1
} ResultInfo;

// Structure for lap rankings temporary storage
typedef struct {
    int id;
    unsigned long long crossing_time;
} LapRankEntry;


// --- Global Variables ---
// Declared as extern here, defined in ep2.c

extern int d;                   // Track length
extern int k;                   // Initial number of cyclists
extern char concurrency_mode;   // 'i' (naive) or 'e' (efficient)
extern bool debug_mode;         // True if -debug flag is present

extern int **pista;                 // 2D array representing the track: pista[meter][lane] = cyclist_id or -1
extern CyclistInfo *cyclists;       // Array of cyclist information
extern ResultInfo *final_results;   // Array to store final rankings

extern int num_active_cyclists;                 // Number of cyclists currently RUNNING
extern int num_finished_cyclists;               // Counter for final results array
extern unsigned long long simulation_time_ms;   // Global simulation clock
extern bool race_over;                          // Flag to signal race completion
extern int current_lap_leader;                  // Tracks the lap number of the leading cyclist

// Synchronization primitives
extern pthread_mutex_t global_lock;             // Used in naive mode and for shared counters
extern pthread_mutex_t *track_mutexes;          // Array of mutexes for efficient mode (one per meter)
extern pthread_mutex_t print_mutex;             // Protects console output
extern pthread_mutex_t results_mutex;           // Protects access to final_results and num_finished_cyclists
extern pthread_barrier_t step_barrier_start;    // Cyclists wait here before calculating move
extern pthread_barrier_t step_barrier_end;      // Cyclists wait here after attempting move

// --- Function Prototypes ---

void *ciclista_func(void *arg);                                                                                             // Cyclist thread function
void initialize_simulation(int argc, char *argv[]);                                                                         // Initializes global state, track, cyclists
void initialize_cyclist_positions();                                                                                        // Sets starting positions
void run_simulation();                                                                                                      // Main simulation loop
void cleanup_simulation();                                                                                                  // Frees memory, destroys mutexes/barriers
void print_track_state();                                                                                                   // Prints track state (for debug mode)
void print_lap_report();                                                                                                    // Prints report at the end of each lap
void print_final_report();                                                                                                  // Prints final rankings
int compare_lap_ranks(const void *a, const void *b);                                                                        // For qsort
int compare_final_ranks(const void *a, const void *b);                                                                      // For qsort
void handle_eliminations(int lap_num);                                                                                      // Handles elimination logic
void record_final_result(int cyclist_id, CyclistState state, int rank, unsigned long long time, int laps, int broken_lap);  // Records result

// Helper for random numbers
int get_random_int(int min, int max, unsigned int *seedp);
double get_random_double(unsigned int *seedp);


#endif // EP2_H