from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os  

# Define the path to the directory containing PDF documents
DATA_PATH = os.path.join("data")

def load_docs():
    """
    Loads PDF documents from the specified directory.

    This function utilizes the PyPDFDirectoryLoader to scan a directory and load all PDF documents 
    for further processing.

    Returns:
        list: A list of loaded documents with their associated metadata.
    """
    document_loader = PyPDFDirectoryLoader(DATA_PATH)
    documents = document_loader.load()
    return documents


def split_docs(docs):
    """
    Splits the loaded documents into smaller chunks of text for processing.

    This function uses the RecursiveCharacterTextSplitter to divide the documents into 
    chunks based on a specified maximum character length and overlap.

    Args:
        docs (list): A list of documents to be split into chunks.

    Returns:
        list: A list of text chunks with metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,          # Maximum characters per chunk
        chunk_overlap=80,        # Overlap between consecutive chunks
        length_function=len,     # Function to calculate chunk length
        is_separator_regex=False # Whether to use regex for splitting
    )
    chunks = splitter.split_documents(docs)
    return chunks


def assign_ids(chunks):
    """
    Assigns unique IDs to each text chunk for tracking and reference.

    This function generates IDs based on the document's source, page number, and 
    the chunk index on that page. It ensures all chunks have a unique identifier.

    Args:
        chunks (list): A list of text chunks with metadata.

    Returns:
        None: Updates the metadata of each chunk with a unique ID.
    """
    last_page_id = None            # Tracks the last processed page ID
    current_chunk_index = 0        # Index of the current chunk on the same page

    for chunk in chunks:
        source = chunk.metadata.get("source")  # Document source (e.g., file name)
        page = chunk.metadata.get("page")     # Page number of the chunk
        current_page_id = f"{source}:{page}"  # Create a unique page ID

        if current_page_id == last_page_id:
            current_chunk_index += 1          # Increment chunk index on the same page
        else:
            current_chunk_index = 0           # Reset chunk index for a new page
            last_page_id = current_page_id    # Update last processed page

        # Assign a unique ID to the chunk
        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"


def get_chunks():
    """
    Loads, splits, and assigns unique IDs to document chunks.

    This function orchestrates the process of loading PDF documents from a directory, 
    splitting them into smaller text chunks, and assigning unique identifiers to each chunk.

    Returns:
        list: A list of text chunks with metadata and unique IDs.
    """
    docs = load_docs()              # Load documents from the specified directory
    chunks = split_docs(docs)       # Split documents into smaller chunks
    assign_ids(chunks)              # Assign unique IDs to each chunk

    print(f"\nNumber of chunks: {len(chunks)}")  # Display the total number of chunks
    return chunks
