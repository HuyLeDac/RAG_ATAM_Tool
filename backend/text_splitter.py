from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os  

# Define the path to the directory containing PDF documents
DATA_PATH = os.path.join("backend", "data")

# Load PDF documents from a specified directory
# Uses PyPDFDirectoryLoader to handle loading all PDFs within the given directory
def load_docs():
    document_loader = PyPDFDirectoryLoader(DATA_PATH)    
    documents = document_loader.load()
    return documents

# Split loaded documents into chunks for processing
# Parameters:
#  - chunk_size: maximum number of characters allowed in each chunk
#  - chunk_overlap: number of overlapping characters between consecutive chunks
#  - length_function: function used to calculate text length
#  - is_separator_regex: determines if a regular expression is used for separating chunks
def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(docs)
    return chunks

# Assign unique IDs to each chunk based on document source and page number
# Ensures IDs follow the format "source:page:chunk_index"
def assign_ids(chunks):
    last_page_id = None            # Stores the previous chunk's page ID for tracking
    current_chunk_index = 0         # Tracks the chunk index within the same page

    for chunk in chunks:
        # Extract the document source and page number from metadata
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"   # Generate page-specific ID

        # Increment chunk index if the page is the same; reset otherwise
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
            last_page_id = current_page_id
        
        # Assign the unique ID to the chunk metadata
        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"

# Main function to load, split, and assign IDs to document chunks
def get_chunks():    
    docs = load_docs()               # Load documents from directory
    chunks = split_docs(docs)        # Split documents into manageable chunks
    assign_ids(chunks)               # Assign unique IDs to each chunk
    print(f"\nNumber of chunks: {len(chunks)}")  # Output the number of chunks generated
    return chunks
