import re
from transformers import T5ForConditionalGeneration, T5Tokenizer

model_name = "t5-small"
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)


def rewrite_task_statement(statement):
    input_text = f"Is the following instruction important enough to have a check box to ensure completion? Respond only with 'yes' or 'no'. : '{statement}'"

    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=100, num_beams=5)

    rewritten_statement = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return rewritten_statement


def split_text_into_pages(text):
    pages = re.split(r'(Page \d+:)', text)

    pages = [pages[i] + pages[i + 1].strip() for i in range(1, len(pages), 2)]

    return pages


file_path = "output/extracted_text.txt"
try:
    with open(file_path, 'r') as file:
        original_text = file.read().strip()
except FileNotFoundError:
    print(f"Error: The file {file_path} was not found.")
    original_text = ""

if original_text:
    pages = split_text_into_pages(original_text)
    for i, page in enumerate(pages):
        print(f"\nProcessing Page {i + 1}:")
        rewritten_page = rewrite_task_statement(page)

        print("Rewritten Page:", rewritten_page)
else:
    print("No text to process.")
