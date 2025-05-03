import numpy as np
from numpy.linalg import solve

def calculate_bilinear_coefficients(compressed_array, x_1, x_2, y_1, y_2, h):
    """
    Calculates the coefficients for bilinear interpolation.
    Args:
        compressed_array: The compressed image array
        x_1 (int): x coordinate of the first pixel
        x_2 (int): x coordinate of the second pixel
        y_1 (int): y coordinate of the first pixel
        y_2 (int): y coordinate of the second pixel
        h (float): Size of interpolation square side
    Returns:
        The coefficients for bilinear interpolation
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
    Performs bilinear interpolation using matrix notation for a pixel at coordinates (y, x).
    
    Args:
        x: X coordinate of the pixel to interpolate
        y: Y coordinate of the pixel to interpolate
        x_base: X coordinate of the base pixel
        y_base: Y coordinate of the base pixel
        alpha: Coefficients for bilinear interpolation
    
    Returns:
        The interpolated pixel value
    """
    dx = (x - x_base)
    dy = (y - y_base)
    value = alpha[0] + alpha[1] * dx + alpha[2] * dy + alpha[3] * dx * dy
    return max(0, min(255, int(value)))