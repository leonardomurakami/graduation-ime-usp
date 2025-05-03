import numpy as np
from PIL import Image

def calculateError(originalImg, decompressedImg):
    """
    Calculates the error between the original and decompressed images.
    Supports RGB (3 channels), RGBA (4 channels), grayscale with alpha (2 channels), 
    and grayscale (1 channel) images.
    
    Args:
        originalImg (str): Path to the original image
        decompressedImg (str): Path to the decompressed image
    
    Returns:
        float: The calculated error (average of errors across all channels)
    """
    # Read the images
    original = np.array(Image.open(originalImg))
    decompressed = np.array(Image.open(decompressedImg))
    
    # Handle grayscale images (2D array)
    if len(original.shape) == 2:
        original = original.reshape(original.shape[0], original.shape[1], 1)
    if len(decompressed.shape) == 2:
        decompressed = decompressed.reshape(decompressed.shape[0], decompressed.shape[1], 1)
    
    # Ensure both images have the same number of channels
    if original.shape[2] != decompressed.shape[2]:
        raise ValueError("Original and decompressed images must have the same number of channels")
    
    num_channels = original.shape[2]
    
    # Calculate error for each channel
    errors = []
    for channel in range(num_channels):
        diff_squared = np.square(original[:,:,channel].astype(float) - decompressed[:,:,channel].astype(float))
        mse = np.mean(diff_squared)
        error = np.sqrt(mse)
        errors.append(error)
    
    # Average error across channels
    avg_error = sum(errors) / num_channels
    
    return avg_error