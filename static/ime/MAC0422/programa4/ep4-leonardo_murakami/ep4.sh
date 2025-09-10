#!/bin/bash

# verifica se pelo menos 2 argumentos foram fornecidos
if [ $# -lt 2 ]; then
    echo "Usage: $0 <num_clients> <file_size_1_MB> [file_size_2_MB] ..."
    exit 1
fi

NUM_CLIENTS=$1
shift
FILE_SIZES=("$@")

# nomes dos servidores e clientes
SERVERS=("ep4-servidor-inet_processos" "ep4-servidor-inet_threads" "ep4-servidor-inet_muxes" "ep4-servidor-unix_threads")
INET_CLIENT="ep4-cliente-inet"
UNIX_CLIENT="ep4-cliente-unix"

# compilacao
echo "Compilando ep4-servidor-inet_processos"
gcc -o /tmp/ep4-servidor-inet_processos ep4-clientes+servidores/ep4-servidor-inet_processos.c -pthread

echo "Compilando ep4-servidor-inet_threads"
gcc -o /tmp/ep4-servidor-inet_threads ep4-clientes+servidores/ep4-servidor-inet_threads.c -pthread

echo "Compilando ep4-servidor-inet_muxes"
gcc -o /tmp/ep4-servidor-inet_muxes ep4-clientes+servidores/ep4-servidor-inet_muxes.c -pthread

echo "Compilando ep4-servidor-unix_threads"
gcc -o /tmp/ep4-servidor-unix_threads ep4-clientes+servidores/ep4-servidor-unix_threads.c -pthread

echo "Compilando ep4-cliente-inet"
gcc -o /tmp/ep4-cliente-inet ep4-clientes+servidores/ep4-cliente-inet.c

echo "Compilando ep4-cliente-unix"
gcc -o /tmp/ep4-cliente-unix ep4-clientes+servidores/ep4-cliente-unix.c

# inicializa arquivo de dados
DATA_FILE="/tmp/ep4-resultados-${NUM_CLIENTS}.data"
> "$DATA_FILE"

# loop principal: itera sobre tamanhos de arquivo
for size in "${FILE_SIZES[@]}"; do
    echo ">>>>>>> Gerando um arquivo texto de: ${size}MB..."
    
    # gera arquivo do tamanho especificado
    FILE_NAME="/tmp/$(printf "%02d" $size)MB.txt"
    base64 /dev/urandom | head -c $((size * 1024 * 1024)) > "$FILE_NAME"
    echo >> "$FILE_NAME"
    
    # array para armazenar resultados de tempo para este tamanho de arquivo
    TIMES=()
    
    # loop para cada servidor
    for server in "${SERVERS[@]}"; do
        echo "Subindo o servidor $server"
        
        # mata instancias existentes para garantir a limpeza dos logs
        pkill -f "$server" 2>/dev/null
        sleep 1
        
        # inicia servidor sem poluir o terminal
        /tmp/$server &>/dev/null &
        
        # pega o pid do servidor
        SERVER_PID=$!
        sleep 2
        
        # registra tempo de inicio
        START_TIME=$(/bin/date "+%Y-%m-%d %H:%M:%S")
        
        echo ">>>>>>> Fazendo $NUM_CLIENTS clientes ecoarem um arquivo de: ${size}MB..."
        
        # inicia clientes concorrentemente
        CLIENT_PIDS=()
        for ((i=1; i<=NUM_CLIENTS; i++)); do
            if [[ "$server" == *"unix"* ]]; then
                /tmp/$UNIX_CLIENT < "$FILE_NAME" &>/dev/null &
            else
                /tmp/$INET_CLIENT 127.0.0.1 < "$FILE_NAME" &>/dev/null &
            fi
            CLIENT_PIDS+=($!)
        done
        
        echo "Esperando os clientes terminarem..."
        
        # espera todos os clientes terminarem
        for pid in "${CLIENT_PIDS[@]}"; do
            wait $pid 2>/dev/null
        done
        
        echo "Verificando os instantes de tempo no journald..."
        
        sleep 2
        
        # encontra informacoes de tempo do journald usando journalctl
        # busca o primeiro "Passou pelo accept" (primeiro cliente conectou)
        FIRST_ACCEPT_RAW=$(journalctl -q --since "$START_TIME" --no-pager | grep "Passou pelo accept" | head -1 | awk '{print $1" "$2" "$3}')
        
        # busca o ultimo "provavelmente enviou um exit" (ultimo cliente terminou)  
        LAST_EXIT_RAW=$(journalctl -q --since "$START_TIME" --no-pager | grep "provavelmente enviou um exit" | tail -1 | awk '{print $1" "$2" "$3}')
        EXIT_COUNT=$(journalctl -q --since "$START_TIME" --no-pager | grep "provavelmente enviou um exit" | wc -l)
        # calcula tempo
        if [ -n "$FIRST_ACCEPT_RAW" ] && [ -n "$LAST_EXIT_RAW" ]; then
            # converte formato journalctl para um formato que o dateutils entende (YYYY-MM-DD HH:MM:SS)
            CURRENT_YEAR=$(date +%Y)
            FIRST_ACCEPT=$(date -d "${FIRST_ACCEPT_RAW} ${CURRENT_YEAR}" "+%Y-%m-%d %H:%M:%S")
            LAST_EXIT=$(date -d "${LAST_EXIT_RAW} ${CURRENT_YEAR}" "+%Y-%m-%d %H:%M:%S")
            TIME_STR=$(dateutils.ddiff "$FIRST_ACCEPT" "$LAST_EXIT" -f "%0M:%0S")
        fi
        
        echo ">>>>>>> $EXIT_COUNT clientes encerraram a conexão"
        echo ">>>>>>> Tempo para servir os $NUM_CLIENTS clientes com o $server: $TIME_STR"
        
        # armazena resultado do tempo
        TIMES+=("$TIME_STR")
        
        # mata o servidor
        echo "Enviando um sinal 15 para o servidor $server..."
        kill -15 $SERVER_PID 2>/dev/null
    done
    
    # adiciona esta linha ao arquivo de dados
    echo -n "$(printf "%02d" $size)" >> "$DATA_FILE"
    for time in "${TIMES[@]}"; do
        echo -n " $time" >> "$DATA_FILE"
    done
    echo >> "$DATA_FILE"
done

# gera arquivo de configuracao do gnuplot
GPI_FILE="/tmp/ep4-resultados-${NUM_CLIENTS}.gpi"
PDF_FILE="ep4-resultados-${NUM_CLIENTS}.pdf"

cat > "$GPI_FILE" << EOF
set ydata time
set timefmt "%M:%S"
set format y "%M:%S"
set xlabel 'Dados transferidos por cliente (MB)'
set ylabel 'Tempo para atender $NUM_CLIENTS clientes concorrentes'
set term pdfcairo
set output "$PDF_FILE"
set grid
set key top left
plot "$DATA_FILE" using 1:2 with linespoints title "Sockets da Internet: Processos",\\
 "$DATA_FILE" using 1:3 with linespoints title "Sockets da Internet: Threads",\\
 "$DATA_FILE" using 1:4 with linespoints title "Sockets da Internet: Mux de E/S",\\
 "$DATA_FILE" using 1:5 with linespoints title "Sockets Unix: Threads"
EOF

echo ">>>>>>> Gerando o gráfico de $NUM_CLIENTS clientes com arquivos de: ${FILE_SIZES[*]}MB"

# gera o grafico
gnuplot "$GPI_FILE"

# limpa arquivos temporarios
rm -f /tmp/ep4-servidor-* /tmp/ep4-cliente-* /tmp/*MB.txt "$GPI_FILE" "$DATA_FILE"

exit 0
