import json
import os
import ollama 

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
    prompt = "We are conducting a qualitative analysis of the architecture of a software system. \
          For that we want to use ATAM. That means, for every scenario given, I want you to analyse the risks, tradeoffs, and sensitivity points for every architectural approach. \
            Only display the scenarios with the mentioned risks, tradeoffs, and sensitivity points. \
                Also consider the hardware constraints " 
    
    # Creating the message to send to the model
    formatted_input = {
        "role": "user",
        "content": f"{prompt}\n\nArchitecture Description: {json.dumps(inputs.architecture_description)}\n\n"
                   f"Architectural Approaches: {json.dumps(inputs.architectural_approaches)}\n\n"
                   f"Quality Criteria: {json.dumps(inputs.quality_criteria)}\n\n"
                   f"Scenarios: {json.dumps(inputs.scenarios)}"
    }
    
    # Send the message to the model
    response = ollama.chat(model='llama3.1:70b', messages=[formatted_input])
    
    # Return the output from the model
    return response['message']['content']


def main():
    inputs = load_inputs()
    output = send_to_llama(inputs)
    print("Output from Llama Model:", output)

if __name__ == "__main__":
    main()
