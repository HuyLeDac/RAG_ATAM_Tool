from langchain_ollama import OllamaEmbeddings

def get_embedding_function():
    """
    Initializes and returns an embedding function using the Ollama model for text embeddings.

    This function sets up the Ollama embeddings model with the specified configuration, 
    in this case, using the "nomic-embed-text" model. The returned embeddings can then
    be used for generating embeddings for text data.

    Returns:
        OllamaEmbeddings: The initialized Ollama embeddings model.
    """
    # Initialize the OllamaEmbeddings with the "nomic-embed-text" model
    embeddings = OllamaEmbeddings(
        model="nomic-embed-text",  # Specify the model to be used for embeddings
    )
    
    # Return the embedding function (model)
    return embeddings
