import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

from calculateError import calculateError


def generate_image(p, function, output_filename="image.png", x_range=(0, 4*np.pi), y_range=(0, 4*np.pi), grayscale=False):
    """
    Generates an image based on a function of x and y coordinates.

    Args:
        p (int): The side length of the square image (p x p pixels).
        function (callable): A function that takes x and y coordinates and returns (r, g, b) values in range [-1, 1].
        output_filename (str): The name of the file to save the image.
        x_range (tuple): A tuple (min, max) defining the range for the x-coordinate.
        y_range (tuple): A tuple (min, max) defining the range for the y-coordinate.
        grayscale (bool): If True, generates a black and white image by averaging RGB values.

    Returns:
        PIL.Image.Image: The generated image object. Returns None if an error occurs.
    """
    if p <= 0:
        print("Error: Image size 'p' must be positive.")
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
        print(f"Image generated and saved as '{output_filename}'")

        return img

    except Exception as e:
        print(f"An error occurred during image generation: {e}")
        return None 
    

def generate_error_graph(original_image: str, images_to_compare: list[str], output_filename: str | None = None):
    """
    Generate a graph comparing the error between an original image and a list of comparison images.

    Args:
        original_image (str): The path to the original image.
        images_to_compare (list[str]): A list of paths to the images to compare against the original.
        output_filename (str | None): Optional path to save the generated graph. If None, the graph is displayed.

    Returns:
        None: Displays or saves the graph of the errors.
    """
    errors = []
    image_labels = []

    try:
        original_img_obj = Image.open(original_image) # Check if original exists
    except FileNotFoundError:
        print(f"Error: Original image not found at '{original_image}'")
        return
    except Exception as e:
        print(f"Error opening original image '{original_image}': {e}")
        return

    print(f"Calculating errors against '{os.path.basename(original_image)}':")
    for image_path in images_to_compare:
        try:
            error = calculateError(original_image, image_path)
            errors.append(error)
            # Use basename for cleaner labels
            image_labels.append(" ".join([_ for _ in os.path.basename(image_path).split('_') if _ != "decompressed"]).capitalize())
            print(f"  - Error for '{os.path.basename(image_path)}': {error:.4f}")
        except FileNotFoundError:
            print(f"  - Warning: Comparison image not found at '{image_path}', skipping.")
        except Exception as e:
            print(f"  - Warning: Could not calculate error for '{image_path}': {e}, skipping.")

    if not errors:
        print("No errors were calculated. Cannot generate graph.")
        return

    # Generate the plot
    plt.figure(figsize=(10, 6))
    plt.style.use('ggplot')
    plt.bar(image_labels, errors, color='skyblue')
    plt.xlabel("Comparison Image")
    plt.ylabel("Error (RMSE)")
    plt.title(f"Image Comparison Error vs '{os.path.basename(original_image)}'")
    plt.xticks(rotation=45, ha='right') 
    plt.tight_layout() 

    if output_filename:
        try:
            plt.savefig(output_filename)
            print(f"Error graph saved as '{output_filename}'")
        except Exception as e:
            print(f"Error saving graph to '{output_filename}': {e}")
            plt.show() # Show plot anyway if saving fails
    else:
        plt.show() 
    