# Documentation Chat Bot

## Project Overview

A sophisticated Telegram bot that implements Retrieval-Augmented Generation (RAG) to provide intelligent answers based on uploaded PDF documents.

###  Key Features
- **PDF Document Processing**: Upload and process PDF files of various sizes
- **Intelligent Q&A**: Ask questions about uploaded documents and get accurate answers
- **Vector Search**: Uses ChromaDB for efficient similarity search
- **Multi-document Support**: Maintain knowledge base across multiple PDFs
- **Admin Controls**: Special commands for bot management and monitoring

### Demo
![Bot Demo](imgs/demo.gif) *Add your GIF here showing:*
- *Ask question according Python doc*
- *Call for admin rights*
- *Become admin*
- *Upload a PDF documents*
- *See the list od docs*
- *Rebuild index for a vector search*
- *Ask questions about the content*
- *Receiving accurate answers*
- *Delete admin*

##  Project Structure

```
telegram-rag-bot/
├── api/
│   ├── __init__.py
│   └── bot.py                    # Vercel serverless function handler
├── bot/
│   ├── __init__.py
│   ├── telegram_bot.py           # Main bot initialization
│   ├── admin_handlers.py         # Admin commands and controls
│   ├── user_handlers.py          # User interaction handlers
│   ├── keyboards.py              # Telegram inline keyboards
├── rag/
│   ├── __init__.py
│   ├── config.py                 # RAG configuration (paths, models)
│   ├── build_vectorstore.py      # PDF processing and vector store creation
│   ├── global_rag.py             # File for the import usage
│   └── rag_pipeline.py           # Core RAG logic and query processing
├── data/
│   └── documents/                # Uploaded PDF storage
├── requirements.txt              # Python dependencies
├── runtime.txt                   # Python version
├── vercel.json                   # Vercel deployment configuration
├── set_webhook.py                # Telegram webhook setup utility
└── README.md                    
```

## Quick Start

### Prerequisites
- Python 3.10+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/telegram-rag-bot.git
cd telegram-rag-bot
```

2. **Create virtual environment and install dependencies**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials:
# TG_TOKEN=your_telegram_bot_token
# ADMIN_ID=your_telegram_id
# GEMINI_API_KEY=your_google_gemini_key
```

4. **Run the bot locally**
```bash
python -m bot.telegram_bot
```

### Bot Commands
- `/start` - Welcome message 
- `/admin` - Display all admin features

## Technical Details

### Core Components

#### 1. **Document Processing Pipeline**
- **PDF Extraction**: Uses PyMuPDF for efficient text extraction
- **Text Chunking**: Implements recursive text splitting with overlap
- **Embedding Generation**: Sentence Transformers create vector representations
- **Vector Storage**: ChromaDB for fast similarity search

#### 2. **RAG Architecture**
```
User Query → Embedding → Vector Search → Context Retrieval → Gemini API → Response
```

#### 3. **Memory Requirements**
# **Memory Requirements and Deployment Challenges**

The bot relies on sophisticated ML libraries that require substantial memory during both build and runtime:

| Dependency | Package Size | **Peak Memory During Installation** | Why Essential |
|------------|--------------|-------------------------------------|---------------|
| **sentence-transformers** | 80MB | **2.1GB+** (downloads 420MB model + compiles C++ dependencies) | State-of-the-art text embeddings for semantic search |
| **ChromaDB** | 10MB | **800MB+** (C++ compilation of hnswlib) | High-performance vector database for similarity search |
| **PyMuPDF** | 80MB | **300MB+** (native C extensions) | Handles complex PDF layouts with tables and images |
| **LangChain** | 50MB | **200MB+** (dependency resolution) | Orchestrates the document processing pipeline |

**Package Total**: ~220MB (download size)  
**Peak Build Memory**: ~3.4GB (theoretical maximum during installation)  
**Actual Build Memory**: ~2.5GB (sequential installation)  
**Runtime Memory**: ~1.2GB (with loaded embedding model)

### **Why These Dependencies Cannot Be Simply Removed**

1. **Embedding Quality**: `sentence-transformers` provides contextual embeddings that understand semantic meaning, not just keywords - lightweight alternatives fail at technical documentation
2. **PDF Processing**: `PyMuPDF` extracts text from complex layouts (scientific papers, reports with tables/columns) where simpler libraries like PyPDF lose structure
3. **Vector Search**: `ChromaDB` enables sub-second retrieval across thousands of document chunks - essential for real-time Q&A
4. **Pipeline Integrity**: `LangChain` ensures reliable document processing and retrieval workflows with error handling

### **The Vercel Memory Wall**

Despite Vercel offering 8GB of build memory, deployment consistently fails with Out-Of-Memory (OOM) errors:

**Optimization Attempts (All Implemented):**
1. ✅ **Switched from FAISS to ChromaDB** (reduced from 300MB to 800MB peak, but better performance)
2. ✅ **Implemented adaptive chunk batching** - processes large PDFs in manageable batches
3. ✅ **Used lightweight embedding model** (`paraphrase-MiniLM-L3-v2` - 65MB instead of 420MB)
4. ✅ **Cleared build caches and optimized dependency versions**

**Service Limitations Analysis:**

| Service | Free Tier Build Memory | Peak Required | Runtime Memory | Build Success | Cost for Adequate Plan |
|---------|-----------------------|---------------|----------------|---------------|------------------------|
| **Vercel** | 8GB (shared) | 2.5GB+ | 1.2GB | ❌ **Fails** (OOM during installation) | $20/month (Pro for 16GB builds) |
| **Railway Free** | 512MB | 2.5GB+ | 1.2GB | ❌ **Insufficient** | $10/month (2GB RAM) |
| **Render Free** | 512MB | 2.5GB+ | 1.2GB | ❌ **Insufficient** | $15/month (2GB RAM) |
| **Koyeb Free** | 512MB | 2.5GB+ | 1.2GB | ❌ **Insufficient** | $9-18/month (1-2GB RAM) |

*Note: Free tiers typically provide 512MB-1GB for builds, but our application requires 2.5GB+ peak during installation due to ML dependency compilation and model downloading.*

### Error Evidence

![Vercel Build Error](imgs/error.png) *Screenshot showing:*
```
▲ Build system report
• At least one "Out of Memory" ("OOM") event was detected during the build
• This occurs when processes completely fill up the available memory (8GB)
• Build container terminates with SIGKILL signal
```

