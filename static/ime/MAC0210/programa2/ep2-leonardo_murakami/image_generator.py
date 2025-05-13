import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

from calculateError import calculateError


def generate_image(p, function, output_filename="image.png", x_range=(0, 4*np.pi), y_range=(0, 4*np.pi), grayscale=False):
    """
    gera uma imagem baseada em uma funcao das coordenadas x e y.

    args:
        p (int): o tamanho do lado da imagem quadrada (p x p pixels).
        function (callable): uma funcao que recebe coordenadas x e y e retorna valores (r, g, b) no intervalo [-1, 1].
        output_filename (str): o nome do arquivo para salvar a imagem.
        x_range (tuple): uma tupla (min, max) definindo o intervalo para a coordenada x.
        y_range (tuple): uma tupla (min, max) definindo o intervalo para a coordenada y.
        grayscale (bool): se verdadeiro, gera uma imagem em preto e branco pela media dos valores rgb.

    returns:
        pil.image.image: o objeto da imagem gerada. retorna none se ocorrer um erro.
    """
    if p <= 0:
        print("erro: tamanho da imagem 'p' deve ser positivo.")
        return None


    try:
        x_vals = np.linspace(x_range[0], x_range[1], p)
        y_vals = np.linspace(y_range[0], y_range[1], p)

        yv, xv = np.meshgrid(y_vals, x_vals, indexing='ij')

        r_channel = np.zeros_like(xv)
        g_channel = np.zeros_like(xv)
        b_channel = np.zeros_like(xv)

        for i in range(p):
            for j in range(p):
                r, g, b = function(xv[i, j], yv[i, j])
                r_channel[i, j] = r
                g_channel[i, j] = g
                b_channel[i, j] = b

        r_scaled = ((r_channel + 1.0) / 2.0 * 255.0)
        g_scaled = ((g_channel + 1.0) / 2.0 * 255.0)
        b_scaled = ((b_channel + 1.0) / 2.0 * 255.0)

        if grayscale:
            gray_channel = (r_scaled + g_scaled + b_scaled) / 3.0
            image_array = np.clip(gray_channel, 0, 255).astype(np.uint8)
            img = Image.fromarray(image_array, 'L')
        else:
            image_array = np.stack(
                (np.clip(r_scaled, 0, 255),
                 np.clip(g_scaled, 0, 255),
                 np.clip(b_scaled, 0, 255)),
                axis=-1
            ).astype(np.uint8)
            img = Image.fromarray(image_array, 'RGB')

        img.save(output_filename, quality=100, optimize=False)
        print(f"imagem gerada e salva como '{output_filename}'")

        return img

    except Exception as e:
        print(f"ocorreu um erro durante a geracao da imagem: {e}")
        return None 
    

def generate_error_graph(original_image: str, images_to_compare: list[str], output_filename: str | None = None):
    """
    gera um grafico comparando o erro entre uma imagem original e uma lista de imagens para comparacao.

    args:
        original_image (str): o caminho para a imagem original.
        images_to_compare (list[str]): uma lista de caminhos para as imagens a comparar com a original.
        output_filename (str | none): caminho opcional para salvar o grafico gerado. se none, o grafico e exibido.

    returns:
        none: exibe ou salva o grafico dos erros.
    """
    errors = []
    image_labels = []

    try:
        original_img_obj = Image.open(original_image) # verifica se a original existe
    except FileNotFoundError:
        print(f"erro: imagem original nao encontrada em '{original_image}'")
        return
    except Exception as e:
        print(f"erro ao abrir imagem original '{original_image}': {e}")
        return

    print(f"calculando erros contra '{os.path.basename(original_image)}':")
    for image_path in images_to_compare:
        try:
            error = calculateError(original_image, image_path)
            errors.append(error)
            # usa basename para labels mais limpos
            image_labels.append(" ".join([_ for _ in os.path.basename(image_path).split('_') if _ != "decompressed"]).capitalize())
            print(f"  - erro para '{os.path.basename(image_path)}': {error:.4f}")
        except FileNotFoundError:
            print(f"  - aviso: imagem de comparacao nao encontrada em '{image_path}', pulando.")
        except Exception as e:
            print(f"  - aviso: nao foi possivel calcular o erro para '{image_path}': {e}, pulando.")

    if not errors:
        print("nenhum erro foi calculado. nao e possivel gerar o grafico.")
        return

    # gera o grafico
    plt.figure(figsize=(10, 6))
    plt.style.use('ggplot')
    plt.bar(image_labels, errors, color='skyblue')
    plt.xlabel("imagem de comparacao")
    plt.ylabel("erro (rmse)")
    plt.title(f"erro de comparacao de imagem vs '{os.path.basename(original_image)}'")
    plt.xticks(rotation=45, ha='right') 
    plt.tight_layout() 

    if output_filename:
        try:
            plt.savefig(output_filename)
            print(f"grafico de erro salvo como '{output_filename}'")
        except Exception as e:
            print(f"erro ao salvar grafico em '{output_filename}': {e}")
            plt.show() # mostra o grafico de qualquer forma se falhar ao salvar
    else:
        plt.show() 
    