import pdfplumber
import os
from PIL import Image

def extract_pdf_data(pdf_path, output_dir):
    # Open the PDF file
    with pdfplumber.open(pdf_path) as pdf:
        text_data = []  # List to store text data
        image_data = []  # List to store image data
        
        # Iterate through the pages
        for page_num, page in enumerate(pdf.pages):

            # Extract text
            text = page.extract_text()
            text_data.append({
                'page_num': page_num + 1,
                'text': text or "No text found"
            })
            
            # Extract images and save them
            for img_index, img in enumerate(page.images):
                # Write the image data as a file
                image_filename = os.path.join(output_dir, f"image_{page_num + 1}_{img_index + 1}.png")

                # Store the image data (you could store bbox info here for later layout reconstruction)
                image_data.append({
                    'page_num': page_num + 1,
                    'img_filename': image_filename,
                    'img_bbox': f"{img['x0']}, {img['top']}, {img['x1']}, {img['bottom']}"
                })

        return text_data, image_data

# Define main function to run the extraction process
def process_document(pdf_path):
    output_dir = "output"    # Directory where the text and images will be saved
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Extract text and images
    text_data, image_data = extract_pdf_data(pdf_path, output_dir)

    return text_data, image_data