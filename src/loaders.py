from pathlib import Path

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader
)

from pdf2image import convert_from_path
import pytesseract


# ======================================================
# Configuration
# ======================================================

MIN_TEXT_LENGTH = 50
OCR_DPI = 200


# ======================================================
# Load PDF Documents
# ======================================================

def load_documents(
    folder_path="uploads"
):

    folder = Path(folder_path)

    print("\n" + "=" * 80)
    print("LOADING PDF DOCUMENTS")
    print("=" * 80)

    print(
        f"Folder: {folder.resolve()}"
    )

    # --------------------------------------------------
    # Check folder
    # --------------------------------------------------

    if not folder.exists():

        print(
            f"Folder does not exist: "
            f"{folder.resolve()}"
        )

        return []

    # --------------------------------------------------
    # Find PDF files
    # --------------------------------------------------

    pdf_files = list(
        folder.glob("*.pdf")
    )

    print(
        f"PDF files found: "
        f"{len(pdf_files)}"
    )

    for pdf_file in pdf_files:

        print(
            f" - {pdf_file.name}"
        )

    if not pdf_files:

        print(
            "No PDF files found."
        )

        return []

    all_documents = []

    # ==================================================
    # Process Each PDF
    # ==================================================

    for pdf_file in pdf_files:

        print("\n" + "-" * 80)

        print(
            f"Processing PDF: "
            f"{pdf_file.name}"
        )

        print("-" * 80)

        # --------------------------------------------------
        # First attempt: normal PDF text extraction
        # --------------------------------------------------

        try:

            loader = PyPDFLoader(
                str(pdf_file)
            )

            pdf_documents = loader.load()

        except Exception as e:

            print(
                f"Normal PDF loading failed: {e}"
            )

            pdf_documents = []

        # --------------------------------------------------
        # Check each page
        # --------------------------------------------------

        for page_number, doc in enumerate(
            pdf_documents,
            start=1
        ):

            text = (
                doc.page_content or ""
            ).strip()

            # ----------------------------------------------
            # Page has sufficient text
            # ----------------------------------------------

            if len(text) >= MIN_TEXT_LENGTH:

                print(
                    f"Page {page_number}: "
                    f"Using extracted text "
                    f"({len(text)} characters)"
                )

                doc.metadata["source_type"] = "pdf"

                doc.metadata["ocr"] = False

                doc.metadata["file_name"] = (
                    pdf_file.name
                )

                all_documents.append(
                    doc
                )

                continue

            # ----------------------------------------------
            # Page has little/no text
            # → OCR required
            # ----------------------------------------------

            print(
                f"Page {page_number}: "
                f"Insufficient text "
                f"({len(text)} characters) "
                f"→ OCR"
            )

        # ==================================================
        # OCR Entire PDF
        # ==================================================

        try:

            print(
                f"\nStarting OCR for: "
                f"{pdf_file.name}"
            )

            images = convert_from_path(
                str(pdf_file),
                dpi=OCR_DPI
            )

            print(
                f"OCR pages available: "
                f"{len(images)}"
            )

            # --------------------------------------------------
            # Process OCR pages
            # --------------------------------------------------

            for page_index, image in enumerate(
                images,
                start=1
            ):

                # ----------------------------------------------
                # Check whether this page already has good text
                # ----------------------------------------------

                existing_text = ""

                if page_index <= len(
                    pdf_documents
                ):

                    existing_text = (
                        pdf_documents[
                            page_index - 1
                        ].page_content or ""
                    ).strip()

                if len(existing_text) >= MIN_TEXT_LENGTH:

                    continue

                # ----------------------------------------------
                # OCR
                # ----------------------------------------------

                print(
                    f"OCR processing page "
                    f"{page_index}..."
                )

                try:

                    ocr_text = pytesseract.image_to_string(
                        image,
                        config="--psm 6"
                    )

                except Exception as e:

                    print(
                        f"OCR failed on page "
                        f"{page_index}: {e}"
                    )

                    continue

                ocr_text = (
                    ocr_text.strip()
                )

                # ----------------------------------------------
                # Save OCR result
                # ----------------------------------------------

                if ocr_text:

                    print(
                        f"Page {page_index}: "
                        f"OCR extracted "
                        f"{len(ocr_text)} characters"
                    )

                    ocr_document = Document(
                        page_content=ocr_text,
                        metadata={
                            "source": str(
                                pdf_file
                            ),
                            "file_name": (
                                pdf_file.name
                            ),
                            "page": (
                                page_index - 1
                            ),
                            "page_number": (
                                page_index
                            ),
                            "source_type": "pdf",
                            "ocr": True
                        }
                    )

                    all_documents.append(
                        ocr_document
                    )

                else:

                    print(
                        f"Page {page_index}: "
                        f"OCR returned no text"
                    )

        except Exception as e:

            print(
                "\nOCR processing failed:"
            )

            print(e)

    # ==================================================
    # Final Result
    # ==================================================

    print("\n" + "=" * 80)

    print(
        f"TOTAL DOCUMENT PAGES LOADED: "
        f"{len(all_documents)}"
    )

    print("=" * 80)

    return all_documents