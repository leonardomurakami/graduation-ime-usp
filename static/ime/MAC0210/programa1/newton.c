#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <complex.h>

#define MAX_ITERATIONS 200
#define TOLERANCE 1e-8
#define P1 2000  // Número de pixels na direção x
#define P2 2000  // Número de pixels na direção y
#define MAX_ROOTS 200

// Domínio do plano real
#define L_REAL -3.5
#define U_REAL 3.5
// Domínio do plano imaginário
#define L_IMAG -3.5
#define U_IMAG 3.5

// Função a ser avaliada f(z) = tan z
double complex evalf(double complex x) {
    return ctan(x);
}

// Função derivada a ser avaliada f'(z) = 1/(cos(z))^2
double complex evalDf(double complex x) {
    return 1/(cpow(ccos(x),2));
}

// Função para verificar se uma raiz já está armazenada
int is_root_stored(double complex root, double complex roots[], int num_roots) {
    for (int i = 0; i < num_roots; i++) {
        if (cabs(root - roots[i]) < TOLERANCE) {
            return i;
        }
    }
    return -1;
}

double complex newton(double complex x0) {
    double complex x = x0;
    double complex fx, dfx;
    int iterations = 0;
    
    while (iterations < MAX_ITERATIONS) {
        fx = evalf(x);
        if (cabs(fx) < TOLERANCE) {
            return x;  // Retorna a raiz convergida
        }
        
        dfx = evalDf(x);
        if (cabs(dfx) < TOLERANCE) {
            return 0; // Derivada muito próxima de zero
        }
        
        x = x - fx / dfx;
        iterations++;
    }
    
    return 0; // Não convergiu (salva na basin 0)
}

void newton_basins(double l1, double u1, double l2, double u2, int p1, int p2) {
    FILE *fp = fopen("output.txt", "w");
    if (fp == NULL) {
        printf("Error opening file!\n");
        return;
    }
    
    double complex roots[MAX_ROOTS];
    int num_roots = 0;
    
    double dx = (u1 - l1) / (p1 - 1);
    double dy = (u2 - l2) / (p2 - 1);
    
    for (int i = 0; i < p2; i++) {
        for (int j = 0; j < p1; j++) {
            double real = l1 + j * dx;
            double imag = l2 + i * dy;
            double complex z0 = real + imag * I;
            
            double complex root = newton(z0);
            if (cabs(root) > TOLERANCE) { 
                int root_index = is_root_stored(root, roots, num_roots);
                if (root_index == -1 && num_roots < MAX_ROOTS) {
                    roots[num_roots++] = root;
                }
            }
        }
    }

    for (int i = 0; i < p2; i++) {
        for (int j = 0; j < p1; j++) {
            double real = l1 + j * dx;
            double imag = l2 + i * dy;
            double complex z0 = real + imag * I;
            
            double complex root = newton(z0);
            int basin = 0; // Basin 0 para não convergência
            
            if (cabs(root) > TOLERANCE) {
                int root_index = is_root_stored(root, roots, num_roots);
                if (root_index != -1) {
                    basin = root_index + 1;
                }
            }
            
            fprintf(fp, "%f %f %d\n", real, imag, basin);
        }
        fprintf(fp, "\n");
    }
    
    fclose(fp);
}

int main() {
    double l1 = L_REAL;  // Limite inferior para parte real
    double u1 = U_REAL;   // Limite superior para parte real
    double l2 = L_IMAG;  // Limite inferior para parte imaginária
    double u2 = U_IMAG;   // Limite superior para parte imaginária
    
    newton_basins(l1, u1, l2, u2, P1, P2);
    
    FILE *gp = fopen("plot.gp", "w");
    if (gp != NULL) {
        fprintf(gp, "set palette model HSV rgbformulae 1,2,3\n");
        fprintf(gp, "set terminal png size %d,%d\n", P1, P2);
        fprintf(gp, "set output 'newton_basins.png'\n");
        fprintf(gp, "set title 'Newton Basins for f(z) = tan z'\n");
        fprintf(gp, "set xlabel 'Re(z)'\n");
        fprintf(gp, "set ylabel 'Im(z)'\n");
        fprintf(gp, "set xrange [%f:%f]\n", l1, u1);
        fprintf(gp, "set yrange [%f:%f]\n", l2, u2);
        fprintf(gp, "plot 'output.txt' using 1:2:3 with points pt 5 palette notitle\n");
        fclose(gp);
    }
    
    system("gnuplot plot.gp");
    
    return 0;
} 