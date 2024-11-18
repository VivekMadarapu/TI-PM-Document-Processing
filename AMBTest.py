import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns

test_texts = [
    "Do not perform work until the tool has been de-energized",
    "Fill the platen chiller",
    "Complete any needed PTS updates and stockroom return paperwork",
    "Prepare Plating cell for Maintenance",
    "Drain the solution",
    "Notify the MFG supervisor the machine is going down for scheduled maintenance.",
    "Check XID of tool for any thing that needs addressed during the PM and complete those items. The XID is the tool Misti ID preceded by an “X” for example the XID for IM401 is XIM401. If the XID cannot be completed document what is needed.",
    "Verify the flow readback shows off when the pump is off or the valves are closed. Verify all the water QD'sare connected and valves are open. From the Operationbutton, UnivESCooling detail the cooling system items will be green when flowing/good and yellow or red when there is a problem. Inspect for any water leaks and repair.",
    "Have ample supply of cleanroom wipes, dry and wetted, near plating cell ready for use",
    "Using 5/32 Allen wrench remove ¼-20Titanium screws that hold active Tophatto brim of clam cell. If screws have dried plating solution on the soak or rinse in DI water to clean. Place screws aside to air dry.Have Maintenance cover ready to transport brim to cleanup hood.",
]

test_labels = [
    0,  # Ambiguous
    0,
    0,
    0,
    0,
    1,  # Specific
    1,
    1,
    1,
    1,
]


model_path = 'scibert_scivocab_AMB_uncased'

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval()

# Move the model to GPU if available
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

class TextClassificationTestDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.encodings = tokenizer(
            texts,
            truncation=True,
            padding=True,
            max_length=max_length
        )
        self.labels = labels

    def __getitem__(self, idx):
        item = {
            key: torch.tensor(val[idx]).to(device)
            for key, val in self.encodings.items()
        }
        item['labels'] = torch.tensor(self.labels[idx], dtype=torch.long).to(device)
        return item

    def __len__(self):
        return len(self.labels)

test_dataset = TextClassificationTestDataset(test_texts, test_labels, tokenizer)
test_loader = DataLoader(test_dataset, batch_size=8, shuffle=False)
all_labels = []
all_preds = []

with torch.no_grad():
    for batch in test_loader:
        # Get the inputs and labels
        input_ids = batch['input_ids']
        attention_mask = batch['attention_mask']
        labels = batch['labels']

        # Forward pass
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

        # Get predictions
        preds = torch.argmax(logits, dim=1)

        # Append labels and predictions
        all_labels.extend(labels.cpu().numpy())
        all_preds.extend(preds.cpu().numpy())

accuracy = accuracy_score(all_labels, all_preds)
precision, recall, f1, _ = precision_recall_fscore_support(
    all_labels, all_preds, average='binary'
)
print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")

report = classification_report(
    all_labels, all_preds, target_names=['Ambiguous', 'Specific']
)
print("\nClassification Report:")
print(report)

cm = confusion_matrix(all_labels, all_preds)

# Plot the confusion matrix using seaborn
plt.figure(figsize=(6, 4))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Ambiguous', 'Specific'],
            yticklabels=['Ambiguous', 'Specific'])
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
plt.show()
