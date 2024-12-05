import torch
from transformers import BartForConditionalGeneration, BartTokenizer

model_name = "facebook/bart-large-cnn"
tokenizer = BartTokenizer.from_pretrained(model_name)
model = BartForConditionalGeneration.from_pretrained(model_name)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

def rewrite_task_statement(statement):
    inputs = tokenizer.encode(statement, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=50, num_beams=5, early_stopping=True)
    rewritten_statement = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return rewritten_statement

# Usage
original_statement = "Conduct analysis on PMD data to identify high-risk areas and prioritize documentation updates."
rewritten_statement = rewrite_task_statement(original_statement)
print("Original:", original_statement)
print("Rewritten:", rewritten_statement)