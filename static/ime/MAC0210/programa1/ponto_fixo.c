#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define MAX_ITER 100
#define TOL 1e-100
#define DIV_TOL 1e10
#define EPS 1e-100

// f(x) = exp(x) - 2x²
double f(double x) {
    return exp(x) - 2 * x * x;
}

// g1(x) = exp(x)/(2x)
double g1(double x) {
    if (fabs(x) < EPS) return 0;
    return exp(x) / (2 * x);
}

// g2(x) = -sqrt(exp(x)/2)
double g2(double x) {
    return -sqrt(exp(x)/2);
}

// g3(x) = x - (exp(x) - 2x²)/(exp(x) - 4x) - Newton-like iteration
double g3(double x) {
    double denominator = exp(x) - 4 * x;
    if (fabs(denominator) < EPS) return x;
    return x - (exp(x) - 2 * x * x) / denominator;
}

// Método de ponto fixo
double fixed_point(double (*g)(double), double x0, int *iterations) {
    double x = x0;
    double x_prev;
    *iterations = 0;
    
    do {
        x_prev = x;
        x = g(x);
        (*iterations)++;
        
        // Verificação de divergência
        if (fabs(x) > DIV_TOL) {
            printf("Método divergiu\n");
            return NAN;
        }
        
        // Verificação de máximo de iterações
        if (*iterations >= MAX_ITER) {
            printf("Máximo de iterações atingido\n");
            return x;
        }
    } while (fabs(x - x_prev) > TOL);
    
    return x;
}

int main() {
    double x0;
    int iterations;
    
    printf("Encontrando raízes de f(x) = exp(x) - 2x²\n\n");
    
    // Primeira raiz (usando g1)
    printf("Primeira raiz (usando g1(x) = exp(x)/(2x)):\n");
    x0 = 1.0;
    double root1 = fixed_point(g1, x0, &iterations);
    printf("Raiz: %.6f\n", root1);
    printf("f(raiz) = %.6e\n", f(root1));
    printf("Iterações: %d\n\n", iterations);
    
    // Segunda raiz (usando g2)
    printf("Segunda raiz (usando g2(x) = -sqrt(exp(x)/2)):\n");
    x0 = -1.0;
    double root2 = fixed_point(g2, x0, &iterations);
    printf("Raiz: %.6f\n", root2);
    printf("f(raiz) = %.6e\n", f(root2));
    printf("Iterações: %d\n\n", iterations);
    
    // Terceira raiz (usando g3)
    printf("Terceira raiz (usando g3(x) = x - (exp(x) - 2x²)/(exp(x) - 4x)):\n");
    x0 = 3.0;
    double root3 = fixed_point(g3, x0, &iterations);
    printf("Raiz: %.6f\n", root3);
    printf("f(raiz) = %.6e\n", f(root3));
    printf("Iterações: %d\n", iterations);
    
    return 0;
}
