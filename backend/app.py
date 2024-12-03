from flask import Flask, request, jsonify, send_file
from flask_cors import CORS  # For communication with Angular
from query import RESPONSES_PATH
import os
import json
import subprocess

app = Flask(__name__)
CORS(app)

# Directory setup
INPUT_DIR = "inputs/temp"
os.makedirs(INPUT_DIR, exist_ok=True)

@app.route('/')
def root():
    # Clear INPUT_DIR contents
    for file in os.listdir(INPUT_DIR):
        os.remove(os.path.join(INPUT_DIR, file))

    # Clear RESPONSES_PATH content
    if os.path.exists(RESPONSES_PATH):
        with open(RESPONSES_PATH, 'w') as file:
            file.write(json.dumps([]))
    return jsonify({"message": "Server active!"})

@app.route('/upload-inputs', methods=['POST'])
def upload_inputs():
    temp_dir = INPUT_DIR

    # clear the temp directory
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))

    # Get the incoming JSON data from the request body
    data = request.get_json()

    # Ensure all required fields are present
    required_fields = [
        "architecture_context",
        "architectural_approaches",
        "quality_criteria",
        "scenarios"
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Save the JSON data to temporary files (you can write each field as its own JSON file)
    os.makedirs(temp_dir, exist_ok=True)

    for field in required_fields:
        with open(os.path.join(temp_dir, f"{field}.json"), 'w') as file:
            json.dump(data[field], file)

    return jsonify({"message": "Inputs uploaded and saved successfully."}), 200


# Endpoint to receive uploaded PDF files
@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    # Check if a file was part of the request
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['pdf']
    
    # If no file was selected
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    # Ensure it's a PDF file
    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid file type, only PDF files are allowed."}), 400
    
    # Directory where the PDF will be saved
    pdf_dir = os.path.join("data")
    os.makedirs(pdf_dir, exist_ok=True)
    
    # Save the file with a unique name (e.g., with timestamp or original name)
    pdf_path = os.path.join(pdf_dir, file.filename)
    file.save(pdf_path)
    
    return jsonify({"message": f"PDF uploaded successfully and saved to {pdf_path}."}), 200

    

# Endpoint to receive a URL for processing
@app.route('/upload-url', methods=['POST'])
def upload_url():
    # Get the incoming JSON data from the request body
    data = request.get_json()

    # Ensure the URL field is present
    if "url" not in data:
        return jsonify({"error": "Missing field: url"}), 400

    url = data["url"]

    # Directory for storing URLs
    url_dir = os.path.join("data")
    os.makedirs(url_dir, exist_ok=True)

    # Path to the URLs file
    url_file_path = os.path.join(url_dir, "URLs.txt")

    # Append the URL to the file
    with open(url_file_path, 'a') as url_file:
        url_file.write(url + "\n")

    return jsonify({"message": "URL uploaded and saved successfully."}), 200


# Endpoint to retrieve the results after processing
@app.route('/get-results', methods=['GET'])
def get_results():
    try:
        # Clear directory
        if os.path.exists(RESPONSES_PATH):
            os.remove(RESPONSES_PATH)

        # Web scraping process
        subprocess.run(['python', 'web_scraper.py'], check=True)

        # Create database
        subprocess.run(['python', 'create_database.py', INPUT_DIR], check=True)

        # Query the model
        subprocess.run(['python', 'query.py', os.path.basename(INPUT_DIR)], check=True)

        # Read and return the responses
        with open(RESPONSES_PATH, 'r') as json_file:
            responses = json.load(json_file)

        return serialize_architectural_data(responses), 200
    except subprocess.CalledProcessError as e:
        return jsonify({"error": f"Subprocess error: {str(e)}"}), 500
    except FileNotFoundError:
        return jsonify({"error": "Response file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/get-results-without-retrieval', methods=['GET'])
def get_results_without_retrieval():
    try:
        # Clear directory
        if os.path.exists(RESPONSES_PATH):
            os.remove(RESPONSES_PATH)

        # Query the model
        subprocess.run(['python', 'query.py', '--without_retrieval', os.path.basename(INPUT_DIR)], check=True)

        # Read and return the responses
        with open(RESPONSES_PATH, 'r') as json_file:
            responses = json.load(json_file)


        return serialize_architectural_data(responses), 200
    except FileNotFoundError:
        return jsonify({"error": "Response file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def serialize_architectural_data(data):
    def custom_sort(item):
        # Define the exact order of keys
        ordered_data = {
            "architecturalApproach": item.get("architecturalApproach"),
            "scenario": item.get("scenario"),
            "architecturalDecision": item.get("architecturalDecision"),
            "risks": item.get("risks"),
            "tradeoffs": item.get("tradeoffs"),
            "sensitivityPoints": item.get("sensitivityPoints"),
            "sources": item.get("sources"),
        }
        return ordered_data
    
    # Apply custom ordering
    ordered_data = [custom_sort(item) for item in data]
    return json.dumps(ordered_data, indent=2)


if __name__ == '__main__':
    app.run(debug=True)
