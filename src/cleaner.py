import re


def clean_documents(documents):
    """
    Clean PDF and webpage content while preserving
    document-specific information.

    PDF content is preserved without website-specific
    boilerplate removal.
    """

    cleaned_docs = []

    # Website-only boilerplate
    website_boilerplate = [
        "Skip to main content",
        "Documentation Index",
        "Create an agent",
        "Privacy",
        "Terms",
        "GitHub",
    ]

    for i, doc in enumerate(
        documents,
        start=1
    ):

        text = (
            doc.page_content or ""
        )

        source_type = doc.metadata.get(
            "type",
            doc.metadata.get(
                "source_type",
                ""
            )
        )

        # ==================================================
        # Website Cleaning
        # ==================================================

        if source_type == "website":

            for item in website_boilerplate:

                text = text.replace(
                    item,
                    ""
                )

        # ==================================================
        # Normalize Whitespace
        # ==================================================

        text = re.sub(
            r"\n{2,}",
            "\n",
            text
        )

        text = re.sub(
            r"[ \t]{2,}",
            " ",
            text
        )

        text = text.strip()

        # ==================================================
        # Skip Very Small Documents
        # ==================================================

        if len(text) < 300:

            print(
                f"Skipped Small Document: "
                f"{doc.metadata.get('source')}"
            )

            continue

        # ==================================================
        # Preserve Document
        # ==================================================

        doc.page_content = text

        cleaned_docs.append(
            doc
        )

        # ==================================================
        # Debug
        # ==================================================

        print(
            "=" * 80
        )

        print(
            f"Document {i}"
        )

        print(
            "Source :",
            doc.metadata.get(
                "source"
            )
        )

        print(
            "Title  :",
            doc.metadata.get(
                "title",
                "Unknown"
            )
        )

        print(
            "Type   :",
            source_type
        )

        print(
            "OCR    :",
            doc.metadata.get(
                "ocr",
                False
            )
        )

        print(
            "Length :",
            len(text)
        )

        print(
            text[:300]
        )

        print(
            "=" * 80
        )

    print(
        f"\nCleaned Documents: "
        f"{len(cleaned_docs)}"
    )

    return cleaned_docs