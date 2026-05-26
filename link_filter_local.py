import json
from openai import OpenAI
from scraper import fetch_website_links

model = "llama3.2"

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
)

brochure_keywords = [
    "about", "company", "team", "careers", "jobs", "mission",
    "values", "product", "products", "services", "customers",
    "clients", "solutions", "contact", "story", "case-study",
    "case-studies", "history", "social", "media", "blog", "news"
]

link_system_prompt = """
    You are provided with a list of links found on a webpage.

    You are able to decide which of the links would be most relevant to include in a brochure about the company,
    
    Select only the links that are most useful for generating a company brochure
    for prospective customers, investors, and recruits. 

    Prefer links such as:
    - About
    - Company
    - Team
    - Careers / Jobs
    - Products / Services
    - Mission / Values
    - Customers / Case Studies
    - Contact
    - Story / History
    - Social media links

    Do not include:
    - Privacy Policy
    - Terms of Service
    - Cookie Policy
    - Login / Signup pages
    - Email links
    
    Return valid JSON in exactly this format

    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page", "url": "https://another.full.url/careers"}
        ]
    }
    """.strip()


def get_links_user_prompt(url: str) -> str:

    """
    Given a url, fetch the links on the webpage and return a user prompt 
    that includes the links and asks the model to select relevant links for a company brochure. 

        url: the url of the webpage to fetch links from
    """

    links = fetch_website_links(url)

    if not links:
        return f"No links found on the webpage {url}"

    scored_links = sorted(
        links,
        key=lambda link: any(keyword in link.lower() for keyword in brochure_keywords),
        reverse=True
    )
    top_links = scored_links[:40]
    user_prompt = f"""
        Here is the list of links on the website {url} -

        Please decide which of these are relevant web links for a brochure about the company, 
        Return only full URLs in JSON format.

        Links:
        """ + "\n".join(top_links)

    return user_prompt


def select_relevant_links(url: str) -> dict:

    """
    Given a url, select the most relevant links for a company brochure
    by calling a local Ollama model with a system prompt and a user prompt
    that includes the links on the webpage.

        url: the url of the webpage to select links from
    """

    try:
        print(f"Selecting relevant links for {url} by calling {model} via Ollama")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": link_system_prompt},
                {"role": "user", "content": get_links_user_prompt(url)}
            ]
        )

        result = response.choices[0].message.content
        
        # Ollama doesn't support response_format=json_object like OpenAI,
        # so we extract the JSON manually from the response
        start = result.find("{")
        end = result.rfind("}") + 1
        if start == -1 or end == 0:
            print("No JSON found in model response")
            return {"links": []}
        
        data = json.loads(result[start:end])

        links = data.get("links", [])
        if not isinstance(links, list):
            return {"links": []}

        cleaned_links = []
        seen = set()

        for item in links:
            if not isinstance(item, dict):
                continue

            link_type = item.get("type", "relevant page")
            link_url = item.get("url", "").strip()

            if not link_url or link_url in seen:
                continue

            seen.add(link_url)
            cleaned_links.append({"type": link_type, "url": link_url})

        return {"links": cleaned_links}

    except Exception as e:
        print(f"Error selecting relevant links: {e}")
        return {"links": []}