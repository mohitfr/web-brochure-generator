import os
from openai import OpenAI
from dotenv import load_dotenv
from link_filter import select_relevant_links
from scraper import fetch_website_contents

model  = "gpt-4o-mini"

load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")


client = OpenAI(api_key=api_key)


def fetch_page_and_all_relevant_links(url):
    contents = fetch_website_contents(url)
    relevant_links = select_relevant_links(url)
    result = f"## Landing Page:\n\n{contents}\n## Relevant Links:\n"

    for link in relevant_links.get("links", []):
        try:
            result += f"\n\n### Link: {link.get('type', 'Unknown')}\n"
            result += fetch_website_contents(link["url"])
        except Exception as e:
            result += f"\n\n[Could not fetch {link.get('url', 'unknown URL')}: {str(e)}]"

    return result

brochure_system_prompt = """
You are an assistant that analyzes the contents of several relevant pages from a company website
and creates a short brochure about the company for prospective customers, investors and recruits.
Respond in markdown without code blocks.
Include details of company culture, customers and careers/jobs if you have the information.
"""

# A different system prompt for a more humorous brochure - this demonstrates how easy it is to incorporate 'tone':

# brochure_system_prompt = """
# You are an assistant that analyzes the contents of several relevant pages from a company website
# and creates a short, humorous, entertaining, witty brochure about the company for prospective customers, investors and recruits.
# Respond in markdown without code blocks.
# Include details of company culture, customers and careers/jobs if you have the information.
# """


def get_brochure_user_prompt(company_name, url):
    user_prompt = f"""
        You are looking at a company called: {company_name}
        Here are the contents of its landing page and other relevant pages;
        use this information to build a short brochure of the company in markdown without code blocks.\n\n
        """
    user_prompt += fetch_page_and_all_relevant_links(url)
    return user_prompt[:5_000] # Truncate if more than 5,000 characters
    

def create_brochure(company_name, url):
    stream = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": brochure_system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
        ],
        stream=True
    )

    for chunk in stream:
        result = chunk.choices[0].delta
        if result and result.content:
            yield result.content


if __name__ == "__main__":
    company_name = input("Enter the company name: ")
    url = input("Enter the company URL: ")
    brochure = create_brochure(company_name, url)
    for chunk in brochure:
        print(chunk, end="", flush=True)