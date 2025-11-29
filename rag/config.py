import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Определяем среду выполнения
if os.environ.get('RENDER'):  # ← ДОБАВИТЬ RENDER
    # Продакшен на Render
    VECTORSTORE_PATH = "/tmp/faiss_index"
    DOCS_DIR = "/tmp/documents"
elif os.environ.get('RAILWAY_ENVIRONMENT'):
    # Продакшен на Railway
    VECTORSTORE_PATH = "/tmp/faiss_index"
    DOCS_DIR = "/tmp/documents"
else:
    # Локальная разработка
    VECTORSTORE_PATH = "data/faiss_index"
    DOCS_DIR = "data/documents"

# Создаем папки если их нет
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)