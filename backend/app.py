from chromadb import Client
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain_chroma import Chroma  # For communication with Angular
from get_embedding_function import get_embedding_function
from create_database import DATABASE_PATH
from query import RESPONSES_PATH
from data_manager import PDFManager
from text_splitter import get_chunks
import os
import json
import subprocess
import shutil
import urllib


app = Flask(__name__)
CORS(app)

# pdf manager
pdf_manager = PDFManager("data")

# Directory setup
INPUT_DIR = "inputs/temp"
os.makedirs(INPUT_DIR, exist_ok=True)

@app.route('/', methods=['POST'])
def root():
    # Clear INPUT_DIR contents
    for file in os.listdir(INPUT_DIR):
        os.remove(os.path.join(INPUT_DIR, file))

    # Clear RESPONSES_PATH content
    if os.path.exists(RESPONSES_PATH):
        with open(RESPONSES_PATH, 'w') as file:
            file.write(json.dumps([]))

    return jsonify({"message": "Server active!"}), 200

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

# Endpoint to upload a PDF file
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
    
    try:
        # Save the PDF using PDFManager
        pdf_manager.add_pdf(file.filename, file.read())
        return jsonify({"message": f"PDF uploaded successfully and saved as {file.filename}."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to upload PDF: {str(e)}"}), 500

@app.route('/delete-pdf/<pdf_name>', methods=['POST'])
def delete_pdf(pdf_name: str):
    try:
        # Step 1: Delete the PDF file from the filesystem
        pdf_path = os.path.join(os.path.dirname(__file__), 'data', pdf_name)
        pdf_path_fixed = urllib.parse.unquote(pdf_path)
        
        if os.path.exists(pdf_path_fixed):
            pdf_manager.delete_pdf(pdf_path_fixed)
            print(f"PDF '{pdf_name}' deleted.")
        else:
            print(f"Error: PDF '{pdf_name}' not found.")
            return jsonify({"error": f"PDF '{pdf_name}' not found."}), 404

        # Step 2: Clear all chunks related to the PDF in the database
        try:

            db = Chroma(
                persist_directory=DATABASE_PATH,
                embedding_function=get_embedding_function()
            )

            print(f"Clearing chunks related to '{pdf_name}' from the database...")

            # TODO: Implement the deletion of chunks related to the PDF
            # Assume 'results' contains the output of db.get(include=["metadatas"])
            results = db.get(include=["metadatas"])

            # Extract the 'metadatas' field
            metadatas = results.get("metadatas", [])

            # Print the sources
            filtered_metadatas = [metadata for metadata in metadatas if str(metadata.get("source")) == "data/" + pdf_name]
            print(f"Filtered metadatas: {filtered_metadatas}")

            # Delete the chunks related to the filtered metadatas
            for metadata in filtered_metadatas:
                db.delete(metadata.get("id"))
            
            print(f"Number of filtered metadatas: {len(filtered_metadatas)}")
            print(f"Chunks related to '{pdf_name}' have been deleted successfully.")
            
            
        except Exception as e:
            print(f"Error clearing chunks for PDF '{pdf_name}': {str(e)}")
            return jsonify({"error": f"Failed to remove chunks related to '{pdf_name}' from the database."}), 500

        # Step 3: Get the updated list of PDFs after deletion
        pdf_files = pdf_manager.get_all_pdfs()

        return jsonify({
            "message": "PDF and chunks deleted, and the database has been updated successfully.",
            "updated_pdf_files": pdf_files
        }), 200

    except subprocess.CalledProcessError as e:
        print(f"Error during subprocess execution: {e}")
        return jsonify({"error": "Failed to update the database."}), 500
    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return jsonify({"error": f"Failed to delete PDF and related chunks: {str(e)}"}), 500


# Endpoint to list all PDF files
@app.route('/list-pdfs', methods=['GET'])
def list_pdfs():
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

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    return send_from_directory("data", filename, as_attachment=True)

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

@app.route('/get-urls', methods=['GET'])
def get_urls():
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
    # Get the incoming JSON data from the request body
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

@app.route('/get-pdfs', methods=['GET'])
def get_pdfs():
    pdfs = pdf_manager.get_all_pdfs()
    return jsonify(pdfs), 200

if __name__ == '__main__':
    app.run(debug=True)
