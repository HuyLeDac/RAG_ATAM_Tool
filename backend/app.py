from chromadb import Client
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain_chroma import Chroma  # For communication with Angular
from get_embedding_function import get_embedding_function
from create_database import DATABASE_PATH
from query import RESPONSES_PATH
from pdf_manager import PDFManager
import os
import json
import subprocess
import urllib


# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Initialize PDF manager with the data directory
pdf_manager = PDFManager("data")

# Directory setup for temporary inputs
INPUT_DIR = "inputs/temp"
os.makedirs(INPUT_DIR, exist_ok=True)

@app.route('/', methods=['POST'])
def root():
    """
    Root endpoint to clear temporary directories and check server status.

    1. Clears the INPUT_DIR by deleting all its contents.
    2. Clears the RESPONSES_PATH file by overwriting it with an empty JSON array.
    3. Returns a message indicating the server is active.

    Returns:
        JSON response with status message and HTTP status code.
    """
    for file in os.listdir(INPUT_DIR):
        os.remove(os.path.join(INPUT_DIR, file))

    if os.path.exists(RESPONSES_PATH):
        with open(RESPONSES_PATH, 'w') as file:
            file.write(json.dumps([]))

    return jsonify({"message": "Server active!"}), 200

@app.route('/upload-inputs', methods=['POST'])
def upload_inputs():
    """
    Endpoint to upload architectural analysis inputs.

    1. Clears the INPUT_DIR to ensure it's empty.
    2. Accepts JSON data containing architecture context, approaches, quality criteria, and scenarios.
    3. Validates required fields and saves each to a separate JSON file in INPUT_DIR.

    Returns:
        JSON response indicating success or an error if validation fails.
    """
    temp_dir = INPUT_DIR

    # Clear the temporary directory
    for file in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir, file))
    
    # Clear the responses file
    with open(RESPONSES_PATH, 'w') as file:
        file.write(json.dumps([]))

    data = request.get_json()

    required_fields = [
        "architecture_context",
        "architectural_approaches",
        "quality_criteria",
        "scenarios"
    ]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400

    # Save each field as its own JSON file
    os.makedirs(temp_dir, exist_ok=True)
    for field in required_fields:
        with open(os.path.join(temp_dir, f"{field}.json"), 'w') as file:
            json.dump(data[field], file)

    return jsonify({"message": "Inputs uploaded and saved successfully."}), 200

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    """
    Endpoint to upload a PDF file.

    1. Validates that a file is included in the request and is a PDF.
    2. Uses PDFManager to save the file to the data directory.

    Returns:
        JSON response indicating success or an error if validation fails.
    """
    if 'pdf' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['pdf']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith('.pdf'):
        return jsonify({"error": "Invalid file type, only PDF files are allowed."}), 400

    try:
        pdf_manager.add_pdf(file.filename, file.read())
        return jsonify({"message": f"PDF uploaded successfully and saved as {file.filename}."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to upload PDF: {str(e)}"}), 500

@app.route('/delete-pdf/<pdf_name>', methods=['POST'])
def delete_pdf(pdf_name: str):
    """
    Endpoint to delete a PDF file and its associated chunks in the database.

    1. Deletes the PDF file from the data directory.
    2. Removes all database chunks associated with the deleted file.
    3. Returns the updated list of PDFs.

    Args:
        pdf_name (str): The name of the PDF file to delete.

    Returns:
        JSON response with the updated list of PDFs or an error if deletion fails.
    """
    try:
        # Delete PDF from the filesystem
        pdf_manager.delete_pdf(pdf_name)
        # Get the updated list of PDFs
        pdf_files = pdf_manager.get_all_pdfs()

        return jsonify({
            "message": "PDF and chunks deleted, and the database has been updated successfully.",
            "updated_pdf_files": pdf_files
        }), 200

    except Exception as e:
        return jsonify({"error": f"Failed to delete PDF and related chunks: {str(e)}"}), 500

# Endpoint to list all PDF files
@app.route('/list-pdfs', methods=['GET'])
def list_pdfs():
    """
    Endpoint to list all PDF files stored in the 'data' directory.

    Steps:
    1. Retrieve the list of all PDF files using the PDFManager.
    2. Return the list in a JSON response.
    3. If no PDFs are found, return a message indicating so.

    Returns:
        JSON response containing:
        - "pdf_files": List of PDF file names if found.
        - "message": If no files are found.
        - Error message if an exception occurs.
    """
    try:
        # Get the list of all PDFs from PDFManager
        pdf_files = pdf_manager.get_all_pdfs()
        if not pdf_files:
            return jsonify({"message": "No PDF files found in the directory."}), 200
        return jsonify({"pdf_files": pdf_files}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to list PDF files: {str(e)}"}), 500


# Endpoint to receive a URL for processing
@app.route('/upload-url', methods=['POST'])
def upload_url():
    """
    Endpoint to upload a URL for further processing.

    Steps:
    1. Accept JSON data from the request containing the "url" field.
    2. Validate the presence of the "url" field.
    3. Save the URL into a file named "URLs.txt" in the 'data' directory.

    Returns:
        JSON response:
        - Success message on successful upload.
        - Error message if validation fails or an exception occurs.
    """
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


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """
    Endpoint to download a file from the 'data' directory.

    Args:
        filename (str): Name of the file to be downloaded.

    Returns:
        The requested file as an attachment.
    """
    return pdf_manager.download_pdf(filename)


@app.route('/get-results', methods=['GET'])
def get_results():
    """
    Endpoint to start the architectural analysis process in form of a RAG pipeline.

    Steps:
    1. Clear the responses file (RESPONSES_PATH) if it exists.
    2. Run subprocesses to:
        - Perform web scraping.
        - Create a database.
        - Query the model.
    3. Read and return the results from RESPONSES_PATH.

    Returns:
        JSON response with serialized architectural data or error messages.
    """
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
    """
    Endpoint to retrieve results without performing retrieval.

    Steps:
    1. Clear the responses file (RESPONSES_PATH) if it exists.
    2. Run the 'query.py' subprocess with a '--without_retrieval' flag.
    3. Read and return the results from RESPONSES_PATH.

    Returns:
        JSON response with serialized architectural data or error messages.
    """
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


@app.route('/get-urls', methods=['GET'])
def get_urls():
    """
    Endpoint to retrieve all stored URLs from the "URLs.txt" file.

    Returns:
        JSON response with a list of URLs or an error if the file is not found.
    """
    url_file_path = os.path.join("data", "URLs.txt")
    
    if not os.path.exists(url_file_path):
        return jsonify({"error": "URLs file not found"}), 404

    try:
        with open(url_file_path, 'r') as url_file:
            urls = url_file.readlines()
        urls = [url.strip() for url in urls]
        return jsonify({"urls": urls}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to read URLs file: {str(e)}"}), 500


@app.route('/update-urls', methods=['POST'])
def update_urls():
    """
    Endpoint to update the list of URLs in the "URLs.txt" file.

    Steps:
    1. Accept JSON data with a "urls" field containing a list of URLs.
    2. Validate the presence of the "urls" field.
    3. Overwrite the "URLs.txt" file with the new list of URLs.

    Returns:
        JSON response:
        - Success message on successful update.
        - Error message if validation fails or an exception occurs.
    """
    data = request.get_json()

    # Ensure the URLs field is present
    if "urls" not in data:
        return jsonify({"error": "Missing field: urls"}), 400

    urls = data["urls"]

    # Directory for storing URLs
    url_dir = os.path.join("data")
    os.makedirs(url_dir, exist_ok=True)

    # Path to the URLs file
    url_file_path = os.path.join(url_dir, "URLs.txt")

    # Write the URLs to the file, overwriting any existing content
    with open(url_file_path, 'w') as url_file:
        for url in urls:
            url_file.write(url + "\n")

    return jsonify({"message": "URLs updated successfully."}), 200


def serialize_architectural_data(data):
    """
    Function to serialize architectural data in a specific order.

    Args:
        data (list): List of architectural data dictionaries.

    Returns:
        str: JSON string with the ordered data.
    """
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
            "time_taken_seconds": item.get("time_taken_seconds"),
            "thoughts": item.get("thoughts")
        }
        return ordered_data
    
    # Apply custom ordering
    ordered_data = [custom_sort(item) for item in data]
    return json.dumps(ordered_data, indent=2)


@app.route('/get-pdfs', methods=['GET'])
def get_pdfs():
    """
    Endpoint to retrieve a list of all PDFs using the PDFManager.

    Returns:
        JSON response containing:
        - List of PDF files if found.
        - Error message if an exception occurs.
    """
    pdfs = pdf_manager.get_all_pdfs()
    return jsonify(pdfs), 200


if __name__ == '__main__':
    app.run(debug=True)
