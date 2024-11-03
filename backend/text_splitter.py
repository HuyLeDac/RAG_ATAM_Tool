# This version uses langchain.py for data embedding
from langchain.document_loaders.pdf import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os  

# Load pdf documents from a directory 
# For other document types, use the appropriate loader from langchain.document_loaders
def load_docs():
    document_loader = PyPDFDirectoryLoader(os.path.join("backend", "data"))    
    documents = document_loader.load()
    return documents

# Split the documents into chunks
#  - chunk_size: the maximum number of characters in a chunk
#  - chunk_overlap: the number of characters that two consecutive chunks share
#  - length_function: a function that returns the length of a text
#  - is_separator_regex: a regular expression that matches the separator between chunks
def split_docs(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = splitter.split_documents(docs)
    return chunks

def assign_ids(chunks):
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0
            last_page_id = current_page_id
        
        chunk.metadata["id"] = f"{current_page_id}:{current_chunk_index}"
        

        

docs = load_docs()
chunks = split_docs(docs)
assign_ids(chunks)
print(f"\nNumber of chunks: {len(chunks)}")

