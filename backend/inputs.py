import json
import os

# Define the Inputs class to store the architecture description, approaches, criteria, and scenarios.
class Inputs:
    def __init__(self, architecture_description, architectural_approaches, quality_criteria, scenarios):
        self.architecture_description = architecture_description
        self.architectural_approaches = architectural_approaches
        self.quality_criteria = quality_criteria
        self.scenarios = scenarios

# Define the InputManager class to manage loading and formatting input data.
class InputLoader:
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

    
    