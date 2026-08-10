import os


# ======================================================
# Upload Directory
# ======================================================

UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# ======================================================
# Save Uploaded PDF Files
# ======================================================

def save_uploaded_files(
    uploaded_files
):

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )

    saved_files = []

    for uploaded_file in uploaded_files:

        file_path = os.path.join(
            UPLOAD_DIR,
            uploaded_file.name
        )

        with open(
            file_path,
            "wb"
        ) as f:

            f.write(
                uploaded_file.getbuffer()
            )

        saved_files.append(
            file_path
        )

        print(
            f"PDF saved: {file_path}"
        )

    print(
        f"Total PDF files saved: "
        f"{len(saved_files)}"
    )

    return saved_files