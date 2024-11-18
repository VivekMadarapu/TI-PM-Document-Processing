from flask import Flask

from AMBPredict import predict_sentences

app = Flask(__name__)


@app.route('/predict-ambiguous')
def predict_ambiguous(text):
    prediction = predict_sentences([text])
    sentence, label = prediction[0]
    return str(label)


if __name__ == '__main__':
    app.run()
