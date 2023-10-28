from PIL import Image
from io import BytesIO
import cv2
import numpy as np
from fpdf import FPDF
import argparse
import os

def generate_aruco_marker(marker_id, dictionary_name, size=(1000, 1000), inverted=False):
    dictionary = cv2.aruco.getPredefinedDictionary(getattr(cv2.aruco, dictionary_name))
    try:
        if marker_id < 0 or marker_id >= 50:
            raise ValueError("Invalid marker ID")
    except AttributeError:
        print("Warning: Unable to validate marker ID. Proceeding without validation.")
    
    marker_image = np.zeros((pixel_size[0], pixel_size[0]), dtype=np.uint8)
    cv2.aruco.generateImageMarker(dictionary, marker_id, pixel_size[0], marker_image)
    
    if inverted:
        marker_image = cv2.bitwise_not(marker_image)
    
    return marker_image

def save_marker_to_pdf(pdf, marker, marker_id, x, y, marker_size, inverted):
    # Create a higher resolution marker
    high_res_size = (marker.shape[1] * 10, marker.shape[0] * 10)
    high_res_marker = cv2.resize(marker, high_res_size, interpolation=cv2.INTER_LINEAR)

    # Stretch the marker in Pillow format
    stretched_size = (int(marker_size[0] * 10), int(marker_size[1] * 10))
    stretched_marker = cv2.resize(high_res_marker, stretched_size, interpolation=cv2.INTER_LINEAR)
    image = Image.fromarray(stretched_marker)

    # Convert the image to a format that FPDF accepts
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    img_str = buffered.getvalue()

    y = y + 3

    if inverted:
        pdf.rect(x - 2, y - 2, marker_size[0] + 4, marker_size[1] + 4, style='F')

    pdf.image(BytesIO(img_str), x=x, y=y, w=marker_size[0], h=marker_size[1])
    
    # Set font: [font family], [style], [size]
    pdf.set_font("helvetica", size = 10)
    
    # Insert marker_id to bottom-right of the marker
    pdf.ln(0)  # Move to a new line
    pdf.set_xy(x, y - 3)  # Adjust the position
    pdf.cell(0, 0, str(marker_id))  # Add the text


def create_marker_pdf(n_markers, marker_ids, pixel_size, dictionary_name, inverted, output_file, mm_size):
    pdf = FPDF(unit="mm", format="letter")
    pdf.add_page()
    
    margin = 0.5 * 25.4  
    spacing = 0.5 * 25.4  
    x, y = margin, margin
    
    for i, (mid, inv) in enumerate(zip(marker_ids, inverted)):
        marker = generate_aruco_marker(mid, dictionary_name, pixel_size, inv)
        
        save_marker_to_pdf(pdf, marker, mid, x, y, mm_size, inv)
        
        x += mm_size[0] + spacing
        if x + mm_size[0] > pdf.w - margin:
            x = margin
            y += mm_size[1] + spacing
            if y + mm_size[1] > pdf.h - margin:
                pdf.add_page()
                y = margin
    
    pdf.output(output_file)

if __name__ == "__main__":
    # Arguments parser part here is unchanged, assuming you are using the same one from previous snippets
    parser = argparse.ArgumentParser(description="Generate ArUco markers in a PDF file")
    parser.add_argument("n_markers", type=int, help="Number of markers to generate")
    parser.add_argument("output_file", type=str, help="Output file name")
    parser.add_argument("--dictionary", default="DICT_6X6_250", type=str, help="ArUco marker dictionary")
    parser.add_argument("--size", default=(100, 100), nargs='+', type=int, help="Size of each marker (width, height) in mm")
    parser.add_argument("--random", default=False, action='store_true', help="Generate random markers")
    parser.add_argument("--inverted", default=False, action='store_true', help="Generate inverted markers")

    args = parser.parse_args()

    if args.random:
        possible_ids = list(range(50))
        np.random.shuffle(possible_ids)
        marker_ids = possible_ids[:args.n_markers]
    else:
        marker_ids = list(range(args.n_markers))
        
    #  debugging to check marker ids
    # if len(set(marker_ids)) != len(marker_ids):
    #     print("Warning: marker_ids contains duplicates: ", marker_ids)
    # else:
    #     print("All marker_ids are unique: ", marker_ids)

    dpi = 300
    pixel_size = tuple((np.array(args.size) / 25.4) * dpi)  # mm -> inches -> pixels
    pixel_size = (int(pixel_size[0]), int(pixel_size[1]))
    mm_size = (args.size[0], args.size[1])
    
    inverted_flags = [args.inverted] * args.n_markers
    
    create_marker_pdf(args.n_markers, marker_ids, pixel_size, args.dictionary, inverted_flags, args.output_file, mm_size)
