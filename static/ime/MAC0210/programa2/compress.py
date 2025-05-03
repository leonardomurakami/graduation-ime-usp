import numpy as np
from PIL import Image

def compress(originalImg, k):
    """
    Compresses a square image by keeping only rows and columns with index congruent to 0 mod (k+1).
    Supports RGB (3 channels), RGBA (4 channels), grayscale with alpha (2 channels), and grayscale (1 channel) images.
    
    Args:
        originalImg (str): Path to the original image to compress
        k (int): Compression rate, i.e., number of rows and columns to remove
    
    Returns:
        None: Saves the compressed image as 'compressed.png'
    """
    img = Image.open(originalImg)
    img_array = np.array(img)
    
    # Handle grayscale images (2D array)
    if len(img_array.shape) == 2:
        img_array = img_array.reshape(img_array.shape[0], img_array.shape[1], 1)
    
    p = img_array.shape[0]
    if p != img_array.shape[1]:
        raise ValueError("The image must be square")
    
    num_channels = img_array.shape[2]
    
    n = int((p + k) / (k + 1))
    compressed = np.zeros((n, n, num_channels), dtype=np.uint8)
    
    for i in range(n):
        for j in range(n):
            orig_i = i * (k + 1)
            orig_j = j * (k + 1)
            compressed[i, j] = img_array[orig_i, orig_j]
    
    if num_channels == 1:
        compressed = compressed.reshape(n, n)
    
    compressed_img = Image.fromarray(compressed)
    compressed_img.save('compressed.png', quality=100, optimize=False)
    print(f"Compressed image saved as 'compressed.png'. Original size: {p}x{p}, Compressed size: {n}x{n}")
    return compressed_img