import fitz  # PyMuPDF

def extract_text_from_pdf(file_stream):
    """Extract text from PDF file stream"""
    doc = fitz.open(stream=file_stream, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text
