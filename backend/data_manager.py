import os

class PDFManager:
    """
    Manages PDF files within a specified directory. Provides functionality to add, delete, 
    retrieve, and list PDF files in the directory.
    """

    def __init__(self, data_directory):
        """
        Initializes the PDFManager with the provided data directory. If the directory doesn't exist, 
        it will be created.

        Args:
            data_directory (str): The directory where PDF files will be stored.
        """
        self.data_directory = data_directory

        # Check if the data directory exists; if not, create it
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

    def add_pdf(self, pdf_name, pdf_content):
        """
        Adds a new PDF file to the data directory.

        Args:
            pdf_name (str): The name of the PDF file.
            pdf_content (bytes): The binary content of the PDF file.
        """
        pdf_path = os.path.join(self.data_directory, pdf_name)

        # Write the binary PDF content to a file in the specified directory
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content)

    def delete_pdf(self, pdf_name):
        """
        Deletes a PDF file from the data directory if it exists.

        Args:
            pdf_name (str): The name of the PDF file to delete.
        """
        pdf_path = os.path.join(self.data_directory, pdf_name)

        # Remove the PDF file if it exists
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def get_all_pdfs(self):
        """
        Retrieves the names of all PDF files in the data directory.

        Returns:
            list: A list of PDF filenames in the directory.
        """
        # List all files in the directory and filter for files that end with '.pdf'
        return [f for f in os.listdir(self.data_directory) if f.endswith('.pdf')]

    def get_pdf(self, pdf_name):
        """
        Retrieves the content of a specific PDF file from the data directory.

        Args:
            pdf_name (str): The name of the PDF file to retrieve.

        Returns:
            bytes: The binary content of the PDF file, or None if the file doesn't exist.
        """
        pdf_path = os.path.join(self.data_directory, pdf_name)

        # Check if the file exists and return its content, otherwise return None
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                return pdf_file.read()
        return None
