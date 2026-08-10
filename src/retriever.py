from src.chroma_store import load_chroma_db


def get_retriever(embeddings, k=3):
    """
    Load the ChromaDB vector store and create a retriever.
    """

    vectorstore = load_chroma_db(embeddings)

    retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20
    }

    )

    print("Retriever created successfully.")

    return retriever