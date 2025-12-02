import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
EMBEDDING_MODEL = "sentence-transformers/paraphrase-MiniLM-L3-v2"

if os.environ.get('KOYEB'):
    VECTORSTORE_PATH = "/tmp/chroma_db"
    DOCS_DIR = "/tmp/documents"
else:
    VECTORSTORE_PATH = "chroma_db"
    DOCS_DIR = "data/documents"

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(VECTORSTORE_PATH, exist_ok=True)