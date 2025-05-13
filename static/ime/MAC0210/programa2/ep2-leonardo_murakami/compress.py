import numpy as np
from PIL import Image

def compress(originalImg, k):
    """
    comprime uma imagem quadrada mantendo apenas as linhas e colunas com indice congruente a 0 mod (k+1).
    suporta imagens rgb (3 canais), rgba (4 canais), escala de cinza com alpha (2 canais) e escala de cinza (1 canal).
    
    args:
        originalImg (str): caminho para a imagem original a comprimir
        k (int): taxa de compressao, i.e., numero de linhas e colunas a remover
    
    returns:
        none: salva a imagem comprimida como 'compressed.png'
    """
    img = Image.open(originalImg)
    img_array = np.array(img)
    
    # trata imagens em escala de cinza (array 2d)
    if len(img_array.shape) == 2:
        img_array = img_array.reshape(img_array.shape[0], img_array.shape[1], 1)
    
    p = img_array.shape[0]
    if p != img_array.shape[1]:
        raise ValueError("a imagem deve ser quadrada")
    
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
    print(f"imagem comprimida salva como 'compressed.png'. tamanho original: {p}x{p}, tamanho comprimido: {n}x{n}")
    return compressed_img