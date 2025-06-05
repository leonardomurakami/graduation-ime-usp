import numpy as np
from numpy.linalg import solve

def calculate_bilinear_coefficients(compressed_array, x_1, x_2, y_1, y_2, h):
    """
    calcula os coeficientes para interpolacao bilinear.
    args:
        compressed_array: o array da imagem comprimida
        x_1 (int): coordenada x do primeiro pixel
        x_2 (int): coordenada x do segundo pixel
        y_1 (int): coordenada y do primeiro pixel
        y_2 (int): coordenada y do segundo pixel
        h (float): tamanho do lado do quadrado de interpolacao
    returns:
        os coeficientes para interpolacao bilinear
    """ 
    f_11 = compressed_array[x_1, y_1]
    f_12 = compressed_array[x_1, y_2]
    f_21 = compressed_array[x_2, y_1]
    f_22 = compressed_array[x_2, y_2]
    h_matrix = np.array([
        [1, 0, 0, 0],
        [1, 0, h, 0],
        [1, h, 0, 0],
        [1, h, h, h**2]
    ])
    f_matrix = np.array([
        [f_11],
        [f_12],
        [f_21],
        [f_22]
    ])
    alpha = solve(h_matrix, f_matrix)    
    return alpha.flatten()


def decompress_bilinear(x, y, x_base, y_base, alpha):
    """
    realiza interpolacao bilinear usando notacao matricial para um pixel nas coordenadas (y, x).
    
    args:
        x: coordenada x do pixel a interpolar
        y: coordenada y do pixel a interpolar
        x_base: coordenada x do pixel base
        y_base: coordenada y do pixel base
        alpha: coeficientes para interpolacao bilinear
    
    returns:
        o valor do pixel interpolado
    """
    dx = (x - x_base)
    dy = (y - y_base)
    value = alpha[0] + alpha[1] * dx + alpha[2] * dy + alpha[3] * dx * dy
    return max(0, min(255, int(value)))