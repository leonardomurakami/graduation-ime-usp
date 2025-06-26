#!/bin/bash

# script para executar automaticamente o ep4.sh com todos os parametros necessarios
# feito para rodar num servidor e esquecer la

chmod +x ep4.sh

CLIENTS=(100 200 300 400 500)
FILE_SIZES=(5 10 15 20 25 30 35)

for clients in "${CLIENTS[@]}"; do
    ./ep4.sh $clients "${FILE_SIZES[@]}"
done 