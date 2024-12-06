import io
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_file
import pdfplumber
import nltk
import re

from makePDF import make_pdf
from checkSheet import generate_checksheet
from pmdocrewriteUpdated import rewrite_task_statement
from AMBPredict import predict_sentences

nltk.download("words")

dictionary_words = set(nltk.corpus.words.words())
acronyms = set(["NASA", "FBI", "CIA"])  # Example acronyms, replace with actual acronyms as needed

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

        processed_response = process_file(uploaded_file)
        return processed_response, 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def process_file(file):
    if file.filename.endswith('.pdf'):
        return process_pdf(file)
    else:
        return jsonify({"error": "Unsupported file format. Only PDF files are supported."})

def process_pdf(file):
    processed_lines = []
    all_lines = []
    ambiguous_lines = []

    with pdfplumber.open(file) as pdf:
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

    extracted_text = "".join(all_lines)
    ambiguous_text = "".join(ambiguous_lines)
    response_data = json.dumps({"processed_lines": processed_lines})

    time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    pdf_output_stream = io.BytesIO()
    pdf_clean_output_stream = io.BytesIO()

    make_pdf(extracted_text, ambiguous_text, response_data, pdf_output_stream, pdf_clean_output_stream)

    checksheet_output_stream = io.BytesIO()
    generate_checksheet(extracted_text, checksheet_output_stream)

    return send_multiple_files([("PMDoc_Report.pdf", pdf_output_stream), ("PMDoc_New.pdf", pdf_clean_output_stream), ("CheckSheet.txt", checksheet_output_stream)])

def send_multiple_files(file_streams):
    import zipfile
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for filename, stream in file_streams:
            stream.seek(0)
            zf.writestr(filename, stream.read())
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
    app.run(host='0.0.0.0', port=5000, debug=True)
