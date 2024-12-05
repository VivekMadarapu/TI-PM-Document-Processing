import pdfplumber
import os
from PIL import Image


def extract_pdf_data(pdf_path, output_dir):
    with pdfplumber.open(pdf_path) as pdf:
        text_data = []
        image_data = []

        for page_num, page in enumerate(pdf.pages):

            text = page.extract_text()
            text_data.append({
                'page_num': page_num + 1,
                'text': text or "No text found"
            })

            for img_index, img in enumerate(page.images):
                image_filename = os.path.join(output_dir, f"image_{page_num + 1}_{img_index + 1}.png")

                image_data.append({
                    'page_num': page_num + 1,
                    'img_filename': image_filename,
                    'img_bbox': f"{img['x0']}, {img['top']}, {img['x1']}, {img['bottom']}"
                })

        return text_data, image_data


def process_document(pdf_path):
    output_dir = "output"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    text_data, image_data = extract_pdf_data(pdf_path, output_dir)

    return text_data, image_data
