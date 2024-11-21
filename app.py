import os

from flask import Flask, request, jsonify

from AMBPredict import predict_sentences

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
    # Check if the request has the 'file' part
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    # Check if a file is selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file to the specified directory
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    # Return a success response
    return jsonify({"message": "File uploaded successfully", "filename": file.filename}), 200


if __name__ == '__main__':
    app.run()
