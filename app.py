import io
import os
import json
from datetime import datetime
from typing import BinaryIO

import pdfplumber
import nltk
from flask import Flask, request, jsonify, send_file
from nltk.corpus import words
import re

from makePDF import make_pdf
from checkSheet import generate_checksheet
from pmdocrewriteUpdated import rewrite_task_statement
from AMBPredict import predict_sentences

nltk.download("words")

dictionary_words = set(words.words())


def load_acronyms(file_path):
    with open(file_path, 'r') as file:
        return set(line.strip() for line in file.readlines())


acronyms = load_acronyms('1.txt')

app = Flask(__name__)


@app.route('/test', methods=['GET'])
def test_connection():
    return jsonify({"message": "Connection successful."}), 200


@app.route('/process', methods=['POST'])
def process_document():
    try:

        if 'file' not in request.files:
            return jsonify({"error": "No file provided."}), 400

        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            return jsonify({"error": "Empty file."}), 400

        file_path = os.path.join("temp", uploaded_file.filename)
        os.makedirs("temp", exist_ok=True)
        uploaded_file.save(file_path)

        processed_response = process_file(file_path)

        os.remove(file_path)

        return processed_response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def process_file(file_path):
    if file_path.endswith('.pdf'):
        return process_pdf(file_path)
    else:
        return {"error": "Unsupported file format. Only PDF files are supported."}


def process_pdf(file_path):
    processed_lines = []
    all_lines = []

    ambiguous_lines = []

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                lines = text.split('\n')
                for i, line in enumerate(lines, start=1):

                    ambiguous_line = predict_sentences([line])
                    sentence, label = ambiguous_line[0]

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

                with open("output/ambiguous.txt", 'w') as f:
                    f.writelines(ambiguous_lines)

    with open("output/response.json", 'w') as f:
        f.writelines(json.dumps({"processed_lines": processed_lines}))

    time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    pdf_output_file = f"documents/PMDoc_Report_{time}.pdf"
    pdf_clean_output_file = f"documents/PMDoc_New_{time}.pdf"
    make_pdf(pdf_output_file, pdf_clean_output_file)

    input_file = "output/extracted_text.txt"
    checksheet_output_file = f"documents/CheckSheet_{time}.txt"

    generate_checksheet(input_file, checksheet_output_file)

    return send_multiple_files([pdf_output_file, pdf_clean_output_file, checksheet_output_file])


def send_multiple_files(file_paths):
    import zipfile

    memory_file: BinaryIO = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file_path in file_paths:
            zf.write(file_path, os.path.basename(file_path))
    memory_file.seek(0)

    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='output_files.zip')


def find_ambiguous_words(line):
    ambiguous_terms = []
    words_in_line = line.split()

    for word in words_in_line:
        stripped_word = re.sub(r'[^\w\s]', '', word)
        if re.search(r'\w+\s*\(.*?\)', word):
            continue

        if stripped_word.lower() in dictionary_words or stripped_word.upper() in acronyms:
            continue

        ambiguous_terms.append(word)

    return ambiguous_terms


if __name__ == '__main__':
    os.makedirs("temp", exist_ok=True)

    app.run(host='0.0.0.0', port=5000, debug=True)
