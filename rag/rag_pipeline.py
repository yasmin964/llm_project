import os
from google import genai
from langchain_chroma import Chroma  
from langchain_huggingface import HuggingFaceEmbeddings
from rag.config import GEMINI_API_KEY, VECTORSTORE_PATH, DOCS_DIR, EMBEDDING_MODEL
from rag.build_vectorstore import build_vectorstore
from rag.build_vectorstore import build_document_chunks

client = genai.Client(api_key=GEMINI_API_KEY)


def ask_gemini(prompt, context):
    full_prompt = f"""
You are a pandas documentation assistant. Use ONLY the context below to answer.

CONTEXT:
{context}

QUESTION:
{prompt}

STRICT RULES:
1. Answer ONLY using information from the context above
2. If the answer is fully in context - provide exact answer with code examples if available
3. If answer is partially in context - answer only the part that exists in context
4. If answer is NOT in context - say: "No information found in documentation. Please check official docs (ex. https://pandas.pydata.org/docs/"
5. DO NOT add any information not present in the context
6. DO NOT make up code examples
7. If context has code examples - use them exactly as provided
8. Keep answers concise and technical

ANSWER:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[full_prompt]
    )
    return response.text


class RAGPipeline:
    def __init__(self):
        self.vectorstore = None
        self.embedding = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"}
        )
        self.load_vectorstore()

    def load_vectorstore(self):
        try:
            self.vectorstore = Chroma(
                persist_directory=VECTORSTORE_PATH,
                embedding_function=self.embedding
            )
            print("VectorStore loaded successfully")

            try:
                count = self.vectorstore._collection.count()
                print(f"Documents in collection: {count}")
            except:
                print("Could not get document count")

        except Exception as e:
            print(f"Error loading VectorStore: {e}")
            self.vectorstore = None

    def rebuild_from_pdf(self, pdf_path):
        try:
            self.vectorstore = build_vectorstore(pdf_path, VECTORSTORE_PATH)
            print("VectorStore rebuilt successfully from new PDF")
            return True
        except Exception as e:
            print(f"Error rebuilding VectorStore: {e}")
            return False

    def rebuild_index(self):
        try:
            pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith('.pdf')]

            if not pdf_files:
                print("No PDF files found")
                return False

            all_chunks = []
            for pdf_file in pdf_files:
                pdf_path = os.path.join(DOCS_DIR, pdf_file)
                chunks = build_document_chunks(pdf_path)
                all_chunks.extend(chunks)

            import shutil
            if os.path.exists(VECTORSTORE_PATH):
                shutil.rmtree(VECTORSTORE_PATH)

            self.vectorstore = Chroma.from_texts(
                texts=all_chunks,
                embedding=self.embedding,
                persist_directory=VECTORSTORE_PATH
            )

            print(f"Index rebuilt with {len(pdf_files)} documents, {len(all_chunks)} total chunks")
            return True

        except Exception as e:
            print(f"Error rebuilding index: {e}")
            return False

    def query(self, question):
        if not self.vectorstore:
            return "No documents available. Please upload a document first."

        docs = self.vectorstore.similarity_search(question, k=6)
        context = "\n\n".join([d.page_content for d in docs])
        return ask_gemini(question, context)

    def add_document(self, pdf_path):
        try:
            new_chunks = build_document_chunks(pdf_path)

            if not new_chunks:
                return False

            BATCH_SIZE = 4000

            if self.vectorstore is None:
                import shutil
                if os.path.exists(VECTORSTORE_PATH):
                    shutil.rmtree(VECTORSTORE_PATH)

                first_batch = new_chunks[:BATCH_SIZE]
                self.vectorstore = Chroma.from_texts(
                    texts=first_batch,
                    embedding=self.embedding,
                    persist_directory=VECTORSTORE_PATH
                )

                for i in range(BATCH_SIZE, len(new_chunks), BATCH_SIZE):
                    batch = new_chunks[i:i + BATCH_SIZE]
                    self.vectorstore.add_texts(batch)
                    print(f"Added batch {i // BATCH_SIZE + 1}")
            else:
                for i in range(0, len(new_chunks), BATCH_SIZE):
                    batch = new_chunks[i:i + BATCH_SIZE]
                    self.vectorstore.add_texts(batch)
                    print(f"Added batch {i // BATCH_SIZE + 1}")

            print(f"Document added in {((len(new_chunks) - 1) // BATCH_SIZE + 1)} batches")
            return True

        except Exception as e:
            print(f"Error adding document: {e}")
            return False