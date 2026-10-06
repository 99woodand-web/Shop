# upscaling_resolution_tool.py (FIXED for Upscaling Orientation)

import os
from PIL import Image

# Define standard paper sizes in mm (width, height)
# 1 inch = 25.4 mm
# 300 DPI = 300 pixels per inch
# To convert mm to pixels at 300 DPI: (mm / 25.4) * 300

PRINT_SIZES_MM = {
    "A4": (210, 297), # Portrait by default
    "A3": (297, 420), # Portrait by default
    "A2": (420, 594), # Portrait by default
    "A1": (594, 841), # Portrait by default
}

def get_pixel_dimensions(size_name, dpi=300):
    """
    Calculates the pixel dimensions for a given print size at a specified DPI.
    
    Args:
        size_name (str): The name of the print size (e.g., "A4", "A3").
        dpi (int): Dots per inch (default 300).
        
    Returns:
        tuple: (width_pixels, height_pixels) or None if size_name is invalid.
    """
    if size_name not in PRINT_SIZES_MM:
        # This error is typically handled by the caller (GUI)
        print(f"Error: Unknown print size '{size_name}'. Available sizes: {list(PRINT_SIZES_MM.keys())}")
        return None

    width_mm, height_mm = PRINT_SIZES_MM[size_name]
    
    width_pixels = int((width_mm / 25.4) * dpi)
    height_pixels = int((height_mm / 25.4) * dpi)
    
    return (width_pixels, height_pixels)

def upscale_image(image_path, target_size_name, dpi=300, output_dir="upscaled_images"):
    """
    Upscales an image to a specified print size and DPI,
    with intelligent rotation to match target orientation if needed.
    
    Args:
        image_path (str): Path to the input image.
        target_size_name (str): The name of the target print size (e.g., "A4").
        dpi (int): Dots per inch for the output image (default 300).
        output_dir (str): Directory to save the upscaled image.
        
    Returns:
        str: Path to the upscaled image, or None if an error occurred.
    """
    if not os.path.exists(image_path):
        print(f"Error: Input image file not found at '{image_path}'")
        return None

    target_dimensions_portrait = get_pixel_dimensions(target_size_name, dpi)
    if target_dimensions_portrait is None:
        return None

    # Determine target orientation based on the standard paper size (usually portrait, W < H)
    target_width, target_height = target_dimensions_portrait
    target_is_portrait = target_width < target_height
    
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            original_is_portrait = original_width < original_height

            print(f"Original image size: {original_width}x{original_height} pixels (Is Portrait: {original_is_portrait})")
            print(f"Target standard size for {target_size_name} at {dpi} DPI: {target_width}x{target_height} (Is Portrait: {target_is_portrait})")

            # If original image orientation doesn't match target paper orientation, rotate the image
            if original_is_portrait != target_is_portrait:
                print(f"Orientation mismatch. Rotating image 90 degrees to match target {target_size_name}.")
                img = img.transpose(Image.ROTATE_90)
                # Update dimensions after rotation
                original_width, original_height = img.size
                original_is_portrait = original_width < original_height # Re-evaluate

            # Now, the image's orientation should match the target paper orientation.
            # Perform resize to the target dimensions.
            upscaled_img = img.resize((target_width, target_height), Image.LANCZOS)
            
            os.makedirs(output_dir, exist_ok=True)
            
            original_file_name = os.path.splitext(os.path.basename(image_path))[0]
            output_filename = f"{original_file_name}_{target_size_name}_{dpi}dpi.png"
            output_path = os.path.join(output_dir, output_filename)
            
            upscaled_img.save(output_path, dpi=(dpi, dpi)) # Save with DPI metadata
            print(f"Image successfully upscaled and saved to: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"Error during image upscaling: {e}")
        return None

# This file is primarily for its utility functions.
# It doesn't have a main execution block for standalone use in the final integrated app.