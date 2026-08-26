#include <stdio.h>
#include <stdlib.h>

int comparar_inteiros(const void *a, const void *b) {
    int valor_a = *(const int *)a;
    int valor_b = *(const int *)b;
    return (valor_a > valor_b) - (valor_a < valor_b);
}

int main(void) {
    enum { TAMANHO = 200 }; // Tamanho do vetor
    const int SEED = 42; // Semente para números aleatórios
    int vetor[TAMANHO];
    int fibonacci[36] = {0, 1};
    int soma = 0;

    for (int i = 2; i < 36; i++) {
        fibonacci[i] = fibonacci[i - 1] + fibonacci[i - 2];
    }

    // Inicializa o gerador de números aleatórios
    srand(SEED);

    // Preenche o vetor com números aleatórios entre 2^2 e (2^2 + 2^5) - 1
    for (int i = 0; i < TAMANHO; i++) {
        vetor[i] = (rand() % (1 << 5)) + (1 << 2);
    }

    // Ordena o vetor usando qsort
    qsort(vetor, TAMANHO, sizeof(vetor[0]), comparar_inteiros);

    // Calcula o Fibonacci para cada elemento e soma os pares
    for (int i = 0; i < TAMANHO; i++) {
        int valor_fibonacci = fibonacci[vetor[i]];
        if (valor_fibonacci % 2 == 0) {
            soma += valor_fibonacci;
        }
    }

    printf("Soma dos números de Fibonacci pares: %d\n", soma);

    return 0;
}