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
            print(f"Processing page {page_num + 1}...")
            
            # Extract text
            text = page.extract_text()
            text_data.append({
                'page_num': page_num + 1,
                'text': text or "No text found"
            })
            
            # Extract images and save them
            for img_index, img in enumerate(page.images):

                x0, top, x1, bottom = img['x0'], img['top'], img['x1'], img['bottom']
                cropped_img = page.within_bbox((x0, top, x1, bottom))

                # Write the image data as a file
                image_filename = os.path.join(output_dir, f"image_{page_num + 1}_{img_index + 1}.png")

                if cropped_img:
                    cropped_img.to_image().save(image_filename)
                
                # Store the image data (you could store bbox info here for later layout reconstruction)
                image_data.append({
                    'page_num': page_num + 1,
                    'img_filename': image_filename,
                    'img_bbox': f"{img['x0']}, {img['top']}, {img['x1']}, {img['bottom']}"
                })

        return text_data, image_data

# Define main function to run the extraction process
def main():
    pdf_path = "documents/sample.pdf"  # Provide the path to your PDF file
    output_dir = "output"    # Directory where the text and images will be saved
    
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Extract text and images
    text_data, image_data = extract_pdf_data(pdf_path, output_dir)
    
    # Save the extracted text to a file (optional)
    text_filename = os.path.join(output_dir, "extracted_text.txt")
    with open(text_filename, 'w') as f:
        for page in text_data:
            f.write(f"Page {page['page_num']}:\n")
            f.write(page['text'])
            f.write("\n\n")
    
    print(f"Text data extracted and saved as {text_filename}")
    
    # Optionally print or save image metadata (bbox, filename, etc.)
    image_filename = os.path.join(output_dir, "image_metadata.txt")
    with open(image_filename, 'w') as f:
        for image in image_data:
            f.write(f"Page {image['page_num']} - Image saved as {image['img_filename']}\n")
            f.write(f"Image bounding box: {image['img_bbox']}\n\n")
    
    print(f"Image metadata saved as {image_filename}")

if __name__ == "__main__":
    main()





