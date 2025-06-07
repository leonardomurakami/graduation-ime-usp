#ifndef EP3_H
#define EP3_H

#include <stdio.h> // para FILE*
#include <stdlib.h> // para exit, atoi
#include <string.h> // para strcmp, strlen, strncpy, strcspn
#include <limits.h> // para INT_MAX
#include <errno.h> // para perror


// ================================================
// =============CONSTANTES PARA MEMORIA============
// ================================================
#define TOTAL_MEMORY_UNITS 65536       // 
#define PGM_WIDTH 256                  // 
#define PGM_HEIGHT 256                 // 
#define PGM_MAX_VAL 255                // 

// CABECALHO PGM: "P2\n256 256\n255\n"
// "P2\n" (3 bytes)
// "256 256\n" (8 bytes)
// "255\n" (4 bytes)
#define PGM_HEADER_SIZE 15             // 

#define UNITS_PER_FILE_LINE 16         // 
// cada linha de dados de pixel: 16 unidades * 3 chars/unidade + 15 espacos + 1 quebra de linha = 48 + 15 + 1 = 64 bytes 
#define BYTES_PER_FILE_DATA_LINE 64

#define STATUS_USED 0                  // representa um pixel preto, unidade em uso 
#define STATUS_FREE 255                // representa um pixel branco, unidade disponivel 

#define TRACE_LINE_MAX_LEN 256
#define MAX_FAILED_REQS 2001 // maximo 2000 linhas no trace + 1 por seguranca 

// ================================================
// =============PROTOTIPOS DE FUNCOES==============
// ================================================

/**
 * @brief copia o conteudo do arquivo PGM de entrada para o arquivo PGM de saida.
 * esta operacao pode usar memoria sem as restricoes usuais do EP.
 * @param input_filename caminho para o arquivo PGM de entrada.
 * @param output_filename caminho para o arquivo PGM de saida a ser criado.
 */
void copy_pgm_file(const char *input_filename, const char *output_filename);

/**
 * @brief calcula o offset do arquivo para um dado indice de unidade de memoria.
 * o offset aponta para o inicio da representacao de 3 caracteres do valor da unidade.
 * @param unit_index o indice baseado em 0 da unidade de memoria (0 a TOTAL_MEMORY_UNITS - 1).
 * @return o offset do arquivo a partir do inicio do arquivo.
 */
long get_unit_file_offset(int unit_index);

/**
 * @brief le o status de uma unidade de memoria diretamente do arquivo PGM.
 * @param fp ponteiro para o arquivo PGM, aberto no modo "r+b".
 * @param unit_index o indice baseado em 0 da unidade de memoria.
 * @return o status da unidade (STATUS_FREE ou STATUS_USED), ou -1 em caso de erro.
 */
int read_unit_status(FILE *fp, int unit_index);

/**
 * @brief escreve o status de uma unidade de memoria diretamente no arquivo PGM.
 * escreve "  0" para STATUS_USED ou "255" para STATUS_FREE.
 * @param fp ponteiro para o arquivo PGM, aberto no modo "r+b".
 * @param unit_index o indice baseado em 0 da unidade de memoria.
 * @param status o novo status a ser escrito (STATUS_FREE ou STATUS_USED).
 */
void write_unit_status(FILE *fp, int unit_index, int status);

/**
 * @brief aloca um bloco de unidades de memoria marcando-as como usadas no arquivo PGM.
 * @param fp ponteiro para o arquivo PGM.
 * @param start_index o indice inicial da unidade do bloco a ser alocado.
 * @param size o numero de unidades a alocar.
 */
void allocate_memory_units(FILE *fp, int start_index, int size);

/**
 * @brief implementa o algoritmo de alocacao de memoria First Fit.
 * encontra o primeiro bloco livre grande o suficiente para o tamanho solicitado.
 * @param fp ponteiro para o arquivo PGM.
 * @param size_needed o numero de unidades de memoria contiguas necessarias.
 * @param total_units numero total de unidades na memoria.
 * @return o indice inicial do bloco alocado, ou -1 se nenhum bloco adequado for encontrado.
 */
int find_first_fit(FILE *fp, int size_needed, int total_units);

/**
 * @brief implementa o algoritmo de alocacao de memoria Next Fit.
 * comeca a busca a partir da posicao apos a ultima alocacao.
 * @param fp ponteiro para o arquivo PGM.
 * @param size_needed o numero de unidades de memoria contiguas necessarias.
 * @param total_units numero total de unidades na memoria.
 * @param last_pos ponteiro para um inteiro armazenando a ultima posicao de alocacao (atualizado por esta funcao).
 * @return o indice inicial do bloco alocado, ou -1 se nenhum bloco adequado for encontrado.
 */
int find_next_fit(FILE *fp, int size_needed, int total_units, int *last_pos);

/**
 * @brief implementa o algoritmo de alocacao de memoria Best Fit.
 * encontra o menor bloco livre que seja grande o suficiente para o tamanho solicitado.
 * @param fp ponteiro para o arquivo PGM.
 * @param size_needed o numero de unidades de memoria contiguas necessarias.
 * @param total_units numero total de unidades na memoria.
 * @return o indice inicial do bloco alocado, ou -1 se nenhum bloco adequado for encontrado.
 */
int find_best_fit(FILE *fp, int size_needed, int total_units);

/**
 * @brief implementa o algoritmo de alocacao de memoria Worst Fit.
 * encontra o maior bloco livre que seja grande o suficiente para o tamanho solicitado.
 * @param fp ponteiro para o arquivo PGM.
 * @param size_needed o numero de unidades de memoria contiguas necessarias.
 * @param total_units numero total de unidades na memoria.
 * @return o indice inicial do bloco alocado, ou -1 se nenhum bloco adequado for encontrado.
 */
int find_worst_fit(FILE *fp, int size_needed, int total_units);

/**
 * @brief compacta a memoria no arquivo PGM.
 * todos os blocos usados sao movidos para o inicio, e todos os blocos livres para o final.
 * isso e feito lendo e escrevendo os status das unidades diretamente no arquivo.
 * @param fp ponteiro para o arquivo PGM.
 * @param total_units numero total de unidades na memoria.
 */
void compact_memory(FILE *fp, int total_units);

#endif // EP3_H