from langchain_chroma import Chroma


CHROMA_PATH = "vector_db/chroma"


def create_chroma_db(chunks, embeddings):
    """
    Create and persist a ChromaDB vector store.
    Documents are added in batches to avoid a long single operation.
    """

    print("=" * 80)
    print(f"Creating ChromaDB with {len(chunks)} chunks")
    print("=" * 80)

    batch_size = 100

    vectorstore = None

    for start in range(0, len(chunks), batch_size):

        end = min(start + batch_size, len(chunks))

        batch = chunks[start:end]

        print(
            f"Adding chunks {start + 1}-{end} "
            f"of {len(chunks)}..."
        )

        if vectorstore is None:

            vectorstore = Chroma.from_documents(
                documents=batch,
                embedding=embeddings,
                persist_directory=CHROMA_PATH
            )

        else:

            vectorstore.add_documents(batch)

        print(
            f"✓ Added {len(batch)} chunks"
        )

    print("=" * 80)
    print("ChromaDB Created Successfully.")
    print("=" * 80)

    return vectorstore


def load_chroma_db(embeddings):
    """
    Load an existing ChromaDB vector store.
    """

    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    print("ChromaDB Loaded Successfully.")

    return vectorstore