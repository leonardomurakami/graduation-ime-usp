#include "ep1.h"

// Variável global para o simulador
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
    sim->simulation_start_time = get_current_time();  // Record simulation start time
    
    // Define o número de CPUs com base no parâmetro ou no número disponível
    if (num_cpus > 0) {
        sim->num_cpus = num_cpus;
    } else {
        // Descobre o número de CPUs disponíveis
        sim->num_cpus = sysconf(_SC_NPROCESSORS_ONLN);
        if (sim->num_cpus <= 0) {
            sim->num_cpus = 1; // Garante pelo menos uma CPU
        }
    }
    
    printf("Simulação utilizando %d CPU(s)\n", sim->num_cpus);
    
    // Inicializa as atribuições de CPU
    for (int i = 0; i < 64; i++) {
        sim->cpu_assignments[i] = -1; // -1 indica CPU livre
    }
    
    // Inicializa o mutex e a condição
    pthread_mutex_init(&sim->mutex, NULL);
    pthread_cond_init(&sim->cond, NULL);
}

// Função para limpar recursos do simulador
void cleanup_simulator(Simulator* sim) {
    // Libera o mutex e a condição
    pthread_mutex_destroy(&sim->mutex);
    pthread_cond_destroy(&sim->cond);
    
    // Libera recursos de cada processo
    for (int i = 0; i < sim->num_processes; i++) {
        pthread_mutex_destroy(&sim->processes[i].mutex);
        pthread_cond_destroy(&sim->processes[i].cond);
    }
}

// Função para ler o arquivo de trace
int read_trace_file(Simulator* sim) {
    FILE* file = fopen(sim->input_file, "r");
    if (!file) {
        perror("Erro ao abrir arquivo de trace");
        return -1;
    }
    
    int count = 0;
    char name[MAX_PROC_NAME + 1];
    int t0, dt, deadline;
    
    // Lê os processos do arquivo
    while (fscanf(file, "%s %d %d %d", name, &t0, &dt, &deadline) == 4 && count < MAX_PROCESSES) {
        Process* proc = &sim->processes[count];
        
        // Copia os dados lidos para a estrutura do processo
        strncpy(proc->name, name, MAX_PROC_NAME);
        proc->name[MAX_PROC_NAME] = '\0';
        proc->t0 = t0 + (int)sim->simulation_start_time;
        proc->dt = dt;
        // Normalize deadline by adding simulation start time
        proc->deadline = deadline + (int)sim->simulation_start_time;
        
        // Inicializa campos adicionais
        proc->remaining_time = dt;
        proc->start_time = -1;
        proc->finish_time = -1;
        proc->is_running = 0;
        proc->is_completed = 0;
        proc->cpu_assigned = -1;
        
        // Inicializa mutex e condição para o processo
        pthread_mutex_init(&proc->mutex, NULL);
        pthread_cond_init(&proc->cond, NULL);
        
        count++;

        fprintf(stderr, "Processo %s: t0 = %d, dt = %d, deadline = %d\n", proc->name, proc->t0, proc->dt, proc->deadline);
    }
    
    sim->num_processes = count;
    fclose(file);
    
    return count;
}

// Função para escrever os resultados no arquivo de saída
int write_results_file(Simulator* sim) {
    FILE* file = fopen(sim->output_file, "w");
    if (!file) {
        perror("Erro ao abrir arquivo de saída");
        return -1;
    }
    
    // Escreve uma linha para cada processo
    for (int i = 0; i < sim->num_processes; i++) {
        Process* proc = &sim->processes[i];
        int tr = proc->finish_time - proc->t0; // Tempo de resposta (tf - t0)
        int cumpriu = (proc->finish_time <= proc->deadline) ? 1 : 0; // Verificação de deadline
        
        fprintf(file, "%s %d %d %d\n", proc->name, tr, proc->finish_time, cumpriu);
    }
    
    // Escreve a linha extra com o número de preempções
    fprintf(file, "%d\n", sim->preemptions);
    
    fclose(file);
    return 0;
}

// Função de execução do processo (thread)
void* process_execution(void* arg) {
    Process* proc = (Process*)arg;
    
    pthread_mutex_lock(&proc->mutex);
    
    // Aguarda até que o escalonador permita a execução
    while (!proc->is_running && !proc->is_completed) {
        pthread_cond_wait(&proc->cond, &proc->mutex);
    }
    
    pthread_mutex_unlock(&proc->mutex);
    
    // Loop principal de execução do processo
    while (1) {
        pthread_mutex_lock(&proc->mutex);
        
        // Verifica se o processo foi concluído
        if (proc->is_completed) {
            pthread_mutex_unlock(&proc->mutex);
            break;
        }
        
        // Verifica se o processo está em execução
        if (!proc->is_running) {
            // Aguarda até que o escalonador permita a execução
            pthread_cond_wait(&proc->cond, &proc->mutex);
            
            if (proc->is_completed) {
                pthread_mutex_unlock(&proc->mutex);
                break;
            }
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
                pthread_mutex_lock(&simulator.mutex);
                proc->finish_time = (int)(get_current_time());
                pthread_mutex_unlock(&simulator.mutex);
                
                // Libera a CPU
                pthread_mutex_lock(&simulator.mutex);
                if (proc->cpu_assigned >= 0) {
                    simulator.cpu_assignments[proc->cpu_assigned] = -1;
                }
                simulator.active_processes--;
                pthread_cond_signal(&simulator.cond);
                pthread_mutex_unlock(&simulator.mutex);
            }
        }
        
        pthread_mutex_unlock(&proc->mutex);
    }
    
    return NULL;
}

// Implementação do escalonador FCFS (First-Come First-Served)
void* fcfs_scheduler(void* arg) {
    Simulator* sim = (Simulator*)arg;
    double simulation_start = get_current_time();
    int current_time = 0;
    
    // Ordena os processos pelo tempo de chegada (t0)
    for (int i = 0; i < sim->num_processes; i++) {
        for (int j = i + 1; j < sim->num_processes; j++) {
            if (sim->processes[i].t0 > sim->processes[j].t0) {
                Process temp = sim->processes[i];
                sim->processes[i] = sim->processes[j];
                sim->processes[j] = temp;
            }
        }
    }
    
    // Loop principal do escalonador
    while (1) {
        pthread_mutex_lock(&sim->mutex);
        
        // Atualiza o tempo da simulação
        current_time = (int)(get_current_time() - simulation_start);
        sim->simulation_time = current_time;
        
        // Verifica se todos os processos foram concluídos
        if (sim->active_processes == 0 && current_time >= sim->processes[sim->num_processes-1].t0) {
            sim->simulation_done = true;
            pthread_mutex_unlock(&sim->mutex);
            break;
        }
        
        // Processa cada processo por ordem de chegada
        for (int i = 0; i < sim->num_processes; i++) {
            Process* proc = &sim->processes[i];
            
            pthread_mutex_lock(&proc->mutex);
            
            // Verifica se o processo chegou e ainda não foi iniciado
            if (current_time >= proc->t0 && proc->start_time == -1 && !proc->is_completed) {
                // Procura uma CPU disponível
                int cpu_id = -1;
                for (int j = 0; j < sim->num_cpus; j++) {
                    if (sim->cpu_assignments[j] == -1) {
                        cpu_id = j;
                        break;
                    }
                }
                
                // Se há CPU disponível, inicia o processo
                if (cpu_id >= 0) {
                    // Atribui a CPU ao processo
                    sim->cpu_assignments[cpu_id] = i;
                    proc->cpu_assigned = cpu_id;
                    
                    // Marca o início da execução
                    proc->start_time = current_time;
                    proc->is_running = 1;
                    sim->active_processes++;
                    
                    // Cria a thread para executar o processo
                    pthread_create(&proc->thread, NULL, process_execution, proc);
                    
                    // Sinaliza à thread do processo que pode começar
                    pthread_cond_signal(&proc->cond);
                }
            }
            
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Aguarda por mudanças (conclusão de processos ou novos processos)
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += 1; // Timeout de 1 segundo
        
        pthread_cond_timedwait(&sim->cond, &sim->mutex, &ts);
        pthread_mutex_unlock(&sim->mutex);
    }
    
    return NULL;
}

// Implementação do escalonador SRTN (Shortest Remaining Time Next)
void* srtn_scheduler(void* arg) {
    Simulator* sim = (Simulator*)arg;
    double simulation_start = get_current_time();
    int current_time = 0;
    
    // Inicialização do escalonador SRTN
    
    // Loop principal do escalonador
    while (1) {
        pthread_mutex_lock(&sim->mutex);
        
        // Atualiza o tempo da simulação
        current_time = (int)(get_current_time() - simulation_start);
        sim->simulation_time = current_time;
        
        // Verifica se todos os processos foram concluídos
        if (sim->active_processes == 0 && current_time >= sim->processes[sim->num_processes-1].t0) {
            sim->simulation_done = true;
            pthread_mutex_unlock(&sim->mutex);
            break;
        }
        
        // Identifica quais processos chegaram mas ainda não foram iniciados
        int available_processes[MAX_PROCESSES];
        int num_available = 0;
        
        for (int i = 0; i < sim->num_processes; i++) {
            Process* proc = &sim->processes[i];
            
            pthread_mutex_lock(&proc->mutex);
            if (current_time >= proc->t0 && !proc->is_completed && proc->remaining_time > 0) {
                available_processes[num_available++] = i;
            }
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Ordena os processos pelo tempo restante
        for (int i = 0; i < num_available; i++) {
            for (int j = i + 1; j < num_available; j++) {
                if (sim->processes[available_processes[i]].remaining_time > 
                    sim->processes[available_processes[j]].remaining_time) {
                    int temp = available_processes[i];
                    available_processes[i] = available_processes[j];
                    available_processes[j] = temp;
                }
            }
        }
        
        // Processa as CPUs
        for (int cpu_id = 0; cpu_id < sim->num_cpus; cpu_id++) {
            // Verifica se há processos disponíveis
            if (num_available <= 0) break;
            
            // Se a CPU estiver livre ou o processo atual não for o de menor tempo restante
            if (sim->cpu_assignments[cpu_id] == -1 || 
                (sim->cpu_assignments[cpu_id] != available_processes[0] && num_available > 0)) {
                
                // Se há um processo rodando nesta CPU, faz a preempção
                if (sim->cpu_assignments[cpu_id] != -1) {
                    Process* running_proc = &sim->processes[sim->cpu_assignments[cpu_id]];
                    
                    pthread_mutex_lock(&running_proc->mutex);
                    
                    // Faz a preempção apenas se o processo não estiver concluído
                    if (!running_proc->is_completed) {
                        running_proc->is_running = 0;
                        sim->preemptions++;
                    }
                    
                    pthread_mutex_unlock(&running_proc->mutex);
                }
                
                // Atribui o processo com menor tempo restante para esta CPU
                int proc_id = available_processes[0];
                Process* proc = &sim->processes[proc_id];
                
                // Remove este processo da lista de disponíveis
                for (int i = 0; i < num_available - 1; i++) {
                    available_processes[i] = available_processes[i + 1];
                }
                num_available--;
                
                pthread_mutex_lock(&proc->mutex);
                
                // Atualiza as informações do processo
                sim->cpu_assignments[cpu_id] = proc_id;
                proc->cpu_assigned = cpu_id;
                
                // Se o processo ainda não foi iniciado, cria a thread
                if (proc->start_time == -1) {
                    proc->start_time = current_time;
                    proc->is_running = 1;
                    sim->active_processes++;
                    
                    pthread_create(&proc->thread, NULL, process_execution, proc);
                } else {
                    // Se já foi iniciado, apenas sinaliza para continuar
                    proc->is_running = 1;
                }
                
                pthread_cond_signal(&proc->cond);
                pthread_mutex_unlock(&proc->mutex);
            }
        }
        
        // Aguarda por mudanças
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += 1; // Timeout de 1 segundo
        
        pthread_cond_timedwait(&sim->cond, &sim->mutex, &ts);
        pthread_mutex_unlock(&sim->mutex);
    }
    
    return NULL;
}

// Implementação do escalonador com prioridade baseado em deadline
void* priority_scheduler(void* arg) {
    Simulator* sim = (Simulator*)arg;
    double simulation_start = get_current_time();
    int current_time = 0;
    
    // Loop principal do escalonador
    while (1) {
        pthread_mutex_lock(&sim->mutex);
        
        // Atualiza o tempo da simulação
        current_time = (int)(get_current_time() - simulation_start);
        sim->simulation_time = current_time;
        
        // Verifica se todos os processos foram concluídos
        if (sim->active_processes == 0 && current_time >= sim->processes[sim->num_processes-1].t0) {
            sim->simulation_done = true;
            pthread_mutex_unlock(&sim->mutex);
            break;
        }
        
        // Identifica quais processos chegaram mas ainda não foram concluídos
        int available_processes[MAX_PROCESSES];
        int num_available = 0;
        
        for (int i = 0; i < sim->num_processes; i++) {
            Process* proc = &sim->processes[i];
            
            pthread_mutex_lock(&proc->mutex);
            if (current_time >= proc->t0 && !proc->is_completed && proc->remaining_time > 0) {
                available_processes[num_available++] = i;
            }
            pthread_mutex_unlock(&proc->mutex);
        }
        
        // Calcula a prioridade de cada processo: quanto menor a folga (deadline - tempo atual - tempo restante), maior a prioridade
        int priority[MAX_PROCESSES];
        for (int i = 0; i < num_available; i++) {
            Process* proc = &sim->processes[available_processes[i]];
            int slack = proc->deadline - current_time - proc->remaining_time;
            priority[i] = slack;
        }
        
        // Ordena os processos pela prioridade (menor slack primeiro)
        for (int i = 0; i < num_available; i++) {
            for (int j = i + 1; j < num_available; j++) {
                if (priority[i] > priority[j]) {
                    // Troca as prioridades
                    int temp_prio = priority[i];
                    priority[i] = priority[j];
                    priority[j] = temp_prio;
                    
                    // Troca os processos
                    int temp_proc = available_processes[i];
                    available_processes[i] = available_processes[j];
                    available_processes[j] = temp_proc;
                }
            }
        }
        
        // Processa as CPUs
        for (int cpu_id = 0; cpu_id < sim->num_cpus; cpu_id++) {
            // Verifica se há processos disponíveis
            if (num_available <= 0) break;
            
            // Se a CPU estiver livre ou o processo atual não for o de maior prioridade
            if (sim->cpu_assignments[cpu_id] == -1 || 
                (sim->cpu_assignments[cpu_id] != available_processes[0] && num_available > 0)) {
                
                // Se há um processo rodando nesta CPU, faz a preempção
                if (sim->cpu_assignments[cpu_id] != -1) {
                    Process* running_proc = &sim->processes[sim->cpu_assignments[cpu_id]];
                    
                    pthread_mutex_lock(&running_proc->mutex);
                    
                    // Faz a preempção apenas se o processo não estiver concluído
                    if (!running_proc->is_completed) {
                        running_proc->is_running = 0;
                        sim->preemptions++;
                    }
                    
                    pthread_mutex_unlock(&running_proc->mutex);
                }
                
                // Atribui o processo com maior prioridade para esta CPU
                int proc_id = available_processes[0];
                Process* proc = &sim->processes[proc_id];
                
                // Remove este processo da lista de disponíveis
                for (int i = 0; i < num_available - 1; i++) {
                    available_processes[i] = available_processes[i + 1];
                    priority[i] = priority[i + 1];
                }
                num_available--;
                
                pthread_mutex_lock(&proc->mutex);
                
                // Atualiza as informações do processo
                sim->cpu_assignments[cpu_id] = proc_id;
                proc->cpu_assigned = cpu_id;
                
                // Se o processo ainda não foi iniciado, cria a thread
                if (proc->start_time == -1) {
                    proc->start_time = current_time;
                    proc->is_running = 1;
                    sim->active_processes++;
                    
                    pthread_create(&proc->thread, NULL, process_execution, proc);
                } else {
                    // Se já foi iniciado, apenas sinaliza para continuar
                    proc->is_running = 1;
                }
                
                pthread_cond_signal(&proc->cond);
                pthread_mutex_unlock(&proc->mutex);
            }
        }
        
        // Aguarda por mudanças
        struct timespec ts;
        clock_gettime(CLOCK_REALTIME, &ts);
        ts.tv_sec += 1; // Timeout de 1 segundo
        
        pthread_cond_timedwait(&sim->cond, &sim->mutex, &ts);
        pthread_mutex_unlock(&sim->mutex);
    }
    
    return NULL;
}

// Função para iniciar a simulação
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
            fprintf(stderr, "Tipo de escalonador inválido: %d\n", sim->scheduler_type);
            return;
    }
    
    // Aguarda o fim da simulação
    while (!sim->simulation_done) {
        sleep(1);
    }
    
    // Aguarda o término do escalonador
    pthread_join(scheduler_thread, NULL);
    
    // Aguarda o término de todos os processos
    for (int i = 0; i < sim->num_processes; i++) {
        if (sim->processes[i].start_time != -1) {
            pthread_join(sim->processes[i].thread, NULL);
        }
    }
}

int main(int argc, char* argv[]) {
    // Verifica o número correto de argumentos
    if (argc < 4 || argc > 5) {
        fprintf(stderr, "Uso: %s <tipo_escalonador> <arquivo_entrada> <arquivo_saida> [num_cpus]\n", argv[0]);
        fprintf(stderr, "Tipos de escalonador:\n");
        fprintf(stderr, "  1 - First-Come First-Served (FCFS)\n");
        fprintf(stderr, "  2 - Shortest Remaining Time Next (SRTN)\n");
        fprintf(stderr, "  3 - Escalonamento com prioridade (baseado em deadline)\n");
        fprintf(stderr, "num_cpus - opcional: número de CPUs a serem usadas na simulação\n");
        return EXIT_FAILURE;
    }
    
    // Obtém os argumentos
    int scheduler_type = atoi(argv[1]);
    if (scheduler_type < 1 || scheduler_type > 3) {
        fprintf(stderr, "Tipo de escalonador inválido: %d\n", scheduler_type);
        return EXIT_FAILURE;
    }
    
    // Verifica se o número de CPUs foi especificado
    int num_cpus = 0; // 0 significa usar todas as CPUs disponíveis
    if (argc == 5) {
        num_cpus = atoi(argv[4]);
        if (num_cpus <= 0) {
            fprintf(stderr, "Número de CPUs deve ser maior que zero. Usando todas as CPUs disponíveis.\n");
            num_cpus = 0;
        }
    }
    
    // Inicializa o simulador
    init_simulator(&simulator, scheduler_type, argv[2], argv[3], num_cpus);
    
    // Lê o arquivo de trace
    if (read_trace_file(&simulator) <= 0) {
        fprintf(stderr, "Erro ao ler o arquivo de trace ou arquivo vazio.\n");
        return EXIT_FAILURE;
    }
    
    // Inicia a simulação
    start_simulation(&simulator);
    
    // Escreve os resultados
    if (write_results_file(&simulator) != 0) {
        fprintf(stderr, "Erro ao escrever o arquivo de saída.\n");
        return EXIT_FAILURE;
    }
    
    // Limpa os recursos
    cleanup_simulator(&simulator);
    
    return EXIT_SUCCESS;
}