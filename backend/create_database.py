from get_embedding_function import get_embedding_function
from text_splitter import get_chunks
from langchain_chroma import Chroma
import os

# Define the path to the database directory
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database')

# Function to create and update the database with new document chunks
def create_database():
    """
    Initializes a Chroma database, retrieves document chunks,
    and updates the database by adding new chunks while avoiding duplicates.
    """
    # Initialize the Chroma database with persistence directory and embedding function
    db = Chroma(
        persist_directory=DATABASE_PATH,  # Directory where the database is persisted
        embedding_function=get_embedding_function()  # Function to compute embeddings
    )

    # Retrieve document chunks from an external function
    chunks = get_chunks()

    # Get existing items from the database to prevent duplicate entries
    existing_items = db.get(include=[])  # Fetch all existing records without specific filters
    existing_ids = set(existing_items["ids"])  # Extract IDs of existing chunks
    print(f"Number of existing items in database: {len(existing_ids)}")

    # Filter out chunks that are already in the database
    new_chunks = [
        chunk for chunk in chunks 
        if chunk.metadata.get("id") not in existing_ids
    ]

    # Check if there are new chunks to add to the database
    if not new_chunks:
        print("No new chunks to add")  # Notify if there are no new chunks
        return  # Exit the function if no new chunks are found

    # Extract IDs of new chunks to add them to the database
    new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]

    # Add new chunks to the database with their IDs
    db.add_documents(new_chunks, ids=new_chunk_ids)

    # Log the number of new chunks added to the database
    print(f"Added {len(new_chunks)} new chunks to database")

# Entry point for the script
if __name__ == "__main__":
    create_database()
