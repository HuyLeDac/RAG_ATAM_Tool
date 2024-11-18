from flask import Flask, request, jsonify, send_file
from flask_cors import CORS #For communication with Angular
from query import RESPONSES_PATH
import os
import json
import subprocess

app = Flask(__name__)
CORS(app)

# Directory setup
INPUT_DIR = "backend/inputs/temp"
os.makedirs(INPUT_DIR, exist_ok=True)

# Endpoint to receive JSON inputs
@app.route('/upload-inputs', methods=['POST'])
def upload_inputs():
    return

@app.route('/upload-files', methods=['POST'])
def upload_files():
    return

@app.route('/upload-url', methods=['POST'])
def upload_url():
    return

# Endpoint to retrieve the results after processing
@app.route('/get-results', methods=['GET'])
def get_results():
    # Web scraping process
    jsonify({"message": "Startig web scraping process."})
    subprocess.run(['python', 'web_scraper.py'])
    jsonify({"message": "Web scraping finished."})

    # Create database 
    jsonify({"message": "Creating database."})
    subprocess.run(['python', 'create_database.py', INPUT_DIR])
    jsonify({"message": "Database created."})

    # Query the model
    jsonify({"message": "Querying the model. This could take a while..."})
    subprocess.run(['python', 'query.py', INPUT_DIR])
    jsonify({"message": "Model queried."})

    with open(RESPONSES_PATH, 'r') as json_file:
        responses = json.load(json_file)

    return jsonify(responses)

if __name__ == '__main__':
    app.run(debug=True)




