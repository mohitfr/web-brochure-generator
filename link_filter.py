import json
from openai import OpenAI
from scraper import fetch_website_links

model = "gpt-4o-mini"

client = OpenAI()

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

    """
    Given a url, fetch the links on the webpage and return a user prompt 
    that includes the links and asks the model to select relevant links for a company brochure. 

        url: the url of the webpage to fetch links from
    """

    user_prompt = f"""
        Here is the list of links on the website {url} -
        Please decide which of these are relevant web links for a brochure about the company, 
        respond with the full https URL in JSON format.
        Do not include Terms of Service, Privacy, email links.

        Links:

        """
    links = fetch_website_links(url)    
    user_prompt += "\n".join(links)

    return user_prompt


def select_relevant_links(url):

    """
    Given a url, select the most relevant links for a company brochure
    by calling the OpenAI API with a system prompt and a user prompt that 
    includes the links on the webpage.

        url: the url of the webpage to select links from
    """

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

