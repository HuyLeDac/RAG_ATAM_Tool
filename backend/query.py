import json
import os
import argparse  # Import argparse for command-line arguments
from inputs import InputLoader, Inputs
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
from create_database import DATABASE_PATH  
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
import time  # For adding a delay between retries


# Initialize the models and embedding function once to optimize performance
model = OllamaLLM(model="nemotron")  # Main model used for querying decisions and scenarios
retrieval_model = OllamaLLM(model="mistral")  # Model for summarizing inputs for retrieval from database
db = Chroma(persist_directory=DATABASE_PATH, embedding_function=get_embedding_function())  # Database for document retrieval

RESPONSES_PATH = "responses/responses.json"  # Path to store responses

# Function: Load JSON data from a specified folder
# - Initializes InputLoader to load JSON data from `folder_name`.
# - Returns an `Inputs` object containing structured architecture data.
def get_inputs(folder_name):
    input_loader = InputLoader(folder_name)
    inputs = input_loader.load_inputs()
    return inputs


# Helper Function: Format JSON data into a readable string
#   - `data`: JSON data to be formatted as a readable string.
#   - `indent`: Number of spaces for indentation in the formatted JSON string.
def format_json(data, indent=2):
    return json.dumps(data, indent=indent)


# Function: Create retrieval query from inputs, specialized for each (scenario, approach, decision) combination.
#   - `inputs`: Structured input data containing architecture, approaches, decisions, and scenarios.
#   - `approach`: The current architectural approach being analyzed.
#   - `decision`: The current architectural decision being analyzed.
#   - `scenario`: The current scenario being analyzed.
# - Converts architecture description, scenario, approach, and decision into a formatted string.
# - Uses `retrieval_model` to generate a specialized query for retrieval.
# - Returns a string with key architectural information for similarity search.
def create_specialized_retrieval_query(inputs, approach, decision, scenario):
    input_data_str = f"""
    Architecture Context: 
    {format_json(inputs.architecture_context)}

    Scenario: {format_json(scenario)}

    Architectural Approach: {approach['approach']}
    Architectural Decision: {decision}
    """

    # Generate a specialized retrieval query for database search
    summarized_query = retrieval_model.invoke(
        "Summarize the most important keywords points of the architecture, decision, and scenario. "
        "Add the keywords risks, tradeoffs, and sensitivity points under the summary:\n" + input_data_str
    )
    return summarized_query


# Function: Perform retrieval query on the database specialized for the specific scenario, approach, and decision
#   - `query_text`: The formatted query text used for similarity search.
# - Searches the Chroma database and returns the top `k` relevant documents.
def retrieval_query(query_text):
    print("Retrieval Query:")
    top_k_results = db.similarity_search_with_score(query_text, k=7)
    for doc, score in top_k_results:
        print(f"Document ID: {doc.metadata.get('id')} - Score: {score}")
    return top_k_results


# Function: Generate analysis prompt for each architectural decision and scenario
#   - `context_output`: Text containing the context retrieved from the database.
#   - `approach`, `decision`, `scenario`: Specific data points for the current architectural decision and scenario.
# - Formats the prompt for the model to evaluate architectural risks, tradeoffs, and sensitivity points.
# - Returns the formatted prompt as a string.
def generate_analysis_prompt(context_output, approach, decision, scenario, inputs):
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
    Use the input data provided, marking any external knowledge as [LLM KNOWLEDGE] and other sources as [DATABASE SOURCE] from the database.
    For each risk/tradeoff/sensitivity point, provide a point for each view (3 in total).
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


# Function: Process multiple architectural approaches, decisions, and scenarios.
#   - `inputs`: Structured input data containing architecture, approaches, decisions, and scenarios.
# - For each combination of approach, decision, and scenario, generate a retrieval query, perform the retrieval, 
#   and then generate a prompt for the model.
# - Appends the response with context and sources to a list.
# - Finally, stores the responses in a JSON file.
def query_specialized_for_each(inputs):
    responses = []  # Initialize an empty list to store responses

    for approach in inputs.architectural_approaches['architecturalApproaches']:
        for decision in approach['architectural decisions']:
            for scenario in inputs.scenarios['scenarios']:
                print(f"\n\nAnalyzing: {approach['approach']} - Decision: {decision} - Scenario: {scenario['scenario']}")  # For debugging
                
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
                        sources = [doc.metadata.get("id") for doc, _ in top_k_results]
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
    args = parser.parse_args()

    # Load input data
    inputs = get_inputs(args.folder_name)

    # Query specialized for each approach, decision, and scenario combination
    responses = query_specialized_for_each(inputs)

    print("Responses saved in:", RESPONSES_PATH)
