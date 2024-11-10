import json
import os
from inputs import InputLoader, Inputs
from get_embedding_function import get_embedding_function 
from langchain_chroma import Chroma
from create_database import DATABASE_PATH  
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# Initialize the models and embedding function once to optimize performance
model = OllamaLLM(model="nemotron")  # Main model used for querying decisions and scenarios
retrieval_model = OllamaLLM(model="mistral")  # Model for summarizing inputs for retrieval from database
embedding = get_embedding_function()  # Embedding function to vectorize inputs for database search
db = Chroma(persist_directory=DATABASE_PATH, embedding_function=embedding)  # Database for document retrieval


# Function: Load JSON data from a specified folder
# - Initializes InputLoader to load JSON data from `folder_name`.
# - Returns an `Inputs` object containing structured architecture data.
def get_inputs(folder_name):
    input_loader = InputLoader(folder_name)
    inputs = input_loader.load_inputs()
    return inputs


# Helper Function: Format JSON data into a readable string
# - `data`: JSON data to be formatted as a readable string.
# - `indent`: Number of spaces for indentation in the formatted JSON string.
def format_json(data, indent=2):
    return json.dumps(data, indent=indent)


# Function: Create retrieval query from inputs
# - Converts architecture description and approaches into a formatted string.
# - Uses `retrieval_model` to generate a summarized query.
# - Returns a string with key architectural information for similarity search.
def create_retrieval_query(inputs):
    input_data_str = f"""
    Architecture Description: 
    {format_json(inputs.architecture_description)}

    Architectural Approaches:
    {format_json(inputs.architectural_approaches)}
    """

    # Generate a summarized retrieval query for database search
    summarized_query = retrieval_model.invoke(
        "Summarize the most important keywords points of the architecture:\n " + input_data_str
    )
    return summarized_query


# Function: Perform retrieval query on the database
# - `query_text`: The formatted query text used for similarity search.
# - Searches the Chroma database and returns the top `k` relevant documents.
def retrieval_query(query_text):
    top_k_results = db.similarity_search_with_score(query_text, k=4)
    return top_k_results


# Function: Generate analysis prompt for each architectural decision and scenario
# - `context_output`: Text containing the context retrieved from the database.
# - `approach`, `decision`, `scenario`: Specific data points for the current architectural decision and scenario.
# - Formats the prompt for the model to evaluate architectural risks, tradeoffs, and sensitivity points.
# - Returns the formatted prompt as a string.
def generate_analysis_prompt(context_output, approach, decision, scenario):
    template = """
    <CONTEXT>
    Use the context and your own knowledge to fulfill the task: 
    {context}
    </CONTEXT>

    -----

    <INPUT>
    User's input data:
    Architecture Description: 
    {architecture_description}
    Architectural Views: 
    {architectural_views}
    Architectural Approach Description:
    {approach_description}
    Quality Criteria:
    {quality_criteria}
    Scenario:
    {scenario}
    </INPUT>

    -----

    <TASK>
    We are conducting a qualitative analysis based on ATAM.

    Task:
    Provide the risks, tradeoffs, and sensitivity points for the scenario in the architectural decision: {decision}.
    Use the input data provided, marking any external knowledge as [LLM KNOWLEDGE].
    </TASK>

    -----
    Format response as. Don't use any other formats:

    # Architectural Approach: {current_approach}
    ## Scenario: {scenario_name}; Quality Attribute: {quality_attribute}
    ### Architectural Decision: {decision}
    #### Risks: [LLM KNOWLEDGE/DATABASE SOURCE](enter risks)
    - (enter risks)
    #### Tradeoffs: [LLM KNOWLEDGE/DATABASE SOURCE](enter tradeoffs)
    - (enter tradeoffs)
    #### Sensitivity Points: [LLM KNOWLEDGE/DATABASE SOURCE](enter sensitivity points)
    - (enter sensitivity points)
    """
    return template.format(
        context=context_output,
        architecture_description=format_json(inputs.architecture_description),
        architectural_views=format_json(inputs.get_architectural_views_as_list()),
        quality_criteria=format_json(inputs.quality_criteria),
        scenario=format_json(scenario),
        current_approach=approach['approach'],
        approach_description=approach['description'],
        decision=decision,
        scenario_name=scenario["scenario"],
        quality_attribute=scenario["attribute"]
    )


# Function: Process multiple architectural approaches, decisions, and scenarios
# - Iterates through each approach, decision, and scenario to generate prompts.
# - Sends prompts to `model` and appends responses with context and sources.
# - Prints each response for debugging and stores responses for further use.
def query_multiple_chunks(top_k_results, inputs):
    # Convert top-k results into context text
    context_output = "\n\n---\n\n".join([doc.page_content for doc, _ in top_k_results])

    responses = []
    for approach in inputs.architectural_approaches['architecturalApproaches']:
        for decision in approach['architectural decisions']:
            for scenario in inputs.scenarios['scenarios']:
                formatted_prompt = generate_analysis_prompt(context_output, approach, decision, scenario)
                
                response_text = model.invoke(formatted_prompt)
                sources = [doc.metadata.get("id") for doc, _ in top_k_results]
                formatted_response = f"{response_text}\n\nSources: {sources}"

                # Display response for debugging purposes
                print("---------------------------------------------------------")
                print("START OF RESPONSE:\n")
                print(formatted_response)
                print("\nEND OF RESPONSE")
                print("---------------------------------------------------------")

                responses.append(formatted_response)  # Store responses for further processing/logging

    return responses


# Main Execution
# Loads input data, creates a retrieval query, searches the database, and generates responses
if __name__ == "__main__":
    # Execute the query pipeline
    inputs = get_inputs("example1")  # Load example data from specified folder
    created_retrieval_query = create_retrieval_query(inputs)  # Summarize input for retrieval
    top_k_results = retrieval_query(created_retrieval_query)  # Retrieve relevant database docs
    query_multiple_chunks(top_k_results, inputs)  # Generate prompts and responses
