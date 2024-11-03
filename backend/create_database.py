from get_embedding_function import get_embedding_function
from text_splitter import chunks
from langchain_chroma import Chroma
import os

db = Chroma(
    persist_directory=os.path.join(os.path.dirname(__file__), 'database'),
    embedding_function=get_embedding_function()
)

existing_items = db.get(include=[])
existing_ids = set(existing_items["ids"])
print(f"Number of existing items in database: {len(existing_ids)}")

new_chunks = []
for chunk in chunks:

    if chunk.metadata.get("id") not in existing_ids:
        new_chunks.append(chunk)  

if not new_chunks:
    print("No new chunks to add")
    exit()
else: 
    new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
    db.add_documents(new_chunks, ids=new_chunk_ids)
    db.from_documents

