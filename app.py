import streamlit as st
import re
from src.rag_pipeline import RAGPipeline
from src.embedding_model import get_embedding_model
from src.chroma_store import load_chroma_db
from src.prompt import get_prompt
from src.llm import get_llm
from src.chat_history import chat_history
from src.source_formatter import format_sources
from src.pdf_uploader import save_uploaded_files
from src.loaders import load_documents
from src.cleaner import clean_documents
from src.chunker import chunk_documents
from src.chroma_store import create_chroma_db
from src.web_loader import load_website
# from src.history_aware_retriever import get_history_aware_retriever

from src.hybrid_retriever import HybridRetriever   
from src.chunk_storage import save_chunks
from src.chunk_storage import load_chunks
# ----------------------------------
# Page Configuration
# ----------------------------------
st.set_page_config(
    page_title="Multi-Source RAG Chatbot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Multi-Source RAG Chatbot")


# ----------------------------------
# Session State
# ----------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# ----------------------------------
# Load Resources
# ----------------------------------

@st.cache_resource
def load_resources():

    # ----------------------------------
    # Step 1: Load Embedding Model
    # ----------------------------------

    print("=" * 60)
    print("Step 1: Loading embedding model...")
    print("=" * 60)

    embeddings = get_embedding_model()

    print("✅ Embedding model loaded")

    # ----------------------------------
    # Step 2: Load ChromaDB
    # ----------------------------------

    print("\n" + "=" * 60)
    print("Step 2: Loading ChromaDB...")
    print("=" * 60)

    vectorstore = load_chroma_db(embeddings)

    print("✅ ChromaDB loaded")

    # ----------------------------------
    # Step 3: Create Score-Aware Retriever
    # ----------------------------------

    print("\n" + "=" * 60)
    print("Step 3: Creating vector retriever...")
    print("=" * 60)

    class ChromaScoreRetriever:

        def __init__(self, vectorstore, k=5):

            self.vectorstore = vectorstore
            self.k = k

        def invoke(self, query):

            results = (
                self.vectorstore
                .similarity_search_with_relevance_scores(
                    query,
                    k=self.k
                )
            )

            documents = []

            print("\n" + "=" * 60)
            print("VECTOR SIMILARITY SCORES")
            print("=" * 60)

            for doc, score in results:

                # Save actual Chroma relevance score
                doc.metadata["vector_score"] = float(score)

                documents.append(doc)

                print(
                    f"Score: {score:.4f} | "
                    f"Title: "
                    f"{doc.metadata.get('title', 'Unknown')}"
                )

            return documents

    vector_retriever = ChromaScoreRetriever(
        vectorstore,
        k=5
    )

    print("✅ Vector retriever created")

    # ----------------------------------
    # Step 4: Load Saved Chunks
    # ----------------------------------

    print("\n" + "=" * 60)
    print("Step 4: Loading saved chunks...")
    print("=" * 60)

    chunks = load_chunks()

    if chunks:

        print(f"Loaded {len(chunks)} chunks.")

    else:

        print("⚠️ No Knowledge Base Found.")

    # ----------------------------------
    # Step 5: Create Hybrid Retriever
    # ----------------------------------

    print("\n" + "=" * 60)
    print("Step 5: Creating hybrid retriever...")
    print("=" * 60)

    hybrid_retriever = HybridRetriever(
        vector_retriever,
        chunks
    )

    print("✅ Hybrid retriever created")

    # ----------------------------------
    # Step 6: Load LLM
    # ----------------------------------

    print("\n" + "=" * 60)
    print("Step 6: Loading LLM...")
    print("=" * 60)

    llm = get_llm()

    print("✅ LLM loaded")

    # ----------------------------------
    # Step 7: Load Prompt
    # ----------------------------------

    print("\n" + "=" * 60)
    print("Step 7: Loading prompt...")
    print("=" * 60)

    prompt = get_prompt()

    print("✅ Prompt loaded")

    # ----------------------------------
    # Return Resources
    # ----------------------------------

    print("\n" + "=" * 60)
    print("ALL RESOURCES LOADED SUCCESSFULLY")
    print("=" * 60)

    return (
        vectorstore,
        hybrid_retriever,
        llm,
        prompt
    )


# ----------------------------------
# Initialize Resources
# ----------------------------------

# vectorstore, hybrid_retriever, llm, prompt = load_resources()

# question_rewriter = get_question_rewriter(llm)

# ----------------------------------
# Initialize RAG Pipeline
# ----------------------------------

print("\n" + "=" * 60)
print("Initializing RAG Pipeline...")
print("=" * 60)

rag_pipeline = RAGPipeline()

print("RAG Pipeline initialized successfully")
# history_retriever = get_history_aware_retriever(
#     llm,
#     retriever
# )


# ----------------------------------
# Display Previous Chat
# ----------------------------------
for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# ----------------------------------
# Chat Input
# ----------------------------------
question = st.chat_input("Ask something ...")


# ----------------------------------
# Process User Question
# ----------------------------------

if question:

    # -------------------------------
    # Show User Message
    # -------------------------------

    with st.chat_message("user"):
        st.write(question)


    # -------------------------------
    # Run RAG Pipeline
    # -------------------------------

    with st.spinner(
        "Thinking..."
    ):

        result = rag_pipeline.ask(
            question,
            chat_history.messages
        )


    # -------------------------------
    # Extract RAG Result
    # -------------------------------

    answer = result["answer"]

    rewritten_question = (
        result["rewritten_question"]
    )

    results = result["documents"]

    unique_docs = result["documents"]

    context = result["context"]

    sources = result["sources"]


    # -------------------------------
    # Debug RAG Result
    # -------------------------------

    print("\n" + "=" * 80)
    print("RAG PIPELINE RESULT")
    print("=" * 80)

    print(
        f"Original Question: "
        f"{question}"
    )

    print(
        f"Rewritten Question: "
        f"{rewritten_question}"
    )

    print(
        f"Documents Used: "
        f"{len(unique_docs)}"
    )

    print(
        f"Context Length: "
        f"{len(context)} characters"
    )

    print("=" * 80)


    # -------------------------------
    # Save Chat History
    # -------------------------------

    chat_history.add_user_message(
        question
    )

    chat_history.add_ai_message(
        answer
    )



    # -------------------------------
    # Save Streamlit History
    # -------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # -------------------------------
    # Display Answer
    # -------------------------------

    with st.chat_message(
        "assistant"
    ):

        st.write(answer)


        with st.expander(
            "📚 Sources"
        ):

            sources = format_sources(
                results
            )


            for source, page in sources:

                if page is not None:

                    st.write(
                        f"📄 {source} "
                        f"(Page {page + 1})"
                    )

                else:

                    st.write(
                        f"📄 {source}"
                    )                


# ----------------------------------
# Sidebar
# ----------------------------------

st.sidebar.title("⚙️ Options")


# -------------------------------
# Upload PDFs
# -------------------------------

st.sidebar.header("📂 Upload PDFs")

uploaded_files = st.sidebar.file_uploader(
    "Choose PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    saved_files = save_uploaded_files(
        uploaded_files
    )

    st.sidebar.success(
        f"{len(saved_files)} PDF(s) uploaded successfully!"
    )


# -------------------------------
# Website
# -------------------------------

st.sidebar.header("🌐 Website")

website_url = st.sidebar.text_input(
    "Enter Website URL",
    placeholder="https://example.com"
)


# -------------------------------
# Build Knowledge Base
# -------------------------------

if st.sidebar.button(
    "📚 Build Knowledge Base"
):

    with st.spinner(
        "Building Knowledge Base..."
    ):

        all_documents = []

        # ----------------------------------
        # Load PDFs
        # ----------------------------------

        pdf_documents = load_documents(
            "uploads"
        )

        if pdf_documents:

            all_documents.extend(
                pdf_documents
            )


        # ----------------------------------
        # Load Website
        # ----------------------------------

        if website_url.strip():

            if website_url.lower().startswith(
                ("http://", "https://")
            ):

                try:

                    print(
                        "=" * 80
                    )

                    print(
                        "Calling load_website()"
                    )

                    print(
                        "=" * 80
                    )

                    website_documents = (
                        load_website(
                            website_url
                        )
                    )

                    all_documents.extend(
                        website_documents
                    )

                except Exception as e:

                    st.sidebar.error(
                        f"Unable to load website.\n\n"
                        f"Error: {e}"
                    )

            else:

                st.sidebar.error(
                    "Please enter a valid website URL."
                )


        # ----------------------------------
        # Check Documents
        # ----------------------------------

        if not all_documents:

            st.sidebar.warning(
                "Upload a PDF or enter a website URL first."
            )

            st.stop()


        # ----------------------------------
        # Clean Documents
        # ----------------------------------

        cleaned_documents = (
            clean_documents(
                all_documents
            )
        )


        # ----------------------------------
        # Create Chunks
        # ----------------------------------

        chunks = chunk_documents(
            cleaned_documents
        )


        # ----------------------------------
        # Save Chunks
        # ----------------------------------

        save_chunks(
            chunks
        )


        # ----------------------------------
        # Load Embedding Model
        # ----------------------------------

        import time

        print(
            "=" * 80
        )

        print(
            "STARTING EMBEDDING MODEL"
        )

        print(
            "=" * 80
        )

        start = time.time()

        embeddings = get_embedding_model()

        print(
            f"Embedding model loaded in "
            f"{time.time() - start:.2f} seconds"
        )


        # ----------------------------------
        # Create ChromaDB
        # ----------------------------------

        print(
            "=" * 80
        )

        print(
            "STARTING CHROMADB CREATION"
        )

        print(
            "=" * 80
        )

        start = time.time()

        create_chroma_db(
            chunks,
            embeddings
        )

        print(
            f"ChromaDB creation took "
            f"{time.time() - start:.2f} seconds"
        )


        # ----------------------------------
        # Knowledge Base Complete
        # ----------------------------------

        print(
            "=" * 80
        )

        print(
            "KNOWLEDGE BASE CREATION COMPLETE"
        )

        print(
            "=" * 80
        )


        # ----------------------------------
        # Clear Cached Resources
        # ----------------------------------

        load_resources.clear()


    st.sidebar.success(
        "✅ Knowledge Base Ready!"
    )

    st.rerun()


# -------------------------------
# Clear Chat
# -------------------------------

if st.sidebar.button(
    "🗑️ Clear Chat"
):

    st.session_state.messages = []

    chat_history.clear()

    st.rerun()