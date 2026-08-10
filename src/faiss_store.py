from langchain_community.vectorstores import FAISS


def create_faiss_db(chunks, embeddings):
    """
    Create and save a FAISS vector database.
    """

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings
    )

    # Save the FAISS database
    vectorstore.save_local("vector_db/faiss")

    print("FAISS Vector Database Created Successfully.")

    return vectorstore


def load_faiss_db(embeddings):
    """
    Load an existing FAISS vector database.
    """

    vectorstore = FAISS.load_local(
        "vector_db/faiss",
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore