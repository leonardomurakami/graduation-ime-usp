# EP2 - MAC0422 - Sistemas Operacionais

## Descrição
Versão unificada do EP2 de MAC0422, com todo o código contido em apenas dois arquivos: ep2.c e ep2.h.

## Compilação
```bash
make
```

## Execução
```bash
./ep2 d k [i|e] [-debug]
```

Onde:
- `d`: tamanho da pista (100 <= d <= 2500)
- `k`: número de ciclistas (5 <= k <= 5 × d)
- `i|e`: abordagem de controle de acesso à pista (i para ingênua, e para eficiente)
- `-debug`: modo de depuração (opcional)

## Exemplos de execução
```bash
./ep2 100 10 e     # Pista de tamanho 100, 10 ciclistas, abordagem eficiente
./ep2 200 20 i     # Pista de tamanho 200, 20 ciclistas, abordagem ingênua
./ep2 500 50 e -debug  # Com modo de depuração ativado
```

## Observações
Esta versão foi criada a partir da junção de todos os arquivos originais, mantendo a mesma funcionalidade do programa original. 