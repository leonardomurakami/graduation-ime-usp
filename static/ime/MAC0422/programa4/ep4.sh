#!/bin/bash

# MAC0422 - Sistemas Operacionais - EP4
# Script para Avaliação de Desempenho de Servidores de Echo Concorrentes

set -euo pipefail

# Argument validation
if [ "$#" -lt 2 ]; then
    echo "ERRO: Número insuficiente de argumentos." >&2
    echo "Uso: $0 <numero_clientes> <tamanho_arquivo1_MB> [<tamanho_arquivo2_MB> ...]" >&2
    exit 1
fi

# Global variables
readonly CLIENT_COUNT="$1"
shift
readonly FILE_SIZES_MB=("$@")
readonly SERVERS=("ep4-servidor-inet_processos" "ep4-servidor-inet_threads" "ep4-servidor-inet_muxes" "ep4-servidor-unix_threads")
readonly CLIENTS=("ep4-cliente-inet" "ep4-cliente-unix")
readonly SOURCE_DIR="ep4-clientes+servidores"
readonly TMP_DIR="/tmp"

TEMP_FILES=()

# Cleanup function
cleanup() {
    echo ">>> Executando limpeza de arquivos e processos..."
    set +e 
    if [ ${#TEMP_FILES[@]} -gt 0 ]; then
        rm -f "${TEMP_FILES[@]}"
    fi
    pkill -f "${TMP_DIR}/ep4-servidor" || true
    pkill -f "${TMP_DIR}/ep4-cliente" || true
    echo "Limpeza concluída."
}

trap cleanup EXIT

# Compilation phase
echo "--- Iniciando Fase de Compilação ---"
ALL_SOURCES=("${SERVERS[@]}" "${CLIENTS[@]}")
for src_base_name in "${ALL_SOURCES[@]}"; do
    echo "Compilando ${src_base_name}"
    src_file="${SOURCE_DIR}/${src_base_name}.c"
    bin_file="${TMP_DIR}/${src_base_name}"

    if ! [ -f "$src_file" ]; then
        echo "ERRO: Arquivo fonte não encontrado: $src_file. Certifique-se de que o diretório '${SOURCE_DIR}' existe." >&2
        exit 1
    fi

    # Thread-based servers require pthread library
    if [[ "$src_base_name" == *"threads"* ]]; then
        gcc -pthread "$src_file" -o "$bin_file"
    else
        gcc "$src_file" -o "$bin_file"
    fi

    TEMP_FILES+=("$bin_file")
done
echo "--- Compilação Concluída ---"
echo

# Data collection phase
echo "--- Iniciando Fase de Testes e Coleta de Dados ---"
readonly DATA_FILE="${TMP_DIR}/ep4-resultados-${CLIENT_COUNT}.data"
TEMP_FILES+=("$DATA_FILE")
touch "$DATA_FILE"

for size_mb in "${FILE_SIZES_MB[@]}"; do
    echo ">>>>>>> Gerando um arquivo texto de: ${size_mb}MB..."
    readonly size_bytes=$((size_mb * 1024 * 1024))
    readonly input_file="${TMP_DIR}/input_${size_mb}MB.txt"
    TEMP_FILES+=("$input_file")
    
    # Generate random content file
    head -c "$size_bytes" /dev/urandom | base64 > "$input_file"
    echo >> "$input_file"

    times_for_size=()

    for server_name in "${SERVERS[@]}"; do
        readonly server_bin="${TMP_DIR}/${server_name}"
        
        # Determine correct client for server type
        local client_name
        if [[ "$server_name" == *"unix"* ]]; then
            client_name="ep4-cliente-unix"
        else
            client_name="ep4-cliente-inet"
        fi
        readonly client_bin="${TMP_DIR}/${client_name}"

        echo "Subindo o servidor ${server_name}"
        # Save start time for journald log filtering
        readonly start_time_log_filter=$(date '+%Y-%m-%d %H:%M:%S')
        sleep 1

        # Start server in background
        "$server_bin" &
        readonly server_pid=$!

        echo ">>>>>>> Fazendo ${CLIENT_COUNT} clientes ecoarem um arquivo de: ${size_mb}MB..."
        
        # Start clients in background
        for ((i=1; i<=CLIENT_COUNT; i++)); do
            if [[ "$client_name" == "ep4-cliente-unix" ]]; then
                "$client_bin" < "$input_file" &>/dev/null &
            else
                "$client_bin" 127.0.0.1 < "$input_file" &>/dev/null &
            fi
        done

        echo "Esperando os clientes terminarem."
        # Wait for all clients to finish
        while pgrep -f "$client_bin" > /dev/null; do
            sleep 1
        done

        echo "Verificando os instantes de tempo no journald..."
        
        # Extract logs from journald
        local log_output
        log_output=$(journalctl --since "$start_time_log_filter" -o short-iso -q SYSLOG_IDENTIFIER="$server_name" || true)

        local num_finished
        num_finished=$(echo "$log_output" | grep -c "fim servico" || true)
        
        echo ">>>>>>> ${num_finished} clientes encerraram a conexão"

        local first_start_time last_end_time
        first_start_time=$(echo "$log_output" | grep "inicio servico" | head -n 1 | cut -d' ' -f1)
        last_end_time=$(echo "$log_output" | grep "fim servico" | tail -n 1 | cut -d' ' -f1)
        
        local total_time="ERRO"
        if [ -n "$first_start_time" ] && [ -n "$last_end_time" ]; then
            # Calculate time difference in MM:SS format
            total_time=$(dateutils.ddiff "$first_start_time" "$last_end_time" -f "%OM:%S")
        else
            echo "AVISO: Não foi possível extrair tempos do journald para ${server_name}. Verifique as mensagens de log." >&2
        fi

        echo ">>>>>>> Tempo para servir os ${CLIENT_COUNT} clientes com o ${server_name}: ${total_time}"
        times_for_size+=("$total_time")
        
        echo "Enviando um sinal 15 para o servidor ${server_name}..."
        # Gracefully terminate server
        kill -15 "$server_pid"
        wait "$server_pid" 2>/dev/null || true
        
        echo
        sleep 1
    done

    # Write data line to file
    echo "$size_mb ${times_for_size[0]} ${times_for_size[1]} ${times_for_size[2]} ${times_for_size[3]}" >> "$DATA_FILE"
done
echo "--- Coleta de Dados Concluída ---"
echo

# Graph generation phase
echo "--- Iniciando Geração do Gráfico ---"
readonly file_sizes_str=$(echo "${FILE_SIZES_MB[*]}" | sed 's/ /MB, /g')MB
echo ">>>>>>> Gerando o gráfico de ${CLIENT_COUNT} clientes com arquivos de: ${file_sizes_str}"

readonly gpi_file="${TMP_DIR}/ep4-plot-${CLIENT_COUNT}.gpi"
TEMP_FILES+=("$gpi_file")
readonly pdf_output_file="ep4-resultados-${CLIENT_COUNT}.pdf"

# Create gnuplot script
cat << EOF > "$gpi_file"
# Time configuration for Y axis
set ydata time
set timefmt "%M:%S"
set format y "%M:%S"

# Labels and title
set xlabel 'Dados transferidos por cliente (MB)'
set ylabel 'Tempo para atender ${CLIENT_COUNT} clientes concorrentes'
set title 'Desempenho de Servidores Concorrentes (${CLIENT_COUNT} clientes)'

# Output and style settings
set term pdfcairo
set output "${pdf_output_file}"
set grid
set key top left

# Plot command
plot "${DATA_FILE}" using 1:4 with linespoints title "Sockets da Internet: Mux de E/S",\\
     "${DATA_FILE}" using 1:3 with linespoints title "Sockets da Internet: Threads",\\
     "${DATA_FILE}" using 1:2 with linespoints title "Sockets da Internet: Processos",\\
     "${DATA_FILE}" using 1:5 with linespoints title "Sockets Unix: Threads"
EOF

# Generate PDF graph
if ! gnuplot "$gpi_file"; then
    echo "ERRO: gnuplot falhou ao gerar o gráfico." >&2
    exit 1
fi

echo "Gráfico gerado com sucesso: ${pdf_output_file}"
echo

echo "Script concluído."
exit 0