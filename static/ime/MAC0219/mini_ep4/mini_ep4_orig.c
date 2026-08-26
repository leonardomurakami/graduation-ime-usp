#include <stdio.h>
#include <stdlib.h>

void slowsort(int arr[], int i, int j) {
    if (i >= j) return;
    int m = (i + j) / 2;
    slowsort(arr, i, m);
    slowsort(arr, m + 1, j);
    if (arr[j] < arr[m]) {
        int temp = arr[j];
        arr[j] = arr[m];
        arr[m] = temp;
    }
    slowsort(arr, i, j - 1);
}

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n - 1) + fibonacci(n - 2);
}

int main() {
    const int TAMANHO = 200; // Tamanho do vetor
    const int SEED = 42; // Semente para números aleatórios
    int vetor[TAMANHO];
    int soma = 0;

    // Inicializa o gerador de números aleatórios
    srand(SEED);

    // Preenche o vetor com números aleatórios entre 2^2 e (2^2 + 2^5) - 1
    for (int i = 0; i < TAMANHO; i++) {
        vetor[i] = (rand() % (1 << 5)) + (1 << 2);
    }

    // Ordena o vetor usando Slowsort
    slowsort(vetor, 0, TAMANHO - 1);

    // Calcula o Fibonacci para cada elemento e soma os pares
    for (int i = 0; i < TAMANHO; i++) {
        int fib = fibonacci(vetor[i]);
        if (fib % 2 == 0) {
            soma += fib;
        }
    }

    printf("Soma dos números de Fibonacci pares: %d\n", soma);

    return 0;
}