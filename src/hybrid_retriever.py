from src.bm25_retriever import BM25Retriever


class HybridRetriever:

    def __init__(
        self,
        vector_retriever,
        documents
    ):

        self.vector_retriever = vector_retriever

        if documents:

            self.bm25_retriever = BM25Retriever(
                documents
            )

        else:

            self.bm25_retriever = None

    # ======================================================
    # Main Retrieval
    # ======================================================

    def invoke(self, query):

        # --------------------------------------------------
        # 1. Dense Retrieval
        # --------------------------------------------------

        vector_docs = (
            self.vector_retriever.invoke(query)
        )

        # --------------------------------------------------
        # 2. Sparse Retrieval
        # --------------------------------------------------

        if self.bm25_retriever:

            bm25_results = (
                self.bm25_retriever.invoke(query)
            )

        else:

            bm25_results = []

        # --------------------------------------------------
        # 3. Extract BM25 Documents
        # --------------------------------------------------

        bm25_docs = [
            doc
            for doc, score in bm25_results
        ]

        bm25_scores = {
            self._get_doc_id(doc): score
            for doc, score in bm25_results
        }

        # --------------------------------------------------
        # 4. Remove Duplicate Sources
        # --------------------------------------------------

        vector_docs = (
            self._deduplicate_by_source(
                vector_docs
            )
        )

        bm25_docs = (
            self._deduplicate_by_source(
                bm25_docs
            )
        )

        # --------------------------------------------------
        # 5. Debug Vector Results
        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("VECTOR RESULTS")
        print("=" * 60)

        for rank, doc in enumerate(
            vector_docs,
            start=1
        ):

            print(
                f"{rank}. "
                f"{doc.metadata.get('title', 'Unknown')}"
            )

        # --------------------------------------------------
        # 6. Debug BM25 Results
        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("BM25 RESULTS")
        print("=" * 60)

        for rank, doc in enumerate(
            bm25_docs,
            start=1
        ):

            doc_id = self._get_doc_id(doc)

            print(
                f"{rank}. "
                f"{doc.metadata.get('title', 'Unknown')} "
                f"| BM25 Score: "
                f"{bm25_scores.get(doc_id, 0.0):.4f}"
            )

        # --------------------------------------------------
        # 7. Create Source-Level Candidates
        # --------------------------------------------------
        #
        # IMPORTANT:
        # Use SOURCE as the identity.
        #
        # This prevents the same webpage/document from
        # appearing multiple times when vector and BM25
        # return different chunks from the same source.
        # --------------------------------------------------

        documents_by_source = {}

        # Vector documents

        for doc in vector_docs:

            source = self._get_source_id(doc)

            documents_by_source[source] = doc

        # BM25 documents

        for doc in bm25_docs:

            source = self._get_source_id(doc)

            if source not in documents_by_source:

                documents_by_source[source] = doc

        # --------------------------------------------------
        # 8. Reciprocal Rank Fusion
        # --------------------------------------------------

        rrf_scores = {}

        rrf_k = 60

        # --------------------------------------------------
        # 8A. Vector Ranking
        # --------------------------------------------------

        for rank, doc in enumerate(
            vector_docs,
            start=1
        ):

            source = self._get_source_id(doc)

            score = 1.0 / (
                rrf_k + rank
            )

            rrf_scores[source] = (
                rrf_scores.get(
                    source,
                    0.0
                )
                + score
            )

        # --------------------------------------------------
        # 8B. BM25 Ranking
        # --------------------------------------------------

        for rank, doc in enumerate(
            bm25_docs,
            start=1
        ):

            source = self._get_source_id(doc)

            score = 1.0 / (
                rrf_k + rank
            )

            rrf_scores[source] = (
                rrf_scores.get(
                    source,
                    0.0
                )
                + score
            )

        # --------------------------------------------------
        # 9. Title Keyword Boost
        # --------------------------------------------------

        query_terms = set(
            query.lower().split()
        )

        for source, doc in (
            documents_by_source.items()
        ):

            title = doc.metadata.get(
                "title",
                ""
            ).lower()

            # Remove common separators

            title = title.replace(
                ">",
                " "
            )

            title = title.replace(
                "/",
                " "
            )

            title_terms = set(
                title.split()
            )

            matching_terms = (
                query_terms.intersection(
                    title_terms
                )
            )

            if matching_terms:

                title_boost = min(
                    0.05 * len(matching_terms),
                    0.15
                )

            else:

                title_boost = 0.0

            doc.metadata[
                "title_boost"
            ] = round(
                title_boost,
                6
            )

            rrf_scores[source] = (
                rrf_scores.get(
                    source,
                    0.0
                )
                + title_boost
            )

        # --------------------------------------------------
        # 10. Sort Final Scores
        # --------------------------------------------------

        ranked_sources = sorted(
            rrf_scores,
            key=rrf_scores.get,
            reverse=True
        )

        # --------------------------------------------------
        # 11. Top K
        # --------------------------------------------------

        top_k = 4

        final_docs = []

        for source in ranked_sources[:top_k]:

            doc = documents_by_source[
                source
            ]

            doc.metadata[
                "rrf_score"
            ] = round(
                float(
                    rrf_scores[source]
                ),
                6
            )

            final_docs.append(doc)

        # --------------------------------------------------
        # 12. Debug Final Results
        # --------------------------------------------------

        print("\n" + "=" * 60)
        print("HYBRID FINAL RESULTS - RRF")
        print("=" * 60)

        print(
            f"RRF Constant: {rrf_k}"
        )

        for rank, doc in enumerate(
            final_docs,
            start=1
        ):

            print(
                f"{rank}. "
                f"{doc.metadata.get('title', 'Unknown')} "
                f"| Title Boost: "
                f"{doc.metadata.get('title_boost', 0.0):.4f} "
                f"| RRF: "
                f"{doc.metadata.get('rrf_score', 0.0):.6f}"
            )

        print(
            f"\nReturning Top "
            f"{len(final_docs)} "
            f"documents."
        )

        return final_docs

    # ======================================================
    # Remove Duplicate Sources
    # ======================================================

    def _deduplicate_by_source(
        self,
        docs
    ):

        unique_docs = []

        seen_sources = set()

        for doc in docs:

            source = self._get_source_id(
                doc
            )

            if source in seen_sources:

                continue

            seen_sources.add(
                source
            )

            unique_docs.append(
                doc
            )

        return unique_docs

    # ======================================================
    # Get Source ID
    # ======================================================

    def _get_source_id(
        self,
        doc
    ):

        source = doc.metadata.get(
            "source",
            ""
        )

        return source.strip()

    # ======================================================
    # Generate Stable Document ID
    # ======================================================

    def _get_doc_id(
        self,
        doc
    ):

        source = doc.metadata.get(
            "source",
            ""
        )

        content = doc.page_content.strip()

        return (
            source
            + "|"
            + content
        )