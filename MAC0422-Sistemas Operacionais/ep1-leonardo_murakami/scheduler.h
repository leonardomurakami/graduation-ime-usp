#ifndef SCHEDULER_H
#define SCHEDULER_H

#include <pthread.h>
#include <limits.h>
#include <stdbool.h>

#define MAX_PROCESSES 100
#define NUM_THREADS 5
#define QUANTUM_SIZE 2
#define TIME_UNIT 1

#define SHORTEST_JOB_FIRST 1
#define ROUND_ROBIN 2
#define PRIORITY_SCHEDULING 3

typedef enum {READY, RUNNING, FINISHED} State;

typedef struct {
    // information
    char name[17];
    pthread_t thread_id;
    // time
    int deadline;
    int t0;
    int dt;
    int tf;
    int remaining_dt;
    // state
    State state;
    // pthread preemption atts
    pthread_mutex_t lock;
    pthread_cond_t cond;
    bool is_preempted;
} Process;

extern Process processes[MAX_PROCESSES];
extern int algorithm;
extern int total_processes;
extern int remaining_processes;
extern int actual_time;
extern int quantum_counter;

extern pthread_mutex_t actual_time_mutex;

void *perform_work(void *args);
void preemptAndRun(Process* process);
void setupProcesses();
void cleanupProcesses();
Process* findNextRoundRobinProcess(int* current_index);
Process* findNextSJFProcess();
Process* findNextPPProcess();
void executeRoundRobin();
void executeSJF();
void executePriorityScheduling();
void executeScheduler(const int schedulerAlgorithm, const char *inputFile, const char *outputFile);

#endif /* SCHEDULER_H */
