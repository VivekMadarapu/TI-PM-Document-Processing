from transformers import T5ForConditionalGeneration, T5Tokenizer

model_name = "t5-small"  
tokenizer = T5Tokenizer.from_pretrained(model_name)
model = T5ForConditionalGeneration.from_pretrained(model_name)
rs = "analyze the PMD data to identify high-risk areas and prioritize updating the documentation."

def rewrite_task_statement(statement):
    input_text = f"simplify: {statement}"

    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(inputs, max_length=50, num_beams=5, early_stopping=True)
    
    rewritten_statement = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return rewritten_statement

# usage
original_statement = "Conduct analysis on PMD data to identify high-risk areas and prioritize documentation updates."
rewritten_statement = rs

print("Original:", original_statement)
print("Rewritten:", rewritten_statement)
