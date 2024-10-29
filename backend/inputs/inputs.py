import json
import os
import ollama 

# Define the base directory path based on the script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Define the paths to the input files
ARCHITECTURE_DESCRIPTION_PATH = os.path.join(BASE_DIR, "architecture_description.json")
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
    with open(ARCHITECTURE_DESCRIPTION_PATH, 'r') as file:
        architecture_description = json.load(file)

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
    prompt = "You are conducting a qualitative analysis of a software system using ATAM. \
                You have the architecture description, architectural approaches, quality criteria, and scenarios provided below. \
                For eachgiven approach, analyse the risks, sensitivity points, and tradeoffs of each architectural decision for each scenario. \
                Please also consider all constraints mentioned.\
                You can focus on following structure: \n"
    
    output_pattern = "architectural approach: (enter approach) \n\
                        - scenario 1: (enter scenario name) \n\
                        -- quality attribute: (enter quality attribute) \n\
                        --- architectural description 1 \n\
                        ---- risks: (enter risks) \n\
                        ---- sensitivity points: (enter sensitivity points) \n\
                        ---- tradeoffs: (enter tradeoffs) \n\
                        --- architectural description 2 \n\
                        ---- risks: (enter risks) \n\
                        ---- sensitivity points: (enter sensitivity points) \n\
                        ---- tradeoffs: (enter tradeoffs) \n\
                        ... (add all mentioned architectural descriptions)\n"

    # Creating the message to send to the model
    formatted_input = {
        "role": "user",
        "content": (f"{prompt}\n\n"
                    f"{output_pattern}\n\n"
                    f"Architecture Description: {json.dumps(inputs.architecture_description)}\n\n"
                    f"Architectural Approaches: {json.dumps(inputs.architectural_approaches)}\n\n"
                    f"Quality Criteria: {json.dumps(inputs.quality_criteria)}\n\n"
                    f"Scenarios: {json.dumps(inputs.scenarios)}")
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
