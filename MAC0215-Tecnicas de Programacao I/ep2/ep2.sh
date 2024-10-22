#!/bin/bash

##################################################################
# MAC0216 - Técnicas de Programação I (2024)
# EP2 - Programação em Bash
#
# Nome do(a) aluno(a) 1: Leonardo Heidi Almeida Murakami
# NUSP 1: 11260186
#
# Nome do(a) aluno(a) 2:
# NUSP 2:
##################################################################

################################################
# GLOBALS
################################################
DATA_DIR="dados"
COMPLETE_FILE="$DATA_DIR/arquivocompleto.csv"
current_file="$COMPLETE_FILE"
declare -a filters=()

################################################
# HEADER
################################################
mostrar_cabecalho() {
    echo "+++++++++++++++++++++++++++++++++++++++"
    echo "Este programa mostra estatísticas do"
    echo "Serviço 156 da Prefeitura de São Paulo"
    echo "+++++++++++++++++++++++++++++++++++++++"
}

################################################
# DATA CHECK
################################################
verificar_diretorio_dados() {
    if [ ! -d "$DATA_DIR" ]; then
        echo "ERRO: Não há dados baixados."
        echo "Para baixar os dados antes de gerar as estatísticas, use:"
        echo "./ep2_servico156.sh <nome do arquivo com URLs de dados do Serviço 156>"
        exit 1
    fi
}

################################################
# DOWNLOAD AND PROCESS
################################################
baixar_e_processar_arquivos() {
    local arquivo_urls="$1"
    mkdir -p "$DATA_DIR"    
    wget -nv -i "$arquivo_urls" -P "$DATA_DIR"    
    for arquivo in "$DATA_DIR"/*.csv; do
        iconv -f ISO-8859-1 -t UTF8 "$arquivo" -o "${arquivo}.tmp"
        mv "${arquivo}.tmp" "$arquivo"
    done
    head -n 1 "$(ls "$DATA_DIR"/*.csv | head -n 1)" > "$COMPLETE_FILE"
    for arquivo in "$DATA_DIR"/*.csv; do
        if [ "$arquivo" != "$COMPLETE_FILE" ]; then
            tail -n +2 "$arquivo" >> "$COMPLETE_FILE"
        fi
    done
}

################################################
# SELECT FILE
################################################
selecionar_arquivo() {
    local arquivos=("$COMPLETE_FILE" $(ls "$DATA_DIR"/*.csv | grep -v "arquivocompleto.csv"))
    PS3="Escolha uma opção de arquivo: "
    select arquivo in "${arquivos[@]}"; do
        if [ -n "$arquivo" ]; then
            current_file="$arquivo"
            filters=()
            mostrar_status_atual
            break
        fi
    done
}

################################################
# COLUMN NAMES
################################################
obter_nomes_colunas() {
    # Lê apenas a primeira linha do arquivo (cabeçalho)
    head -n 1 "$current_file" | \
    # Divide a linha em colunas usando ponto e vírgula como separador
    awk -F';' '{
        # Processa cada coluna
        for(i=1; i<=NF; i++) {
            # Remove espaços em branco no início e fim
            gsub(/^[[:space:]]+|[[:space:]]+$/, "", $i)
            # Imprime o nome da coluna
            print $i
        }
    }'
}

################################################
# ADD FILTER
################################################
adicionar_filtro_coluna() {
    # Cria array com nomes das colunas
    mapfile -t colunas < <(obter_nomes_colunas)
    
    echo "Escolha uma opção de coluna para o filtro:"
    local i=1
    for coluna in "${colunas[@]}"; do
        # Remove caracteres de nova linha e espaços extras
        coluna=$(echo "$coluna" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        printf "%2d) %s\n" $i "$coluna"
        ((i++))
    done
    
    read -p "#? " opcao
    
    if [[ "$opcao" =~ ^[0-9]+$ ]] && [ "$opcao" -ge 1 ] && [ "$opcao" -le "${#colunas[@]}" ]; then
        local coluna_selecionada="${colunas[$((opcao-1))]}"
        
        # Obtém valores únicos para a coluna selecionada usando awk para preservar o valor completo
        echo "Obtendo valores únicos para a coluna..."
        mapfile -t valores < <(awk -F';' -v col="$opcao" '
            NR > 1 {  # Skip header
                val = $col
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", val)  # Trim spaces
                if (val != "" && !seen[val]++) {  # Only print unique, non-empty values
                    print val
                }
            }
        ' "$current_file" | sort)
        
        echo "Escolha uma opção de valor para $coluna_selecionada:"
        local j=1
        for valor in "${valores[@]}"; do
            if [ ! -z "$valor" ]; then
                printf "%2d) %s\n" $j "$valor"
                ((j++))
            fi
        done
        
        read -p "#? " opcao_valor
        
        if [[ "$opcao_valor" =~ ^[0-9]+$ ]] && [ "$opcao_valor" -ge 1 ] && [ "$opcao_valor" -le "${#valores[@]}" ]; then
            local valor_selecionado="${valores[$((opcao_valor-1))]}"
            filters+=("$coluna_selecionada = $valor_selecionado")
            mostrar_status_atual
        fi
    fi
}


################################################
# REMOVE FILTERS
################################################
limpar_filtros() {
    filters=()
    mostrar_status_atual
}

################################################
# SHOW CURRENT STATUS
################################################
mostrar_status_atual() {
    echo "+++ Arquivo atual: $(basename "$current_file")"
    if [ ${#filters[@]} -gt 0 ]; then
        echo "+++ Filtros atuais:"
        # HACK: There must be a better way to do this
        [[ ${#filters[@]} -gt 0 ]] && printf "%s" "${filters[0]}" && \
        for ((i=1; i<${#filters[@]}; i++)); do printf " | %s" "${filters[$i]}"; done
        echo ""
    fi
    echo "+++ Número de reclamações: $(contar_linhas_filtradas)"
    echo "+++++++++++++++++++++++++++++++++++++++"
}

################################################
# COUNT LINES
################################################
contar_linhas_filtradas() {
    local resultado=$(cat "$current_file")
    local num_coluna
    
    for filtro in "${filters[@]}"; do
        local coluna=$(echo "$filtro" | cut -d'=' -f1 | tr -d ' ')
        local valor=$(echo "$filtro" | cut -d'=' -f2 | tr -d ' ')
        
        # Obtém número da coluna
        num_coluna=$(head -n 1 "$current_file" | tr ';' '\n' | grep -n "^$coluna$" | cut -d: -f1)
        
        # Aplica filtro
        resultado=$(echo "$resultado" | awk -F';' -v col="$num_coluna" -v val="$valor" '$col == val')
    done
    
    echo "$resultado" | wc -l
}

################################################
# SHOW MEAN DURATION
################################################
# FIXME: Not correctly calculating average duration, sometimes
mostrar_duracao_media() {
    local resultado=$(cat "$current_file")
    
    # Aplica os filtros existentes
    for filtro in "${filters[@]}"; do
        local coluna=$(echo "$filtro" | cut -d'=' -f1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        local valor=$(echo "$filtro" | cut -d'=' -f2- | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        
        # Encontra o número da coluna
        local num_coluna=1
        while IFS= read -r col; do
            col=$(echo "$col" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
            if [ "$col" = "$coluna" ]; then
                break
            fi
            ((num_coluna++))
        done < <(obter_nomes_colunas)
        
        resultado=$(echo "$resultado" | awk -F';' -v col="$num_coluna" -v val="$valor" '
            function trim(str) {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", str)
                return str
            }
            {
                if (NR == 1 || trim($col) == val) {
                    print
                }
            }
        ')
    done

    # Calcula a duração média usando um único comando awk
    local stats=$(echo "$resultado" | awk -F';' '
        function to_seconds(date_str) {
            gsub(/^[[:space:]]+|[[:space:]]*$/, "", date_str)
            cmd = "date -d \"" date_str "\" +%s"
            cmd | getline seconds
            close(cmd)
            return seconds
        }
        
        NR > 1 && $1 != "" && $13 != "" {
            abertura = to_seconds($1)
            parecer = to_seconds($13)
            if (abertura > 0 && parecer > 0) {
                diff_dias = int((parecer - abertura) / 86400)
                total += diff_dias
                count++
            }
        }
        
        END {
            if (count > 0) {
                printf "%d %d", total, count
            }
        }
    ')
    
    if [ ! -z "$stats" ]; then
        local total_dias=$(echo "$stats" | cut -d' ' -f1)
        local contagem=$(echo "$stats" | cut -d' ' -f2)
        local media_dias=$((total_dias / contagem))
        echo "+++ Duração média da reclamação: $media_dias dias"
    else
        echo "+++ Não há dados suficientes para calcular a duração média"
    fi
    echo "+++++++++++++++++++++++++++++++++++++++"
}

################################################
# SHOW RANKING
################################################
# FIXME: Show ranking is not displaying the ranking
mostrar_ranking_reclamacoes() {
    # Cria array com nomes das colunas
    mapfile -t colunas < <(obter_nomes_colunas)
    
    echo "Escolha uma opção de coluna para análise:"
    local i=1
    for coluna in "${colunas[@]}"; do
        # Remove caracteres de nova linha e espaços extras
        coluna=$(echo "$coluna" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        printf "%2d) %s\n" $i "$coluna"
        ((i++))
    done
    
    read -p "#? " opcao
    
    if [[ "$opcao" =~ ^[0-9]+$ ]] && [ "$opcao" -ge 1 ] && [ "$opcao" -le "${#colunas[@]}" ]; then
        local coluna_selecionada="${colunas[$((opcao-1))]}"
        local resultado=$(cat "$current_file")
        
        if [ ${#filters[@]} -gt 0 ]; then
            for filtro in "${filters[@]}"; do
                local coluna_filtro=$(echo "$filtro" | cut -d'=' -f1 | tr -d ' ')
                local valor_filtro=$(echo "$filtro" | cut -d'=' -f2 | tr -d ' ')
                
                local num_coluna=1
                for col in "${colunas[@]}"; do
                    col=$(echo "$col" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
                    if [ "$col" = "$coluna_filtro" ]; then
                        break
                    fi
                    ((num_coluna++))
                done
                
                resultado=$(echo "$resultado" | awk -F';' -v col="$num_coluna" -v val="$valor_filtro" '$col == val')
            done
        fi
        
        echo "+++ $coluna_selecionada com mais reclamações:"
        echo "$resultado" | cut -d';' -f$opcao | tail -n +2 | sort | uniq -c | sort -rn | head -n 5
        echo "+++++++++++++++++++++++++++++++++++++++"
    fi
}

################################################
# SHOW FILTERED
################################################
mostrar_reclamacoes() {
    local resultado=$(cat "$current_file")
    
    for filtro in "${filters[@]}"; do
        local coluna=$(echo "$filtro" | cut -d'=' -f1 | tr -d ' ')
        local valor=$(echo "$filtro" | cut -d'=' -f2 | tr -d ' ')
        
        local num_coluna=$(head -n 1 "$current_file" | tr ';' '\n' | grep -n "^$coluna$" | cut -d: -f1)
        resultado=$(echo "$resultado" | awk -F';' -v col="$num_coluna" -v val="$valor" '$col == val')
    done
    
    echo "$resultado" | tail -n +2
    mostrar_status_atual
}

################################################
#   __  __          _____ _   _ 
#  |  \/  |   /\   |_   _| \ | |
#  | \  / |  /  \    | | |  \| |
#  | |\/| | / /\ \   | | | . ` |
#  | |  | |/ ____ \ _| |_| |\  |
#  |_|  |_/_/    \_\_____|_| \_|                     
################################################

mostrar_cabecalho

if [ $# -eq 1 ]; then
    if [ ! -f "$1" ]; then
        echo "ERRO: O arquivo $1 não existe."
        exit 1
    fi
    baixar_e_processar_arquivos "$1"
else
    verificar_diretorio_dados
fi

################################################
# MAIN MENU
################################################
while true; do
    echo "Escolha uma opção de operação:"
    PS3="#? "
    select opt in "selecionar_arquivo" "adicionar_filtro_coluna" "limpar_filtros_colunas" \
                 "mostrar_duracao_media_reclamacao" "mostrar_ranking_reclamacoes" \
                 "mostrar_reclamacoes" "sair"; do
        case $opt in
            "selecionar_arquivo")
                selecionar_arquivo
                break
                ;;
            "adicionar_filtro_coluna")
                adicionar_filtro_coluna
                break
                ;;
            "limpar_filtros_colunas")
                limpar_filtros
                break
                ;;
            "mostrar_duracao_media_reclamacao")
                mostrar_duracao_media
                break
                ;;
            "mostrar_ranking_reclamacoes")
                mostrar_ranking_reclamacoes
                break
                ;;
            "mostrar_reclamacoes")
                mostrar_reclamacoes
                break
                ;;
            "sair")
                echo "Fim do programa"
                echo "+++++++++++++++++++++++++++++++++++++++"
                exit 0
                ;;
        esac
    done
done