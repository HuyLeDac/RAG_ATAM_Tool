import json
import os
from inputs import InputLoader, Inputs
from get_embedding_function import get_embedding_function 
from langchain_chroma import Chroma
from create_database import DATABASE_PATH  
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM

# Define the prompt template for generating the analysis
PROMPT_TEMPLATE = """
For the following context, you can use the following context AND your own knowledge to answer the question: 
{context}

-----
Also, consider the following inputs:

Architecture Description: 
{architecture_description}

Architectural Approaches:
{architectural_approaches}

Quality Criteria:
{quality_criteria}

Scenarios:
{scenarios}

-----
Situation:

We are in the middle of a software architecture design process called the Architecture Tradeoff Analysis Method (ATAM).
Right now, we are trying to analyse different architectural approaches/styles mentioned above.
For each approach we have a set of architectural decisions and we need to analyse the risks, tradeoffs and sensitivity points for each decision.
We provided different architectural views and an architecture description to help us with analysis. 
Additionally, we have a set of quality criteria and scenarios to consider.

Task:
Your task is to provide an analysis of the architectural decisions for each architectural approach/style mentioned above.
You can use the provided context and inputs to answer the question.
For the unknown context, you can use your own knowledge to answer the question.
Try to provide a detailed analysis of the risks, tradeoffs and sensitivity points for each architectural decision for each decision mentioned in the architectural approach/style.

-----
Only respond with the format mentioned as follows. Don't include any other character or text in the response. Do this for each architectural decision mentioned in the architectural approach/style.:

# Architectural Approach: (enter the name of the architectural approach)

    ## Scenario: (enter the name of the scenario)
        ## Architectural decision: (enter the architectural decision)
            ### Risks: (enter the risks)
            ### Tradeoffs: (enter the tradeoffs)
            ### Sensitivity Points (enter the sensitivity points)
    
        ## (Add other architectural decisions mentioned from the architectural_approach file)
    
    ## (Add other scenarios mentioned from the scenarios file)

# (Add other architectural approaches mentioned from the architectural_approaches file)

"""

# Function to load input data from a specified folder
def get_inputs(folder_name):
    input_loader = InputLoader(folder_name)
    inputs = input_loader.load_inputs()
    return inputs

# Function to format the input data for embedding
def create_retrieval_query(inputs):
    # Convert input data into a single string representation
    stringified_inputs = f"""
    Architecture Description: 
    {json.dumps(inputs.architecture_description, indent=2)}

    Architectural Approaches:
    {json.dumps(inputs.architectural_approaches, indent=2)}

    Quality Criteria:
    {json.dumps(inputs.quality_criteria, indent=2)}

    Scenarios:
    {json.dumps(inputs.scenarios, indent=2)}

    """
    return stringified_inputs

# Function to perform a retrieval query on the database
def retrieval_query(retrieved_docs, inputs):
    embedding = get_embedding_function()  # Load the embedding function

    # Initialize Chroma database with persistence and embedding function
    db = Chroma(
        persist_directory=DATABASE_PATH,
        embedding_function=embedding
    )

    # Perform similarity search in the database
    top_k_results = db.similarity_search_with_score(retrieved_docs, k=3)

    # Construct context output and format the prompt
    context_output = "\n\n---\n\n".join([doc.page_content for doc, _score in top_k_results])
    template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = template.format(
        context=context_output, 
        architecture_description=inputs.architecture_description, 
        architectural_approaches=inputs.architectural_approaches, 
        quality_criteria=inputs.quality_criteria, 
        scenarios=inputs.scenarios
    )
    
    # Display prompt for debugging purposes
    print("------------------------------------------------")
    print("START OF PROMPT")
    print(prompt)
    print("END OF PROMPT")
    print("------------------------------------------------\n\n")
    
    return [top_k_results, prompt]

# Function to invoke the model for a response based on the retrieval results
def query(retireval_results):
    model = OllamaLLM(model="nemotron")  # Initialize model with the specified model name
    response_text = model.invoke(retireval_results[1])  # Generate response from prompt

    # Extract sources and format the response output
    sources = [doc.metadata.get("id", None) for doc, _score in retireval_results[0]]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    
    # Display the response for debugging purposes
    print("---------------------------------------------------------")
    print("START OF RESPONSE:\n")
    print(formatted_response)
    print("END OF RESPONSE")
    print("---------------------------------------------------------")
    
    return response_text

if __name__ == "__main__":
    # Execute the query pipeline
    inputs = get_inputs("example1")
    retrieval = create_retrieval_query(inputs)
    prompt = retrieval_query(retrieval, inputs)
    query(prompt)
