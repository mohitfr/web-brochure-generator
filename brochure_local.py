import os
from openai import OpenAI
from scraper import fetch_website_contents
from link_filter import select_relevant_links

model = "llama3.2"

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1",
    )


def fetch_page_and_all_relevant_links(url: str) -> str:

    """
    Fetch the contents of the page at the given url, 
    and also fetch the contents of any relevant links on the page.
    Return the combined contents as a string.

        url: the url of the page to fetch
    """

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

#Different brochure system prompts for different tones of brochure

brochure_system_prompts = {
    "Professional": """
    You are an assistant that analyzes the contents of several relevant pages from a company website
    and creates a short brochure about the company for prospective customers, investors, and recruits.
    Respond in markdown without code blocks.
    Include details of company culture, customers, and careers/jobs if available.
    """,
    "Humorous": """
    You are an assistant that analyzes the contents of several relevant pages from a company website
    and creates a short, humorous, witty brochure about the company for prospective customers, investors, and recruits.
    Respond in markdown without code blocks.
    Include details of company culture, customers, and careers/jobs if available.
    """,
    "Concise": """
    You are an assistant that analyzes the contents of several relevant pages from a company website
    and creates a very short brochure in bullet points for prospective customers, investors, and recruits.
    Respond in markdown without code blocks.
    Keep it brief — no more than 20 bullet points total.
    """
}


def get_brochure_user_prompt(company_name: str, url: str) -> str:

    """
    Call the fetch_page_and_all_relevant_links function to get the contents 
    of the page and relevant links, and then return a user prompt for the brochure creation 
    that includes the company name and the contents.

        company_name: the name of the company to create a brochure for
        url: the url of the company's website
    """

    website_content = fetch_page_and_all_relevant_links(url)

    user_prompt = f"""
        You are looking at a company called: {company_name}
        Here are the contents of its landing page and other relevant pages;
        use this information to build a short brochure of the company in markdown without code blocks.

        {website_content}
        """
    return user_prompt[:8000]


def create_brochure(company_name: str, url: str, tone: str = "Professional"):

    """
    Create a brochure for the given company based on its website content and the specified tone
    by calling a local Ollama model with a system prompt and a user prompt.

        company_name: the name of the company to create a brochure for
        url: the url of the company's website
        tone: the desired tone for the brochure ("Professional", "Humorous", "Concise")
    """
    tone = tone if tone in brochure_system_prompts else "Professional"

    try:
        yield "Fetching page content..."
        user_prompt = get_brochure_user_prompt(company_name, url)

        yield "Filtering relevant links..."

        yield "Generating brochure...\n\n"

        stream = client.chat.completions.create(
            model = model,
            messages = [
                {"role": "system", "content": brochure_system_prompts[tone]},
                {"role": "user", "content": user_prompt}
            ],
            stream = True
        )

        for chunk in stream:
            result = chunk.choices[0].delta
            if result and result.content:
                yield result.content

    except Exception as e:
        yield f"\n\nSomething went wrong: {str(e)}\n\nMake sure Ollama is running with: ollama serve"


