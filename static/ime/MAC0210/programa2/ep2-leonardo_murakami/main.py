import numpy as np
import shutil
import os

from compress import compress
from decompress import decompress
from image_generator import generate_image, generate_error_graph

def empty_dir(dir):
    for file in os.listdir(dir):
        os.remove(os.path.join(dir, file))

def default_rgb_function(x, y):
    r = np.sin(x)
    g = (np.sin(y) + np.sin(x)) / 2
    b = np.sin(x)
    return (r, g, b)

def test_rgb_function(x, y):
    r = (np.cos(x) - np.sin(y))/2
    g = np.sin(y)*np.cos(x)
    b = np.sin(x)**2
    return (r, g, b)

def non_c2_rgb_function(x, y):
    r = np.abs(np.sin(x)) - 0.5 
    g = np.abs(x - np.pi) / np.pi
    b = np.max([np.sin(y), np.cos(x)])
    
    # garante que os valores estao no intervalo [-1, 1]
    return (np.clip(r, -1, 1), np.clip(g, -1, 1), np.clip(b, -1, 1))


def case_1():
    # caso 1 - funcao base
    # k = 1, h = 2
    case_1_dir = os.path.join(output_dir, "case_1")
    os.makedirs(case_1_dir, exist_ok=True)
    empty_dir(case_1_dir)

    generate_image(p=257, function=default_rgb_function, output_filename=os.path.join(case_1_dir, "base_image.png"))
    
    compress(os.path.join(case_1_dir, "base_image.png"), k=1)
    os.rename("compressed.png", os.path.join(case_1_dir, "compressed.png"))

    decompress(os.path.join(case_1_dir, "compressed.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_1_dir, "bilinear_decompressed_k1_h2.png"))
    decompress(os.path.join(case_1_dir, "compressed.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_1_dir, "bicubic_decompressed_k1_h2.png"))

    # k = 1, h = 4
    decompress(os.path.join(case_1_dir, "compressed.png"), method=1, k=1, h=4)
    os.rename("decompressed.png", os.path.join(case_1_dir, "bilinear_decompressed_k1_h4.png"))
    decompress(os.path.join(case_1_dir, "compressed.png"), method=2, k=1, h=4)
    os.rename("decompressed.png", os.path.join(case_1_dir, "bicubic_decompressed_k1_h4.png"))
    
    # k = 1, h = 8
    decompress(os.path.join(case_1_dir, "compressed.png"), method=1, k=1, h=8)
    os.rename("decompressed.png", os.path.join(case_1_dir, "bilinear_decompressed_k1_h8.png"))
    decompress(os.path.join(case_1_dir, "compressed.png"), method=2, k=1, h=8)
    os.rename("decompressed.png", os.path.join(case_1_dir, "bicubic_decompressed_k1_h8.png"))

    generate_error_graph(
        os.path.join(case_1_dir, "base_image.png"), 
        [
            os.path.join(case_1_dir, "bilinear_decompressed_k1_h2.png"), 
            os.path.join(case_1_dir, "bicubic_decompressed_k1_h2.png"), 
            os.path.join(case_1_dir, "bilinear_decompressed_k1_h4.png"), 
            os.path.join(case_1_dir, "bicubic_decompressed_k1_h4.png"), 
            os.path.join(case_1_dir, "bilinear_decompressed_k1_h8.png"), 
            os.path.join(case_1_dir, "bicubic_decompressed_k1_h8.png"), 
        ], output_filename=os.path.join(case_1_dir, "error_graph.png"))

def case_2():
    # caso 2 - outra funcao
    case_2_dir = os.path.join(output_dir, "case_2")
    os.makedirs(case_2_dir, exist_ok=True)
    empty_dir(case_2_dir)

    generate_image(p=257, function=test_rgb_function, output_filename=os.path.join(case_2_dir, "base_image.png"))
    
    compress(os.path.join(case_2_dir, "base_image.png"), k=3)
    os.rename("compressed.png", os.path.join(case_2_dir, "compressed.png"))

    decompress(os.path.join(case_2_dir, "compressed.png"), method=1, k=3, h=2)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bilinear_decompressed_k3_h2.png"))
    decompress(os.path.join(case_2_dir, "compressed.png"), method=2, k=3, h=2)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bicubic_decompressed_k3_h2.png"))
    
    decompress(os.path.join(case_2_dir, "compressed.png"), method=1, k=3, h=4)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bilinear_decompressed_k3_h4.png"))
    decompress(os.path.join(case_2_dir, "compressed.png"), method=2, k=3, h=4)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bicubic_decompressed_k3_h4.png"))
    
    decompress(os.path.join(case_2_dir, "compressed.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bilinear_decompressed_k1_h2_step1.png"))
    decompress(os.path.join(case_2_dir, "bilinear_decompressed_k1_h2_step1.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bilinear_decompressed_k1_h2_step2.png"))

    decompress(os.path.join(case_2_dir, "compressed.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bicubic_decompressed_k1_h2_step1.png"))
    decompress(os.path.join(case_2_dir, "bicubic_decompressed_k1_h2_step1.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_2_dir, "bicubic_decompressed_k1_h2_step2.png"))

    generate_error_graph(
        os.path.join(case_2_dir, "base_image.png"), 
        [
            os.path.join(case_2_dir, "bilinear_decompressed_k3_h2.png"), 
            os.path.join(case_2_dir, "bicubic_decompressed_k3_h2.png"), 
            os.path.join(case_2_dir, "bilinear_decompressed_k1_h2_step2.png"), 
            os.path.join(case_2_dir, "bicubic_decompressed_k1_h2_step2.png"), 
        ], output_filename=os.path.join(case_2_dir, "error_graph.png"))

def case_3():
    # caso 3 - k = 7 vs 3 * k = 1
    case_3_dir = os.path.join(output_dir, "case_3")
    os.makedirs(case_3_dir, exist_ok=True)
    empty_dir(case_3_dir)

    generate_image(p=257, function=default_rgb_function, output_filename=os.path.join(case_3_dir, "base_image.png"))

    compress(os.path.join(case_3_dir, "base_image.png"), k=7)
    os.rename("compressed.png", os.path.join(case_3_dir, "compressed_k7.png"))

    decompress(os.path.join(case_3_dir, "compressed_k7.png"), method=1, k=7, h=8)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bilinear_decompressed_k7_h8.png"))
    decompress(os.path.join(case_3_dir, "compressed_k7.png"), method=2, k=7, h=8)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bicubic_decompressed_k7_h8.png"))
    
    decompress(os.path.join(case_3_dir, "compressed_k7.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bilinear_decompressed_k1_h2_step1.png"))
    decompress(os.path.join(case_3_dir, "bilinear_decompressed_k1_h2_step1.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bilinear_decompressed_k1_h2_step2.png"))
    decompress(os.path.join(case_3_dir, "bilinear_decompressed_k1_h2_step2.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bilinear_decompressed_k1_h2_step3.png"))

    decompress(os.path.join(case_3_dir, "compressed_k7.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bicubic_decompressed_k1_h2_step1.png"))
    decompress(os.path.join(case_3_dir, "bicubic_decompressed_k1_h2_step1.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bicubic_decompressed_k1_h2_step2.png"))
    decompress(os.path.join(case_3_dir, "bicubic_decompressed_k1_h2_step2.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_3_dir, "bicubic_decompressed_k1_h2_step3.png"))
    
    generate_error_graph(
        os.path.join(case_3_dir, "base_image.png"), 
        [
            os.path.join(case_3_dir, "bilinear_decompressed_k7_h8.png"), 
            os.path.join(case_3_dir, "bicubic_decompressed_k7_h8.png"), 
            os.path.join(case_3_dir, "bilinear_decompressed_k1_h2_step3.png"), 
            os.path.join(case_3_dir, "bicubic_decompressed_k1_h2_step3.png")
        ], output_filename=os.path.join(case_3_dir, "error_graph.png")
    )

def case_4():
    # caso 4 - funcao nao c2
    case_4_dir = os.path.join(output_dir, "case_4")
    os.makedirs(case_4_dir, exist_ok=True)
    empty_dir(case_4_dir)

    generate_image(p=257, function=non_c2_rgb_function, output_filename=os.path.join(case_4_dir, "base_image.png"))

    compress(os.path.join(case_4_dir, "base_image.png"), k=1)
    os.rename("compressed.png", os.path.join(case_4_dir, "compressed.png"))

    decompress(os.path.join(case_4_dir, "compressed.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_4_dir, "bilinear_decompressed_k1_h2.png"))
    
    decompress(os.path.join(case_4_dir, "compressed.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_4_dir, "bicubic_decompressed_k1_h2.png"))

    generate_error_graph(
        os.path.join(case_4_dir, "base_image.png"), 
        [
            os.path.join(case_4_dir, "bilinear_decompressed_k1_h2.png"), 
            os.path.join(case_4_dir, "bicubic_decompressed_k1_h2.png")
        ],
        output_filename=os.path.join(case_4_dir, "error_graph.png")
    )

def case_5():
    # caso 5 - escala de cinza
    case_5_dir = os.path.join(output_dir, "case_5")
    os.makedirs(case_5_dir, exist_ok=True)
    empty_dir(case_5_dir)

    generate_image(p=257, function=default_rgb_function, output_filename=os.path.join(case_5_dir, "base_image.png"), grayscale=True)
    
    compress(os.path.join(case_5_dir, "base_image.png"), k=1)
    os.rename("compressed.png", os.path.join(case_5_dir, "compressed_k1.png"))

    compress(os.path.join(case_5_dir, "base_image.png"), k=7)
    os.rename("compressed.png", os.path.join(case_5_dir, "compressed_k7.png"))

    decompress(os.path.join(case_5_dir, "compressed_k1.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_5_dir, "bilinear_decompressed_k1_h2.png"))
    
    decompress(os.path.join(case_5_dir, "compressed_k1.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_5_dir, "bicubic_decompressed_k1_h2.png"))

    decompress(os.path.join(case_5_dir, "compressed_k7.png"), method=1, k=7, h=8)
    os.rename("decompressed.png", os.path.join(case_5_dir, "bilinear_decompressed_k7_h8.png"))
    
    decompress(os.path.join(case_5_dir, "compressed_k7.png"), method=2, k=7, h=8)
    os.rename("decompressed.png", os.path.join(case_5_dir, "bicubic_decompressed_k7_h8.png"))

    generate_error_graph(
        os.path.join(case_5_dir, "base_image.png"), 
        [
            os.path.join(case_5_dir, "bilinear_decompressed_k1_h2.png"), 
            os.path.join(case_5_dir, "bicubic_decompressed_k1_h2.png"),
            os.path.join(case_5_dir, "bilinear_decompressed_k7_h8.png"), 
            os.path.join(case_5_dir, "bicubic_decompressed_k7_h8.png")
        ],
        output_filename=os.path.join(case_5_dir, "error_graph.png")
    )
    
def case_6(real_image):
    # caso 6 - a selva
    case_6_dir = os.path.join(output_dir, "case_6")
    os.makedirs(case_6_dir, exist_ok=True)
    empty_dir(case_6_dir)

    shutil.copy(real_image, os.path.join(case_6_dir, real_image))
    compress(os.path.join(case_6_dir, real_image), k=1)
    os.rename("compressed.png", os.path.join(case_6_dir, "compressed_k1.png"))

    compress(os.path.join(case_6_dir, real_image), k=3)
    os.rename("compressed.png", os.path.join(case_6_dir, "compressed_k3.png"))

    decompress(os.path.join(case_6_dir, "compressed_k1.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_6_dir, "bilinear_decompressed_k1_h2.png"))

    decompress(os.path.join(case_6_dir, "compressed_k1.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_6_dir, "bicubic_decompressed_k1_h2.png"))

    decompress(os.path.join(case_6_dir, "compressed_k3.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_6_dir, "bilinear_decompressed_k1_h2_step1.png"))
    decompress(os.path.join(case_6_dir, "bilinear_decompressed_k1_h2_step1.png"), method=1, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_6_dir, "bilinear_decompressed_k1_h2_step2.png"))

    decompress(os.path.join(case_6_dir, "compressed_k3.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_6_dir, "bicubic_decompressed_k1_h2_step1.png"))
    decompress(os.path.join(case_6_dir, "bicubic_decompressed_k1_h2_step1.png"), method=2, k=1, h=2)
    os.rename("decompressed.png", os.path.join(case_6_dir, "bicubic_decompressed_k1_h2_step2.png"))
    
    

    generate_error_graph(
        os.path.join(case_6_dir, real_image), 
        [
            os.path.join(case_6_dir, "bilinear_decompressed_k1_h2.png"), 
            os.path.join(case_6_dir, "bicubic_decompressed_k1_h2.png"),
            os.path.join(case_6_dir, "bilinear_decompressed_k1_h2_step3.png"),
            os.path.join(case_6_dir, "bicubic_decompressed_k1_h2_step3.png"),
        ],
        output_filename=os.path.join(case_6_dir, "error_graph.png")
    )

if __name__ == "__main__":
    output_dir = "results"
    real_image = "balotelli.png"
    os.makedirs(output_dir, exist_ok=True)

    case_1()
    case_2()
    case_3()
    case_4()
    case_5()
    case_6(real_image)

    
     

