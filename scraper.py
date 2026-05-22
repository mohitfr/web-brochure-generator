from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def _get_soup(url: str):

    """
    Fetch the webpage at the given url and return a BeautifulSoup object of the page content.
    If the request fails, return None.

        url: the url of the webpage to fetch
    """

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def fetch_website_contents(url: str, max_chars: int = 2000) -> str:

    """
    Return the title and contents of the website at the given url, 
    truncate to 2,000 characters as a sensible limit

        url: the url of the webpage to fetch contents from
    """

    soup = _get_soup(url)
    if not soup:
        return ""
    
    title = soup.title.string if soup.title else "No title found"

    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input", "svg", "noscript"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""

    cleaned = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    return f"{title}\n\n{cleaned}"[:max_chars]


def fetch_website_links(url: str) -> list[str]:

    """
    Return the links on the website at the given url.
        url: the url of the webpage to fetch links from
    """

    soup = _get_soup(url)
    if not soup:
        return []
    
    found_links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()

        if not href or href.startswith(("#", "mailto:", "javascript:", "tel:")):
            continue

        absolute_url = urljoin(url, href)
        parsed = urlparse(absolute_url)

        if parsed.scheme in {"http", "https"} and parsed.netloc:
            found_links.append(absolute_url)

    return list(dict.fromkeys(found_links))