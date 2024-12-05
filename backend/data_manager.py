import os

class PDFManager:
    def __init__(self, data_directory):
        self.data_directory = data_directory
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

    def add_pdf(self, pdf_name, pdf_content):
        pdf_path = os.path.join(self.data_directory, pdf_name)
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_content)

    def delete_pdf(self, pdf_name):
        pdf_path = os.path.join(self.data_directory, pdf_name)
        if os.path.exists(pdf_path):
            os.remove(pdf_path)

    def get_all_pdfs(self):
        return [f for f in os.listdir(self.data_directory) if f.endswith('.pdf')]
    
    def get_pdf(self, pdf_name):
        pdf_path = os.path.join(self.data_directory, pdf_name)
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as pdf_file:
                return pdf_file.read()
        return None
    