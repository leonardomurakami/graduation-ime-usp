#ifndef EP2_H
#define EP2_H

#include <pthread.h>
#include <stdbool.h>

#define MAX_SIDE_BY_SIDE 10
#define MAX_CYCLISTS 12500  // Maximum possible cyclists (5 * 2500)
#define LAP_COMPLETION_BUFFER_SIZE 1000  // Size of circular buffer for lap completions

typedef struct {
    int id;                  // Cyclist identifier
    int position;            // Current position in the track
    int lane;                // Current lane (0 is innermost)
    int lap;                 // Current lap
    int last_lap_time;       // Time when the last lap was completed
    int last_speed;          // Speed in the last lap (30 or 60 km/h)
    int current_speed;       // Current speed (30 or 60 km/h)
    bool eliminated;         // Whether the cyclist is eliminated
    bool broken;             // Whether the cyclist has broken down
    int broken_lap;          // Lap when the cyclist broke down
    int final_position;      // Final position in the race
    int final_time;          // Time when the cyclist finished the race
    pthread_t thread;        // Thread identifier
    pthread_mutex_t mutex;   // Mutex for cyclist state
} Cyclist;

// Structure to track elimination lap completions
typedef struct {
    int cyclist_id;          // ID of the cyclist who completed the lap
    int lap_number;          // The lap number that was completed
    int completion_time;     // Time when the lap was completed
    pthread_mutex_t mutex;   // Mutex for this completion record
} LapCompletion;

typedef struct {
    int d;                   // Track length in meters
    int k;                   // Number of cyclists
    bool efficient;          // Whether to use efficient or naive approach
    bool debug;              // Whether to print debug information
    int clock;               // Global clock (in ms)
    int lap_leader;          // Current lap of the race leader
    int cyclists_in_race;    // Number of cyclists still in the race
    Cyclist *cyclists;       // Array of cyclists
    int **track;             // Track matrix: track[position][lane] = cyclist_id or -1 if empty
    pthread_mutex_t *track_mutex;  // Mutex for each position of the track (efficient approach)
    pthread_mutex_t global_mutex;  // Mutex for global variables (cyclists_in_race, elimination state)
    pthread_mutex_t clock_mutex;   // Mutex for clock
    pthread_cond_t clock_cond;     // Condition variable for clock
    pthread_mutex_t leader_mutex;  // Mutex for race leader updates

    // State for "Miss and out" elimination logic
    int current_elimination_lap;    // The even lap we are currently tracking for elimination (starts at 2)
    LapCompletion *lap_completions; // Circular buffer to track lap completions
    int completion_head;            // Index of the oldest completion in the buffer
    int completion_tail;            // Index where the next completion will be written
    int num_completions;            // Number of valid completions in the buffer
    pthread_mutex_t completion_mutex; // Mutex for lap completion buffer
} Race;

// Function prototypes
void *cyclist_thread(void *arg);
void initialize_race(Race *race, int d, int k, bool efficient, bool debug);
void start_race(Race *race);
void cleanup_race(Race *race);
void print_track_debug(Race *race);
void print_lap_report(Race *race);
void print_final_report(Race *race);
void check_eliminations(Race *race);
bool is_race_finished(Race *race);
bool all_cyclists_ready(Race *race);
int random_between(int min, int max);
void update_cyclist_speed(Cyclist *cyclist);
bool check_cyclist_breakdown(Cyclist *cyclist);
bool try_move_cyclist(Race *race, Cyclist *cyclist);
bool can_overtake(Race *race, Cyclist *cyclist, int target_position);
void sort_cyclists_by_position(Race *race);

#endif /* EP2_H */
