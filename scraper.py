from bs4 import BeautifulSoup
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

def _get_soup(url: str):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return None


def fetch_website_contents(url: str) -> str:
    """
    Return the title and contents of the website at the given url, 
    truncate to 2,000 characters as a sensible limit
    """
    soup = _get_soup(url)
    if not soup:
        return ""
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]


def fetch_website_links(url: str) -> list[str]:
    "Return the links on the website at the given url"
    soup = _get_soup(url)
    if not soup:
        return []
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link and link.startswith("http")]