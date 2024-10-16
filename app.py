from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)

# Serve the index.html file
@app.route('/')
def serve_index():
    return send_from_directory(os.getcwd(), 'index.html')

# Dummy endpoint to process input text
@app.route('/process', methods=['POST'])
def process_text():
    data = request.json  # Get the JSON data from the request
    input_text = data.get('text', '')  # Extract the text field
    # Simulate processing the input text
    output_text = f"Processed: {input_text}"  # Replace this with LLM processing
    return jsonify({"output": output_text})  # Return the output as JSON

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)  # Make server accessible on the network