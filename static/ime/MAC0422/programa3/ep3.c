#include "ep3.h"
#include <errno.h> // para perror

void copy_pgm_file(const char *input_filename, const char *output_filename) {
    FILE *in_file = fopen(input_filename, "rb");
    if (!in_file) {
        perror("Erro ao abrir arquivo PGM de entrada para copia");
        exit(EXIT_FAILURE);
    }

    FILE *out_file = fopen(output_filename, "wb");
    if (!out_file) {
        perror("Erro ao abrir arquivo PGM de saida para copia");
        fclose(in_file);
        exit(EXIT_FAILURE);
    }

    char buffer[1024];
    size_t bytes_read;
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), in_file)) > 0) {
        if (fwrite(buffer, 1, bytes_read, out_file) != bytes_read) {
            perror("Erro ao escrever durante copia do PGM");
            fclose(in_file);
            fclose(out_file);
            exit(EXIT_FAILURE);
        }
    }

    if (ferror(in_file)) {
        perror("Erro ao ler durante copia do PGM");
        fclose(in_file);
        fclose(out_file);
        exit(EXIT_FAILURE);
    }

    fclose(in_file);
    fclose(out_file);
}

long get_unit_file_offset(int unit_index) {
    if (unit_index < 0 || unit_index >= TOTAL_MEMORY_UNITS) {
        return -1; // indice invalido
    }
    // cada valor de unidade tem 3 caracteres, seguido por um espaco (ou nova linha para o ultimo da linha)
    // efetivamente, cada slot de unidade ocupa 4 caracteres na estrutura da linha do arquivo
    int file_line_index = unit_index / UNITS_PER_FILE_LINE; // indice da linha no arquivo (comecando em 0)
    int unit_pos_in_file_line = unit_index % UNITS_PER_FILE_LINE; // posicao da unidade dentro da linha (comecando em 0)

    long offset = PGM_HEADER_SIZE +                              // pula o cabecalho
                  (long)file_line_index * BYTES_PER_FILE_DATA_LINE + // move para a linha correta
                  (long)unit_pos_in_file_line * 4;               // move para o inicio correto da unidade na linha
    return offset;
}

int read_unit_status(FILE *fp, int unit_index) {
    long offset = get_unit_file_offset(unit_index);
    if (offset == -1) {
        fprintf(stderr, "read_unit_status: indice de unidade invalido %d\n", unit_index);
        return -1; // erro
    }

    if (fseek(fp, offset, SEEK_SET) != 0) {
        perror("read_unit_status: erro no fseek");
        return -1; // erro
    }

    char value_str[4]; // 3 caracteres para o valor + terminador nulo
    if (fread(value_str, 1, 3, fp) != 3) {
        if(feof(fp)) fprintf(stderr, "read_unit_status: erro no fread - EOF alcancado prematuramente no indice %d, offset %ld\n", unit_index, offset);
        else perror("read_unit_status: erro no fread");
        return -1; // erro
    }
    value_str[3] = '\0';

    return atoi(value_str); // 0 para preto (usado), 255 para branco (livre)
}

void write_unit_status(FILE *fp, int unit_index, int status) {
    long offset = get_unit_file_offset(unit_index);
    if (offset == -1) {
        fprintf(stderr, "write_unit_status: indice de unidade invalido %d\n", unit_index);
        return;
    }

    if (fseek(fp, offset, SEEK_SET) != 0) {
        perror("write_unit_status: erro no fseek");
        return;
    }

    char value_str[4];
    // formata como 3 caracteres, preenchido com espacos a esquerda (ex: "  0" ou "255")
    sprintf(value_str, "%3d", status);

    if (fwrite(value_str, 1, 3, fp) != 3) {
        perror("write_unit_status: erro no fwrite");
        return;
    }
    if (fflush(fp) != 0) { // garante que os dados sao escritos no disco imediatamente
        perror("write_unit_status: erro no fflush");
    }
}

void allocate_memory_units(FILE *fp, int start_index, int size) {
    for (int i = 0; i < size; ++i) {
        write_unit_status(fp, start_index + i, STATUS_USED);
    }
}

int find_first_fit(FILE *fp, int size_needed, int total_units) {
    int current_block_start = -1;
    int current_block_size = 0;

    for (int i = 0; i < total_units; ++i) {
        int status = read_unit_status(fp, i);
        if (status == -1) return -1; // Read error

        if (status == STATUS_FREE) {
            if (current_block_start == -1) {
                current_block_start = i;
            }
            current_block_size++;
            if (current_block_size >= size_needed) {
                return current_block_start; // Found a fit
            }
        } else { // Unit is used or error
            current_block_start = -1;
            current_block_size = 0;
        }
    }
    return -1; // No suitable block found
}

int find_next_fit(FILE *fp, int size_needed, int total_units, int *last_pos) {
    int current_block_start = -1;
    int current_block_size = 0;
    int initial_pos = *last_pos;
    int i = initial_pos;
    int wrapped_around = 0;

    do {
        int status = read_unit_status(fp, i);
        if (status == -1) return -1; // Read error

        if (status == STATUS_FREE) {
            if (current_block_start == -1) {
                current_block_start = i;
            }
            current_block_size++;
            if (current_block_size >= size_needed) {
                // *last_pos = (current_block_start + size_needed) % total_units; // Updated in main
                return current_block_start;
            }
        } else {
            current_block_start = -1;
            current_block_size = 0;
        }

        i = (i + 1) % total_units;
        if (i == initial_pos) { // Full circle
            wrapped_around = 1;
        }
    } while (!wrapped_around || (wrapped_around && i != initial_pos && current_block_start == -1) );
     // The condition can be simplified to run for 'total_units' iterations or until found.
     // Let's re-evaluate the loop condition for clarity for 'total_units' iterations.

    // Corrected loop structure for Next Fit (scan up to N units)
    current_block_start = -1;
    current_block_size = 0;
    for (int count = 0; count < total_units; ++count) {
        int current_idx = (initial_pos + count) % total_units;
        int status = read_unit_status(fp, current_idx);
        if (status == -1) return -1;

        if (status == STATUS_FREE) {
            if (current_block_size == 0) { // Start of a new potential block
                current_block_start = current_idx;
            }
            current_block_size++;
            if (current_block_size >= size_needed) {
                return current_block_start;
            }
        } else { // Block broken
            current_block_size = 0;
        }
    }


    return -1; // No suitable block found
}


int find_best_fit(FILE *fp, int size_needed, int total_units) {
    int best_fit_start = -1;
    int best_fit_size = INT_MAX; // Using INT_MAX from <limits.h>

    int current_block_start = -1;
    int current_block_size = 0;

    for (int i = 0; i < total_units; ++i) {
        int status = read_unit_status(fp, i);
        if (status == -1) return -1; // Read error

        if (status == STATUS_FREE) {
            if (current_block_start == -1) {
                current_block_start = i;
            }
            current_block_size++;
        } else { // Unit is used or end of a block
            if (current_block_start != -1) { // We just finished a free block
                if (current_block_size >= size_needed) {
                    if (current_block_size < best_fit_size) {
                        best_fit_size = current_block_size;
                        best_fit_start = current_block_start;
                    }
                }
            }
            current_block_start = -1;
            current_block_size = 0;
        }
    }
    // Check last block if the memory ends with a free block
    if (current_block_start != -1 && current_block_size >= size_needed) {
        if (current_block_size < best_fit_size) {
            best_fit_start = current_block_start;
        }
    }
    return best_fit_start;
}

int find_worst_fit(FILE *fp, int size_needed, int total_units) {
    int worst_fit_start = -1;
    int worst_fit_size = -1;

    int current_block_start = -1;
    int current_block_size = 0;

    for (int i = 0; i < total_units; ++i) {
        int status = read_unit_status(fp, i);
        if (status == -1) return -1; // Read error

        if (status == STATUS_FREE) {
            if (current_block_start == -1) {
                current_block_start = i;
            }
            current_block_size++;
        } else { // Unit is used or end of a block
            if (current_block_start != -1) { // We just finished a free block
                if (current_block_size >= size_needed) {
                    if (current_block_size > worst_fit_size) {
                        worst_fit_size = current_block_size;
                        worst_fit_start = current_block_start;
                    }
                }
            }
            current_block_start = -1;
            current_block_size = 0;
        }
    }
    // Check last block if the memory ends with a free block
    if (current_block_start != -1 && current_block_size >= size_needed) {
        if (current_block_size > worst_fit_size) {
            worst_fit_start = current_block_start;
            // worst_fit_size = current_block_size; // Not strictly needed here
        }
    }
    return worst_fit_start;
}

void compact_memory(FILE *fp, int total_units) {
    int write_ptr = 0; // aponta para a proxima posicao para escrever um bloco usado

    // primeira passagem: move todos os blocos usados para o inicio
    for (int read_ptr = 0; read_ptr < total_units; ++read_ptr) {
        int status = read_unit_status(fp, read_ptr);
        if (status == -1) {
            fprintf(stderr, "Erro ao ler unidade %d durante compactacao. Abortando compactacao.\n", read_ptr);
            return;
        }

        if (status == STATUS_USED) {
            if (read_ptr != write_ptr) {
                // unidade esta usada e nao esta em sua posicao final compactada
                write_unit_status(fp, write_ptr, STATUS_USED);
            }
            write_ptr++; // avanca o ponteiro de escrita para a proxima unidade usada
        }
    }

    // segunda passagem: preenche o espaco restante (de write_ptr ate o fim) com blocos livres
    // todas as unidades do write_ptr atual ate o fim da memoria se tornam livres
    for (int i = write_ptr; i < total_units; ++i) {
        // verifica o status atual apenas para evitar escritas redundantes se desejado,
        // mas sobrescrever garante a corretude. o problema implica manipulacao direta,
        // entao escrever "255" e a maneira mais direta de marcar como livre
        write_unit_status(fp, i, STATUS_FREE);
    }
}


int main(int argc, char *argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Uso: %s <algoritmo> <arq_in.pgm> <arq_trace> <arq_out.pgm>\n", argv[0]);
        fprintf(stderr, "Algoritmo: 1 (First Fit), 2 (Next Fit), 3 (Best Fit), 4 (Worst Fit)\n");
        return EXIT_FAILURE;
    }

    int algo_choice = atoi(argv[1]);
    const char *input_pgm_name = argv[2];
    const char *trace_file_name = argv[3];
    const char *output_pgm_name = argv[4];

    // validacao da entrada para escolha do algoritmo
    if (algo_choice < 1 || algo_choice > 4) {
        fprintf(stderr, "Erro: Numero do algoritmo invalido. Use 1, 2, 3, ou 4.\n");
        return EXIT_FAILURE;
    }

    copy_pgm_file(input_pgm_name, output_pgm_name);

    FILE *pgm_fp = fopen(output_pgm_name, "r+b"); // abre para leitura e escrita em modo binario
    if (!pgm_fp) {
        perror("Erro ao abrir arquivo PGM de saida para processamento");
        return EXIT_FAILURE;
    }

    FILE *trace_fp = fopen(trace_file_name, "r");
    if (!trace_fp) {
        perror("Erro ao abrir arquivo de trace");
        fclose(pgm_fp);
        return EXIT_FAILURE;
    }

    int unfulfilled_allocations_count = 0;
    static int next_fit_last_search_pos = 0; // para o algoritmo Next Fit

    char trace_line_buffer[TRACE_LINE_MAX_LEN];
    int trace_line_number_from_file; // numero da linha dado no arquivo de trace (para contexto, nao para indexacao de array)
    char request_str[50]; // para ler tamanho ou "COMPACTAR"

    while (fgets(trace_line_buffer, sizeof(trace_line_buffer), trace_fp) != NULL) {
        // remove caractere de nova linha se presente
        trace_line_buffer[strcspn(trace_line_buffer, "\r\n")] = 0;

        if (sscanf(trace_line_buffer, "%d %49s", &trace_line_number_from_file, request_str) != 2) {
            // assumindo formato valido do arquivo de trace conforme descricao do problema
            // se houver uma linha malformada, ela pode ser pulada ou causar um erro dependendo do sscanf
            // para robustez, poderia-se adicionar verificacao de erro mais detalhada para linhas de trace
            continue;
        }
        
        // verifica se request_str e "COMPACTAR" antes de tentar atoi
        if (strcmp(request_str, "COMPACTAR") == 0) {
            compact_memory(pgm_fp, TOTAL_MEMORY_UNITS);
        } else {
            int size_requested = atoi(request_str);
            // conforme o problema: 1 < m < 256, entao size_requested esta entre 2 e 255 inclusive
            // nenhum tratamento de erro especifico para valores invalidos de m e solicitado, assumindo trace valido

            int allocation_start_index = -1;

            switch (algo_choice) {
                case 1: // First Fit
                    allocation_start_index = find_first_fit(pgm_fp, size_requested, TOTAL_MEMORY_UNITS);
                    break;
                case 2: // Next Fit
                    allocation_start_index = find_next_fit(pgm_fp, size_requested, TOTAL_MEMORY_UNITS, &next_fit_last_search_pos);
                    if (allocation_start_index != -1) {
                        next_fit_last_search_pos = (allocation_start_index + size_requested) % TOTAL_MEMORY_UNITS;
                    }
                    break;
                case 3: // Best Fit
                    allocation_start_index = find_best_fit(pgm_fp, size_requested, TOTAL_MEMORY_UNITS);
                    break;
                case 4: // Worst Fit
                    allocation_start_index = find_worst_fit(pgm_fp, size_requested, TOTAL_MEMORY_UNITS);
                    break;
                // caso padrao tratado pela verificacao inicial de algo_choice
            }

            if (allocation_start_index != -1) {
                allocate_memory_units(pgm_fp, allocation_start_index, size_requested);
            } else {
                // alocacao falhou
                printf("%s\n", trace_line_buffer); // imprime a linha original do trace que falhou
                unfulfilled_allocations_count++;
            }
        }
    }

    printf("%d\n", unfulfilled_allocations_count); // imprime o total de alocacoes nao atendidas

    fclose(pgm_fp);
    fclose(trace_fp);

    return EXIT_SUCCESS; // indica que o simulador termina apos processar o trace
}