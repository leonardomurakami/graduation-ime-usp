#ifndef EP2_H
#define EP2_H

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <unistd.h>
#include <sys/time.h>
#include <string.h>

/* ========== Definicoes de constantes ========== */
#define MAIN_THREAD_NANO_SLEEP 1000
#define CYCLIST_THREAD_NANO_SLEEP 10
#define DEFAULT_BASE_TIME_DELTA 2
#define DEFAULT_APPROACH 'e'  // 'e' para eficiente, 'i' para ingenuo (naive)
#define BREAKDOWN_PROBABILITY 0.1  // 10% de chance de quebrar apos BREAKDOWN_CHECK_INTERVAL voltas
#define BREAKDOWN_CHECK_INTERVAL 5  // verifica quebras a cada n voltas
#define TIME_DELTA 60

/* ========== Constantes de velocidade ========== */
#define SPEED_30KMH 1
#define SPEED_60KMH 2

/* ========== Constantes de probabilidade ========== */
#define PROB_30KMH_TO_60KMH 0.75  // 75% chance de acelerar de 30km/h para 60km/h
#define PROB_60KMH_STAYS_60KMH 0.45  // 45% chance de manter 60km/h

/* ========== Dimensoes da pista ========== */
#define MAX_LANES 10  // numero maximo de faixas na pista

/* ========== Constantes de UI ========== */
#define RANK_FRAME_WIDTH 40  // largura do quadro de exibicao da classificacao

/* ========== Configuracoes de cores do terminal ========== */
extern bool colors_enabled;  // flag global para habilitar/desabilitar cores

/* ========== Definicoes de cores e controle do terminal ========== */
#define RESET       (colors_enabled ? "\033[0m" : "")
#define BOLD        (colors_enabled ? "\033[1m" : "")
#define BLACK       (colors_enabled ? "\033[30m" : "")
#define RED         (colors_enabled ? "\033[31m" : "")
#define GREEN       (colors_enabled ? "\033[32m" : "")
#define YELLOW      (colors_enabled ? "\033[33m" : "")
#define BLUE        (colors_enabled ? "\033[34m" : "")
#define MAGENTA     (colors_enabled ? "\033[35m" : "")
#define CYAN        (colors_enabled ? "\033[36m" : "")
#define WHITE       (colors_enabled ? "\033[37m" : "")
#define BG_BLACK    (colors_enabled ? "\033[40m" : "")
#define BG_RED      (colors_enabled ? "\033[41m" : "")
#define BG_GREEN    (colors_enabled ? "\033[42m" : "")
#define BG_YELLOW   (colors_enabled ? "\033[43m" : "")
#define BG_BLUE     (colors_enabled ? "\033[44m" : "")
#define BG_MAGENTA  (colors_enabled ? "\033[45m" : "")
#define BG_CYAN     (colors_enabled ? "\033[46m" : "")
#define BG_WHITE    (colors_enabled ? "\033[47m" : "")

/* ========== Estruturas de dados ========== */

/* Estrutura representando um ciclista */
typedef struct Cyclist cyclist_t;
struct Cyclist {
    int number;           // numero de identificacao do ciclista
    int pos_x, pos_y;     // coordenadas de posicao na pista
    int arrived_flag;     // flag de sincronizacao
    int continue_flag;    // flag de sincronizacao
    int laps;             // numero de voltas completadas
    int speed;            // 1: 30km/h, 2: 60km/h
    int time_delta;       // tempo ate a proxima movimentacao
    pthread_t thread_id;
    cyclist_t *next;
    bool round_completed; // indica se o ciclista completou sua volta atual
    bool broken_down;     // indica se o ciclista quebrou
};

typedef struct RankCell {
    int lap;           // numero de volta
    int count;         // numero de ciclistas ativos nesta volta
    int *cyclist_ids;  // array de numeros de identificacao dos ciclistas ordenados pela posicao nesta volta
    int size;          // tamanho do array de identificacoes e tempos
    int *times;        // para o ciclista na posicao i no rank[], indica o tempo que ele cruzou a linha de chegada nesta volta
} RankCell;
typedef RankCell *Rank;

/* Estrutura de lista encadeada */
typedef struct RankNode {
    Rank rank;
    struct RankNode *next;
} RankNode;
typedef RankNode *RankList;

/* ========== Variaveis globais ========== */

/* Variaveis globais relacionadas a pista */
extern cyclist_t ***track;
extern cyclist_t *head;  // ponteiro para o inicio da lista encadeada de ciclistas
extern int track_size, num_cyclists;
extern pthread_mutex_t **mutex;
extern pthread_mutex_t global_mutex;
extern char approach;  // 'i' para ingenuo, 'e' para eficiente

/* Variaveis globais relacionadas ao status da corrida */
extern _Atomic int active_cyclists, num_breakdowns;
extern int total_laps;
extern bool cyclist_broke_down;
extern bool final_laps;
extern bool waiting_for_second_in_final_laps;
extern _Atomic long long int current_time;

/* Variaveis globais relacionadas a classificacao */
extern pthread_mutex_t insert_mutex;
extern Rank final_rank;
extern Rank breakdown_rank;
extern RankList rank_list;

/* Variaveis de debug e desempenho */
extern long total_memory;
extern int debug_parameter;
extern int base_time_delta;

/* ========== Prototipos de funcoes ========== */

/* Funcoes de terminal */
void clear_screen();
void move_cursor_to_home();
void hide_cursor();
void show_cursor();

/* Funcoes de utilidade */
double random_double(double min, double max);

/* Funcoes de classificacao */
void adjust_first_place(Rank rank, int winner);
void insert_cyclist_in_rank(Rank rank, int cyclist_id, int time);
void insert_cyclist(RankList list, int size, int lap, int cyclist_id, int time);
void destroy_rank(Rank rank);
void destroy_rank_list(RankList list);
void print_rank(RankList list, int lap);
void print_final_rank(Rank rank);
void print_breakdown_rank(Rank rank);
int get_last_place(RankList list, int lap);
int get_new_last_place(RankList list, int lap, int cyclist_id);
int get_first_place(RankList list, int lap);
Rank create_rank(int lap, int size);
Rank find_rank(RankList list, int lap);
RankList create_rank_list();
RankList remove_rank(RankList list);
RankList remove_ranks_by_lap(RankList list, int lap);

/* Funcoes de thread de ciclista */
void *cyclist_thread(void *arg);
void move_forward(cyclist_t *cyclist);
void move_to_outer_lane(cyclist_t *cyclist);
void move_to_inner_lane(cyclist_t *cyclist);
void set_cyclist_speed(cyclist_t *cyclist);
void check_cyclists_ahead(cyclist_t *cyclist);
void handle_finish_line(cyclist_t *cyclist);

/* Funcoes de thread de coordenador */
void *coordinator_thread(void *arg);
void display_track();
void eliminate_cyclist(cyclist_t *cyclist_head, int cyclist_number, bool should_print);
void eliminate_broken_down(cyclist_t *cyclist_head);
void declare_winner(int winner);
void declare_elimination(int cyclist_number);
void declare_breakdown(int cyclist_number);

/* Funcoes do programa principal */
void destroy_track();
void clean_up();
void initialize_variables();
void create_coordinator_thread();
void create_cyclist_threads();
void join_cyclist_threads();
void join_coordinator_thread();

#endif /* EP2_H */ 