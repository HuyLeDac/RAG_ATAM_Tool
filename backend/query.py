import json
import os
import argparse 
from inputs import InputLoader
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
from create_database import DATABASE_PATH  
from langchain_ollama import OllamaLLM
import time 
from datetime import datetime
import re


# Initialize the models and embedding function once to optimize performance
model = OllamaLLM(
    model="llama3:70b", # or deepseek-r1:70b
    temperature=0.2,  # Lower temperature for deterministic responses
    top_p=0.7,  # Keep responses focused, avoiding excessive randomness
    top_k=50,  # Select high-quality tokens for structured output
    repeat_penalty=1.1,  # Prevent redundant phrasing
    num_ctx=8192  # Longer context for handling architecture documentation
) # Main model used for querying decisions and scenarios
summarize_model = OllamaLLM(model="mistral:latest")  # Model for summarizing inputs for retrieval from database
db = Chroma(persist_directory=DATABASE_PATH, embedding_function=get_embedding_function())  # Database for document retrieval
RESPONSES_PATH = "responses/responses.json"  # Path to store responses
LOGS_DIR = "logs"  # Directory for logs

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
    Scenario: {format_json(scenario)}

    Architectural Approach: {approach['approach']}
    Architectural Decision: {decision}
    """

    # Generate a specialized retrieval query for database search
    summarized_query = summarize_model.invoke(
        "Summarize the most important keywords points of the architecture, decision, and scenario. It should be ideal for Retrieval Augmented Generation Procedures. "
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
    top_k_results = db.similarity_search_with_score(query_text, k=4)
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
    <TASK>
    You are an expert analyst for software architecture. We are conducting a qualitative analysis of architectural decisions against quality attribute scenrios based on the Architecture Tradeoff Analysis Method (ATAM). 

    You are given a user input of the approach: {current_approach}

    Task:
    Provide the risks, tradeoffs, and sensitivity points regarding the quality attribute scenario in the architectural decision: {decision}.
    If you think the decision does not have anything to do with the scenario, you can state [NO RELATIONSHIP].

    We provided you some chunks from scientific articles which could be relevant to the architecture. 
    They are provided in the '<SNIPPETS FROM ARTICLES>' section.
    Use the input data provided (USER INPUT and CONTEXT from a database).
    If you use knowledge from '<SNIPPETS FROM ARTICLES>', mark them as '[DATABASE SOURCE]'.   
    When you use your own knowledge for analysis, mark them as '[LLM KNOWLEDGE]'.

    For each risk/tradeoff/sensitivity point, provide a point for each architectural view from <USER INPUT> (development view, process view, physical view).
    You are given multiple architectural view in PlantUML format.

    Consider the technical constraints from the architecture context and try to analyze the architectures using the '<CONTEXT>' section.
    </TASK>

    -----

    <USER INPUT>
    User query:
    Architecture Context: \n{architecture_context}\n
    Architectural Approach Description: \n{approach_description}\n
    Architectural Views (PlantUML): \n{architectural_views}\n
    Quality Criteria: \n{quality_criteria}\n
    Scenario: \n{scenario}\n
    </USER INPUT>

    -----

    <SNIPPETS FROM ARTICLES> 
    {context}
    </SNIPPETS FROM ARTICLES>

    -----
    Format response as json format. Only use the format below and DO NOT ADD ADDITIONAL CHARACTERS:
    
    {{
     "architecturalApproach": "{current_approach}",
     "scenario": {{
         "name": "{scenario_name}",
         "qualityAttribute": "{quality_attribute}"
     }},
     "architecturalDecision": "{decision}",
     "risks": [
         {{
         "source": "[LLM KNOWLEDGE] or [DATABASE SOURCE] or [NO RELATIONSHIP]",
         "details": "(enter risks here)"
         }}
     ],
     "tradeoffs": [
         {{
         "source": "[LLM KNOWLEDGE] or [DATABASE SOURCE] or [NO RELATIONSHIP]",
         "details": "(enter tradeoffs here)"
         }}
     ],
     "sensitivityPoints": [
         {{
         "source": "[LLM KNOWLEDGE] or [DATABASE SOURCE] or [NO RELATIONSHIP]",
         "details": "(enter sensitivity points here)"
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

    total_start_time = time.time()  # Start total time measurement
    log_data = []

    for approach in inputs.architectural_approaches['architecturalApproaches']:
        for decision in approach['architectural decisions']:
            for scenario in inputs.scenarios['scenarios']:
                print(f"\n\nAnalyzing: {approach['approach']} - Decision: {decision} - Scenario: {scenario['scenario']}")  # For debugging

                tuple_start_time = time.time()  # Measure time for each tuple
                
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

                max_retries = 3  # Number of retries in case the LLM response is invalid
                retry_count = 0

                while retry_count < max_retries:
                    try:
                        # Get the model's response
                        response_text = model.invoke(formatted_prompt)

                        # Extract <think> section
                        think_match = re.search(r"<think>(.*?)</think>", response_text, re.DOTALL)
                        think_text = think_match.group(1).strip() if think_match else ""

                        # Remove <think> section from response_text (relevant for deepseek-r1:70b model)
                        cleaned_response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip()

                        # Remove any Markdown-style code blocks containing "json"
                        cleaned_response_text = re.sub(r"```json\s*", "", cleaned_response_text)
                        cleaned_response_text = re.sub(r"```$", "", cleaned_response_text)

                        # Ensure no trailing/leading whitespace
                        cleaned_response_text = cleaned_response_text.strip()

                        # Attempt to parse the cleaned response as JSON
                        response_dict = json.loads(cleaned_response_text)

                        # Add the extracted <think> section separately
                        response_dict["thoughts"] = think_text  # Store the extracted section

                        response_dict["architecturalApproach"] = approach['approach']

                        # Add sources to the response dictionary
                        sources = [] if without_retrieval else [doc.metadata.get("id") for doc, _ in top_k_results]
                        response_dict['sources'] = sources

                        # Track processing time
                        tuple_end_time = time.time()
                        tuple_time_taken = tuple_end_time - tuple_start_time
                        log_data.append({
                            "approach": approach['approach'],
                            "decision": decision,
                            "scenario": scenario['scenario'],
                            "time_taken_seconds": tuple_time_taken
                        })

                        # Append response
                        response_dict['time_taken_seconds'] = tuple_time_taken

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

    # Measure total time
    total_end_time = time.time()
    total_time_taken = total_end_time - total_start_time
    log_data.append({"total_time_taken_seconds": total_time_taken})

    # Save logs
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_filename = os.path.join(LOGS_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(log_filename, 'w') as log_file:
        json.dump(log_data, log_file, indent=2)

    # For debugging
    print(f"Logs saved to {log_filename}") 

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
