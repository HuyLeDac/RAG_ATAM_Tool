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

# Endpoint to retrieve the results after processing
@app.route('/get-results', methods=['GET'])
def get_results():
    return

if __name__ == '__main__':
    app.run(debug=True)




