#ifndef EP1_H
#define EP1_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>
#include <signal.h>
#include <errno.h>
#include <stdbool.h>
#include <sched.h>    // Para CPU_ZERO e CPU_SET

// Definição de constantes
#define MAX_PROC_NAME 32
#define MAX_PROCESSES 100

// Estrutura para representar um processo
typedef struct {
    char name[MAX_PROC_NAME + 1];  // Nome do processo (+1 para o \0)
    int t0;                        // Tempo de chegada
    int dt;                        // Tempo de execução necessário
    int deadline;                  // Tempo limite
    
    // Campos adicionais para controle durante a execução
    pthread_t thread;              // Thread associada ao processo
    int remaining_time;            // Tempo restante de execução
    int start_time;                // Tempo real em que o processo começou a executar
    int finish_time;               // Tempo real em que o processo terminou de executar
    int is_running;                // Flag para indicar se o processo está em execução
    int is_completed;              // Flag para indicar se o processo foi concluído
    int cpu_assigned;              // Núcleo de CPU atribuído
    pthread_mutex_t mutex;         // Mutex para controle de acesso às variáveis do processo
    pthread_cond_t cond;           // Condição para controle de execução do processo
} Process;

// Estrutura para controle global do simulador
typedef struct {
    int scheduler_type;            // Tipo de escalonador (1=FCFS, 2=SRTN, 3=Prioridade)
    char input_file[256];          // Nome do arquivo de entrada
    char output_file[256];         // Nome do arquivo de saída
    int num_processes;             // Número total de processos
    Process processes[MAX_PROCESSES]; // Array de processos
    int active_processes;          // Número de processos ativos
    int simulation_time;           // Tempo atual da simulação
    int preemptions;               // Número de preempções
    int num_cpus;                  // Número de CPUs disponíveis
    int cpu_assignments[64];       // Mapeamento de CPUs para processos
    pthread_mutex_t mutex;         // Mutex para controle de acesso às variáveis do simulador
    pthread_cond_t cond;           // Condição para controle de execução do simulador
    bool simulation_done;          // Flag para indicar o fim da simulação
    double simulation_start_time;  // Tempo de início da simulação
} Simulator;

// Funções de escalonamento
void* fcfs_scheduler(void* arg);
void* srtn_scheduler(void* arg);
void* priority_scheduler(void* arg);

// Funções de processo
void* process_execution(void* arg);

// Funções auxiliares
int read_trace_file(Simulator* sim);
int write_results_file(Simulator* sim);
void init_simulator(Simulator* sim, int scheduler_type, char* input_file, char* output_file, int num_cpus);
void cleanup_simulator(Simulator* sim);
void start_simulation(Simulator* sim);

#endif // EP1_H