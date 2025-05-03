import numpy as np

def calculate_bicubic_coefficients(compressed_array, x_1, x_2, y_1, y_2, h):
    """
    Calculates the coefficients for bicubic interpolation using finite differences
    with explicit boundary handling.
    Args:
        compressed_array: The compressed image array (single channel)
        x_1 (int): Row index of the top-left pixel
        x_2 (int): Row index of the bottom-left pixel
        y_1 (int): Column index of the top-left pixel
        y_2 (int): Column index of the top-right pixel
        h (float): Distance between known pixels (used in derivative calculation)
    Returns:
        The 16 coefficients for bicubic interpolation (alpha matrix)
    """
    n = compressed_array.shape[0]
    f = compressed_array.astype(np.float64)

    def get_fx(i, j):
        if i == 0:
            return (f[i+1, j] - f[i, j]) / h
        elif i == n - 1:
            return (f[i, j] - f[i-1, j]) / h
        else:
            return (f[i+1, j] - f[i-1, j]) / (2 * h)

    def get_fy(i, j):
        if j == 0:
            return (f[i, j+1] - f[i, j]) / h
        elif j == n - 1:
            return (f[i, j] - f[i, j-1]) / h
        else:
            return (f[i, j+1] - f[i, j-1]) / (2 * h)

    def get_fxy(i, j):
        if i == 0:
            if j == 0:
                return (f[1, 1] - f[1, 0] - f[0, 1] + f[0, 0]) / h**2
            elif j == n - 1:
                return (f[1, n-1] - f[1, n-2] - f[0, n-1] + f[0, n-2]) / h**2
            else: 
                return ( (f[1, j+1] - f[0, j+1]) - (f[1, j-1] - f[0, j-1]) ) / (2 * h**2)
        elif i == n - 1:
            if j == 0: 
                return (f[n-1, 1] - f[n-1, 0] - f[n-2, 1] + f[n-2, 0]) / h**2
            elif j == n - 1: 
                return (f[n-1, n-1] - f[n-1, n-2] - f[n-2, n-1] + f[n-2, n-2]) / h**2
            else: 
                return ( (f[n-1, j+1] - f[n-2, j+1]) - (f[n-1, j-1] - f[n-2, j-1]) ) / (2 * h**2)
        else: 
            if j == 0: 
                return ( (f[i+1, 1] - f[i+1, 0]) - (f[i-1, 1] - f[i-1, 0]) ) / (2 * h**2)
            elif j == n - 1: 
                return ( (f[i+1, n-1] - f[i+1, n-2]) - (f[i-1, n-1] - f[i-1, n-2]) ) / (2 * h**2)
            else:
                return (f[i+1, j+1] - f[i+1, j-1] - f[i-1, j+1] + f[i-1, j-1]) / (4 * h**2)


    f_11 = f[x_1, y_1]
    f_12 = f[x_1, y_2]
    f_21 = f[x_2, y_1]
    f_22 = f[x_2, y_2]

    fx_11 = get_fx(x_1, y_1)
    fx_12 = get_fx(x_1, y_2)
    fx_21 = get_fx(x_2, y_1)
    fx_22 = get_fx(x_2, y_2)

    fy_11 = get_fy(x_1, y_1)
    fy_12 = get_fy(x_1, y_2)
    fy_21 = get_fy(x_2, y_1)
    fy_22 = get_fy(x_2, y_2)

    fxy_11 = get_fxy(x_1, y_1)
    fxy_12 = get_fxy(x_1, y_2)
    fxy_21 = get_fxy(x_2, y_1)
    fxy_22 = get_fxy(x_2, y_2)

    f_matrix = np.array([
        [f_11,   f_12,   fy_11,  fy_12],
        [f_21,   f_22,   fy_21,  fy_22],
        [fx_11,  fx_12,  fxy_11, fxy_12],
        [fx_21,  fx_22,  fxy_21, fxy_22],
    ])

    B = np.array([
        [1, 0, 0, 0],
        [1, h, h**2, h**3],
        [0, 1, 0, 0],
        [0, 1, 2*h, 3*h**2]
    ])

    B_inv = np.linalg.inv(B)
    alpha = B_inv @ f_matrix @ B_inv.T
    return alpha

def decompress_bicubic(x, y, x_base, y_base, alpha):
    """
    Performs bicubic interpolation for a pixel at coordinates (y, x).
    Assumes alpha coefficients were calculated considering spacing h.
    
    Args:
        x: X coordinate (column) of the pixel to interpolate
        y: Y coordinate (row) of the pixel to interpolate
        x_base: X coordinate (column) of the top-left known pixel (reference)
        y_base: Y coordinate (row) of the top-left known pixel (reference)
        alpha: Coefficients for bicubic interpolation
    
    Returns:
        The interpolated pixel value
    """
    dx = x - x_base
    dy = y - y_base

    x_vec = np.array([1, dx, dx**2, dx**3])
    y_vec = np.array([1, dy, dy**2, dy**3])

    result = x_vec @ alpha @ y_vec.T 

    return np.clip(np.round(result), 0, 255).astype(np.uint8)