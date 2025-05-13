import numpy as np
from PIL import Image

def calculateError(originalImg, decompressedImg):
    """
    calcula o erro entre as imagens original e descomprimida.
    suporta imagens rgb (3 canais), rgba (4 canais), escala de cinza com alpha (2 canais) 
    e escala de cinza (1 canal).
    
    args:
        originalImg (str): caminho para a imagem original
        decompressedImg (str): caminho para a imagem descomprimida
    
    returns:
        float: o erro calculado (media dos erros em todos os canais)
    """
    # le as imagens
    original = np.array(Image.open(originalImg))
    decompressed = np.array(Image.open(decompressedImg))
    
    # trata imagens em escala de cinza (array 2d)
    if len(original.shape) == 2:
        original = original.reshape(original.shape[0], original.shape[1], 1)
    if len(decompressed.shape) == 2:
        decompressed = decompressed.reshape(decompressed.shape[0], decompressed.shape[1], 1)
    
    # garante que ambas as imagens tem o mesmo numero de canais
    if original.shape[2] != decompressed.shape[2]:
        raise ValueError("as imagens original e descomprimida devem ter o mesmo numero de canais")
    
    num_channels = original.shape[2]
    
    # calcula o erro para cada canal
    errors = []
    for channel in range(num_channels):
        diff_squared = np.square(original[:,:,channel].astype(float) - decompressed[:,:,channel].astype(float))
        mse = np.mean(diff_squared)
        error = np.sqrt(mse)
        errors.append(error)
    
    # media do erro entre os canais
    avg_error = sum(errors) / num_channels
    
    return avg_error