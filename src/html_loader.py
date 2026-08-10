import requests
from bs4 import BeautifulSoup
from langchain_core.documents import Document


def load_html_page(url):
    """
    Download a webpage and extract readable text.
    """

    headers = {
        "User-Agent": "Mozilla/5.0 (RAG Chatbot)"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    # Remove unwanted tags
    for tag in soup([
        "script",
        "style",
        "noscript",
        "header",
        "footer",
        "nav",
        "svg"
    ]):
        tag.decompose()

    # Prefer the main content if available
    main = soup.find("main")

    if main:
        text = main.get_text("\n", strip=True)
    else:
        text = soup.get_text("\n", strip=True)

    return Document(
        page_content=text,
        metadata={
            "source": url,
            "type": "website"
        }
    )