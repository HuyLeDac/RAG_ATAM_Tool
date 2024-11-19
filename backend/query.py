import os
import json
import argparse
from inputs import InputLoader, Inputs
from get_embedding_function import get_embedding_function
from langchain_chroma import Chroma
from create_database import DATABASE_PATH
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# Constants
RESPONSES_PATH = "backend/responses/responses.json"  # Path to store responses

# Initialize models and database
MODEL = OllamaLLM(model="nemotron")
SUMMARIZE_MODEL = OllamaLLM(model="mistral")
DB = Chroma(persist_directory=DATABASE_PATH, embedding_function=get_embedding_function())

# Helper Functions
def format_json(data: dict, indent: int = 2) -> str:
    """
    Format JSON data into a readable string.

    Args:
        data (dict): The JSON data to format.
        indent (int): Number of spaces for indentation.

    Returns:
        str: Formatted JSON string.
    """
    return json.dumps(data, indent=indent)

# Input Handling
def get_inputs(folder_name: str) -> Inputs:
    """
    Load JSON data from the specified folder.

    Args:
        folder_name (str): Folder containing input JSON files.

    Returns:
        Inputs: Structured architecture data.
    """
    input_loader = InputLoader(folder_name)
    return input_loader.load_inputs()

# Retrieval Functions
def create_retrieval_query(inputs: Inputs) -> str:
    """
    Create a summarized retrieval query from the inputs.

    Args:
        inputs (Inputs): Architecture data including context and approaches.

    Returns:
        str: Summarized query for database search.
    """
    input_data = f"""
    Architecture Context: 
    {format_json(inputs.architecture_context)}

    Architectural Approaches:
    {format_json(inputs.architectural_approaches)}
    """
    return SUMMARIZE_MODEL.invoke(
        "Summarize the most important keywords and points of the architecture. "
        "Add keywords such as risks, tradeoffs, sensitivity points, pros, and cons under the summary:\n"
        + input_data
    )

def retrieval_query(query_text: str, k: int = 7):
    """
    Perform a retrieval query on the database.

    Args:
        query_text (str): The query text for similarity search.
        k (int): Number of top results to retrieve.

    Returns:
        List[Tuple[Document, float]]: Retrieved documents and their scores.
    """
    print("Retrieval Query:")
    top_k_results = DB.similarity_search_with_score(query_text, k=k)
    for doc, score in top_k_results:
        print(f"Document ID: {doc.metadata.get('id')} - Score: {score}")
    return top_k_results

# Analysis Functions
def generate_analysis_prompt(context_output: str, approach: dict, decision: str, scenario: dict, inputs: Inputs) -> str:
    """
    Generate an analysis prompt for architectural decision and scenario evaluation.

    Args:
        context_output (str): Context text retrieved from the database.
        approach (dict): Architectural approach data.
        decision (str): Specific architectural decision.
        scenario (dict): Scenario details.
        inputs (Inputs): Full input data.

    Returns:
        str: Formatted prompt for model analysis.
    """
    template = """
    <CONTEXT>
    Use the context and your own knowledge to fulfill the task: 
    {context}
    </CONTEXT>

    -----

    <INPUT>
    User's input data:
    Architecture Context: 
    {architecture_context}
    Architectural Approach Description: 
    {approach_description}
    Architectural Views: 
    {architectural_views}
    Quality Criteria: 
    {quality_criteria}
    Scenario: 
    {scenario}
    </INPUT>

    -----

    <TASK>
    We are conducting a qualitative analysis based on ATAM.

    Task:
    Provide the risks, tradeoffs, and sensitivity points regarding the scenario in the architectural decision: {decision}.
    Use the input data provided, marking any external knowledge as [LLM KNOWLEDGE].
    </TASK>

    -----
    Format the response strictly in JSON as follows:
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

def query_multiple_chunks(top_k_results, inputs: Inputs):
    """
    Process multiple architectural approaches, decisions, and scenarios.

    Args:
        top_k_results: Retrieved top-k documents.
        inputs (Inputs): Full input data.

    Returns:
        list: Responses generated by the model.
    """
    context_output = "\n\n---\n\n".join([doc.page_content for doc, _ in top_k_results])
    responses = []

    for approach in inputs.architectural_approaches['architecturalApproaches']:
        for scenario in inputs.scenarios['scenarios']:
            for decision in approach['architectural decisions']:
                print(f"Analyzing: {approach['approach']} - Decision: {decision} - Scenario: {scenario['scenario']}")
                prompt = generate_analysis_prompt(context_output, approach, decision, scenario, inputs)
                response_text = MODEL.invoke(prompt)
                response_dict = json.loads(response_text)
                response_dict['sources'] = [doc.metadata.get("id") for doc, _ in top_k_results]
                responses.append(response_dict)
                print(json.dumps(response_dict, indent=2))
    
    os.makedirs(os.path.dirname(RESPONSES_PATH), exist_ok=True)
    with open(RESPONSES_PATH, 'w') as json_file:
        json.dump(responses, json_file, indent=2)

    return responses

# Main Function
def main():
    parser = argparse.ArgumentParser(description="Query Pipeline for Architectural Analysis")
    parser.add_argument("folder_name", type=str, help="The folder containing the input data")
    args = parser.parse_args()

    inputs = get_inputs(args.folder_name)
    retrieval_query_text = create_retrieval_query(inputs)
    top_k_results = retrieval_query(retrieval_query_text)
    query_multiple_chunks(top_k_results, inputs)
    print(f"Responses stored in: {RESPONSES_PATH}")

if __name__ == "__main__":
    main()
