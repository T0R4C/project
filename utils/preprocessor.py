import re

def remove_bibliography(text, exclude_refs=False):
    if not exclude_refs:
        return text
    
    # Patterns for bibliography section (case-insensitive)
    biblio_patterns = [
        r'\n\s*DAFTAR PUSTAKA\s*\n',
        r'\n\s*REFERENCES\s*\n',
        r'\n\s*BIBLIOGRAFI\s*\n',
        r'\n\s*\d+\.\s*[A-Z].*'  # Simple numbered ref pattern
    ]
    
    # Find first occurrence and truncate
    for pattern in biblio_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return text[:match.start()]
    return text

def clean_text(text):
    # Remove extra whitespace, normalize
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
