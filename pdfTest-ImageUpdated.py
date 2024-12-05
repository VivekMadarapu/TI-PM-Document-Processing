import os
import json
import pdfplumber
import nltk
from flask import Flask, request, jsonify
from nltk.corpus import words
import re
from pmdocrewriteUpdated import rewrite_task_statement
from AMBPredict import predict_sentences

# Download NLTK data
nltk.download("words")

# Load English dictionary words
dictionary_words = set(words.words())

# Load acronyms from a text file
def load_acronyms(file_path):
    with open(file_path, 'r') as file:
        return set(line.strip() for line in file.readlines())

acronyms = load_acronyms('1.txt')  # Update the file path as necessary

# Flask app setup
app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_document():
    try:
        # Check for file in the request
        if 'file' not in request.files:
            return jsonify({"error": "No file provided."}), 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({"error": "Empty file."}), 400

        # Save file temporarily
        file_path = os.path.join("temp", uploaded_file.filename)
        os.makedirs("temp", exist_ok=True)
        uploaded_file.save(file_path)

        # Process the uploaded file
        processed_data = process_file(file_path)

        # Clean up the temp file
        os.remove(file_path)

        return jsonify(processed_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_file(file_path):
    # Determine file extension and process accordingly
    if file_path.endswith('.pdf'):
        return process_pdf(file_path)
    else:
        return {"error": "Unsupported file format. Only PDF files are supported."}

def process_pdf(file_path):
    processed_lines = []
    all_lines = []
    # all_rewritten_lines = []
    ambiguous_lines = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for i, line in enumerate(lines, start=1):
                    
                    # rewritten_line = rewrite_task_statement(line)
                    ambiguous_line = predict_sentences([line])
                    sentence, label = ambiguous_line[0]

                    # all_rewritten_lines.append(f"\n{rewritten_line}")
                    all_lines.append(f"\n{line}")
                    if label == "ambiguous":
                        ambiguous_lines.append(f"\n{line}")

                    ambiguous_words = find_ambiguous_words(line)
                    processed_lines.append({
                        "line_number": i,
                        "original_text": line,
                        "ambiguous_words": ambiguous_words
                    })

                with open("output/extracted_text.txt", 'w') as f:
                    f.writelines(all_lines)
                # with open("output/extracted_rewritten_text.txt", 'w') as f:
                #     f.writelines(all_rewritten_lines)
                with open("output/ambiguous.txt", 'w') as f:
                    f.writelines(ambiguous_lines)

    with open("output/response.json", 'w') as f:
        f.writelines(json.dumps({"processed_lines": processed_lines}))

    return {"processed_lines": processed_lines}

def find_ambiguous_words(line):
    ambiguous_terms = []
    words_in_line = line.split()

    for word in words_in_line:
        # Remove any punctuation for checking dictionary/acronym
        stripped_word = re.sub(r'[^\w\s]', '', word)

        # Check for parentheses pattern (e.g., word (something))
        if re.search(r'\w+\s*\(.*?\)', word):
            continue
        # Check if the word is in the dictionary or acronyms
        if stripped_word.lower() in dictionary_words or stripped_word.upper() in acronyms:
            continue
        # Otherwise, it's ambiguous
        ambiguous_terms.append(word)

    return ambiguous_terms

if __name__ == '__main__':
    # Ensure the temporary folder exists
    os.makedirs("temp", exist_ok=True)

    # Start Flask app
    app.run(debug=True)
