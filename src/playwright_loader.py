from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from langchain_core.documents import Document


def load_js_page(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        )

        print("\n" + "=" * 80)
        print("Requested URL:", url)

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Wait for JavaScript to finish loading
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(5000)

        print("Actual URL :", page.url)
        print("Title      :", page.title())

        try:
            h1 = page.locator("h1").first.inner_text()
            print("H1         :", h1)
        except:
            print("H1         : Not Found")

        html = page.content()

        print("HTML Length:", len(html))
        print("=" * 80)

        soup = BeautifulSoup(html, "html.parser")

        # Remove unwanted elements
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

        # Debug HTML structure
        print("\nSearching for main tag...")

        main = soup.find("main")

        if main:

            print("✓ MAIN TAG FOUND")
            print("-" * 80)
            print(main.prettify()[:1500])
            print("-" * 80)

            text = main.get_text("\n", strip=True)

        else:

            print("✗ MAIN TAG NOT FOUND")
            text = soup.get_text("\n", strip=True)

        print("\nExtracted Text Length:", len(text))
        print("-" * 80)
        print(text[:500])
        print("-" * 80)

        browser.close()

    return Document(
        page_content=text,
        metadata={
            "source": url,
            "type": "website"
        }
    )