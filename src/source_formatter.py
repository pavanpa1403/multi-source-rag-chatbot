from pathlib import Path

def format_sources(results):
    """
    Returns unique source names and page numbers.
    """

    sources = []
    seen = set()

    for doc in results:

        source = Path(doc.metadata.get("source", "Unknown")).name
        page = doc.metadata.get("page")

        key = (source, page)

        if key not in seen:
            seen.add(key)
            sources.append((source, page))

    return sources