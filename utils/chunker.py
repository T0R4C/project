import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt', quiet=True)

def sentence_tokenize(text):
    return nltk.sent_tokenize(text)

def create_chunks(sentences, chunk_size=4):
    """Group sentences into chunks of chunk_size sentences"""
    chunks = []
    for i in range(0, len(sentences), chunk_size):
        chunk = " ".join(sentences[i:i+chunk_size])
        chunks.append(chunk)
    return chunks
