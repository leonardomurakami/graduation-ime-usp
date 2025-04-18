#!/bin/bash
for i in {1..30}; 
do 
echo "Executando FCFS $i"
./ep1 1 entrada-inesperado.txt inesperado/6-threads/fcfs/output_$i.txt --cpu 6; 
done && 
for i in {1..30}; 
do 
echo "Executando SRTN $i"
./ep1 2 entrada-inesperado.txt inesperado/6-threads/srtn/output_$i.txt --cpu 6; 
done && 
for i in {1..30}; 
do 
echo "Executando Priority $i"
./ep1 3 entrada-inesperado.txt inesperado/6-threads/priority/output_$i.txt --cpu 6; 
done