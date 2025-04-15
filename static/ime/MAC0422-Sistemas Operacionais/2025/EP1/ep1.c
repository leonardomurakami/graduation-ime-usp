#include "ep1.h"

// Variavel global para o simulador
Simulator simulator;

// Funcao para obter o tempo atual em segundos
double get_current_time() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec + tv.tv_usec / 1000000.0;
}

// Funcao para "consumir" tempo de CPU (operacao de loop que consome ciclos)
void consume_cpu_time(int seconds) {
    double start_time = get_current_time();
    double current_time;
    volatile unsigned long long dummy = 0;
    
    do {
        // Operacao que consome ciclos de CPU - carga intensiva
        for (int i = 0; i < 10000000; i++) {
            dummy += i * i;
            dummy ^= (dummy >> 2);
        }
        
        current_time = get_current_time();
    } while (current_time - start_time < seconds);
}

// Funcao para inicializar o simulador
void init_simulator(Simulator* sim, int scheduler_type, char* input_file, char* output_file, int num_cpus) {
    // Inicializa as variaveis do simulador
    sim->scheduler_type = scheduler_type;
    // Arquivo de entrada
    strncpy(sim->input_file, input_file, 255);
    sim->input_file[255] = '\0';
    // Arquivo de saida
    strncpy(sim->output_file, output_file, 255);
    sim->output_file[255] = '\0';
    // Processos
    sim->num_processes = 0;
    sim->active_processes = 0;
    // Preempcoes
    sim->preemptions = 0;
    // Tempo da simulacao
    sim->simulation_time = 0;
    sim->simulation_done = false;
    sim->simulation_start_time = get_current_time();  // Registra tempo de inicio da simulacao
    
    // Define o numero de CPUs com base no parametro ou no numero disponivel
    if (num_cpus > 0) {
        sim->num_cpus = num_cpus < sysconf(_SC_NPROCESSORS_ONLN) ? num_cpus : sysconf(_SC_NPROCESSORS_ONLN);
    } else {
        // Descobre o numero de CPUs disponiveis
        sim->num_cpus = sysconf(_SC_NPROCESSORS_ONLN);
        if (sim->num_cpus <= 0) {
            sim->num_cpus = 1; // Garante pelo menos uma CPU
        }
    }
        
    // Inicializa as atribuicoes de CPU
    for (int i = 0; i < 64; i++) {
        sim->cpu_assignments[i] = -1; // -1 indica CPU livre
    }
    
    // Inicializa o mutex e a condicao
    pthread_mutex_init(&sim->mutex, NULL);
    pthread_cond_init(&sim->cond, NULL);
}

// Funcao para limpar recursos do simulador
void cleanup_simulator(Simulator* sim) {
    // Libera o mutex e a condicao
    pthread_mutex_destroy(&sim->mutex);
    pthread_cond_destroy(&sim->cond);
    
    // Libera recursos de cada processo
    for (int i = 0; i < sim->num_processes; i++) {
        pthread_mutex_destroy(&sim->processes[i].mutex);
        pthread_cond_destroy(&sim->processes[i].cond);
    }
}

// Funcao para ler o arquivo de trace
int read_trace_file(Simulator* sim) {
    FILE* file = fopen(sim->input_file, "r");
    if (!file) {
        perror("Erro ao abrir arquivo de trace");
        return -1;
    }
    
    int count = 0;
    char name[MAX_PROC_NAME + 1];
    int t0, dt, deadline;
    
    // Le os processos do arquivo
    while (fscanf(file, "%s %d %d %d", name, &t0, &dt, &deadline) == 4 && count < MAX_PROCESSES) {
        Process* proc = &sim->processes[count];
        
        // Copia os dados lidos para a estrutura do processo
        strncpy(proc->name, name, MAX_PROC_NAME);
        proc->name[MAX_PROC_NAME] = '\0';
        proc->t0 = t0;
        proc->dt = dt;
        // Normaliza o deadline adicionando o tempo de inicio da simulacao
        proc->deadline = deadline;
        
        // Inicializa campos adicionais
        proc->remaining_time = dt;
        proc->start_time = -1;
        proc->finish_time = -1;
        proc->is_running = 0;
        proc->is_completed = 0;
        proc->cpu_assigned = -1;
        
        // Inicializa mutex e condicao para o processo
        pthread_mutex_init(&proc->mutex, NULL);
        pthread_cond_init(&proc->cond, NULL);
        
        count++;
    }
    
    sim->num_processes = count;
    fclose(file);
    
    return count;
}

// Funcao para escrever os resultados no arquivo de saida
int write_results_file(Simulator* sim) {
    FILE* file = fopen(sim->output_file, "w");
    if (!file) {
        perror("Erro ao abrir arquivo de saida");
        return -1;
    }
    
    // Escreve uma linha para cada processo
    for (int i = 0; i < sim->num_processes; i++) {
        Process* proc = &sim->processes[i];
        int tr = proc->finish_time - proc->t0; // Tempo de resposta (tf - t0)
        int cumpriu = (proc->finish_time <= proc->deadline) ? 1 : 0; // Verificacao de deadline
        
        fprintf(file, "%s %d %d %d\n", proc->name, tr, proc->finish_time, cumpriu);
    }
    
    // Escreve a linha extra com o numero de preempcoes
    fprintf(file, "%d\n", sim->preemptions);
    
    fclose(file);
    return 0;
}

// Funcao para imprimir o estado atual das atribuicoes de CPU
void print_cpu_assignments(Simulator* sim) {
    pthread_mutex_lock(&sim->mutex);
    printf("\nCPU Assignments:\n");
    for (int i = 0; i < sim->num_cpus; i++) {
        if (sim->cpu_assignments[i] == -1) {
            printf("CPU %d: [FREE]\n", i);
        } else {
            Process* proc = &sim->processes[sim->cpu_assignments[i]];
            printf("CPU %d: Process %s (Remaining: %d, Deadline: %d)\n",
                   i, proc->name, proc->remaining_time, proc->deadline);
        }
    }
    printf("\n");
    pthread_mutex_unlock(&sim->mutex);
}

// Funcao para atribuir uma CPU a um processo de forma atomica
// Retorna o ID da CPU atribuida ou -1 se nao houver CPU disponivel
static int assign_cpu(Simulator* sim, int process_id) {
    pthread_mutex_lock(&sim->mutex);
    int assigned_cpu = -1;
    
    // Procura uma CPU livre
    for (int i = 0; i < sim->num_cpus; i++) {
        if (sim->cpu_assignments[i] == -1) {
            sim->cpu_assignments[i] = process_id;
            assigned_cpu = i;
            break;
        }
    }
    
    pthread_mutex_unlock(&sim->mutex);
    return assigned_cpu;
}

// Funcao para liberar uma CPU de forma atomica
static void free_cpu(Simulator* sim, int cpu_id) {
    if (cpu_id >= 0 && cpu_id < sim->num_cpus) {
        pthread_mutex_lock(&sim->mutex);
        sim->cpu_assignments[cpu_id] = -1;
        pthread_mutex_unlock(&sim->mutex);
    }
}

// Funcao de execucao do processo (thread)
void* process_execution(void* arg) {
    Process* proc = (Process*)arg;
    
    while (!proc->is_completed) {
        pthread_mutex_lock(&proc->mutex);
        
        // Se nao estiver rodando, aguarda sinal do escalonador
        if (!proc->is_running) {
            pthread_cond_wait(&proc->cond, &proc->mutex);
            pthread_mutex_unlock(&proc->mutex);
            continue;
        }
        
        pthread_mutex_unlock(&proc->mutex);
        
        // Executa o processo (consome CPU)
        consume_cpu_time(1); // Executa por 1 segundo por vez
        
        pthread_mutex_lock(&proc->mutex);
        
        // Atualiza o tempo restante
        if (proc->remaining_time > 0) {
            proc->remaining_time--;
            
            // Se o processo terminou
            if (proc->remaining_time == 0) {
                proc->is_completed = 1;
                proc->is_running = 0;
                
                pthread_mutex_lock(&simulator.mutex);
                proc->finish_time = (int)(get_current_time() - simulator.simulation_start_time);
                simulator.active_processes--;
                pthread_mutex_unlock(&simulator.mutex);
                
                // Libera a CPU
                if (proc->cpu_assigned >= 0) {
                    free_cpu(&simulator, proc->cpu_assigned);
                    proc->cpu_assigned = -1;
                }
                
                pthread_cond_signal(&simulator.cond);
            }
        }
        
        pthread_mutex_unlock(&proc->mutex);
    }
    
    return NULL;
}

// Implementacao do escalonador FCFS (First-Come First-Served)
void* fcfs_scheduler(void* arg) {
    Simulator* sim = (Simulator*)arg;
    double simulation_start = get_current_time();
    int current_time;
    int last_debug_time = -1;
    
    if (sim->debug_mode) {
        printf("\n=== FCFS Scheduler Debug ===\n");
        printf("Number of CPUs: %d\n", sim->num_cpus);
        printf("Number of processes: %d\n", sim->num_processes);
        
        printf("\nProcess arrival order:\n");
        for (int i = 0; i < sim->num_processes; i++) {
            printf("Process %s: t0=%d, dt=%d, deadline=%d\n", 
                   sim->processes[i].name, 
                   sim->processes[i].t0,
                   sim->processes[i].dt,
                   sim->processes[i].deadline);
        }
    }
    
    while (1) {
        // Atualiza tempo atual
        current_time = (int)(get_current_time() - simulation_start);
        sim->simulation_time = current_time;
        
        // Saida de debug apenas quando o tempo muda
        if (sim->debug_mode && current_time != last_debug_time) {
            printf("\nTime: %d\n", current_time);
            printf("Active processes: %d\n", sim->active_processes);
            print_cpu_assignments(sim);
            last_debug_time = current_time;
        }
        
        // Verifica processos completados
        bool all_completed = true;
        for (int i = 0; i < sim->num_processes; i++) {
            pthread_mutex_lock(&sim->processes[i].mutex);
            if (!sim->processes[i].is_completed) {
                all_completed = false;
                pthread_mutex_unlock(&sim->processes[i].mutex);
                break;
            }
            pthread_mutex_unlock(&sim->processes[i].mutex);
        }
        
        if (all_completed) {
            if (sim->debug_mode) {
                printf("\n=== Simulacao Completa ===\n");
            }
            sim->simulation_done = true;
            break;
        }
        
        // Tenta escalonar novos processos
        for (int i = 0; i < sim->num_processes; i++) {
            Process* proc = &sim->processes[i];
            
            pthread_mutex_lock(&proc->mutex);
            
            // Pula se o processo nao esta pronto, ja esta rodando, ou completado
            if (current_time < proc->t0 || proc->is_running || proc->is_completed || proc->start_time != -1) {
                pthread_mutex_unlock(&proc->mutex);
                continue;
            }
            
            // Tenta atribuir uma CPU
            int cpu_id = assign_cpu(sim, i);
            if (cpu_id >= 0) {
                if (sim->debug_mode) {
                    printf("Iniciando processo %s na CPU %d no tempo %d\n", proc->name, cpu_id, current_time);
                }
                
                // Inicializa processo
                proc->start_time = current_time;
                proc->is_running = 1;
                proc->cpu_assigned = cpu_id;
                
                // Cria thread e inicia processo
                pthread_create(&proc->thread, NULL, process_execution, proc);
                pthread_cond_signal(&proc->cond);
                
                sim->active_processes++;
            }
            
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Pequeno sleep para evitar espera ocupada
        usleep(100000); // 100ms sleep
    }
    
    return NULL;
}

// Implementacao do escalonador SRTN (Shortest Remaining Time Next)
void* srtn_scheduler(void* arg) {
    Simulator* sim = (Simulator*)arg;
    double simulation_start = get_current_time();
    int current_time;
    int last_debug_time = -1;  // Rastreia ultimo tempo de saida de debug
    
    if (sim->debug_mode) {
        printf("\n=== SRTN Scheduler Debug ===\n");
        printf("Numero de CPUs: %d\n", sim->num_cpus);
        printf("Numero de processos: %d\n", sim->num_processes);
        
        printf("\nOrdem de chegada dos processos:\n");
        for (int i = 0; i < sim->num_processes; i++) {
            printf("Processo %s: t0=%d, dt=%d, deadline=%d\n", 
                   sim->processes[i].name, 
                   sim->processes[i].t0,
                   sim->processes[i].dt,
                   sim->processes[i].deadline);
        }
    }
    
    while (1) {
        // Atualiza tempo atual
        current_time = (int)(get_current_time() - simulation_start);
        sim->simulation_time = current_time;
        
        // Saida de debug apenas quando o tempo muda
        if (sim->debug_mode && current_time != last_debug_time) {
            printf("\nTempo: %d\n", current_time);
            printf("Processos ativos: %d\n", sim->active_processes);
            print_cpu_assignments(sim);
            last_debug_time = current_time;
        }
        
        // Verifica processos completados
        bool all_completed = true;
        for (int i = 0; i < sim->num_processes; i++) {
            pthread_mutex_lock(&sim->processes[i].mutex);
            if (!sim->processes[i].is_completed) {
                all_completed = false;
                pthread_mutex_unlock(&sim->processes[i].mutex);
                break;
            }
            pthread_mutex_unlock(&sim->processes[i].mutex);
        }
        
        if (all_completed) {
            if (sim->debug_mode) {
                printf("\n=== Simulacao Completa ===\n");
            }
            sim->simulation_done = true;
            break;
        }
        
        // Identifica processos disponiveis e ordena por tempo restante
        int available_processes[MAX_PROCESSES];
        int num_available = 0;
        
        for (int i = 0; i < sim->num_processes; i++) {
            Process* proc = &sim->processes[i];
            
            pthread_mutex_lock(&proc->mutex);
            if (current_time >= proc->t0 && !proc->is_completed && !proc->is_running) {
                available_processes[num_available++] = i;
            }
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Ordena por tempo restante
        for (int i = 0; i < num_available; i++) {
            for (int j = i + 1; j < num_available; j++) {
                Process* proc1 = &sim->processes[available_processes[i]];
                Process* proc2 = &sim->processes[available_processes[j]];
                
                pthread_mutex_lock(&proc1->mutex);
                int rt1 = proc1->remaining_time;
                pthread_mutex_unlock(&proc1->mutex);
                
                pthread_mutex_lock(&proc2->mutex);
                int rt2 = proc2->remaining_time;
                pthread_mutex_unlock(&proc2->mutex);
                
                if (rt1 > rt2) {
                    int temp = available_processes[i];
                    available_processes[i] = available_processes[j];
                    available_processes[j] = temp;
                }
            }
        }
        
        // Tenta escalonar processos
        for (int i = 0; i < num_available; i++) {
            Process* proc = &sim->processes[available_processes[i]];
            
            pthread_mutex_lock(&proc->mutex);
            
            // Pula se o processo ja esta rodando ou completado
            if (proc->is_running || proc->is_completed) {
                pthread_mutex_unlock(&proc->mutex);
                continue;
            }
            
            // Tenta atribuir uma CPU
            int cpu_id = assign_cpu(sim, available_processes[i]);
            if (cpu_id >= 0) {
                if (sim->debug_mode) {
                    printf("Iniciando processo %s na CPU %d no tempo %d (restante: %d)\n", 
                           proc->name, cpu_id, current_time, proc->remaining_time);
                }
                
                // Inicializa processo se ainda nao foi iniciado
                if (proc->start_time == -1) {
                    proc->start_time = current_time;
                    pthread_create(&proc->thread, NULL, process_execution, proc);
                }
                
                proc->is_running = 1;
                proc->cpu_assigned = cpu_id;
                pthread_cond_signal(&proc->cond);
                
                sim->active_processes++;
            }
            
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Verifica oportunidades de preempcao
        for (int cpu_id = 0; cpu_id < sim->num_cpus; cpu_id++) {
            pthread_mutex_lock(&sim->mutex);
            int running_proc_id = sim->cpu_assignments[cpu_id];
            pthread_mutex_unlock(&sim->mutex);
            
            if (running_proc_id != -1 && num_available > 0) {
                Process* running_proc = &sim->processes[running_proc_id];
                Process* shortest_proc = &sim->processes[available_processes[0]];
                
                pthread_mutex_lock(&running_proc->mutex);
                int running_time = running_proc->remaining_time;
                pthread_mutex_unlock(&running_proc->mutex);
                
                pthread_mutex_lock(&shortest_proc->mutex);
                int shortest_time = shortest_proc->remaining_time;
                pthread_mutex_unlock(&shortest_proc->mutex);
                
                if (shortest_time < running_time) {
                    // Interrompe o processo em execucao
                    pthread_mutex_lock(&running_proc->mutex);
                    running_proc->is_running = 0;
                    free_cpu(sim, cpu_id);
                    sim->preemptions++;
                    pthread_mutex_unlock(&running_proc->mutex);
                }
            }
        }
        
        // Pequeno sleep para evitar espera ocupada
        usleep(100000); // 100ms sleep
    }
    
    return NULL;
}

// Implementacao do escalonador com prioridade baseado em deadline
void* priority_scheduler(void* arg) {
    Simulator* sim = (Simulator*)arg;
    double simulation_start = get_current_time();
    int current_time;
    int last_debug_time = -1;  // Rastreia ultimo tempo de saida de debug
    
    if (sim->debug_mode) {
        printf("\n=== Escalonador por Prioridade Debug ===\n");
        printf("Numero de CPUs: %d\n", sim->num_cpus);
        printf("Numero de processos: %d\n", sim->num_processes);
        
        printf("\nOrdem de chegada dos processos:\n");
        for (int i = 0; i < sim->num_processes; i++) {
            printf("Processo %s: t0=%d, dt=%d, deadline=%d\n", 
                   sim->processes[i].name, 
                   sim->processes[i].t0,
                   sim->processes[i].dt,
                   sim->processes[i].deadline);
        }
    }
    
    while (1) {
        // Atualiza tempo atual
        current_time = (int)(get_current_time() - simulation_start);
        sim->simulation_time = current_time;
        
        // Saida de debug apenas quando o tempo muda
        if (sim->debug_mode && current_time != last_debug_time) {
            printf("\nTempo: %d\n", current_time);
            printf("Processos ativos: %d\n", sim->active_processes);
            print_cpu_assignments(sim);
            last_debug_time = current_time;
        }
        
        // Verifica processos completados
        bool all_completed = true;
        for (int i = 0; i < sim->num_processes; i++) {
            pthread_mutex_lock(&sim->processes[i].mutex);
            if (!sim->processes[i].is_completed) {
                all_completed = false;
                pthread_mutex_unlock(&sim->processes[i].mutex);
                break;
            }
            pthread_mutex_unlock(&sim->processes[i].mutex);
        }
        
        if (all_completed) {
            if (sim->debug_mode) {
                printf("\n=== Simulacao Completa ===\n");
            }
            sim->simulation_done = true;
            break;
        }
        
        // Identifica processos disponiveis e calcula prioridades
        int available_processes[MAX_PROCESSES];
        int priorities[MAX_PROCESSES];
        int num_available = 0;
        
        for (int i = 0; i < sim->num_processes; i++) {
            Process* proc = &sim->processes[i];
            
            pthread_mutex_lock(&proc->mutex);
            if (current_time >= proc->t0 && !proc->is_completed && !proc->is_running) {
                available_processes[num_available] = i;
                // Prioridade = deadline - (tempo_atual + tempo_restante)
                priorities[num_available] = proc->deadline - (current_time + proc->remaining_time);
                num_available++;
            }
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Ordena por prioridade (maior prioridade = menor tempo de folga)
        for (int i = 0; i < num_available; i++) {
            for (int j = i + 1; j < num_available; j++) {
                if (priorities[i] > priorities[j]) {
                    // Troca prioridades
                    int temp_prio = priorities[i];
                    priorities[i] = priorities[j];
                    priorities[j] = temp_prio;
                    
                    // Troca processos
                    int temp_proc = available_processes[i];
                    available_processes[i] = available_processes[j];
                    available_processes[j] = temp_proc;
                }
            }
        }
        
        // Tenta escalonar processos
        for (int i = 0; i < num_available; i++) {
            Process* proc = &sim->processes[available_processes[i]];
            
            pthread_mutex_lock(&proc->mutex);
            
            // Pula se o processo ja esta rodando ou completado
            if (proc->is_running || proc->is_completed) {
                pthread_mutex_unlock(&proc->mutex);
                continue;
            }
            
            // Tenta atribuir uma CPU
            int cpu_id = assign_cpu(sim, available_processes[i]);
            if (cpu_id >= 0) {
                if (sim->debug_mode) {
                    printf("Iniciando processo %s na CPU %d no tempo %d (folga: %d)\n", 
                           proc->name, cpu_id, current_time, priorities[i]);
                }
                
                // Inicializa processo se ainda nao foi iniciado
                if (proc->start_time == -1) {
                    proc->start_time = current_time;
                    pthread_create(&proc->thread, NULL, process_execution, proc);
                }
                
                proc->is_running = 1;
                proc->cpu_assigned = cpu_id;
                pthread_cond_signal(&proc->cond);
                
                sim->active_processes++;
            }
            
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Verifica oportunidades de preempcao
        for (int cpu_id = 0; cpu_id < sim->num_cpus; cpu_id++) {
            pthread_mutex_lock(&sim->mutex);
            int running_proc_id = sim->cpu_assignments[cpu_id];
            pthread_mutex_unlock(&sim->mutex);
            
            if (running_proc_id != -1 && num_available > 0) {
                Process* running_proc = &sim->processes[running_proc_id];
                
                pthread_mutex_lock(&running_proc->mutex);
                int running_slack = running_proc->deadline - (current_time + running_proc->remaining_time);
                pthread_mutex_unlock(&running_proc->mutex);
                
                if (priorities[0] < running_slack) {
                    // Interrompe o processo em execucao
                    pthread_mutex_lock(&running_proc->mutex);
                    running_proc->is_running = 0;
                    free_cpu(sim, cpu_id);
                    sim->preemptions++;
                    pthread_mutex_unlock(&running_proc->mutex);
                }
            }
        }
        
        // Small sleep to prevent busy waiting
        usleep(100000); // 100ms sleep
    }
    
    return NULL;
}

// Funcao para iniciar a simulacao
void start_simulation(Simulator* sim) {
    pthread_t scheduler_thread;
    
    // Escolhe o escalonador com base no tipo especificado
    switch (sim->scheduler_type) {
        case 1:
            pthread_create(&scheduler_thread, NULL, fcfs_scheduler, sim);
            break;
        case 2:
            pthread_create(&scheduler_thread, NULL, srtn_scheduler, sim);
            break;
        case 3:
            pthread_create(&scheduler_thread, NULL, priority_scheduler, sim);
            break;
        default:
            fprintf(stderr, "Tipo de escalonador invalido: %d\n", sim->scheduler_type);
            return;
    }
    
    // Aguarda o fim da simulacao
    while (!sim->simulation_done) {
        sleep(1);
    }
    
    // Aguarda o termino do escalonador
    pthread_join(scheduler_thread, NULL);
    
    // Aguarda o termino de todos os processos
    for (int i = 0; i < sim->num_processes; i++) {
        if (sim->processes[i].start_time != -1) {
            pthread_join(sim->processes[i].thread, NULL);
        }
    }
}

int main(int argc, char* argv[]) {
    // Valores padrao
    int scheduler_type = 0;
    char* input_file = NULL;
    char* output_file = NULL;
    int num_cpus = 0;  // 0 significa usar todas as CPUs disponiveis
    int debug_mode = 0;

    // Verifica numero minimo de argumentos
    if (argc < 4) {
        fprintf(stderr, "Uso: %s <tipo_escalonador> <arquivo_entrada> <arquivo_saida> [--cpu <n>] [--debug]\n", argv[0]);
        fprintf(stderr, "Tipos de escalonador:\n");
        fprintf(stderr, "  1 - First-Come First-Served (FCFS)\n");
        fprintf(stderr, "  2 - Shortest Remaining Time Next (SRTN)\n");
        fprintf(stderr, "  3 - Escalonamento baseado em prioridade (deadline)\n");
        fprintf(stderr, "Opcoes:\n");
        fprintf(stderr, "  --cpu <n>    : Numero de CPUs a usar (padrao: todas disponiveis)\n");
        fprintf(stderr, "  --debug      : Ativa modo debug\n");
        return EXIT_FAILURE;
    }

    // Obtem argumentos obrigatorios
    scheduler_type = atoi(argv[1]);
    input_file = argv[2];
    output_file = argv[3];

    // Valida tipo de escalonador
    if (scheduler_type < 1 || scheduler_type > 3) {
        fprintf(stderr, "Tipo de escalonador invalido: %d\n", scheduler_type);
        return EXIT_FAILURE;
    }

    // Processa argumentos opcionais
    for (int i = 4; i < argc; i++) {
        if (strcmp(argv[i], "--cpu") == 0 && i + 1 < argc) {
            num_cpus = atoi(argv[++i]);
            if (num_cpus <= 0) {
                fprintf(stderr, "Numero de CPUs deve ser maior que 0. Usando todas as CPUs disponiveis.\n");
                num_cpus = 0;
            }
        } else if (strcmp(argv[i], "--debug") == 0) {
            debug_mode = 1;
        } else {
            fprintf(stderr, "Opcao desconhecida: %s\n", argv[i]);
            return EXIT_FAILURE;
        }
    }

    // Inicializa simulador
    init_simulator(&simulator, scheduler_type, input_file, output_file, num_cpus);
    simulator.debug_mode = debug_mode;

    // Le o arquivo de trace
    if (read_trace_file(&simulator) <= 0) {
        fprintf(stderr, "Erro ao ler o arquivo de trace ou arquivo vazio.\n");
        return EXIT_FAILURE;
    }
    
    // Inicia a simulacao
    start_simulation(&simulator);
    
    // Escreve os resultados
    if (write_results_file(&simulator) != 0) {
        fprintf(stderr, "Erro ao escrever o arquivo de saida.\n");
        return EXIT_FAILURE;
    }
    
    // Limpa os recursos
    cleanup_simulator(&simulator);
    
    return EXIT_SUCCESS;
}