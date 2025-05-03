import numpy as np

from PIL import Image

from bilinear import calculate_bilinear_coefficients, decompress_bilinear
from bicubic import calculate_bicubic_coefficients, decompress_bicubic

def decompress(compressedImg, method, k, h):
    """
    Decompresses an image by adding k rows and columns between each of the n rows and columns
    and interpolating the missing values. 
    Supports 
        - RGB (3 channels)
        - RGBA (4 channels)
        - Grayscale with alpha (2 channels)
        - Grayscale (1 channel)
    
    Args:
        compressedImg (str): Path to the compressed image
        method (int): Interpolation method (1 - Bilinear, 2 - Bicubic)
        k (int): Decompression rate, matching the compression rate
        h (float): Size of interpolation square side
    
    Returns:
        None: Saves the decompressed image as 'decompressed.png'
    """
    compressed_img = Image.open(compressedImg)
    compressed_array = np.array(compressed_img)
    
    # Handle grayscale images (2D array)
    if len(compressed_array.shape) == 2:
        compressed_array = compressed_array.reshape(compressed_array.shape[0], compressed_array.shape[1], 1)
    
    n = compressed_array.shape[0]
    num_channels = compressed_array.shape[2]
    p = n + (n - 1) * k
    
    # Initialize the decompressed image array
    decompressed = np.zeros((p, p, num_channels), dtype=np.uint8)

    for i in range(n):
        for j in range(n):
            y_pos = i * (k+1)
            x_pos = j * (k+1)
            decompressed[y_pos, x_pos] = compressed_array[i, j]
    
    h = int(h) if h > 1 else 1
    for channel in range(num_channels):
        for square_y in range(0, p, h):
            for square_x in range(0, p, h):
                # Define the boundaries of this square
                y_start = square_y
                y_end = min(square_y + h, p)
                x_start = square_x
                x_end = min(square_x + h, p)
                
                i1 = max(0, y_start // (k+1))
                i2 = min(n-1, (y_end + k) // (k+1))
                j1 = max(0, x_start // (k+1))
                j2 = min(n-1, (x_end + k) // (k+1))
                
                if method == 1:  # Bilinear
                    alpha = calculate_bilinear_coefficients(
                        compressed_array[:,:,channel], 
                        i1, i2, 
                        j1, j2,
                        h
                    )
                    # Calculate all pixels inside the square using the bilinear interpolation with the coefficients found
                    for y in range(y_start, y_end):
                        for x in range(x_start, x_end):
                            if y % (k+1) == 0 and x % (k+1) == 0 and y//(k+1) < n and x//(k+1) < n:
                                continue
                            y_base = i1 * (k+1)
                            x_base = j1 * (k+1)
                            decompressed[y, x, channel] = decompress_bilinear(x, y, x_base, y_base, alpha)
                
                elif method == 2:  # Bicubic
                    alpha = calculate_bicubic_coefficients(
                        compressed_array[:,:,channel], 
                        i1, i2, 
                        j1, j2,
                        h
                    )
                    # Calculate all pixels inside the square using the bicubic interpolation with the coefficients found
                    for y in range(y_start, y_end):
                        for x in range(x_start, x_end):
                            if y % (k+1) == 0 and x % (k+1) == 0 and y//(k+1) < n and x//(k+1) < n:
                                continue
                            y_base = i1 * (k+1)
                            x_base = j1 * (k+1)
                            decompressed[y, x, channel] = decompress_bicubic(x, y, x_base, y_base, alpha)
    
    if num_channels == 1:
        decompressed = decompressed.reshape(p, p)
    
    decompressed_img = Image.fromarray(decompressed)
    decompressed_img.save('decompressed.png', quality=100, optimize=False)
    print(f"Decompressed image saved as 'decompressed.png'. Size: {p}x{p}")

    return decompressed_img
