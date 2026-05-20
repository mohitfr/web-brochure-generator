import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from scraper import fetch_website_links

model = "gpt-4o-mini"

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = OpenAI(api_key=api_key)

link_system_prompt = """
    You are provided with a list of links found on a webpage.
    You are able to decide which of the links would be most relevant to include in a brochure about the company,
    such as links to an About page, or a Company page, or Careers/Jobs pages.
    You should respond in JSON as in this example:

    {
        "links": [
            {"type": "about page", "url": "https://full.url/goes/here/about"},
            {"type": "careers page", "url": "https://another.full.url/careers"}
        ]
    }
    """


def get_links_user_prompt(url):
    user_prompt = f"""
        Here is the list of links on the website {url} -
        Please decide which of these are relevant web links for a brochure about the company, 
        respond with the full https URL in JSON format.
        Do not include Terms of Service, Privacy, email links.

        Links (some might be relative links):

        """
    links = fetch_website_links(url)
    user_prompt += "\n".join(links)
    return user_prompt


def select_relevant_links(url):
    print(f"Selecting relevant links for {url} by calling {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(url)}
        ],
        response_format={"type": "json_object"}
    )
    result = response.choices[0].message.content
    links = json.loads(result)
    print(f"Found {len(links['links'])} relevant links")
    return links

