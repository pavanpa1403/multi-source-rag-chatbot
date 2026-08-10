import sys
import os

# ============================================================
# Add project root to Python path
# ============================================================

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)


# ============================================================
# Imports
# ============================================================

from src.test_questions import test_questions

from src.embedding_model import get_embedding_model
from src.chroma_store import load_chroma_db
from src.hybrid_retriever import HybridRetriever
from src.chunk_storage import load_chunks
from src.llm import get_llm
from src.prompt import get_prompt


# ============================================================
# STEP 1: Load Embedding Model
# ============================================================

print("=" * 80)
print("STEP 1: LOADING EMBEDDING MODEL")
print("=" * 80)

embeddings = get_embedding_model()

print("✅ Embedding model loaded")


# ============================================================
# STEP 2: Load ChromaDB
# ============================================================

print("\n" + "=" * 80)
print("STEP 2: LOADING CHROMADB")
print("=" * 80)

vectorstore = load_chroma_db(
    embeddings
)

print("✅ ChromaDB loaded")


# ============================================================
# STEP 3: Create Vector Retriever
# ============================================================

print("\n" + "=" * 80)
print("STEP 3: CREATING VECTOR RETRIEVER")
print("=" * 80)

vector_retriever = vectorstore.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 5,
        "fetch_k": 20
    }
)

print("✅ Vector retriever created")


# ============================================================
# STEP 4: Load Saved Chunks
# ============================================================

print("\n" + "=" * 80)
print("STEP 4: LOADING SAVED CHUNKS")
print("=" * 80)

documents = load_chunks()

print(
    f"✅ Loaded {len(documents)} chunks"
)


# ============================================================
# STEP 5: Create Hybrid Retriever
# ============================================================

print("\n" + "=" * 80)
print("STEP 5: CREATING HYBRID RETRIEVER")
print("=" * 80)

hybrid_retriever = HybridRetriever(
    vector_retriever,
    documents
)

print("✅ Hybrid retriever created")


# ============================================================
# STEP 6: Load LLM
# ============================================================

print("\n" + "=" * 80)
print("STEP 6: LOADING LLM")
print("=" * 80)

llm = get_llm()

print("✅ LLM loaded")


# ============================================================
# STEP 7: Load Prompt
# ============================================================

print("\n" + "=" * 80)
print("STEP 7: LOADING PROMPT")
print("=" * 80)

prompt = get_prompt()

print("✅ Prompt loaded")


# ============================================================
# STEP 8: Evaluation
# ============================================================

print("\n" + "=" * 80)
print("STEP 8: STARTING ANSWER EVALUATION")
print("=" * 80)


total_questions = len(test_questions)

retrieval_passed = 0
answer_passed = 0


# ============================================================
# Evaluate Each Question
# ============================================================

for i, item in enumerate(
    test_questions,
    start=1
):

    question = item["question"]

    expected_source = item[
        "expected_source"
    ]

    expected_keywords = item[
        "expected_answer_keywords"
    ]


    print("\n" + "=" * 80)
    print(
        f"QUESTION {i}/{total_questions}"
    )
    print("=" * 80)

    print(
        f"Question: {question}"
    )

    print(
        f"Expected Source: "
        f"{expected_source}"
    )


    # ========================================================
    # 1. Hybrid Retrieval
    # ========================================================

    results = hybrid_retriever.invoke(
        question
    )


    # ========================================================
    # 2. Check Retrieval
    # ========================================================

    retrieved_sources = []

    for doc in results:

        title = doc.metadata.get(
            "title",
            ""
        )

        retrieved_sources.append(
            title
        )


    retrieval_found = any(
        expected_source.lower()
        in source.lower()
        for source in retrieved_sources
    )


    if retrieval_found:

        retrieval_passed += 1

        print(
            "\n✅ RETRIEVAL: PASS"
        )

    else:

        print(
            "\n❌ RETRIEVAL: FAIL"
        )


    print(
        "\nRetrieved Sources:"
    )

    for rank, source in enumerate(
        retrieved_sources,
        start=1
    ):

        print(
            f"{rank}. {source}"
        )


    # ========================================================
    # 3. Build Context
    # ========================================================

    MAX_CONTEXT_DOCS = 3

    context_docs = results[
        :MAX_CONTEXT_DOCS
    ]


    # Remove duplicate content

    unique_docs = []

    seen = set()


    for doc in context_docs:

        text = doc.page_content.strip()

        if text in seen:

            continue

        unique_docs.append(doc)

        seen.add(text)


    # ========================================================
    # 4. Build Optimized Context
    # ========================================================

    context_parts = []


    for index, doc in enumerate(
        unique_docs,
        start=1
    ):

        title = doc.metadata.get(
            "title",
            "Unknown"
        )

        source = doc.metadata.get(
            "source",
            ""
        )

        text = doc.page_content.strip()


        context_parts.append(
            f"""
Document {index}

Title:
{title}

Source:
{source}

Content:
{text}
"""
        )


    context = "\n\n".join(
        context_parts
    )


    # ========================================================
    # 5. Create Prompt
    # ========================================================

    formatted_prompt = prompt.invoke(
        {
            "history": [],
            "context": context,
            "question": question
        }
    )


    # ========================================================
    # 6. Generate Answer
    # ========================================================

    print(
        "\nGenerating answer..."
    )

    response = llm.invoke(
        formatted_prompt
    )


    answer = response.content.strip()


    # ========================================================
    # 7. Display Answer
    # ========================================================

    print("\n" + "-" * 80)
    print("GENERATED ANSWER")
    print("-" * 80)

    print(answer)


    # ========================================================
    # 8. Check Answer Keywords
    # ========================================================

    answer_lower = answer.lower()


    matched_keywords = []

    missing_keywords = []


    for keyword in expected_keywords:

        if keyword.lower() in answer_lower:

            matched_keywords.append(
                keyword
            )

        else:

            missing_keywords.append(
                keyword
            )


    # ========================================================
    # 9. Calculate Answer Score
    # ========================================================

    keyword_score = (
        len(matched_keywords)
        / len(expected_keywords)
    )


    # We consider the answer passing
    # when at least 70% of expected
    # concepts are present.

    if keyword_score >= 0.70:

        answer_passed += 1

        print(
            "\n✅ ANSWER QUALITY: PASS"
        )

    else:

        print(
            "\n❌ ANSWER QUALITY: FAIL"
        )


    print(
        f"Keyword Score: "
        f"{keyword_score * 100:.2f}%"
    )


    print(
        f"Matched Keywords: "
        f"{matched_keywords}"
    )


    print(
        f"Missing Keywords: "
        f"{missing_keywords}"
    )


# ============================================================
# STEP 9: Final Evaluation
# ============================================================

retrieval_accuracy = (
    retrieval_passed
    / total_questions
) * 100


answer_accuracy = (
    answer_passed
    / total_questions
) * 100


print("\n" + "=" * 80)
print("FINAL RAG EVALUATION")
print("=" * 80)


print(
    f"Total Questions: "
    f"{total_questions}"
)


print(
    f"Retrieval Passed: "
    f"{retrieval_passed}"
)


print(
    f"Retrieval Failed: "
    f"{total_questions - retrieval_passed}"
)


print(
    f"Retrieval Accuracy: "
    f"{retrieval_accuracy:.2f}%"
)


print(
    f"\nAnswer Quality Passed: "
    f"{answer_passed}"
)


print(
    f"Answer Quality Failed: "
    f"{total_questions - answer_passed}"
)


print(
    f"Answer Quality Accuracy: "
    f"{answer_accuracy:.2f}%"
)


print("=" * 80)