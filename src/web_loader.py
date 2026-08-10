# from langchain_community.document_loaders import WebBaseLoader


# def load_website(url):
#     """
#     Load documents from a website.
#     """

#     loader = WebBaseLoader(url)

#     documents = loader.load()

#     # Add metadata
#     for doc in documents:
#         doc.metadata["type"] = "website"

#     print(f"Loaded {len(documents)} webpage(s).")

#     return documents


from src.web_crawler import crawl_website
from src.html_loader import load_html_page
from src.playwright_loader import load_js_page
from urllib.parse import urlparse


def load_website(url):
    """
    Crawl a website and load content from all discovered pages.
    Automatically chooses the best loader.
    """

    print("=" * 80)
    print("load_website() called")
    print("=" * 80)
    print(f"URL: {url}")

    # urls = crawl_website(
    #     start_url=url,
    #     max_pages=20
    # )

    allowed_paths = []

# FastAPI
    if "fastapi.tiangolo.com" in url:
        allowed_paths = [
            "/tutorial",
            "/advanced",
            "/deployment",
            "/reference"
            ]

# Python Docs
    elif "docs.python.org" in url:
        allowed_paths = [
            "/3/tutorial",
            "/3/library",
            "/3/reference"
            ]

# LangChain
    elif "langchain.com" in url:
        allowed_paths = [
            "/docs",
            "/oss/python"
            ]

    urls = crawl_website(
        start_url=url,
        max_pages=100,
        allowed_paths=allowed_paths
        )

    print(f"\nFound {len(urls)} page(s).\n")

    all_documents = []

    # Websites that require JavaScript rendering
    js_sites = [
        "langchain.com",
        "vercel.com",
        "nextjs.org",
        "react.dev"
    ]

    for i, page_url in enumerate(urls, start=1):

        try:

            print(f"[{i}/{len(urls)}] Loading: {page_url}")

            # Decide which loader to use
            if any(site in page_url for site in js_sites):
                document = load_js_page(page_url)
            else:
                document = load_html_page(page_url)

            text = document.page_content

            # Remove blank lines
            text = "\n".join(
                line.strip()
                for line in text.splitlines()
                if line.strip()
            )

            # Remove duplicate consecutive lines
            cleaned_lines = []
            seen = set()

            for line in text.splitlines():

                if line not in seen:
                    cleaned_lines.append(line)
                    seen.add(line)

            document.page_content = "\n".join(cleaned_lines)

            # document.metadata["type"] = "website"
            # document.metadata["source"] = page_url
            

            parsed = urlparse(page_url)

            path = parsed.path.strip("/")
            if path == "":
                 title = "Home"
            else:
                 title = (
                      path.replace("-", " ")
                      .replace("/", " > ")
                      .title()
                      )

            document.metadata = {
            "source": page_url,
            "title": title,
            "domain": parsed.netloc,
            "path": parsed.path,
            "type": "website"
            }

            print("Metadata:", document.metadata)

            all_documents.append(document)

            print(f"✓ Loaded ({len(document.page_content)} characters)")

        except Exception as e:

            print(f"✗ Failed: {page_url}")
            print(e)

    print("\n" + "=" * 60)
    print(f"Total Website Documents Loaded: {len(all_documents)}")
    print("=" * 60)

    return all_documents