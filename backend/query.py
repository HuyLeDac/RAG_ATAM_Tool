from inputs import InputLoader, Inputs
from get_embedding_function import get_embedding_function 
from langchain_chroma import Chroma
from create_database import DATABASE_PATH  
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
import json


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
Only respond with the format mentioned as follows. Don't include any other character or text in the response:

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

def get_inputs(folder_name):
    input_loader = InputLoader(folder_name)
    inputs = input_loader.load_inputs()
    return inputs

def create_retrieval_query(inputs):
    stringified_inputs= f"""
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
    

def retrieval_query(retrieved_docs, inputs):
    embedding = get_embedding_function()

    db = Chroma(
        persist_directory=DATABASE_PATH,
        embedding_function=embedding
    )

    top_k_results = db.similarity_search_with_score(retrieved_docs, k=3)

    context_output =  "\n\n---\n\n".join([doc.page_content for doc, _score in top_k_results])
    template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = template.format(context=context_output, architecture_description=inputs.architecture_description, architectural_approaches=inputs.architectural_approaches, quality_criteria=inputs.quality_criteria, scenarios=inputs.scenarios)
    print("------------------------------------------------")
    print("START OF PROMPT")
    print(prompt)
    print("END OF PROMPT")
    print("------------------------------------------------")
    return [top_k_results, prompt]

def query(retireval_results):
    model = OllamaLLM(model="nemotron")
    response_text = model.invoke(retireval_results[1])

    sources = [doc.metadata.get("id", None) for doc, _score in retireval_results[0]]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print("---------------------------------------------------------")
    print("SRART OF RESPONS:\n")
    print(formatted_response)
    print("END OF RESPONSE")
    print("---------------------------------------------------------")
    return response_text

    
inputs = get_inputs("example1")
retrieval = create_retrieval_query(inputs)
prompt = retrieval_query(retrieval, inputs)
query(prompt)



