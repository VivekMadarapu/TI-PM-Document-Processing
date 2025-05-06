
# TI-PM Document Processing

This project analyzes procedural maintenance documents using various machine learning models. Follow the steps below to set up the environment and run the application.

---

## Setup

### 1. Install Conda Distribution
The recommended Conda distribution for this project is [Miniforge](https://github.com/conda-forge/miniforge).

### 2. Create and Activate the Environment
Use the provided `environment.yml` file to create the environment, then install the necessary packages.

```bash
conda env create --name <env_name> --file=environment.yml
conda activate <env_name>
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126
python -m spacy download en_core_web_sm
pip install --upgrade transformers
pip install accelerate pdfplumber
```

### 3. Train the Ambiguous Detection Model (if not already present)
Run the following script to create the ambiguous detection model:

```bash
python AMBTrain.py
```

---

## Processing Steps

### 1. Start the Server
Run the server using the following command:

```bash
conda run -n <env_name> --no-capture-output python app.py
```

### 2. Send a POST Request
Send a POST request to the server with the PDF file you wish to process. Use the key `file` and send the request as `multipart/form-data`.

```bash
curl -X POST -F "file=@<path_to_pdf>" http://localhost:5000/process --output output.zip
```

The processed output will be saved as a ZIP file.

---
