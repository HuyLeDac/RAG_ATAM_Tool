from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import os

URLS_PATH = "data/URLs.txt"

def read_urls(file_path):
    """
    Reads a list of URLs from a file.

    This function reads a text file containing URLs, each on a new line, 
    and returns them as a list of strings.

    Args:
        file_path (str): The path to the file containing URLs.

    Returns:
        list: A list of URLs read from the file.
    """
    with open(file_path, 'r') as f:
        return f.read().splitlines()

# Read URLs from the file
URLS = read_urls(URLS_PATH)

def scrape_website(url):
    """
    Scrapes the content of a website, extracting the title and paragraph text.

    This function sends a GET request to the specified URL, parses the HTML using 
    BeautifulSoup, and extracts the title and all text from <p> tags.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        dict: A dictionary containing the website URL, title, and extracted text.
        None: If an error occurs during the request or parsing.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP issues

        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text() for p in paragraphs])

        return {
            'url': url,
            'title': title,
            'text': text
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_to_pdf(data, output_dir="data"):
    """
    Saves scraped website data to a PDF file.

    This function generates a PDF file containing the title, URL, and main text 
    from the scraped data. It ensures filenames are sanitized and avoids overwriting 
    existing PDFs.

    Args:
        data (dict): A dictionary containing the website's URL, title, and text.
        output_dir (str): The directory where the PDF will be saved. Default is "data".

    Returns:
        None: Saves the PDF file to the specified directory.
    """
    if not os.path.exists(output_dir):
        print(f"Error: Directory '{output_dir}' does not exist.")
        return

    # Sanitize the filename based on the URL
    sanitized_url = data['url'].replace("https://", "").replace("http://", "").replace("/", "_").replace("#", "_")
    pdf_filename = os.path.join(output_dir, f"{sanitized_url}.pdf")

    # Check if the PDF already exists
    if os.path.exists(pdf_filename):
        print(f"Skipping: {pdf_filename} already exists.")
        return

    # Create the PDF with UTF-8 support
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add title and URL
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, data['title'].encode('latin1', 'replace').decode('latin1'), ln=True, align="C")
    pdf.set_font("Arial", "I", 12)
    pdf.cell(0, 10, data['url'].encode('latin1', 'replace').decode('latin1'), ln=True, align="C")
    pdf.ln(10)

    # Add main text
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, data['text'].encode('latin1', 'replace').decode('latin1'))

    # Save PDF
    pdf.output(pdf_filename)
    print(f"Saved: {pdf_filename}")

def main():
    """
    Main function to scrape websites and save their content to PDFs.

    This function reads a list of URLs from the predefined file, scrapes their content, 
    and saves the data to individual PDF files in the specified directory.

    Returns:
        None: Executes the full workflow of scraping and PDF creation.
    """
    for url in URLS:
        data = scrape_website(url)
        if data:
            save_to_pdf(data)

if __name__ == "__main__":
    main()
