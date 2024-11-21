import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_path = 'scibert_scivocab_uncased'

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

def predict_sentences(sentences):
    inputs = tokenizer(
        sentences,
        padding=True,
        truncation=True,
        max_length=128,
        return_tensors='pt'
    ).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
    probabilities = torch.softmax(logits, dim=-1)
    predicted_class_ids = torch.argmax(probabilities, dim=-1).cpu().numpy()
    labels = ['ambiguous', 'specific']
    predicted_labels = [labels[class_id] for class_id in predicted_class_ids]
    return list(zip(sentences, predicted_labels))


