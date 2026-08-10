from src.embedding_model import get_embedding_model
from src.chroma_store import load_chroma_db
from src.prompt import get_prompt
from src.llm import get_llm
from src.question_rewriter import get_question_rewriter
from src.hybrid_retriever import HybridRetriever
from src.chunk_storage import load_chunks


class ChromaScoreRetriever:

    def __init__(
        self,
        vectorstore,
        k=5
    ):

        self.vectorstore = vectorstore
        self.k = k

    def invoke(
        self,
        query
    ):

        results = (
            self.vectorstore
            .similarity_search_with_relevance_scores(
                query,
                k=self.k
            )
        )

        documents = []

        for doc, score in results:

            doc.metadata["vector_score"] = float(
                score
            )

            documents.append(
                doc
            )

        return documents


class RAGPipeline:

    def __init__(self):

        # --------------------------------------------------
        # 1. Embedding Model
        # --------------------------------------------------

        self.embeddings = get_embedding_model()

        # --------------------------------------------------
        # 2. ChromaDB
        # --------------------------------------------------

        self.vectorstore = load_chroma_db(
            self.embeddings
        )

        # --------------------------------------------------
        # 3. Vector Retriever
        # --------------------------------------------------

        self.vector_retriever = ChromaScoreRetriever(
            self.vectorstore,
            k=5
        )

        # --------------------------------------------------
        # 4. Load Saved Chunks
        # --------------------------------------------------

        self.chunks = load_chunks()

        # --------------------------------------------------
        # 5. Hybrid Retriever
        # --------------------------------------------------

        self.hybrid_retriever = HybridRetriever(
            self.vector_retriever,
            self.chunks
        )

        # --------------------------------------------------
        # 6. LLM
        # --------------------------------------------------

        self.llm = get_llm()

        # --------------------------------------------------
        # 7. Prompt
        # --------------------------------------------------

        self.prompt = get_prompt()

        # --------------------------------------------------
        # 8. Question Rewriter
        # --------------------------------------------------

        self.question_rewriter = (
            get_question_rewriter(
                self.llm
            )
        )

    # ======================================================
    # Build Context
    # ======================================================

    def _build_context(
        self,
        documents,
        max_documents=3
    ):

        context_docs = documents[
            :max_documents
        ]

        unique_docs = []

        seen = set()

        for doc in context_docs:

            text = doc.page_content.strip()

            if text in seen:

                continue

            unique_docs.append(
                doc
            )

            seen.add(
                text
            )

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

        return context, unique_docs

   # ======================================================
    # Rewrite Question
    # ======================================================

    def _rewrite_question(
        self,
        question,
        history
    ):

        # --------------------------------------------------
        # No history
        # --------------------------------------------------

        if not history:

            return question.strip()

        # --------------------------------------------------
        # Build History Text
        # --------------------------------------------------

        history_text = []

        for message in history:

            # LangChain message
            if hasattr(
                message,
                "type"
            ):

                message_type = message.type
                message_content = message.content

                history_text.append(
                    f"{message_type}: "
                    f"{message_content}"
                )

            # Dictionary message
            elif isinstance(
                message,
                dict
            ):

                role = message.get(
                    "role",
                    ""
                )

                content = message.get(
                    "content",
                    ""
                )

                history_text.append(
                    f"{role}: {content}"
                )

        history_text = "\n".join(
            history_text
        )

        # --------------------------------------------------
        # Rewrite Question
        # --------------------------------------------------

        rewritten_question = (
            self.question_rewriter.invoke(
                {
                    "history": history_text,
                    "question": question
                }
            )
        )

        rewritten_question = (
            rewritten_question.content
            .strip()
        )

        # --------------------------------------------------
        # Safety Fallback
        # --------------------------------------------------

        if not rewritten_question:

            rewritten_question = (
                question.strip()
            )

        return rewritten_question


    # ======================================================
    # Ask Question
    # ======================================================

    def ask(
        self,
        question,
        history=None
    ):

        # --------------------------------------------------
        # Validate Question
        # --------------------------------------------------

        if not question:

            return {
                "question": "",
                "rewritten_question": "",
                "answer": (
                    "I couldn't find the answer "
                    "in the provided documents."
                ),
                "sources": [],
                "documents": [],
                "context": ""
            }

        question = question.strip()

        # --------------------------------------------------
        # Initialize History
        # --------------------------------------------------

        if history is None:

            history = []

        # --------------------------------------------------
        # 1. Rewrite Question
        # --------------------------------------------------

        rewritten_question = (
            self._rewrite_question(
                question,
                history
            )
        )


        # --------------------------------------------------
        # 2. Hybrid Retrieval
        # --------------------------------------------------


        results = (
            self.hybrid_retriever.invoke(
                rewritten_question
            )
        )

        # --------------------------------------------------
        # 3. Build Optimized Context
        # --------------------------------------------------

        context, context_documents = (
            self._build_context(
                results,
                max_documents=3
            )
        )


        # --------------------------------------------------
        # 4. Create RAG Prompt
        # --------------------------------------------------

        formatted_prompt = (
            self.prompt.invoke(
                {
                    "history": history,
                    "context": context,
                    "question": rewritten_question
                }
            )
        )

        # --------------------------------------------------
        # 5. Generate Answer
        # --------------------------------------------------


        response = self.llm.invoke(
            formatted_prompt
        )

        answer = (
            response.content
            .strip()
        )

        # --------------------------------------------------
        # 6. Extract Sources
        # --------------------------------------------------

        sources = []

        seen_sources = set()

        for doc in context_documents:

            title = doc.metadata.get(
                "title",
                "Unknown"
            )

            source = doc.metadata.get(
                "source",
                ""
            )

            key = (
                title,
                source
            )

            if key in seen_sources:

                continue

            sources.append(
                {
                    "title": title,
                    "source": source
                }
            )

            seen_sources.add(
                key
            )

        # --------------------------------------------------
        # 7. Return Complete RAG Result
        # --------------------------------------------------

        return {
            "question": question,

            "rewritten_question": (
                rewritten_question
            ),

            "answer": answer,

            "sources": sources,

            "documents": context_documents,

            "context": context
        }