from get_embedding_function import get_embedding_function
from text_splitter import get_chunks
from langchain_chroma import Chroma
import os

# Define the path to the database directory
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database')

# Function to create and update the database with new document chunks
def create_database():
    # Initialize the Chroma database with a specified directory and embedding function
    db = Chroma(
        persist_directory=DATABASE_PATH,
        embedding_function=get_embedding_function()
    )

    # Retrieve the list of document chunks
    chunks = get_chunks()

    # Retrieve existing items from the database to avoid duplicate entries
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])  # Extract existing chunk IDs
    print(f"Number of existing items in database: {len(existing_ids)}")

    # Filter out chunks that already exist in the database by ID
    new_chunks = []
    for chunk in chunks:
        if chunk.metadata.get("id") not in existing_ids:
            new_chunks.append(chunk)  # Add new chunks only if not already in database

    # Check if there are any new chunks to add
    if not new_chunks:
        print("No new chunks to add")  # Notify if no new chunks found
        return  # Exit if no new chunks are available
    else: 
        # Extract IDs of new chunks for adding to the database
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        
        # Add new chunks to the database with their corresponding IDs
        db.add_documents(new_chunks, ids=new_chunk_ids)
        
        # Print confirmation of added chunks
        print(f"Added {len(new_chunks)} new chunks to database")

if __name__ == "__main__":
    create_database()
