from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # For communication with Angular
from query import RESPONSES_PATH
import os
import json
import subprocess

app = Flask(__name__)
CORS(app)

# Directory setup
INPUT_DIR = "inputs/example1"
os.makedirs(INPUT_DIR, exist_ok=True)

@app.route('/')
def root():
    return jsonify({"message": "Hello World!"})

@app.route('/upload-inputs', methods=['POST'])
def upload_inputs():
    # Create the temp directory if it doesn't exist
    temp_dir = INPUT_DIR
    os.makedirs(temp_dir, exist_ok=True)
    
    # Get uploaded files
    files = request.files
    required_files = [
        "architectural_approaches",
        "architecture_context",
        "quality_criteria",
        "scenarios"
    ]

    # Ensure all required files are present
    for file_key in required_files:
        if file_key not in files:
            return jsonify({"error": f"Missing file: {file_key}"}), 400

    # Save each file to the temp directory
    for file_key in required_files:
        file = files[file_key]
        file.save(os.path.join(temp_dir, f"{file_key}.json"))

    return jsonify({"message": "Files uploaded and saved successfully."}), 200

# Endpoint to receive uploaded files
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    # Directory for storing PDF files
    pdf_dir = os.path.join("data")
    os.makedirs(pdf_dir, exist_ok=True)

    # Get uploaded files
    files = request.files.getlist("pdfs")  # Allows multiple file uploads with the key "pdfs"

    if not files:
        return jsonify({"error": "No files uploaded"}), 400

    saved_files = []

    for file in files:
        if file.filename.endswith('.pdf'):
            # Save the PDF file
            file_path = os.path.join(pdf_dir, file.filename)
            file.save(file_path)
            saved_files.append(file.filename)
        else:
            return jsonify({"error": f"Invalid file format: {file.filename}. Only PDF files are allowed."}), 400

    return jsonify({"message": "PDF files uploaded successfully", "files": saved_files}), 200

# Endpoint to receive a URL for processing
@app.route('/upload-url', methods=['POST'])
def upload_url():
    # Directory for storing URLs
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)

    # File to store the URLs
    url_file = os.path.join(data_dir, "URLs.txt")

    # Get the URL from the request
    data = request.get_json()
    if not data or "url" not in data:
        return jsonify({"error": "Missing 'url' in the request body."}), 400

    url = data["url"]

    # Validate the URL format (optional, can be more robust)
    if not url.startswith(("http://", "https://")):
        return jsonify({"error": "Invalid URL format."}), 400

    # Append the URL to the file
    try:
        with open(url_file, "a") as f:
            f.write(f"{url}\n")
    except Exception as e:
        return jsonify({"error": f"Failed to write URL to file: {str(e)}"}), 500

    return jsonify({"message": "URL saved successfully", "url": url}), 200


# Endpoint to retrieve the results after processing
@app.route('/get-results', methods=['GET'])
def get_results():
    try:
        # Web scraping process
        subprocess.run(['python', 'web_scraper.py'], check=True)

        # Create database
        subprocess.run(['python', 'create_database.py', INPUT_DIR], check=True)

        # Query the model
        subprocess.run(['python', 'query.py', os.path.basename(INPUT_DIR)], check=True)

        # Read and return the responses
        with open(RESPONSES_PATH, 'r') as json_file:
            responses = json.load(json_file)

        return jsonify(responses), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Subprocess error: {str(e)}"}), 500
    except FileNotFoundError:
        return jsonify({"error": "Response file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
