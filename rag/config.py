# bot/config.py
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def is_vercel():
    return os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None

def is_koyeb():
    return os.environ.get('KOYEB') is not None

def is_local():
    return not (is_vercel() or is_koyeb())

if is_vercel():
    VECTORSTORE_PATH = "/tmp/faiss_index"
    DOCS_DIR = "/tmp/documents"
    print("Running on Vercel - using /tmp storage")
else:
    VECTORSTORE_PATH = "data/faiss_index"
    DOCS_DIR = "data/documents"
    print(" Running locally - using persistent storage")

os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)

print(f" DOCS_DIR: {DOCS_DIR}")
print(f" VECTORSTORE_PATH: {VECTORSTORE_PATH}")