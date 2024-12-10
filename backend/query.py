import json
import os
import argparse  # Import argparse for command-line arguments
from inputs import InputLoader
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
from create_database import DATABASE_PATH  
from langchain_ollama import OllamaLLM
import time  # For adding a delay between retries


# Initialize the models and embedding function once to optimize performance
model = OllamaLLM(model="nemotron")  # Main model used for querying decisions and scenarios
summarize_model = OllamaLLM(model="mistral")  # Model for summarizing inputs for retrieval from database
db = Chroma(persist_directory=DATABASE_PATH, embedding_function=get_embedding_function())  # Database for document retrieval

RESPONSES_PATH = "responses/responses.json"  # Path to store responses

def get_inputs(folder_name):
    """
    Loads JSON data from a specified folder and returns an `Inputs` object.
    
    This function initializes the `InputLoader` to load structured input data from the folder 
    and returns it as an `Inputs` object for further processing.

    Args:
        folder_name (str): The name of the folder containing input data.

    Returns:
        Inputs: A structured object containing the architecture data loaded from JSON files.
    """
    input_loader = InputLoader(folder_name)
    inputs = input_loader.load_inputs()
    return inputs


def format_json(data, indent=2):
    """
    Converts the given data into a readable JSON string with proper indentation.

    Args:
        data (dict): The data to be formatted as a JSON string.
        indent (int, optional): The number of spaces for indentation. Defaults to 2.

    Returns:
        str: A JSON-formatted string.
    """
    return json.dumps(data, indent=indent)


def create_specialized_retrieval_query(inputs, approach, decision, scenario):
    """
    Creates a specialized retrieval query based on the inputs, approach, decision, and scenario.

    This function formats the architectural context, scenario, and decision information into 
    a query string that will be used to retrieve relevant information from the database.

    Args:
        inputs (Inputs): The structured input data containing architecture context.
        approach (dict): The current architectural approach being analyzed.
        decision (str): The current architectural decision being evaluated.
        scenario (dict): The scenario under consideration for the analysis.

    Returns:
        str: A formatted query string for retrieval.
    """
    input_data_str = f"""
    Architecture Context: 
    {format_json(inputs.architecture_context)}

    Scenario: {format_json(scenario)}

    Architectural Approach: {approach['approach']}
    Architectural Decision: {decision}
    """

    # Generate a specialized retrieval query for database search
    summarized_query = summarize_model.invoke(
        "Summarize the most important keywords points of the architecture, decision, and scenario. "
        "Add the keywords risks, tradeoffs, and sensitivity points under the summary:\n" + input_data_str
    )
    return summarized_query


def retrieval_query(query_text):
    """
    Performs a retrieval query on the database to find the top-k relevant documents.

    This function uses the Chroma database to search for documents that match the provided query 
    based on similarity scoring, returning the most relevant results.

    Args:
        query_text (str): The query text to be used for the retrieval search.

    Returns:
        list: A list of the top-k documents and their similarity scores.
    """
    print("Retrieval Query:")
    top_k_results = db.similarity_search_with_score(query_text, k=7)
    for doc, score in top_k_results:
        print(f"Document ID: {doc.metadata.get('id')} - Score: {score}")
    return top_k_results


def generate_analysis_prompt(context_output, approach, decision, scenario, inputs):
    """
    Generates a formatted prompt for the model to analyze architectural risks, tradeoffs, and sensitivity points.

    This function combines context from the database, user inputs, and the scenario to create 
    a prompt that the model can use to provide an analysis of the architectural decision.

    Args:
        context_output (str): The context retrieved from the database for the current scenario.
        approach (dict): The current architectural approach being analyzed.
        decision (str): The architectural decision being evaluated.
        scenario (dict): The scenario under consideration for the analysis.
        inputs (Inputs): The structured input data containing architecture context and other relevant information.

    Returns:
        str: The formatted prompt that will be sent to the model for analysis.
    """
    
    template = """
    <CONTEXT>
    Use the context and your own knowledge to fulfill the task: 
    {context}
    </CONTEXT>

    -----

    <INPUT>
    User's input data:
    Architecture Context: \n{architecture_context}
    Architectural Approach Description: \n{approach_description}
    Architectural Views: \n{architectural_views}
    Quality Criteria: \n{quality_criteria}
    Scenario: \n{scenario}
    </INPUT>

    -----

    <TASK>
    We are conducting a qualitative analysis based on ATAM. You are given multiple architectural view in PlantUML format.

    Task:
    Provide the risks, tradeoffs, and sensitivity points regarding the scenario in the architectural decision: {decision}.
    Use the input data provided, marking any external knowledge as [LLM KNOWLEDGE] and sources from the context section as [DATABASE SOURCE].
    For each risk/tradeoff/sensitivity point, provide a point for each architectural 1view (3 in total).
    Consider the technical constraints from the architecture context.
    </TASK>

    -----
    Format response as json format. Don't use any other formats and especially don't add any additional characters or spaces:
    
    {{
     "architecturalApproach": "{current_approach}",
     "scenario": {{
         "name": "{scenario_name}",
         "qualityAttribute": "{quality_attribute}"
     }},
     "architecturalDecision": "{decision}",
     "risks": [
         {{
         "source": "[LLM KNOWLEDGE/DATABASE SOURCE]",
         "details": "(enter risks)"
         }}
     ],
     "tradeoffs": [
         {{
         "source": "[LLM KNOWLEDGE/DATABASE SOURCE]",
         "details": "(enter tradeoffs)"
         }}
     ],
     "sensitivityPoints": [
         {{
         "source": "[LLM KNOWLEDGE/DATABASE SOURCE]",
         "details": "(enter sensitivity points)"
         }}
     ]
    }}

    """
    return template.format(
        context=context_output,
        architecture_context=format_json(inputs.architecture_context),
        architectural_views=format_json(inputs.get_architectural_views_as_list()),
        quality_criteria=format_json(inputs.quality_criteria),
        scenario=format_json(scenario),
        current_approach=approach.get('approach', 'Unknown'),
        approach_description=approach.get('description', 'No description provided'),
        decision=decision,
        scenario_name=scenario.get("scenario", "Unnamed Scenario"),
        quality_attribute=scenario.get("attribute", "No attribute provided")
    )


def query_specialized_for_each(inputs, without_retrieval=False):
    """
    Processes multiple architectural approaches, decisions, and scenarios, 
    querying the database and generating analysis prompts for each combination.

    This function iterates over all architectural approaches, decisions, and scenarios, 
    performs retrieval for each, and generates a prompt for analysis. The results are 
    collected and stored in a JSON file.

    Args:
        inputs (Inputs): The structured input data containing architecture context, 
                         approaches, decisions, and scenarios.
        without_retrieval (bool): Flag to skip retrieval and directly query the LLM.

    Returns:
        list: A list of responses containing the analysis results for each combination.
    """
    responses = []  # Initialize an empty list to store responses

    for approach in inputs.architectural_approaches['architecturalApproaches']:
        for decision in approach['architectural decisions']:
            for scenario in inputs.scenarios['scenarios']:
                print(f"\n\nAnalyzing: {approach['approach']} - Decision: {decision} - Scenario: {scenario['scenario']}")  # For debugging
                
                if without_retrieval:
                    context_output = ""  # No retrieval, so no context from the database
                else:
                    # Create specialized retrieval query for this (approach, decision, scenario)
                    retrieval_query_text = create_specialized_retrieval_query(inputs, approach, decision, scenario)
                    
                    # Perform retrieval based on the specialized query
                    top_k_results = retrieval_query(retrieval_query_text)
                    
                    # Convert top-k results into context text
                    context_output = "\n\n---\n\n".join([doc.page_content for doc, _ in top_k_results])

                # Generate the prompt for the model
                formatted_prompt = generate_analysis_prompt(context_output, approach, decision, scenario, inputs)

                max_retries = 3  # Number of retries
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        # Get the model's response
                        response_text = model.invoke(formatted_prompt)

                        # Attempt to parse the response as JSON
                        response_dict = json.loads(response_text)
                        
                        # Add sources to the response dictionary
                        sources = [] if without_retrieval else [doc.metadata.get("id") for doc, _ in top_k_results]
                        response_dict['sources'] = sources
                        
                        # Append the response dictionary to the list of responses
                        responses.append(response_dict)

                        # Display response for debugging purposes
                        print("---------------------------------------------------------")
                        print("START OF RESPONSE:\n")
                        print(json.dumps(response_dict, indent=2))  # Print formatted JSON for clarity
                        print("\nEND OF RESPONSE")
                        print("---------------------------------------------------------")
                        
                        # Break out of the retry loop on success
                        break
                    except json.JSONDecodeError as e:
                        retry_count += 1
                        print(f"JSON decoding failed (attempt {retry_count}/{max_retries}): {e}")
                        print("Response text was:")
                        print(response_text)  # Log problematic response
                        if retry_count < max_retries:
                            print("Retrying...")
                            time.sleep(1)  # Optional: Add delay between retries
                        else:
                            print("Max retries reached. Skipping this input.")
                            response_dict = {
                                "error": "Invalid JSON response",
                                "response_text": response_text,
                                "sources": sources
                            }
                            responses.append(response_dict)
                            break

    # Ensure the directory exists
    os.makedirs(os.path.dirname(RESPONSES_PATH), exist_ok=True)

    # After all responses are generated, store them in a JSON file
    with open(RESPONSES_PATH, 'w') as json_file:
        json.dump(responses, json_file, indent=2)

    return responses


# Main Function
if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description="Query and analyze architecture.")
    parser.add_argument("folder_name", type=str, help="Folder name to load inputs.")
    parser.add_argument("--without_retrieval", action="store_true", help="Skip the retrieval process.")
    args = parser.parse_args()

    # Load input data
    inputs = get_inputs(args.folder_name)

    # Run the analysis
    query_specialized_for_each(inputs, without_retrieval=args.without_retrieval)
