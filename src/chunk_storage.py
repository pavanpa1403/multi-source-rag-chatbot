import os
import pickle


CHUNK_FILE = "vector_db/chunks.pkl"


def save_chunks(chunks):
    """
    Save document chunks to disk.
    """

    os.makedirs("vector_db", exist_ok=True)

    with open(CHUNK_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print(f"Saved {len(chunks)} chunks.")


def load_chunks():
    """
    Load document chunks from disk.
    """

    if not os.path.exists(CHUNK_FILE):
        print("No saved chunks found.")
        return []

    with open(CHUNK_FILE, "rb") as f:
        chunks = pickle.load(f)

    print(f"Loaded {len(chunks)} chunks.")

    return chunks