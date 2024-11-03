import json
import os
import ollama

# Define the Inputs class to store the architecture description, approaches, criteria, and scenarios.
class Inputs:
    def __init__(self, architecture_description, architectural_approaches, quality_criteria, scenarios):
        self.architecture_description = architecture_description
        self.architectural_approaches = architectural_approaches
        self.quality_criteria = quality_criteria
        self.scenarios = scenarios

# Define the InputManager class to manage loading and formatting input data.
class InputManager:
    def __init__(self, folder_name):
        """
        Initializes the InputManager instance with a base directory path.
        The path is derived from the script's directory and the specified folder name.
        """
        self.base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", folder_name)

    def load_inputs(self):
        """
        Loads JSON files containing the architecture description, architectural approaches,
        quality criteria, and scenarios from the specified input folder.

        Returns:
            Inputs: An instance of the Inputs class populated with the loaded data.
        """

        # Define paths for each input JSON file
        architecture_description_path = os.path.join(self.base_dir, "architecture_description.json")
        architectural_approaches_path = os.path.join(self.base_dir, "architectural_approaches.json")
        quality_criteria_path = os.path.join(self.base_dir, "quality_criteria.json")
        scenarios_path = os.path.join(self.base_dir, "scenarios.json")

        # Load JSON data from each file
        with open(architecture_description_path, 'r') as file:
            architecture_description = json.load(file)

        with open(architectural_approaches_path, 'r') as file:
            architectural_approaches = json.load(file)
        
        with open(quality_criteria_path, 'r') as file:
            quality_criteria = json.load(file)
        
        with open(scenarios_path, 'r') as file:
            scenarios = json.load(file)

        # Return an instance of Inputs with the loaded data
        return Inputs(
            architecture_description=architecture_description,
            architectural_approaches=architectural_approaches,
            quality_criteria=quality_criteria,
            scenarios=scenarios
        )

    @staticmethod
    def format_to_string(inputs):
        """
        Formats the loaded inputs into a structured prompt for the model.

        Args:
            inputs (Inputs): The input data to be formatted.

        Returns:
            str: A formatted string combining all input data with a specific analysis template.
        """

        # Instruction prompt for the model
        prompt = "You are conducting a qualitative analysis of a software system using ATAM. \
                    You have the architecture description, architectural approaches, quality criteria, and scenarios provided below. \
                    For each given approach, analyze the risks, sensitivity points, and tradeoffs of each architectural decision for each scenario. \
                    Try to argue with the inputs provided. \
                    Use the following template, and only fill in the blanks of this template, nothing else:\n"
        
        # Template pattern for the model output
        output_pattern = """
        **{architecture_approach}**

        ### Scenario {scenario_number}: {scenario_name}

        * **Quality Attribute:** {quality_attribute}
        * **Architectural Description 1:** {architectural_description_1}
                + Risks: {risks_1}
                + Sensitivity Points: {sensitivity_points_1}
                + Tradeoffs: {tradeoffs_1}
        * **Architectural Description 2:** {architectural_description_2}
                + Risks: {risks_2}
                + Sensitivity Points: {sensitivity_points_2}
                + Tradeoffs: {tradeoffs_2}
        """

        # Concatenate the prompt and data in JSON format
        stringified_input = (
            f"{prompt}\n\n"
            f"{output_pattern}\n\n"
            f"Architecture Description: {json.dumps(inputs.architecture_description)}\n\n"
            f"Architectural Approaches: {json.dumps(inputs.architectural_approaches)}\n\n"
            f"Quality Criteria: {json.dumps(inputs.quality_criteria)}\n\n"
            f"Scenarios: {json.dumps(inputs.scenarios)}"
        )

        return stringified_input

"""
# Usage Example:
# Initialize the input manager with the folder name containing your JSON files
input_manager = InputManager(folder_name="example1")
inputs = input_manager.load_inputs()

# Format the input in the correct format for ollama.chat
formatted_input = {
    "role": "user",
    "content": InputManager.format_to_string(inputs)
}

# Send the message to the model
response = ollama.chat(model='nemotron', messages=[formatted_input])

# Output the response
print(response['message']['content'])
"""
