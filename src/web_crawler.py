import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


def crawl_website(start_url, max_pages=100,allowed_paths=None):
    """
    Generic website crawler.
    Crawls only useful internal documentation pages.
    """

    visited = set()
    queue = [start_url]

    domain = urlparse(start_url).netloc
    if allowed_paths is None:
        allowed_paths = []

    # Skip file types
    skip_extensions = (
        ".pdf",
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".svg",
        ".ico",
        ".zip",
        ".tar",
        ".gz",
        ".css",
        ".js",
        ".xml",
        ".json",
        ".rss",
    )

    # Skip unwanted keywords
    skip_keywords = [
        "login",
        "logout",
        "signup",
        "register",
        "privacy",
        "terms",
        "license",
        "github",
        "twitter",
        "linkedin",
        "facebook",
        "youtube",
        "mailto:",
        "llms.txt" 
    ]

    # Skip translated pages
    language_prefixes = [
        "/de",
        "/es",
        "/fr",
        "/hi",
        "/ja",
        "/ko",
        "/pt",
        "/ru",
        "/tr",
        "/uk",
        "/zh",
        "/zh-hant",
    ]

    while queue and len(visited) < max_pages:

        url = queue.pop(0)

        if url in visited:
            continue

        try:

            response = requests.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (RAG Chatbot)"
                },
                timeout=10
            )

            if response.status_code != 200:
                continue

            visited.add(url)

            soup = BeautifulSoup(response.text, "html.parser")

            for link in soup.find_all("a", href=True):

                href = link["href"]

                absolute = urljoin(url, href)
                absolute = absolute.split("#")[0]
                absolute = absolute.rstrip("/")

                parsed = urlparse(absolute)
                # Crawl only selected documentation paths (optional)
                if allowed_paths:
                    if not any(parsed.path.startswith(path) for path in allowed_paths):
                        continue

                # Stay inside same domain
                if parsed.netloc != domain:
                    continue

                # Skip file downloads
                if absolute.lower().endswith(skip_extensions):
                    continue

                # Skip unwanted URLs
                if any(word in absolute.lower() for word in skip_keywords):
                    continue

                # Skip language pages
                if any(parsed.path.startswith(lang) for lang in language_prefixes):
                    continue

                # Skip empty root duplicates
                if absolute in ("", start_url.rstrip("/")):
                    continue

                if absolute not in visited and absolute not in queue:
                    queue.append(absolute)

        except Exception as e:
            print(f"Failed: {url}")
            print(e)

    urls = sorted(visited)

    print("\nPages to Crawl")
    print("=" * 60)

    for i, page in enumerate(urls, start=1):
        print(f"{i}. {page}")

    print("=" * 60)
    print(f"Total Pages Found: {len(urls)}")

    return urls