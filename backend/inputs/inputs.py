import json
import os
import subprocess

# Define the base directory path based on the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the input files
ARCHITECTURE_VIEWS_PATH = os.path.join(BASE_DIR, "architectural_views")
ARCHITECTURAL_APPROACHES_PATH = os.path.join(BASE_DIR, "architectural_approaches.json")
QUALITY_CRITERIA_PATH = os.path.join(BASE_DIR, "quality_criteria.json")
SCENARIOS_PATH = os.path.join(BASE_DIR, "scenarios.json")

class Inputs:
    def __init__(self, architecture_description, architectural_approaches, quality_criteria, scenarios):
        self.architecture_description = architecture_description
        self.architectural_approaches = architectural_approaches
        self.quality_criteria = quality_criteria
        self.scenarios = scenarios

def load_inputs():
    # Load architecture views
    architecture_description = {}
    for file_name in os.listdir(ARCHITECTURE_VIEWS_PATH):
        file_path = os.path.join(ARCHITECTURE_VIEWS_PATH, file_name)
        with open(file_path, 'r') as file:
            view_name = os.path.splitext(file_name)[0]
            architecture_description[view_name] = file.read()
    
    # Load other inputs
    with open(ARCHITECTURAL_APPROACHES_PATH, 'r') as file:
        architectural_approaches = json.load(file)
    
    with open(QUALITY_CRITERIA_PATH, 'r') as file:
        quality_criteria = json.load(file)
    
    with open(SCENARIOS_PATH, 'r') as file:
        scenarios = json.load(file)

    return Inputs(
        architecture_description=architecture_description,
        architectural_approaches=architectural_approaches,
        quality_criteria=quality_criteria,
        scenarios=scenarios
    )

def send_to_llama(inputs):
    # Format inputs for the model
    formatted_input = {
        "prompt": "Evaluate every scenario for risks, tradeoffs and sensitivity points",
        "architecture_description": inputs.architecture_description,
        "architectural_approaches": inputs.architectural_approaches,
        "quality_criteria": inputs.quality_criteria,
        "scenarios": inputs.scenarios
    }
    
    # Convert to JSON string for sending
    input_json = json.dumps(formatted_input)
    
    # Use Ollama to send the input to the model
    result = subprocess.run(
        ['ollama', 'run', 'llama3.1:70'], 
        input=input_json, 
        text=True, 
        capture_output=True
    )
    
    # Check for errors and return output
    if result.returncode != 0:
        print("Error:", result.stderr)
    return result.stdout

def main():
    inputs = load_inputs()
    output = send_to_llama(inputs)
    print("Output from Llama Model:", output)

if __name__ == "__main__":
    main()
