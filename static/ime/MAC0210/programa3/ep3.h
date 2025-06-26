#ifndef EP3_H
#define EP3_H

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

/**
 * @brief Estrutura para representar um ponto de dados com coordenadas x e y
 * 
 * Esta estrutura é usada para armazenar pontos de dados que serão utilizados
 * na interpolação de Lagrange.
 */
typedef struct {
    double x;  /**< Coordenada x do ponto */
    double y;  /**< Coordenada y do ponto */
} DataPoint;

/**
 * @brief Realiza interpolação de Lagrange para um conjunto de pontos
 * 
 * Esta função calcula os coeficientes do polinômio interpolador de Lagrange
 * para um conjunto de n pontos de dados.
 * 
 * @param n Número de pontos de dados
 * @param data Array de pontos de dados do tipo DataPoint
 * @return Ponteiro para array de coeficientes do polinômio (deve ser liberado com free())
 *         ou NULL em caso de erro de alocação de memória
 * 
 * @note O caller é responsável por liberar a memória retornada usando free()
 * @warning Os pontos devem ter coordenadas x distintas para evitar divisão por zero
 */
double* lagrange_interpolation(int n, DataPoint *data);

/**
 * @brief Executa a primeira parte do exercício programa
 * 
 * Esta função implementa a resolução da primeira parte do EP3, realizando
 * interpolação de Lagrange em um conjunto predefinido de 7 pontos de dados
 * e exibindo os coeficientes resultantes.
 */
void part_1(void);

/**
 * @brief Avalia um polinômio em um ponto específico
 * 
 * Esta função avalia um polinômio representado por seus coeficientes
 * em um ponto x específico.
 * 
 * @param coefficients Array de coeficientes do polinômio
 * @param n Grau do polinômio + 1 (número de coeficientes)
 * @param x Ponto onde avaliar o polinômio
 * @return Valor do polinômio no ponto x
 */
double evaluate_polynomial(double *coefficients, int n, double x);

/**
 * @brief Integra numericamente usando a regra do trapézio
 * 
 * Esta função calcula a integral numérica de um polinômio usando
 * a regra do trapézio composta.
 * 
 * @param coefficients Array de coeficientes do polinômio
 * @param n Grau do polinômio + 1 (número de coeficientes)
 * @param a Limite inferior de integração
 * @param b Limite superior de integração
 * @param num_intervals Número de intervalos para a integração
 * @return Valor aproximado da integral
 */
double trapezoid_rule(double *coefficients, int n, double a, double b, int num_intervals);

/**
 * @brief Integra numericamente usando a regra de Simpson
 * 
 * Esta função calcula a integral numérica de um polinômio usando
 * a regra de Simpson composta (1/3).
 * 
 * @param coefficients Array de coeficientes do polinômio
 * @param n Grau do polinômio + 1 (número de coeficientes)
 * @param a Limite inferior de integração
 * @param b Limite superior de integração
 * @param num_intervals Número de intervalos para a integração (deve ser par)
 * @return Valor aproximado da integral
 * 
 * @warning O número de intervalos deve ser par para a regra de Simpson
 */
double simpson_rule(double *coefficients, int n, double a, double b, int num_intervals);

/**
 * @brief Executa a segunda parte do exercício programa
 * 
 * Esta função implementa a resolução da segunda parte do EP3.
 * 
 * @note Implementação ainda não finalizada
 */
void part_2(void);

#endif /* EP3_H */
