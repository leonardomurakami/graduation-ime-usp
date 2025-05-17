#define _GNU_SOURCE
#include "ep2.h"

/*===============================================*/
/*================   GLOBALS   ==================*/
/*===============================================*/
cyclist_t ***track;
cyclist_t *head;

int track_size, num_cyclists;
int base_time_delta = DEFAULT_BASE_TIME_DELTA;
int total_laps;
int winner_id;
int debug_parameter = 0;
bool colors_enabled = false;  // cores desativadas por default 

_Atomic int active_cyclists, num_breakdowns;
_Atomic long long int current_time = 0;

bool cyclist_broke_down;
bool final_laps = false;
bool waiting_for_second_in_final_laps = false;

pthread_mutex_t **mutex;
pthread_mutex_t global_mutex;
pthread_mutex_t insert_mutex;
pthread_t coordinator;

Rank final_rank;
Rank breakdown_rank;
RankList rank_list;

char approach = DEFAULT_APPROACH;  // abordagem: 'i' para ingenua, 'e' para eficiente

/*===============================================*/
/*================    UTILS    ==================*/
/*===============================================*/

// retorna um real aleatorio no intervalo [min, max]
double random_double(double min, double max) {
    double r1 = (double)rand() / RAND_MAX;
    double r2 = (double)rand() / RAND_MAX;
    double d = r1 + r2 / (RAND_MAX + 1.0);
    return min + d * (max - min);
}

/*===============================================*/
/*==============   TERMINAL UTILS   =============*/
/*===============================================*/

// Limpa a tela do terminal
void clear_screen() {
    printf("\033[2J");
}

// Move o cursor para a posicao inicial (top-left)
void move_cursor_to_home() {
    printf("\033[H");
}

// Esconde o cursor
void hide_cursor() {
    printf("\033[?25l");
}

// Mostra o cursor
void show_cursor() {
    printf("\033[?25h");
}

/*===============================================*/
/*==============   RANK FUNCTIONS   =============*/
/*===============================================*/

// Cria um Rank vazio e retorna um ponteiro para ele
Rank create_rank(int lap, int size) {
    Rank rank = malloc(sizeof(RankCell));
    rank->lap = lap;
    rank->count = 0;
    rank->cyclist_ids = malloc(size * sizeof(int));

    rank->times = malloc(size * sizeof(int));
    rank->size = size;
    return rank;
}

// Insere um ciclista em uma estrutura Rank sem utilizar listas encadeadas
// Esta estrutura e reutilizada para armazenar a classificacao final da corrida
void insert_cyclist_in_rank(Rank rank, int cyclist_id, int time) {
    rank->cyclist_ids[rank->count] = cyclist_id;
    rank->times[rank->count] = time;
    (rank->count)++;
}


// Insere um ciclista com ID cyclist_id no tempo t em uma lista
void insert_cyclist(RankList list, int size, int lap, int cyclist_id, int time) {
    Rank rank = NULL; // Rank da volta correspondente
    if (list->rank == NULL) { // lista vazia
        list->rank = create_rank(lap, size);
        rank = list->rank;
    }
    else { // lista nao vazia
        RankList current_list = list;
        while (1) { // procura se ja existe um rank para esta volta
            if (current_list->rank->lap == lap) {
                rank = current_list->rank;
                break;
            }
            if (current_list->next == NULL) break;
            else current_list = current_list->next;
        }
        if (rank == NULL) { // Nao existe, precisa criar
            RankList new_list = create_rank_list();
            rank = create_rank(lap, size);
            current_list->next = new_list;
            new_list->rank = rank;
        }
    }
    rank->cyclist_ids[rank->count] = cyclist_id;
    rank->times[rank->count] = time;
    (rank->count)++;
}


// Cria uma lista encadeada de Ranks, com o primeiro rank de tamanho 'size'
// e retorna um ponteiro para a lista criada
RankList create_rank_list() {
    RankList list = malloc(sizeof(RankNode));
    list->rank = NULL;
    list->next = NULL;
    return list;
}

// Destroi um Rank
void destroy_rank(Rank rank) {
    free(rank->cyclist_ids);
    free(rank->times);
    free(rank);
}

// Recebe uma RankList list e remove o rank do inicio da lista
RankList remove_rank(RankList list) {
    Rank rank = list->rank;
    RankList next_list = list->next;
    destroy_rank(rank);
    free(list);
    return next_list;
}

// Recebe uma RankList list e remove ranks menores que 'lap'
RankList remove_ranks_by_lap(RankList list, int lap) {
    if (list == NULL) return NULL;
    if (list != NULL && list->rank != NULL && list->next != NULL && list->rank->lap < lap) {
        list = remove_rank(list);
    }
    return list;
}

// Destroi uma lista de ranks
void destroy_rank_list(RankList list) {
    while (list != NULL && list->rank != NULL)
        list = remove_rank(list);
}

// Imprime a lista de classificacao de uma volta especifica com cores e atualizacao do terminal
void print_rank(RankList list, int lap) {
    Rank rank = NULL;
    for (RankList current = list; current != NULL; current = current->next)
        if (current->rank->lap == lap) {
            rank = current->rank;
            break;
        }
    if (rank == NULL) {
        printf("%sERRO! Volta nao encontrada na lista de classificacao. (volta %d)%s\n", RED, lap, RESET);
        return;
    }
    
    // Limpa a tela e move o cursor para a posicao inicial
    // Usado para depuracao e para um programa mais interativo 
    // (a tela limpa a cada volta, inves de printar todo o trace)

    // clear_screen();
    // move_cursor_to_home();
    
    // Borda superior
    printf("%s%s┌", BOLD, YELLOW);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┐\n");
    
    // Titulo
    char title[50];
    sprintf(title, "== CLASSIFICACAO - VOLTA %d ==", lap);
    int title_len = strlen(title);
    int left_padding = (RANK_FRAME_WIDTH - title_len) / 2;
    int right_padding = RANK_FRAME_WIDTH - title_len - left_padding - 2;
    printf("│%*s%s%*s│\n", left_padding, "", title, right_padding, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤\n");
    
    // Cabecalho da tabela
    printf("│ %sCiclista    Pos     Tempo (ms)%s", BOLD, RESET);
    printf("%*s│\n", RANK_FRAME_WIDTH - 33, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤%s\n", RESET);
    
    for (int i = 0; i < rank->count; i++) {
        char* color = RESET;
        
        // Atribui cores com base na posicao
        if (i == 0) color = GREEN;       // 1 lugar - Verde
        else if (i == 1) color = CYAN;   // 2 lugar - Ciano
        else if (i == 2) color = BLUE;   // 3 lugar - Azul
        else if (i == rank->count-1) color = RED; // Ultimo lugar - Vermelho
        
        printf("%s%s│ %s%-10d %-7d %-10d%s%*s│%s\n", 
               BOLD, YELLOW,
               color, 
               rank->cyclist_ids[i], 
               i+1, 
               rank->times[i],
               RESET,
               RANK_FRAME_WIDTH - 32, // ajuste para corresponder a largura de todos os itens formatados
               "",
               RESET);
    }
    
    // Borda inferior
    printf("%s%s└", BOLD, YELLOW);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┘%s\n\n", RESET);
}

// Imprime a lista de classificacao final com cores
void print_final_rank(Rank rank) {
    // Limpa a tela e move o cursor para a posicao inicial
    // Usado mais para debug e para um programa mais limpinho/interativo
    
    // clear_screen();
    // move_cursor_to_home();
    
    // Borda superior
    printf("%s%s┌", BOLD, YELLOW);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┐\n");
    
    // Titulo
    char title[] = "== CLASSIFICACAO FINAL ==";
    int title_len = strlen(title);
    int left_padding = (RANK_FRAME_WIDTH - title_len) / 2;
    int right_padding = RANK_FRAME_WIDTH - title_len - left_padding - 2;
    printf("│%*s%s%*s│\n", left_padding, "", title, right_padding, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤\n");
    
    // Cabecalho da tabela
    printf("│ %sCiclista    Pos     Tempo%s", BOLD, RESET);
    printf("%*s│\n", RANK_FRAME_WIDTH - 28, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤%s\n", RESET);
    
    for (int i = rank->count - 1; i >= 0; i--) {
        char* color = RESET;
        int position = rank->count - i;
        
        // Atribui cores com base na posicao
        if (position == 1) color = GREEN;       // 1º lugar - Verde
        else if (position == 2) color = CYAN;   // 2º lugar - Ciano
        else if (position == 3) color = BLUE;   // 3º lugar - Azul
        else if (position == rank->count) color = RED; // Último lugar - Vermelho
        
        printf("%s%s│ %s%-10d %-7d %-10d%s%*s│%s\n", 
               BOLD, YELLOW,
               color, 
               rank->cyclist_ids[i], 
               position, 
               rank->times[i],
               RESET,
               RANK_FRAME_WIDTH - 32, // ajuste para corresponder à largura de todos os itens formatados
               "",
               RESET);
    }
    
    // Borda inferior
    printf("%s%s└", BOLD, YELLOW);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┘%s\n\n", RESET);
    
    // Nao mostre o cursor aqui, pois podemos ter mais coisas para exibir (ciclistas quebrados, etc)
}

// Imprime a lista de classificacao de quebra de classificacao com cores
void print_breakdown_rank(Rank rank) {
    printf("%s%s┌", BOLD, MAGENTA);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┐\n");
    
    // Titulo
    char title[] = "== CLASSIFICACAO DE BREAKDOWN ==";
    int title_len = strlen(title);
    int left_padding = (RANK_FRAME_WIDTH - title_len) / 2;
    int right_padding = RANK_FRAME_WIDTH - title_len - left_padding - 2;
    printf("│%*s%s%*s│\n", left_padding, "", title, right_padding, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤\n");
    
    // Cabecalho da tabela
    printf("│ %sCiclista    Volta que quebrou%s", BOLD, RESET);
    printf("%*s│\n", RANK_FRAME_WIDTH - 32, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤%s\n", RESET);
    
    for (int i = rank->count - 1; i >= 0; i--) {
        printf("%s%s│ %s%-10d %-15d%s%*s│%s\n", 
               BOLD, MAGENTA,
               RED, 
               rank->cyclist_ids[i], 
               rank->times[i],
               RESET,
               RANK_FRAME_WIDTH - 29, // ajuste para a largura de itens formatados
               "",
               RESET);
    }
    
    // Borda inferior
    printf("%s%s└", BOLD, MAGENTA);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┘%s\n\n", RESET);
}

// Recebe uma RankList list e uma volta e retorna um ponteiro para o Rank
// daquela volta.
Rank find_rank(RankList list, int lap) {
    Rank rank = NULL;
    RankList current_list = list;
    while (1) { // procura se ja existe um rank para esta volta
        if (current_list->rank->lap == lap) {
            rank = current_list->rank;
            break;
        }
        if (current_list->next == NULL) break;
        else current_list = current_list->next;
    }
    return rank;
}

// Recebe uma lista de ranks por volta e retorna o ultimo colocado no final
// dessa volta. Se houver mais de um ultimo colocado, seleciona aleatoriamente um
int get_last_place(RankList list, int lap) {
    Rank rank = find_rank(list, lap);
    if (rank == NULL) {
        printf("ERRO! Volta nao encontrada na funcao get_last_place. (volta %d)\n", lap);
        exit(1);
    }
    return rank->cyclist_ids[rank->count-1];
}

// Recebe uma lista de ranks por volta, uma volta e um numero de ciclista.
// A funcao remove o ciclista do rank dessa volta e retorna um novo ultimo colocado
int get_new_last_place(RankList list, int lap, int cyclist_id) {
    Rank rank = find_rank(list, lap);
    if (rank == NULL) {
        printf("ERRO! Volta nao encontrada na funcao get_new_last_place. (volta %d)\n", lap);
        exit(1);
    }
    
    int index = -1;
    for (int i = 0; i < rank->count; i++) {
        if (rank->cyclist_ids[i] == cyclist_id) {
            index = i;
            break;
        }
    }
    
    if (index == -1) {
        printf("ERRO! Ciclista %d nao encontrado no rank da volta %d\n", cyclist_id, lap);
        exit(1);
    }
    
    // Desloca os ciclistas restantes
    for (int i = index; i < rank->count - 1; i++) {
        rank->cyclist_ids[i] = rank->cyclist_ids[i+1];
        rank->times[i] = rank->times[i+1];
    }
    
    rank->count--;
    return rank->cyclist_ids[rank->count-1];
}

// Recebe um rank e o numero do ciclista vencedor. A funcao ajusta as posicoes
// da classificacao final para que o vencedor seja o primeiro lugar, ja que sua thread
// foi a primeira a ser destruida na ultima volta.
void adjust_first_place(Rank rank, int winner) {
    if (rank == NULL) {
        printf("ERRO! Rank nulo em adjust_first_place.\n");
        exit(1);
    }
    
    // Encontra o vencedor no rank
    int index = -1;
    for (int i = 0; i < rank->count; i++) {
        if (rank->cyclist_ids[i] == winner) {
            index = i;
            break;
        }
    }
    
    if (index == -1) {
        // Se o vencedor não está no rank, adiciona-o
        insert_cyclist_in_rank(rank, winner, current_time);
        index = rank->count - 1;
        printf("Vencedor %d adicionado à classificação final\n", winner);
    }
    
    // Troca o vencedor com o primeiro lugar (ultima posicao no array)
    int temp_id = rank->cyclist_ids[rank->count-1];
    int temp_time = rank->times[rank->count-1];
    
    rank->cyclist_ids[rank->count-1] = rank->cyclist_ids[index];
    rank->times[rank->count-1] = rank->times[index];
    
    rank->cyclist_ids[index] = temp_id;
    rank->times[index] = temp_time;
}

// Recebe uma lista de ranks por volta e retorna o primeiro lugar dessa volta.
int get_first_place(RankList list, int lap) {
    Rank rank = find_rank(list, lap);
    if (rank == NULL) {
        printf("ERRO! Volta nao encontrada na funcao get_first_place. (volta %d)\n", lap);
        exit(1);
    }
    return rank->cyclist_ids[0];
}

/*===============================================*/
/*=============   CYCLIST THREADS   =============*/
/*===============================================*/

void *cyclist_thread(void *arg)
{
    pthread_setcanceltype(PTHREAD_CANCEL_ASYNCHRONOUS, NULL);
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = CYCLIST_THREAD_NANO_SLEEP;

    cyclist_t *cyclist = (cyclist_t *) arg;

    // primeira volta sempre a 30km/h (1m a cada 120ms)
    cyclist->speed = SPEED_30KMH;
    cyclist->time_delta = 2; // base_time_delta - cyclist->speed;
    
    while (true) {
        if (true) { // Tarefa da thread
            cyclist->round_completed = false;
            cyclist->time_delta = cyclist->time_delta - 1;  // Sempre decrementa em 1
            
            if (cyclist->time_delta <= 0) { // Velocidade permite que o ciclista avance a cada iteracao
                bool advanced = false;
                int attempt_count = 0;
                
                while (attempt_count++ < 2) { // Tenta avancar algumas vezes
                    // Abordagem de acesso a pista
                    if (approach == 'i') {
                        // Abordagem ingena: um unico mutex para toda a pista
                        pthread_mutex_lock(&global_mutex);
                        
                        int next_pos = (cyclist->pos_x + 1) % track_size;
                        if (track[cyclist->pos_y][next_pos] == NULL) {
                            // Posicao a frente esta livre, move o ciclista
                            track[cyclist->pos_y][next_pos] = cyclist;
                            track[cyclist->pos_y][cyclist->pos_x] = NULL;
                            cyclist->pos_x = next_pos;
                            advanced = true;
                        }
                        
                        pthread_mutex_unlock(&global_mutex);
                        if (advanced) break;
                    } else {
                        // Abordagem eficiente: mutex por posicao na pista
                        if (pthread_mutex_trylock(&mutex[cyclist->pos_y][(cyclist->pos_x + 1) % track_size]) == 0) {
                            if (track[cyclist->pos_y][(cyclist->pos_x + 1) % track_size] == NULL) {
                                // A posicao a frente esta livre
                                move_forward(cyclist);
                                pthread_mutex_unlock(&mutex[cyclist->pos_y][cyclist->pos_x]);
                                advanced = true;
                                break;
                            } else {
                                pthread_mutex_unlock(&mutex[cyclist->pos_y][(cyclist->pos_x + 1) % track_size]);
                            }
                        } else {
                            nanosleep(&ts, NULL); // Espera um pouco para tentar novamente
                        }
                    }
                }
                
                if (!advanced) {
                    // Se nao conseguiu avancar diretamente, tenta ultrapassar
                    // usando faixas externas
                    move_to_outer_lane(cyclist);
                }
                
                // Verifica se cruzou a linha de chegada
                if (cyclist->pos_x == 0) {
                    handle_finish_line(cyclist);
                }
                
                // Reinicia o tempo para o proximo movimento com base na velocidade atual
                if (cyclist->speed == SPEED_30KMH) { // 30km/h: 1m a cada 120ms
                    cyclist->time_delta = 2;
                } else if (cyclist->speed == SPEED_60KMH) { // 60km/h: 1m a cada 60ms
                    cyclist->time_delta = 1;
                }
            }
            
            cyclist->round_completed = true;
            nanosleep(&ts, NULL);

            // tenta voltar para a faixa interna
            // fazemos isso para que o ciclista nao fique preso na faixa externa apos algumas ultrapassagens
            move_to_inner_lane(cyclist);
        }

        // barreira de sincronizacao
        cyclist->arrived_flag = 1;
        while (!cyclist->continue_flag) usleep(1);
        cyclist->continue_flag = 0;
    }
    
    return NULL;
}

// Define a velocidade do ciclista
void set_cyclist_speed(cyclist_t *cyclist) {
    // primeira volta sempre a 30km/h
    if (cyclist->laps < 1) {
        cyclist->speed = SPEED_30KMH;
        return;
    }
    
    double prob = random_double(0, 1);
    
    if (cyclist->speed == SPEED_30KMH) {
        // se estava a 30km/h, 75% de chance de ir para 60km/h
        if (prob < PROB_30KMH_TO_60KMH) {
            cyclist->speed = SPEED_60KMH; // 60km/h
        } else {
            cyclist->speed = SPEED_30KMH; // 30km/h
        }
    } else { // cyclist->speed == SPEED_60KMH
        // se estava a 60km/h, 45% de chance de continuar a 60km/h
        if (prob < PROB_60KMH_STAYS_60KMH) {
            cyclist->speed = SPEED_60KMH; // 60km/h
        } else {
            cyclist->speed = SPEED_30KMH; // 30km/h
        }
    }
    
    // verifica ciclistas afrente e ajusta a velocidade se necessario
    check_cyclists_ahead(cyclist);
}

// verifica se ha ciclistas afrente impedindo uma velocidade maior
void check_cyclists_ahead(cyclist_t *cyclist) {
    // se o ciclista esta a 60km/h, verifica se ha alguem a 30km/h afrente
    if (cyclist->speed == SPEED_60KMH) {
        int next_pos = (cyclist->pos_x + 1) % track_size;
        
        if (approach == 'i') {
            pthread_mutex_lock(&global_mutex);
            
            // verifica se ha um ciclista na mesma fila e posicao afrente
            if (track[cyclist->pos_y][next_pos] != NULL) {
                cyclist_t *ahead = track[cyclist->pos_y][next_pos];
                if (ahead->speed == SPEED_30KMH) {
                    // ha um ciclista a 30km/h afrente, ajusta velocidade
                    cyclist->speed = SPEED_30KMH;
                }
            }
            
            pthread_mutex_unlock(&global_mutex);
        } else {
            // abordagem eficiente
            if (pthread_mutex_trylock(&mutex[cyclist->pos_y][next_pos]) == 0) {
                if (track[cyclist->pos_y][next_pos] != NULL) {
                    cyclist_t *ahead = track[cyclist->pos_y][next_pos];
                    if (ahead->speed == SPEED_30KMH) {
                        // ha um ciclista a 30km/h afrente, ajusta velocidade
                        cyclist->speed = SPEED_30KMH;
                    }
                }
                pthread_mutex_unlock(&mutex[cyclist->pos_y][next_pos]);
            }
        }
    }
}

// move para frente
void move_forward(cyclist_t *cyclist) {
    int next_pos = (cyclist->pos_x + 1) % track_size;
    track[cyclist->pos_y][next_pos] = cyclist;
    track[cyclist->pos_y][cyclist->pos_x] = NULL;
    cyclist->pos_x = next_pos;
}

// procura por uma faixa externa para avancar
void move_to_outer_lane(cyclist_t *cyclist) {
    int i, j;
    bool found_outer_lane = false;
    
    if (approach == 'e') {
        // abordagem eficiente: usa locks especificos
        for (i = cyclist->pos_y + 1; i < MAX_LANES; i++) { // procura por uma faixa externa livre
            pthread_mutex_lock(&mutex[i][cyclist->pos_x]);
            if (track[i][cyclist->pos_x] == NULL) {
                found_outer_lane = true;
                break;
            }
            pthread_mutex_unlock(&mutex[i][cyclist->pos_x]);
        }
        
        if (found_outer_lane) {
            track[i][cyclist->pos_x] = cyclist;
            track[cyclist->pos_y][cyclist->pos_x] = NULL;
            cyclist->pos_y = i;
            pthread_mutex_unlock(&mutex[i][cyclist->pos_x]);
        }
        
        if (found_outer_lane) {
            for (j = 0; j < MAX_LANES; j++) { // procura por espaco na fila da frente
                pthread_mutex_lock(&mutex[j][(cyclist->pos_x+1)%track_size]);
                if (track[j][(cyclist->pos_x+1)%track_size] == NULL) {
                    track[j][(cyclist->pos_x+1)%track_size] = cyclist;
                    track[cyclist->pos_y][cyclist->pos_x] = NULL;
                    cyclist->pos_x = (cyclist->pos_x+1)%track_size;
                    cyclist->pos_y = j;
                    pthread_mutex_unlock(&mutex[j][cyclist->pos_x]);
                    break;
                }
                pthread_mutex_unlock(&mutex[j][(cyclist->pos_x+1)%track_size]);
            }
        }
    } else {
        pthread_mutex_lock(&global_mutex);
        for (i = cyclist->pos_y + 1; i < MAX_LANES; i++) {
            if (track[i][cyclist->pos_x] == NULL) {
                found_outer_lane = true;
                break;
            }
        }
        
        if (found_outer_lane) {
            track[i][cyclist->pos_x] = cyclist;
            track[cyclist->pos_y][cyclist->pos_x] = NULL;
            cyclist->pos_y = i;
            
            // tenta avancar para frente
            for (j = 0; j < MAX_LANES; j++) {
                if (track[j][(cyclist->pos_x+1)%track_size] == NULL) {
                    track[j][(cyclist->pos_x+1)%track_size] = cyclist;
                    track[cyclist->pos_y][cyclist->pos_x] = NULL;
                    cyclist->pos_x = (cyclist->pos_x+1)%track_size;
                    cyclist->pos_y = j;
                    break;
                }
            }
        }
        pthread_mutex_unlock(&global_mutex);
    }
}

// trata o ciclista na linha de chegada. sorteia se ele vai quebrar, se quebrar, ativa a flag broken_down. 
// se nao, insere ele no rank da volta completada e recalcula sua velocidade.
void handle_finish_line(cyclist_t *cyclist) {
    bool broke_down = false;
    (cyclist->laps)++; // completou a volta ou comecou a corrida
    
    // verifica quebra a cada 5 voltas com 10% de chance
    if (cyclist->laps > 0 && cyclist->laps % BREAKDOWN_CHECK_INTERVAL == 0) {
        if(random_double(0, 1) < BREAKDOWN_PROBABILITY) {
            cyclist_broke_down = true;
            cyclist->broken_down = true;
            broke_down = true;
        }
    }
    
    if (!broke_down) {
        pthread_mutex_lock(&insert_mutex);
        insert_cyclist(rank_list, num_cyclists, cyclist->laps, cyclist->number, current_time);
        pthread_mutex_unlock(&insert_mutex);
        set_cyclist_speed(cyclist);
    }
}

// no final do seu movimento, o ciclista trata de se mover para a faixa interna possivel
void move_to_inner_lane(cyclist_t *cyclist) {
    bool found = false;
    int i = cyclist->pos_y;
    
    if (approach == 'e') {
        // eficiente
        for ( ; i >= 0; i--) {
            pthread_mutex_lock(&mutex[i][cyclist->pos_x]);
            if (track[i][cyclist->pos_x] == NULL) {
                found = true;
                break;
            }
            pthread_mutex_unlock(&mutex[i][cyclist->pos_x]);
        }
        
        if (found) {
            if (i < cyclist->pos_y) {
                track[cyclist->pos_y][cyclist->pos_x] = NULL;
                track[i][cyclist->pos_x] = cyclist;
                cyclist->pos_y = i;
            }
            pthread_mutex_unlock(&mutex[i][cyclist->pos_x]);
        }
    } else {
        // ingenua
        pthread_mutex_lock(&global_mutex);
        for (i = cyclist->pos_y - 1; i >= 0; i--) {
            if (track[i][cyclist->pos_x] == NULL) {
                found = true;
                break;
            }
        }
        
        if (found) {
            track[cyclist->pos_y][cyclist->pos_x] = NULL;
            track[i][cyclist->pos_x] = cyclist;
            cyclist->pos_y = i;
        }
        pthread_mutex_unlock(&global_mutex);
    }
}

/*===============================================*/
/*==========    COORDINATOR THREAD    ===========*/
/*===============================================*/

void declare_winner(int winner) {
    // Borda superior
    printf("%s%s┌", BOLD, GREEN);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┐\n");
    
    // Titulo
    char title[] = "=== WINNER ===";
    int title_len = strlen(title);
    int left_padding = (RANK_FRAME_WIDTH - title_len) / 2;
    int right_padding = RANK_FRAME_WIDTH - title_len - left_padding - 2;
    printf("│%*s%s%*s│\n", left_padding, "", title, right_padding, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤\n");
    
    // Mensagem
    char message[50];
    sprintf(message, "Cyclist %d won the race!", winner);
    int msg_len = strlen(message);
    int msg_left_padding = (RANK_FRAME_WIDTH - msg_len) / 2;
    int msg_right_padding = RANK_FRAME_WIDTH - msg_len - msg_left_padding - 2;
    printf("│%*s%s%s%s%*s│\n", 
           msg_left_padding, "", 
           BOLD, message, RESET,
           msg_right_padding, "");
    
    // Borda inferior
    printf("%s%s└", BOLD, GREEN);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┘%s\n\n", RESET);
}

void debug_print_active_cyclists(cyclist_t *cyclist_head) {
    printf("%s%s┌", BOLD, CYAN);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┐\n");
    
    // Título
    char title[] = "=== CICLISTAS ATIVOS ===";
    int title_len = strlen(title);
    int left_padding = (RANK_FRAME_WIDTH - title_len) / 2;
    int right_padding = RANK_FRAME_WIDTH - title_len - left_padding - 2;
    printf("│%*s%s%*s│\n", left_padding, "", title, right_padding, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤\n");
    
    // Cabeçalho
    printf("│ %sID    Pos(x,y)  Voltas  Veloc  Estado%s", BOLD, RESET);
    printf("%*s│\n", RANK_FRAME_WIDTH - 40, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤%s\n", RESET);
    
    // Total atual
    printf("│ Total de ciclistas ativos: %d%*s│\n", active_cyclists, 
           RANK_FRAME_WIDTH - 30, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤%s\n", RESET);
    
    // Lista de ciclistas
    int count = 0;
    for (cyclist_t *cyclist = cyclist_head->next; cyclist != head; cyclist = cyclist->next) {
        char* speed_str = cyclist->speed == SPEED_30KMH ? "30km/h" : "60km/h";
        char* state = cyclist->broken_down ? "Quebrado" : "OK";
        
        printf("│ %-4d  (%3d,%d)   %-6d  %-5s  %-7s%*s│\n",
               cyclist->number,
               cyclist->pos_x,
               cyclist->pos_y,
               cyclist->laps,
               speed_str,
               state,
               RANK_FRAME_WIDTH - 45,
               "");
        count++;
    }
    
    if (count == 0) {
        printf("│ %sNenhum ciclista ativo%s%*s│\n",
               BOLD, RESET, 
               RANK_FRAME_WIDTH - 24, "");
    }
    
    // Borda inferior
    printf("%s%s└", BOLD, CYAN);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┘%s\n\n", RESET);
}

void *coordinator_thread(void *arg)
{

    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = MAIN_THREAD_NANO_SLEEP;

    cyclist_t *cyclist_head = (cyclist_t *) arg;

    /* flags auxiliares */
    int min_lap = 0;  // minimo de voltas locais dos ciclistas
    int max_lap = 0;  // maximo de voltas locais dos ciclistas
    int last_elimination_lap = 0; // menor volta local do coordenador
    int highest_lap = 0;  // maior volta do coordenador
    int winner = -1;

    while (true) {
        if (active_cyclists <= 0) {
            pthread_exit(0);  // Sai quando não há mais ciclistas
        }
        
        for (cyclist_t *cyclist = cyclist_head->next; cyclist != head; cyclist = cyclist->next) {
            while (cyclist->arrived_flag == 0 && active_cyclists > 1) {
                nanosleep(&ts, NULL);
            }
            cyclist->arrived_flag = 0;
        }
        
        // trata quebras de ciclistas
        if (cyclist_broke_down) {
            eliminate_broken_down(cyclist_head);
            cyclist_broke_down = false;
        }
        
        // encontra minimo e maximo de voltas dos ciclistas
        if (active_cyclists > 0) {
            min_lap = max_lap;
            for (cyclist_t *cyclist = cyclist_head->next; cyclist != head; cyclist = cyclist->next) {
                if (max_lap < cyclist->laps) max_lap = cyclist->laps;
                if (min_lap > cyclist->laps) min_lap = cyclist->laps;
            }
        }
        
        if (highest_lap != max_lap) highest_lap = max_lap;
        
        // controla voltas e eliminacoes
        while (min_lap > 0 && last_elimination_lap < min_lap) {
            if (last_elimination_lap > 0 && active_cyclists > 1 && !debug_parameter) {
                print_rank(rank_list, last_elimination_lap);
            }
            last_elimination_lap++;
            
            // a cada 2 voltas, elimina o ultimo colocado
            if (last_elimination_lap % 2 == 0) {
                // se temos apenas 2 ciclistas restantes, declara o primeiro como vencedor
                if (active_cyclists == 2) {
                    winner = get_first_place(rank_list, last_elimination_lap);
                    int last = get_last_place(rank_list, last_elimination_lap);
                    winner_id = winner;
                    
                    // elimina o ultimo colocado
                    eliminate_cyclist(cyclist_head, last, true);
                    active_cyclists--;
                    
                    // elimina o vencedor tambem para terminar a corrida
                    eliminate_cyclist(cyclist_head, winner, false);
                    active_cyclists--;
                    
                    
                    // ajusta a classificacao final e sai da thread
                    adjust_first_place(final_rank, winner);
                    
                    if (!debug_parameter) {
                        print_rank(rank_list, last_elimination_lap);
                    }

                    
                    pthread_exit(0);
                } else {
                    // caso normal: elimina o ultimo colocado
                    int last = get_last_place(rank_list, last_elimination_lap);
                    eliminate_cyclist(cyclist_head, last, true);
                }
            }
        }
        
        // avanca o tempo em 60ms
        current_time += TIME_DELTA;
        
        // modo de depuracao: imprime o estado da pista a cada 60ms
        if (debug_parameter) {
            display_track();
        }
        
        // remove ranks antigos para economizar memoria
        if (last_elimination_lap > 0) rank_list = remove_ranks_by_lap(rank_list, last_elimination_lap);

        // permite que os ciclistas continuem
        for (cyclist_t *cyclist = head->next; cyclist != head; cyclist = cyclist->next) {
            cyclist->continue_flag = 1;
        }
    }
}

// imprime visualizacao da pista na saida padrao
void display_track()
{
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < track_size; j++) {
            if (track[i][j] != NULL) {
                printf("%02d ", track[i][j]->number);
            } else {
                printf(". ");
            }
        }
        printf("\n");
    }
    printf("\n");
}

void declare_elimination(int cyclist_number) {
    // Borda superior
    printf("%s%s┌", BOLD, RED);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┐\n");
    
    // Titulo
    char title[] = "=== ELIMINACAO ===";
    int title_len = strlen(title);
    int left_padding = (RANK_FRAME_WIDTH - title_len) / 2;
    int right_padding = RANK_FRAME_WIDTH - title_len - left_padding - 2;
    printf("│%*s%s%*s│\n", left_padding, "", title, right_padding, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤\n");
    
    // Mensagem
    char message[50];
    sprintf(message, "Cyclist %d foi eliminado!", cyclist_number);
    int msg_len = strlen(message);
    int msg_left_padding = (RANK_FRAME_WIDTH - msg_len) / 2;
    int msg_right_padding = RANK_FRAME_WIDTH - msg_len - msg_left_padding - 2;
    printf("│%*s%s%s%s%*s│\n", 
           msg_left_padding, "", 
           BOLD, message, RESET,
           msg_right_padding, "");
    
    // Borda inferior
    printf("%s%s└", BOLD, RED);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┘%s\n\n", RESET);
}

void declare_breakdown(int cyclist_number) {
    // Borda superior
    printf("%s%s┌", BOLD, MAGENTA);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┐\n");
    
    // Titulo
    char title[] = "=== QUEBROU ===";
    int title_len = strlen(title);
    int left_padding = (RANK_FRAME_WIDTH - title_len) / 2;
    int right_padding = RANK_FRAME_WIDTH - title_len - left_padding - 2;
    printf("│%*s%s%*s│\n", left_padding, "", title, right_padding, "");
    
    // Separador
    printf("├");
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┤\n");
    
    // Mensagem
    char message[50];
    sprintf(message, "Cyclist %d quebrou ;-;", cyclist_number);
    int msg_len = strlen(message);
    int msg_left_padding = (RANK_FRAME_WIDTH - msg_len) / 2;
    int msg_right_padding = RANK_FRAME_WIDTH - msg_len - msg_left_padding - 2;
    printf("│%*s%s%s%s%*s│\n", 
           msg_left_padding, "", 
           BOLD, message, RESET,
           msg_right_padding, "");
    
    // Borda inferior
    printf("%s%s└", BOLD, MAGENTA);
    for (int i = 0; i < RANK_FRAME_WIDTH - 2; i++) printf("─");
    printf("┘%s\n\n", RESET);
}

// recebe um numero de ciclista, remove-o da pista, remove o ciclista
// com esse numero da estrutura de dados, insere-o na classificacao final,
// termina sua thread e libera a memoria alocada
void eliminate_cyclist(cyclist_t *cyclist_head, int cyclist_number, bool should_print) {
    
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = MAIN_THREAD_NANO_SLEEP;
    cyclist_t *current, *previous;
    previous = cyclist_head;
    
    for (current = cyclist_head->next; current != head; current = current->next) {
        if (current->number == cyclist_number) break;
        previous = current;
    }
    
    if (should_print) {
        if (!debug_parameter) {
            declare_elimination(current->number);
        }
    }

    if (approach == 'i') {
        pthread_mutex_lock(&global_mutex);
        track[current->pos_y][current->pos_x] = NULL;
        pthread_mutex_unlock(&global_mutex);
    } else {
        pthread_mutex_lock(&mutex[current->pos_y][current->pos_x]);
        track[current->pos_y][current->pos_x] = NULL;
        pthread_mutex_unlock(&mutex[current->pos_y][current->pos_x]);
    }
    
    insert_cyclist_in_rank(final_rank, current->number, current_time);
    if (current->thread_id != 0) {
        pthread_cancel(current->thread_id);
    }
    active_cyclists--;
    previous->next = current->next;
    nanosleep(&ts, NULL); // dorme para esperar a thread parar
    free(current);
}

// verifica se ha ciclistas com a flag broken_down e os elimina:
// remove-os da pista, remove-os da estrutura de dados, insere-os
// na classificacao de quebras, termina suas threads e libera a memoria alocada
void eliminate_broken_down(cyclist_t *cyclist_head) {
    struct timespec ts;
    ts.tv_sec = 0;
    ts.tv_nsec = MAIN_THREAD_NANO_SLEEP;
    
    cyclist_t *current = cyclist_head->next;
    cyclist_t *previous = cyclist_head;
    
    while (current != head) {
        if (current->broken_down) {
            // remove da pista
            if (approach == 'i') {
                pthread_mutex_lock(&global_mutex);
                track[current->pos_y][current->pos_x] = NULL;
                pthread_mutex_unlock(&global_mutex);
            } else {
                pthread_mutex_lock(&mutex[current->pos_y][current->pos_x]);
                track[current->pos_y][current->pos_x] = NULL;
                pthread_mutex_unlock(&mutex[current->pos_y][current->pos_x]);
            }
            
            // insere na classificacao de quebras
            insert_cyclist_in_rank(breakdown_rank, current->number, current->laps);

            if (!debug_parameter) declare_breakdown(current->number);
            
            // atualiza lista encadeada e libera memoria
            cyclist_t *to_remove = current;
            current = current->next;
            previous->next = current;
            active_cyclists--;
            
            // cancela thread e libera memoria
            pthread_cancel(to_remove->thread_id);
            nanosleep(&ts, NULL); // dorme para esperar a thread parar
            free(to_remove);
            
            num_breakdowns++;
        } else {
            previous = current;
            current = current->next;
        }
    }
}

/*===============================================*/
/*==========     MAIN FUNCTIONS     =============*/
/*===============================================*/

void initialize_variables() {
    /* inicializacao de variaveis */
    active_cyclists = num_cyclists;
    num_breakdowns = 0;
    total_laps = 2 * num_cyclists - 2;

    /* inicializa mutexes */
    pthread_mutex_init(&insert_mutex, NULL);
    pthread_mutex_init(&global_mutex, NULL);

    /* cria lista de classificacao por volta */
    rank_list = create_rank_list();
    /* cria lista de classificacao final */
    final_rank = create_rank(0, num_cyclists);
    breakdown_rank = create_rank(0, num_cyclists);

    /* cria pista como uma matriz de ponteiros e matriz de mutexes para ela */
    track = malloc(10 * sizeof(cyclist_t**));
    mutex = malloc(10 * sizeof(pthread_mutex_t *));
    for (int i = 0; i < 10; i++) {
        track[i] = malloc(track_size * sizeof(cyclist_t*));
        mutex[i] = malloc(track_size * sizeof(pthread_mutex_t));
    }

    /* inicializa pista e seus mutexes */
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < track_size; j++) {
            track[i][j] = NULL;
            pthread_mutex_init(&mutex[i][j], NULL);
        }
    }

    /* cria ciclistas e posiciona-os na pista */
    head = malloc(sizeof(cyclist_t));
    head->next = head;
    
    // posicionamento inicial dos ciclistas
    int competitor_num = 1;
    int pos = 0;
    int lane = 0;
    
    // coloca no maximo 5 ciclistas lado a lado na linha de partida
    for (int i = 0; i < num_cyclists; i++) {
        cyclist_t *new_cyclist = malloc(sizeof(cyclist_t));
        track[lane][track_size-1-pos] = new_cyclist;
        
        new_cyclist->number = competitor_num++;
        new_cyclist->arrived_flag = 0;
        new_cyclist->continue_flag = 0;
        new_cyclist->pos_x = track_size-1-pos;
        new_cyclist->pos_y = lane;
        new_cyclist->laps = -1;
        new_cyclist->round_completed = false;
        new_cyclist->speed = SPEED_30KMH; // First lap always at 30km/h
        new_cyclist->broken_down = false;
        new_cyclist->next = head->next;
        head->next = new_cyclist;
        
        lane++;
        if (lane >= 5) {
            lane = 0;
            pos++;
        }
    }
}

void create_coordinator_thread() {
    if (pthread_create(&coordinator, NULL, coordinator_thread, (void*) head)) {
        printf("\n ERRO criando thread coordenador\n");
        exit(1);
    }
}

void create_cyclist_threads() {
    for (cyclist_t *cyclist = head->next; cyclist != head; cyclist = cyclist->next) {
      if (pthread_create(&cyclist->thread_id, NULL, cyclist_thread, (void*) cyclist)) {
          printf("\n ERRO criando thread %ld\n", cyclist->thread_id);
          exit(1);
      }
    }
}

void join_cyclist_threads() {
    if (active_cyclists < 1) {
        for (cyclist_t *cyclist = head->next; cyclist != head; cyclist = cyclist->next) {
            if (cyclist->thread_id != 0) {
                pthread_cancel(cyclist->thread_id);
            }
      }
    }
    for (cyclist_t *cyclist = head->next; cyclist != head; cyclist = cyclist->next) {
      if (pthread_join(cyclist->thread_id, NULL)) {
          printf("\n ERRO juntando thread %ld\n", cyclist->thread_id);
          exit(1);
      }
    }
}

void join_coordinator_thread() {
    if (pthread_join(coordinator, NULL)) {
        printf("\n ERRO juntando thread coordenador\n");
        exit(1);
    }
}

void destroy_track() {
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < track_size; j++) {
            pthread_mutex_destroy(&mutex[i][j]);
        }
        free(track[i]);
        free(mutex[i]);
    }
    free(track);
    free(mutex);
}

void clean_up() {
    pthread_mutex_destroy(&insert_mutex);
    pthread_mutex_destroy(&global_mutex);

    destroy_track();
    destroy_rank_list(rank_list);
    destroy_rank(final_rank);
    destroy_rank(breakdown_rank);
    free(head);
}

int main(int argc, char const *argv[]) {
    srand(time(NULL));
    
    // inicializa o terminal
    hide_cursor();

    // verifica argumentos da linha de comando
    if (argc < 3) {
        printf("Uso: %s d k <i|e> [-debug] [-color]\n", argv[0]);
        printf("  d: tamanho da pista (100 <= d <= 2500)\n");
        printf("  k: numero de ciclistas (5 <= k <= 5 × d)\n");
        printf("  i|e: abordagem de controle de acesso a pista (i para ingenua, e para eficiente)\n");
        printf("  -debug: modo de depuracao (opcional)\n");
        printf("  -color: desativa cores no terminal (opcional)\n");
        return 1;
    }
    
    track_size = atoi(argv[1]);
    num_cyclists = atoi(argv[2]);
    
    // verifica limites para track_size e num_cyclists
    if (track_size < 100 || track_size > 2500) {
        printf("Erro: o tamanho da pista deve estar entre 100 e 2500\n");
        return 1;
    }
    if (num_cyclists < 5 || num_cyclists > 5 * track_size) {
        printf("Erro: o numero de ciclistas deve estar entre 5 e 5 × d\n");
        return 1;
    }
    
    // determina a abordagem
    if (argc > 3) {
        if (argv[3][0] == 'i' || argv[3][0] == 'e') {
            approach = argv[3][0];
        } else {
            printf("Erro: a abordagem deve ser 'i' <ingenua> ou 'e' <eficiente>\n");
            return 1;
        }
        
        // Verifica argumentos opcionais
        for (int i = 4; i < argc; i++) {
            if (strcmp("-debug", argv[i]) == 0) {
                debug_parameter = 1;
            } else if (strcmp("-color", argv[i]) == 0) {
                colors_enabled = true;  // Disable colors if -color flag is present
            }
        }
    }

    initialize_variables();

    // cria threads
    
    create_coordinator_thread();
    create_cyclist_threads();
    join_cyclist_threads();
    join_coordinator_thread();

    if (!debug_parameter) {
        declare_winner(winner_id);
    }

    print_final_rank(final_rank);
    print_breakdown_rank(breakdown_rank);
    
    show_cursor();

    clean_up();

    return 0;
} 