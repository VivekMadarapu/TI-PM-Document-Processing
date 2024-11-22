import os
from flask import Flask, request, jsonify
from AMBPredict import predict_sentences
from ProcessPDF import process_document

app = Flask(__name__)

UPLOAD_FOLDER = 'documents'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/predict-ambiguous')
def predict_ambiguous(text):
    prediction = predict_sentences([text])
    sentence, label = prediction[0]
    return str(label)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    text_data, image_data = process_document(file_path)

    document_data = ""
    for page in text_data:
        document_data += page['text'] + "\n\n"

    response = jsonify({"message": "File uploaded successfully", "filename": file.filename, "data": document_data})
    print(response)

    return response, 200


if __name__ == '__main__':
    app.run()
