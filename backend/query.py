import json
import os
from inputs import InputLoader, Inputs
from get_embedding_function import get_embedding_function 
from langchain_chroma import Chroma
from create_database import DATABASE_PATH  
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# Initialize model and embedding function only once
model = OllamaLLM(model="nemotron")
retrieval_model = OllamaLLM(model="mistral")
embedding = get_embedding_function()  
db = Chroma(persist_directory=DATABASE_PATH, embedding_function=embedding)

# Load JSON data from a specified folder
def get_inputs(folder_name):
    input_loader = InputLoader(folder_name)
    inputs = input_loader.load_inputs()
    return inputs

# Helper function to format JSON data into a readable string
def format_json(data, indent=2):
    return json.dumps(data, indent=indent)

# Create retrieval query from inputs, using architecture description and approaches
def create_retrieval_query(inputs):
    input_data_str = f"""
    Architecture Description: 
    {format_json(inputs.architecture_description)}

    Architectural Approaches:
    {format_json(inputs.architectural_approaches)}
    """

    # Generate a summarized retrieval query
    summarized_query = retrieval_model.invoke(
        "Summarize the most important keywords points of the architecture:\n " + input_data_str
    )
    return summarized_query

# Function to perform retrieval query on the database
def retrieval_query(query_text):
    top_k_results = db.similarity_search_with_score(query_text, k=4)
    return top_k_results

# Function to format and send prompt to the model for each architectural decision and scenario
def generate_analysis_prompt(context_output, approach, decision, scenario):
    template = """
    <CONTEXT>
    Use the context and your own knowledge to fullfill the task: 
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
    {appraoch_description}
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
    Format response as:

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
        appraoch_description=approach['description'],
        decision=decision,
        scenario_name=scenario["scenario"],
        quality_attribute=scenario["attribute"]
    )

# Process and generate responses for each architectural approach, decision and scenario
def query_multiple_chunks(top_k_results, inputs):
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




## -----------------------------------------------------------------------------------------------
# Below are the old functions. They invoked the whole process in one go.

# Define the prompt template for generating the analysis
# PROMPT_TEMPLATE = """

# <CONTEXT>

# For the following context, you can use the following context AND your own knowledge to answer the question: 

# {context}

# </CONTEXT>

# -----

# <INPUT>

# This is the user's input data:

# Architecture Description: 
# {architecture_description}

# Architectural Approaches:
# {architectural_approaches}

# Quality Criteria:
# {quality_criteria}

# Scenarios:
# {scenarios}

# </INPUT>

# -----

# <TASK>

# Situation:

# You have a list of architectural approaches provided above. 
# In each architectural approach we have a list of architectural decisions.
# We are conducting a qualitative analysis based on ATAM.

# Task:
# The json data called Architectural Approaches contains a list of architectural decisions for each approach.
# For each architectural decision mentioned per approach, provide the risks, tradeoffs, and sensitivity points for each scenario mentioned in the scenarios.
# You are required to use the input data provided above to generate the response, but mark it with [EXTERNAL SOURCE]. 
# If the information is not available in the input data, you can use your own knowledge to generate the response, but mark it as [LLM KNOWLEDGE].
# Consider the architecture description and technical constrains and system interactions in your analysis.

# </TASK>

# -----
# For each appraoch, only respond with the format mentioned as follows. 
# Don't include any other character or text in the response. 
# Do this for each architectural decision mentioned in the architectural approach/style.

# <TEMPLATE>

# # Architectural Approach: (enter the approach)

#     ## Scenario: (enter the name of the scenario)
#         Quality Attribute: (enter the quality attribute)
#         ## Architectural decision X: (enter the architectural decision)
#             ### Risks: [LLM KNOWLEDGE or EXTERNAL SOURCE](enter the risks)
#             ### Tradeoffs: [LLM KNOWLEDGE or EXTERNAL SOURCE](enter the tradeoffs)
#             ### Sensitivity Points: [LLM KNOWLEDGE or EXTERNAL SOURCE](enter the sensitivity points)
#         ## Architectural decision Y: (enter the architectural decision)
#             ### Risks: [LLM KNOWLEDGE or EXTERNAL SOURCE](enter the risks)
#             ### Tradeoffs: [LLM KNOWLEDGE or EXTERNAL SOURCE](enter the tradeoffs)
#             ### Sensitivity Points: [LLM KNOWLEDGE or EXTERNAL SOURCE](enter the sensitivity points)
#         ## (Add other architectural decisions from architectural_approaches/architectural_decisions.json)
    
# </TEMPLATE>
# """

# def create_prompt(top_k_results, inputs):
#     # Construct context output and format the prompt
#     context_output = "\n\n---\n\n".join([doc.page_content for doc, _score in top_k_results])
#     template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
#     prompt = template.format(
#         context=context_output, 
#         architecture_description=inputs.architecture_description, 
#         architectural_approaches=inputs.architectural_approaches, 
#         quality_criteria=inputs.quality_criteria, 
#         scenarios=inputs.scenarios
#     )
    
#     # Display prompt for debugging purposes
#     print("------------------------------------------------")
#     print("START OF PROMPT")
#     print(prompt)
#     print("END OF PROMPT")
#     print("------------------------------------------------\n\n")

#     return prompt


# # Function to invoke the model for a response based on the retrieval results
# def query(prompt, top_k_results):
#     model = OllamaLLM(model="nemotron")  # Initialize model with the specified model name
#     response_text = model.invoke(prompt)  # Generate response from prompt

#     # Extract sources and format the response output
#     sources = [doc.metadata.get("id", None) for doc, _score in top_k_results]
#     formatted_response = f"Response: {response_text}\nSources: {sources}"
    
#     # Display the response for debugging purposes
#     print("---------------------------------------------------------")
#     print("START OF RESPONSE:\n")
#     print(formatted_response)
#     print("\nEND OF RESPONSE")
#     print("---------------------------------------------------------")
    
#     return response_text
## -----------------------------------------------------------------------------------------------

if __name__ == "__main__":
    # Execute the query pipeline
    inputs = get_inputs("example1")
    created_retrieval_query = create_retrieval_query(inputs)
    top_k_results = retrieval_query(created_retrieval_query)

    query_multiple_chunks(top_k_results, inputs)

    #prompt = create_prompt(top_k_results, inputs)
    #response = query(prompt, top_k_results)
    