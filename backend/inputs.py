import json
import os

# Define the Inputs class to store the architecture description, approaches, criteria, and scenarios.
class Inputs:
    def __init__(self, architecture_context, architectural_approaches, quality_criteria, scenarios):
        self.architecture_context = architecture_context
        self.architectural_approaches = architectural_approaches
        self.quality_criteria = quality_criteria
        self.scenarios = scenarios

    def get_architectural_decisions_as_list(self):
        """
        Extracts all architectural decisions from the architectural approaches.

        Returns:
            list: A list of architectural decisions from each approach.
        """
        decisions_list = []
        for approach in self.architectural_approaches["architecturalApproaches"]:
            decisions = approach.get("architectural decisions", [])
            decisions_list.extend(decisions)
        return decisions_list

    def get_architectural_views_as_list(self):
        """
        Extracts all architectural views from each approach in the architectural approaches.

        Returns:
            list: A list of dictionaries, each containing information about an architectural view.
        """
        views_list = []
        for approach in self.architectural_approaches["architecturalApproaches"]:
            views = approach.get("architectural views", [])
            views_list.extend(views)
        return views_list


# Define the InputLoader class to manage loading and formatting input data from JSON files.
class InputLoader:
    def __init__(self, folder_name):
        """
        Initializes the InputLoader instance with a base directory path.
        
        Args:
            folder_name (str): The folder name containing the input JSON files.
        """
        # Set the base directory path for input files based on the script's directory
        self.base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "inputs", folder_name)

    def load_inputs(self):
        """
        Loads JSON files containing architecture description, architectural approaches,
        quality criteria, and scenarios from the specified input folder.

        Returns:
            Inputs: An instance of the Inputs class populated with the loaded data.
        """

        # Define paths for each input JSON file
        architecture_context_path = os.path.join(self.base_dir, "architecture_context.json")
        architectural_approaches_path = os.path.join(self.base_dir, "architectural_approaches.json")
        quality_criteria_path = os.path.join(self.base_dir, "quality_criteria.json")
        scenarios_path = os.path.join(self.base_dir, "scenarios.json")

        # Load JSON data from each file, ensuring each required file is opened and read
        with open(architecture_context_path, 'r') as file:
            architecture_context = json.load(file)

        with open(architectural_approaches_path, 'r') as file:
            architectural_approaches = json.load(file)
        
        with open(quality_criteria_path, 'r') as file:
            quality_criteria = json.load(file)
        
        with open(scenarios_path, 'r') as file:
            scenarios = json.load(file)

        # Return an instance of Inputs populated with the data from the loaded JSON files
        return Inputs(
            architecture_context=architecture_context,
            architectural_approaches=architectural_approaches,
            quality_criteria=quality_criteria,
            scenarios=scenarios
        )

    def get_architectural_decisions_as_list(self):
        """
        Loads and extracts all architectural decisions from the architectural approaches JSON.

        Returns:
            list: A list of architectural decisions from each approach.
        """
        inputs = self.load_inputs()
        decisions_list = []
        for approach in inputs.architectural_approaches["architecturalApproaches"]:
            decisions = approach.get("architectural decisions", [])
            decisions_list.extend(decisions)
        return decisions_list

    def get_architectural_views_as_list(self):
        """
        Loads and extracts all architectural views from each approach in the architectural approaches JSON.

        Returns:
            list: A list of dictionaries, each containing information about an architectural view.
        """
        inputs = self.load_inputs()
        views_list = []
        for approach in inputs.architectural_approaches["architecturalApproaches"]:
            views = approach.get("architectural views", [])
            views_list.extend(views)
        return views_list

    
    
