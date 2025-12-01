from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from rag.config import VECTORSTORE_PATH
import pymupdf
import os


def load_pdf(path):
    doc = pymupdf.open(path)
    text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        text += f"\nPage {page_num + 1} \n"
        text += page.get_text("text") + "\n"

    return text


def build_vectorstore(pdf_path, vectorstore_path=VECTORSTORE_PATH):
    print(f"Load PDF with PyMuPDF: {pdf_path}")
    full_text = load_pdf(pdf_path)

    print("Cut to chunks with better splitting...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        length_function=len,
    )

    chunks = splitter.split_text(full_text)
    print(f"Created {len(chunks)} chunks")

    print("Create embeddings...")
    embedding = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

    print("Create FAISS vectorstore...")
    vectorstore = FAISS.from_texts(chunks, embedding)

    os.makedirs(os.path.dirname(vectorstore_path), exist_ok=True)

    vectorstore.save_local(vectorstore_path)
    print(f"FAISS index saved to {vectorstore_path}!")

    return vectorstore


def build_document_chunks(pdf_path):
    print(f"Processing PDF: {pdf_path}")

    try:
        full_text = load_pdf(pdf_path)

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=200,
            separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
            length_function=len,
        )

        chunks = splitter.split_text(full_text)
        print(f" Created {len(chunks)} chunks from {os.path.basename(pdf_path)}")
        return chunks

    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        build_vectorstore(sys.argv[1])
    else:
        print("Usage: python build_vectorstore.py <path_to_pdf>")