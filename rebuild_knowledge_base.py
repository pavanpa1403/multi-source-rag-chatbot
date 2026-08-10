import shutil
from pathlib import Path

from src.loaders import load_documents
from src.web_loader import load_website
from src.cleaner import clean_documents
from src.chunker import chunk_documents
from src.embedding_model import get_embedding_model
from src.chroma_store import create_chroma_db
from src.chunk_storage import save_chunks


# ======================================================
# Configuration
# ======================================================

PDF_FOLDER = "uploads"

WEBSITE_URL = "https://fastapi.tiangolo.com/"

CHROMA_PATH = Path(
    "vector_db/chroma"
)


# ======================================================
# Start
# ======================================================

print("\n" + "=" * 80)
print("REBUILDING MULTI-SOURCE KNOWLEDGE BASE")
print("=" * 80)


# ======================================================
# 1. Load PDF + OCR
# ======================================================

print("\n" + "=" * 80)
print("STEP 1: LOADING PDF DOCUMENTS")
print("=" * 80)

pdf_documents = load_documents(
    PDF_FOLDER
)

print(
    f"PDF documents loaded: "
    f"{len(pdf_documents)}"
)


# ======================================================
# 2. Load FastAPI Website
# ======================================================

print("\n" + "=" * 80)
print("STEP 2: LOADING FASTAPI WEBSITE")
print("=" * 80)

website_documents = load_website(
    WEBSITE_URL
)

print(
    f"Website documents loaded: "
    f"{len(website_documents)}"
)


# ======================================================
# 3. Combine Sources
# ======================================================

print("\n" + "=" * 80)
print("STEP 3: COMBINING SOURCES")
print("=" * 80)

all_documents = (
    pdf_documents
    +
    website_documents
)

print(
    f"Total documents before cleaning: "
    f"{len(all_documents)}"
)


# ======================================================
# 4. Clean Documents
# ======================================================

print("\n" + "=" * 80)
print("STEP 4: CLEANING DOCUMENTS")
print("=" * 80)

cleaned_documents = clean_documents(
    all_documents
)

print(
    f"Cleaned documents: "
    f"{len(cleaned_documents)}"
)


# ======================================================
# 5. Create Chunks
# ======================================================

print("\n" + "=" * 80)
print("STEP 5: CREATING CHUNKS")
print("=" * 80)

chunks = chunk_documents(
    cleaned_documents
)

print(
    f"Total chunks: "
    f"{len(chunks)}"
)


# ======================================================
# 6. Save Chunks
# ======================================================

print("\n" + "=" * 80)
print("STEP 6: SAVING CHUNKS")
print("=" * 80)

save_chunks(
    chunks
)

print("Chunks saved successfully.")


# ======================================================
# 7. Remove Old ChromaDB
# ======================================================

print("\n" + "=" * 80)
print("STEP 7: REMOVING OLD CHROMADB")
print("=" * 80)

if CHROMA_PATH.exists():

    print(
        f"Removing existing ChromaDB: "
        f"{CHROMA_PATH}"
    )

    shutil.rmtree(
        CHROMA_PATH
    )

    print(
        "Old ChromaDB removed."
    )

else:

    print(
        "No existing ChromaDB found."
    )


# ======================================================
# 8. Load Embedding Model
# ======================================================

print("\n" + "=" * 80)
print("STEP 8: LOADING EMBEDDING MODEL")
print("=" * 80)

embeddings = get_embedding_model()

print(
    "Embedding model loaded."
)


# ======================================================
# 9. Create New ChromaDB
# ======================================================

print("\n" + "=" * 80)
print("STEP 9: CREATING NEW CHROMADB")
print("=" * 80)

vectorstore = create_chroma_db(
    chunks,
    embeddings
)


# ======================================================
# Complete
# ======================================================

print("\n" + "=" * 80)
print("KNOWLEDGE BASE REBUILD COMPLETE")
print("=" * 80)

print(
    f"PDF documents: "
    f"{len(pdf_documents)}"
)

print(
    f"Website documents: "
    f"{len(website_documents)}"
)

print(
    f"Combined documents: "
    f"{len(all_documents)}"
)

print(
    f"Total chunks: "
    f"{len(chunks)}"
)

print(
    f"ChromaDB: "
    f"{CHROMA_PATH}"
)

print("=" * 80)
