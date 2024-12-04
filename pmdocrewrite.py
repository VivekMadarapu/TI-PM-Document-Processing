import re
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load model and tokenizer
model_name = "t5-small"  # You can use "t5-base" or "t5-large" for more complex results
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)


# Function to rewrite a task statement
def rewrite_task_statement(statement):
    # input_text = f"simplify: {statement}"
    input_text = f"Is the following instruction important enough to have a check box to ensure completion? Respond only with 'yes' or 'no'. : '{statement}'"

    # Tokenize and encode input
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=100, num_beams=5)  # You can adjust max_length as needed

    rewritten_statement = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return rewritten_statement


# Function to split input text into pages based on "Page [number]:"
def split_text_into_pages(text):
    # Regular expression to split the text by "Page [number]:"
    pages = re.split(r'(Page \d+:)', text)

    # Combine "Page [number]:" with its corresponding content
    pages = [pages[i] + pages[i + 1].strip() for i in range(1, len(pages), 2)]

    return pages


# Read the original statement from the file
file_path = "output/extracted_text.txt"
try:
    with open(file_path, 'r') as file:
        original_text = file.read().strip()  # Read and remove leading/trailing whitespace
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
    original_text = ""  # Empty text in case of error

# If the file was read successfully, process each page
if original_text:
    pages = split_text_into_pages(original_text)
    for i, page in enumerate(pages):
        print(f"\nProcessing Page {i + 1}:")
        rewritten_page = rewrite_task_statement(page)
        # print("Original Page:", page)
        print("Rewritten Page:", rewritten_page)
else:
    print("No text to process.")