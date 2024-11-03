from query import InputManager
import chromadb
from chromadb.config import Settings
import fitz  # PyMuPDF for PDF extraction
import os
import ollama



# Get the stringified input data
input_manager = InputManager(folder_name="example1")
inputs = input_manager.load_inputs()
input_string = InputManager.format_to_string(inputs)

# 