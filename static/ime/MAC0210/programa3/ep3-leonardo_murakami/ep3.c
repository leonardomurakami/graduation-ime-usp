#include <stdio.h>
#include <math.h>
#include <stdlib.h> // For rand(), srand()
#include <time.h>   // For time()

// =============================================================================
// CONSTANTES E DADOS
// =============================================================================

// Dados da Tabela 1 para F(x)cos(theta(x))
static const double x_values[] = {0.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0};
static const double FcosTheta_values[] = {0.0000, 1.5297, 9.5120, 8.7025, 2.8087, 1.0881, 0.3537};
static const int num_points = sizeof(x_values) / sizeof(x_values[0]);

// =============================================================================
// FUNCOES DE INTERPOLACAO
// =============================================================================

/**
 * Interpolacao de Lagrange para um ponto alvo dado
 * @param x_target: Ponto a ser interpolado
 * @param x_data: Array de coordenadas x
 * @param y_data: Array de coordenadas y
 * @param n: Numero de pontos de dados
 * @return: Valor interpolado em x_target
 */
double lagrange_interp(double x_target, const double x_data[], const double y_data[], int n) {
    double result = 0.0;
    for (int j = 0; j < n; j++) {
        double L_j = 1.0;
        for (int k = 0; k < n; k++) {
            if (k != j) {
                L_j *= (x_target - x_data[k]) / (x_data[j] - x_data[k]);
            }
        }
        result += y_data[j] * L_j;
    }
    return result;
}

/**
 * Funcao wrapper para g(x) interpolada usando dados da tabela
 */
double tau_interpd(double x) {
    return lagrange_interp(x, x_values, FcosTheta_values, num_points);
}

// =============================================================================
// FUNCOES DE INTEGRACAO NUMERICA
// =============================================================================

/**
 * Regra do Trapezio Composta para funcao generica
 * @param func: Funcao a ser integrada
 * @param a: Limite inferior
 * @param b: Limite superior
 * @param n_intervals: Numero de intervalos
 * @return: Aproximacao da integral numerica
 */
double trapezoidal_rule_interp(double (*func)(double), double a, double b, int n_intervals) {
    double h = (b - a) / n_intervals;
    double sum = (func(a) + func(b)) / 2.0;
    
    for (int i = 1; i < n_intervals; i++) {
        sum += func(a + i * h);
    }
    
    return h * sum;
}

/**
 * Regra de Simpson Composta para funcao generica
 * @param func: Funcao a ser integrada
 * @param a: Limite inferior
 * @param b: Limite superior
 * @param n_intervals: Numero de intervalos (deve ser par)
 * @return: Aproximacao da integral numerica
 */
double simpson_rule_interp(double (*func)(double), double a, double b, int n_intervals) {
    if (n_intervals % 2 != 0) {
        printf("Erro: A regra de Simpson requer um numero par de intervalos.\n");
        return -1.0;
    }
    
    double h = (b - a) / n_intervals;
    double sum = func(a) + func(b);
    
    // Indices impares (multiplicar por 4)
    for (int i = 1; i < n_intervals; i += 2) {
        sum += 4 * func(a + i * h);
    }
    
    // Indices pares (multiplicar por 2)
    for (int i = 2; i < n_intervals; i += 2) {
        sum += 2 * func(a + i * h);
    }
    
    return (h / 3.0) * sum;
}

// =============================================================================
// FUNCOES DE INTEGRACAO MONTE CARLO
// =============================================================================

/**
 * Gera numero aleatorio uniforme entre 0 e 1
 */
double random_uniform() {
    return (double)rand() / RAND_MAX;
}

/**
 * Integracao Monte Carlo 1D
 * @param g: Funcao a ser integrada
 * @param a: Limite inferior
 * @param b: Limite superior
 * @param n_samples: Numero de amostras aleatorias
 * @return: Aproximacao Monte Carlo
 */
double monte_carlo_1d(double (*g)(double), double a, double b, int n_samples) {
    double sum_g_values = 0.0;
    
    for (int i = 0; i < n_samples; i++) {
        double u = random_uniform();
        double x = a + (b - a) * u;
        sum_g_values += g(x);
    }
    
    return (b - a) * sum_g_values / n_samples;
}

/**
 * Integracao Monte Carlo multidimensional
 * @param g: Funcao a ser integrada (recebe array de coordenadas)
 * @param d: Dimensao
 * @param n_samples: Numero de amostras aleatorias
 * @return: Aproximacao Monte Carlo
 */
double monte_carlo_md(double (*g)(double[], int), int d, int n_samples) {
    double sum_g_values = 0.0;
    double *u_values = (double *)malloc(d * sizeof(double));

    for (int i = 0; i < n_samples; i++) {
        for (int j = 0; j < d; j++) {
            u_values[j] = random_uniform();
        }
        sum_g_values += g(u_values, d);
    }

    free(u_values);
    return sum_g_values / n_samples;
}

// =============================================================================
// FUNCOES DE TESTE PARA INTEGRACAO
// =============================================================================

double g_sin_x(double x) {
    return sin(x);
}

double g_x_cubed(double x) {
    return x * x * x;
}

double g_exp_neg_x(double x) {
    return exp(-x);
}

double g_pi_approx(double coords[], int d) {
    if (d != 2) {
        printf("Erro: g_pi_approx espera 2 coordenadas.\n");
        return 0.0;
    }
    
    double x = coords[0];
    double y = coords[1];
    
    return (x * x + y * y <= 1.0) ? 1.0 : 0.0;
}

// =============================================================================
// FUNCOES UTILITARIAS PARA SAIDA
// =============================================================================

/**
 * Imprime uma linha separadora
 */
void print_separator() {
    printf("================================================================================\n");
}

/**
 * Imprime um cabecalho de secao com formatacao decorativa
 */
void print_section_header(const char* title) {
    printf("\n");
    print_separator();
    printf("  %s\n", title);
    print_separator();
}

/**
 * Imprime um cabecalho de subsecao
 */
void print_subsection_header(const char* title) {
    printf("\n--- %s ---\n", title);
}

/**
 * Calcula e exibe erro relativo
 */
void print_result_with_error(int n, double approximation, double analytical, const char* unit) {
    double relative_error = fabs((approximation - analytical) / analytical) * 100.0;
    printf("  %8d | %12.6f %s | %8.3f%%\n", 
           n, approximation, unit, relative_error);
}

/**
 * Imprime valor analitico com formatacao
 */
void print_analytical_value(double value, const char* unit) {
    printf("  ---------|---------------|----------\n");
    printf("  Analitico: %10.6f %s\n", value, unit);
}

// =============================================================================
// SECOES PRINCIPAIS DO PROGRAMA
// =============================================================================

/**
 * Parte 1: Calcula trabalho usando interpolacao de Lagrange com regras compostas
 */
void run_work_calculation() {
    print_section_header("PARTE 1: CALCULO DE TRABALHO USANDO INTERPOLACAO DE LAGRANGE");

    double a_part1 = x_values[0];
    double b_part1 = x_values[num_points - 1];

    printf("\nLimites de integracao: [%.1f, %.1f]\n", a_part1, b_part1);
    printf("Usando pontos de dados F(x)cos(theta(x)) com interpolacao de Lagrange\n");

    // Regra do trapezio com interpolacao
    print_subsection_header("Resultados da Regra do Trapezio Composta");
    printf("  Intervalos | Trabalho (J)\n");
    printf("  -----------|--------------\n");
    
    for (int n_intervals = 6; n_intervals <= 600; n_intervals += 60) {
        double work = trapezoidal_rule_interp(tau_interpd, a_part1, b_part1, n_intervals);
        printf("  %9d  |   %10.4f\n", n_intervals, work);
    }

    // Regra de Simpson com interpolacao
    print_subsection_header("Resultados da Regra de Simpson Composta");
    printf("  Intervalos | Trabalho (J)\n");
    printf("  -----------|--------------\n");
    
    for (int n_intervals = 6; n_intervals <= 60; n_intervals += 6) {
        double work = simpson_rule_interp(tau_interpd, a_part1, b_part1, n_intervals);
        if (work != -1.0) {
            printf("  %9d  |   %10.4f\n", n_intervals, work);
        }
    }
}

/**
 * Parte 2: Exemplos de integracao Monte Carlo
 */
void run_monte_carlo_integration() {
    print_section_header("PARTE 2: METODOS DE INTEGRACAO MONTE CARLO");

    // Integral 1: integral de 0 a 1 de sin(x)dx
    print_subsection_header("Integral 1: integral de 0 a 1 de sin(x) dx");
    double analytical_sin = 1.0 - cos(1.0);
    
    printf("  Amostras |  Aproximacao  | Erro Rel.\n");
    printf("  ---------|---------------|----------\n");
    
    for (int n_samples = 1000; n_samples <= 1000000; n_samples *= 10) {
        double result = monte_carlo_1d(g_sin_x, 0.0, 1.0, n_samples);
        print_result_with_error(n_samples, result, analytical_sin, "");
    }
    print_analytical_value(analytical_sin, "");

    // Integral 2: integral de 3 a 7 de x^3 dx
    print_subsection_header("Integral 2: integral de 3 a 7 de x^3 dx");
    double analytical_x3 = (pow(7.0, 4.0) / 4.0) - (pow(3.0, 4.0) / 4.0);
    
    printf("  Amostras |  Aproximacao  | Erro Rel.\n");
    printf("  ---------|---------------|----------\n");
    
    for (int n_samples = 1000; n_samples <= 1000000; n_samples *= 10) {
        double result = monte_carlo_1d(g_x_cubed, 3.0, 7.0, n_samples);
        print_result_with_error(n_samples, result, analytical_x3, "");
    }
    print_analytical_value(analytical_x3, "");

    // Integral 3: integral de 0 a infinito de e^(-x)dx (usando limite superior razoavel)
    print_subsection_header("Integral 3: integral de 0 a infinito de e^(-x) dx");
    double analytical_exp_neg_x = 1.0; // O valor analitico correto e 1
    double upper_bound = 100.0; // Usa 100 em vez de INT_MAX para evitar overflows
    
    printf("  Amostras |  Aproximacao  | Erro Rel.\n");
    printf("  ---------|---------------|----------\n");
    
    for (int n_samples = 1000; n_samples <= 10000000; n_samples *= 5) {
        double result = monte_carlo_1d(g_exp_neg_x, 0.0, upper_bound, n_samples);
        print_result_with_error(n_samples, result, analytical_exp_neg_x, "");
    }
    print_analytical_value(analytical_exp_neg_x, "");
    printf("  Nota: Usando limite superior = %.1f para \"aproximar\" infinito\n", upper_bound);

    // Integral 4: Aproximacao de Pi usando quarto de circulo
    print_subsection_header("Integral 4: Aproximacao do pi Usando o Metodo do Quarto de Circulo");
    
    printf("  Amostras |  Aproximacao  | Erro Rel.\n");
    printf("  ---------|---------------|----------\n");
    
    for (int n_samples = 1000; n_samples <= 10000000; n_samples *= 10) {
        double quarter_circle_area = monte_carlo_md(g_pi_approx, 2, n_samples);
        double pi_approx = 4.0 * quarter_circle_area; 
        print_result_with_error(n_samples, pi_approx, M_PI, "");
    }
    print_analytical_value(M_PI, "");
}

// =============================================================================
// FUNCAO PRINCIPAL
// =============================================================================

int main() {
    // Inicializa gerador de numeros aleatorios
    srand(time(NULL));
    
    printf("\n");
    print_separator();
    printf("  ------------------- EP3 ------------------- \n");
    printf("  MAC0210 - Laboratorio de Metodos Numericos\n");
    print_separator();
    
    run_work_calculation();
    run_monte_carlo_integration();
    
    printf("\n");
    print_separator();
    printf("  EXECUCAO DO PROGRAMA CONCLUIDA\n");
    print_separator();
    printf("\n");
    
    return 0;
}