import os
import pdfplumber
import ollama
import json

def parse_file(file):
    if not os.path.exists(file):
        raise FileNotFoundError(f"File not found: {file}")
    elif file.endswith('.pdf'):
        paragraphs = []

        # Open the PDF file with pdfplumber
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Extract text from each page
                text = page.extract_text()
                if text:
                    # Split the text by double newlines to separate paragraphs
                    page_paragraphs = text.split('\n\n')
                    paragraphs.extend(page_paragraphs)

        return paragraphs
    
    else:
        # Parse the file and return the data
        with open(file, encoding='utf-8-sig') as f:
            paragraphs = []
            buffer = []

            for line in f:
                line = line.strip()
                if line:
                    buffer.append(line)
                elif buffer:
                    paragraphs.append(" ".join(buffer))
                    buffer = []

            if len(buffer):
                paragraphs.append(" ".join(buffer))
            return paragraphs

def save_embeddings(file, embeddings):
    base_name = os.path.splitext(os.path.basename(file))
    print(f"Base name: {base_name}")  # Debug print
    save_path = f"database/embeddings/{base_name}.json"
    
    if not os.path.exists("database/embeddings"):
        os.makedirs("database/embeddings")
    print(f"Attempting to save embeddings to {os.path.abspath(save_path)}")  # Debug print to verify path
    
    # Save embeddings folder
    with open(save_path, "w") as f:
        json.dump(embeddings, f)
    print("Embeddings saved successfully.")

    
def load_embeddings(file):
    base_name = os.path.splitext(os.path.basename(file))[0]
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "embeddings", f"{base_name}.json")
    
    print(f"Loading embeddings from {file_path}")  # Debug print to verify load path
    if not os.path.exists(file_path):
        return False
    else:
        with open(file_path, "r") as f:
            return json.load(f)
        
def get_embeddings(filename, embedding_model, paragraphs):
    # Check if embeddings already exist
    if (embeddings := load_embeddings(filename)) is not False:
        return embeddings
    
    # Generate and save embeddings
    embeddings = [ollama.embeddings(model=embedding_model, prompt=paragraph)["embedding"] for paragraph in paragraphs]
    save_embeddings(filename, embeddings)
    return embeddings


# Example usage
file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'Software-Architecture-Patterns.pdf')
paragraphs = parse_file(file)

# Load embeddings and print a sample
embedding = get_embeddings(file, "all-minilm:l6-v2", paragraphs)
#print(embedding[5:10])

# Print size of embeddings
print(f"Number of embeddings: {len(embedding)}")
