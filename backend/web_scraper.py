from fpdf import FPDF
import requests
from bs4 import BeautifulSoup
import os

URLS_PATH = "data/URLs.txt"

def read_urls(file_path):
    with open(file_path, 'r') as f:
        return f.read().splitlines()
    
# Example usage
URLS = read_urls(URLS_PATH)
    
def scrape_website(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for HTTP errors

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
    if not os.path.exists(output_dir):
        print(f"Error: Directory '{output_dir}' does not exist.")
        return

    # Sanitize the filename based on the URL
    sanitized_url = data['url'].replace("https://", "").replace("http://", "").replace("/", "_")
    pdf_filename = os.path.join(output_dir, f"{sanitized_url}.pdf")

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
    for url in URLS:
        data = scrape_website(url)
        if data:
            save_to_pdf(data)

if __name__ == "__main__":
    main()