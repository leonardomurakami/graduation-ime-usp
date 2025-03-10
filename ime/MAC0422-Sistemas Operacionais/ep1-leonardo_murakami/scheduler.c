#define _GNU_SOURCE

#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include <limits.h>
#include <sched.h>
#include <time.h>

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

Process processes[MAX_PROCESSES];

int algorithm = -1;
int total_processes = 0;
int remaining_processes = 0;
int quantum_counter = 0;
int context_switches = 0;

time_t actual_time;
time_t start_time;

pthread_mutex_t actual_time_mutex = PTHREAD_MUTEX_INITIALIZER;

void *perform_work(void *args) {
    Process *process = (Process *)args;

    while (true) {
        pthread_mutex_lock(&process->lock);
        while (process->is_preempted) {
            pthread_cond_wait(&process->cond, &process->lock);
        }
        if (process->remaining_dt <= 0) {
            pthread_mutex_unlock(&process->lock);
            break;
        }
        pthread_mutex_unlock(&process->lock);

        int workTime = (algorithm == ROUND_ROBIN && process->remaining_dt > QUANTUM_SIZE) ? QUANTUM_SIZE : process->remaining_dt;
        printf("[Process %s] Working for %d seconds\n", process->name, workTime);
        sleep(workTime);
        

        pthread_mutex_lock(&actual_time_mutex);
        process->remaining_dt -= workTime;
        actual_time = time(NULL);
        if (process->remaining_dt <= 0) {
            printf("[Process %s] Finished at time %ld\n", process->name, actual_time-start_time);
            process->tf = actual_time-start_time;
            process->state = FINISHED;
            remaining_processes--;
        }
        pthread_mutex_unlock(&actual_time_mutex);

        if (algorithm == ROUND_ROBIN) {
            break; // in rr, process works for one quantum at a time
        }
    }

    return NULL;
}


void preemptAndRunSingleCpu(Process* process) {
    pthread_mutex_lock(&process->lock);
    if (process->is_preempted) {
        process->is_preempted = false;
        pthread_cond_signal(&process->cond);
    } else {
        process->state = RUNNING;
        pthread_mutex_unlock(&process->lock);
        pthread_create(&process->thread_id, NULL, perform_work, process);
        pthread_join(process->thread_id, NULL);
        return;
    }
    pthread_mutex_unlock(&process->lock);
}

void preemptAndRun(Process* process) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(0, &cpuset);

    pthread_attr_t attr;
    pthread_attr_init(&attr);
    pthread_attr_setaffinity_np(&attr, sizeof(cpu_set_t), &cpuset);

    pthread_mutex_lock(&process->lock);
    if (process->is_preempted) {
        process->is_preempted = false;
        pthread_cond_signal(&process->cond);
    } else {
        process->state = RUNNING;
        pthread_mutex_unlock(&process->lock);
        pthread_create(&process->thread_id, &attr, perform_work, process);
        pthread_join(process->thread_id, NULL);
        return;
    }
    pthread_mutex_unlock(&process->lock);
    pthread_attr_destroy(&attr);
}

void setupProcesses() {
    for (int i = 0; i < total_processes; i++) {
        pthread_mutex_init(&processes[i].lock, NULL);
        pthread_cond_init(&processes[i].cond, NULL);
        processes[i].is_preempted = false;
        processes[i].state = READY;
        processes[i].remaining_dt = processes[i].dt;
    }
}

void cleanupProcesses() {
    for (int i = 0; i < total_processes; i++) {
        pthread_mutex_destroy(&processes[i].lock);
        pthread_cond_destroy(&processes[i].cond);
    }
}

Process* findNextRoundRobinProcess(int* current_index) {
    int count = total_processes;
    while (count-- > 0) {
        int idx = (*current_index + 1) % total_processes;
        if (processes[idx].state != FINISHED && actual_time-start_time >= processes[idx].t0) {
            *current_index = idx;
            return &processes[idx];
        }
        *current_index = idx;
    }
    return NULL;
}

Process* findNextSJFProcess() {
    int shortestTime = INT_MAX;
    Process* nextProcess = NULL;
    for (int i = 0; i < total_processes; i++) {
        if (processes[i].state != FINISHED && actual_time-start_time >= processes[i].t0 && processes[i].remaining_dt < shortestTime) {
            shortestTime = processes[i].remaining_dt;
            nextProcess = &processes[i];
        }
    }
    return nextProcess;
}

Process* findNextPPProcess() {
    int highestPriority = INT_MAX;
    Process* nextProcess = NULL;
    for (int i = 0; i < total_processes; i++) {
        if (processes[i].state != FINISHED && actual_time-start_time >= processes[i].t0 && processes[i].deadline < highestPriority) {
            highestPriority = processes[i].deadline;
            nextProcess = &processes[i];
        }
    }
    return nextProcess;
}


void executeRoundRobin() {
    setupProcesses();
    int current_index = -1;
    remaining_processes = total_processes;
    Process* prev_process = NULL;
    while (remaining_processes > 0) {
        Process* next_process = findNextRoundRobinProcess(&current_index);
        if (next_process) {
            if (prev_process != NULL && prev_process != next_process) {
                context_switches++;
            }
            prev_process = next_process;
            preemptAndRun(next_process);
        } else {
            sleep(TIME_UNIT);
            actual_time=time(NULL);
        }
    }
    cleanupProcesses();
}


void executeSJF() {
    setupProcesses();
    remaining_processes = total_processes;
    Process* prev_process = NULL;
    while (remaining_processes > 0) {
        Process* next_process = findNextSJFProcess();
        if (next_process) {
            if (prev_process != NULL && prev_process != next_process) {
                context_switches++;
            }
            prev_process = next_process;
            preemptAndRun(next_process);
        } else {
            sleep(TIME_UNIT);
            actual_time=time(NULL);
        }
    }
    cleanupProcesses();
}




void executePriorityScheduling() {
    setupProcesses();
    remaining_processes = total_processes;
    Process* prev_process = NULL;
    while (remaining_processes > 0) {
        Process* next_process = findNextPPProcess();
        if (next_process) {
            if (prev_process != NULL && prev_process != next_process) {
                context_switches++;
            }
            prev_process = next_process;
            preemptAndRun(next_process);
        } else {
            sleep(TIME_UNIT);
            actual_time=time(NULL);
        }
    }
    cleanupProcesses();
}


void executeScheduler(const int schedulerAlgorithm, const char *inputFile, const char *outputFile) {
    remaining_processes = 0;
    total_processes = 0;
    context_switches = 0;
    
    FILE *input = fopen(inputFile, "r");
    FILE *output = fopen(outputFile, "w");
    if (!input || !output) {
        perror("Erro ao abrir arquivos");
        if (input) fclose(input);
        if (output) fclose(output);
        return;
    }

    while (fscanf(input, "%s %d %d %d", processes[total_processes].name, &processes[total_processes].deadline,
                  &processes[total_processes].t0, &processes[total_processes].dt) == 4) {
        total_processes++;
        if (total_processes >= MAX_PROCESSES) break;
    }
    fclose(input);

    
    actual_time = time(NULL);
    start_time = time(NULL);

    switch (schedulerAlgorithm) {
        case ROUND_ROBIN:
            algorithm = ROUND_ROBIN;
            executeRoundRobin();
            break;
        case SHORTEST_JOB_FIRST:
            algorithm = SHORTEST_JOB_FIRST;
            executeSJF();
            break;
        case PRIORITY_SCHEDULING:
            algorithm = PRIORITY_SCHEDULING;
            executePriorityScheduling();
            break;
        default:
            printf("Algoritmo de escalonamento desconhecido.\n");
            return;
    }

    for (int i = 0; i < total_processes; i++) {
        fprintf(output, "%d %d\n", processes[i].tf - processes[i].t0, processes[i].tf);
        // fprintf(output, "%s %d %d\n", processes[i].name, processes[i].tf - processes[i].t0, processes[i].tf);
    }
    fprintf(output, "%d\n", context_switches);
    fclose(output);
}

// int main(int argc, char *argv[]) {
//     if (argc != 4) {
//         fprintf(stderr, "Usage: %s <scheduler_algorithm> <input_file> <output_file>\n", argv[0]);
//         return EXIT_FAILURE;
//     }

//     // Parse the scheduling algorithm
//     int schedulerAlgorithm = atoi(argv[1]);
//     if (schedulerAlgorithm < 1 || schedulerAlgorithm > 3) {
//         fprintf(stderr, "Invalid scheduler algorithm. Please select 1 for SHORTEST_JOB_FIRST, 2 for ROUND_ROBIN, or 3 for PRIORITY_SCHEDULING.\n");
//         return EXIT_FAILURE;
//     }

//     // Assign input and output file names
//     const char *inputFile = argv[2];
//     const char *outputFile = argv[3];

//     // Initialize processes and execute the selected scheduler
//     executeScheduler(schedulerAlgorithm, inputFile, outputFile);

//     return EXIT_SUCCESS;
// }
