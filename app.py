import gradio as gr
import tempfile
from urllib.parse import urlparse
from brochure import create_brochure


def is_valid_url(url: str) -> bool:

    """
    Checks if a URL is valid.
    A valid URL must have a scheme (http or https) and a netloc (domain).

        url: the URL to validate
        returns: True if the URL is valid, False otherwise
    """
    
    try:
        parsed = urlparse(url.strip())
        return parsed.scheme in {"http", "https"} and parsed.netloc != ""
    
    except Exception:
        return False


def generate_brochure(company_name, url, tone):
    
    """
    Generates a brochure for the given company,
    by validating the inputs, calling the create_brochure function to generate the brochure content,
    and yielding the content in a streaming fashion to update the Gradio interface in real time.

        company_name: the name of the company to create a brochure for
        url: the url of the company's website
        tone: the desired tone for the brochure ("Professional", "Humorous", "Concise")
    """
    
    company_name = company_name.strip()
    url = url.strip()
    tone = tone.strip()

    if not company_name or not url:
        yield "Please provide both a company name and website links.", None
        return
    
    if not is_valid_url(url):
        yield "Please provide a valid website URL.", None
        return 

    full_brochure = ""

    for is_status, chunk in create_brochure(company_name, url, tone):
        if is_status:
            yield chunk, None
        else:
            full_brochure += chunk
            yield full_brochure, None

    # save to a temp file once streaming is done
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
        f.write(full_brochure)
        temp_path = f.name
    
    yield full_brochure, temp_path


page = gr.Interface(
    fn=generate_brochure,
    inputs=[
        gr.Textbox(label="Company Name",placeholder="Enter company name:"),
        gr.Textbox(label="Company Website URL",placeholder="Enter website URL:"),
        gr.Dropdown(
            choices=["Professional", "Humorous", "Concise"], 
            label="Tone", 
            value="Professional")
    ],
    outputs=[
        gr.Markdown(label="Generated Brochure"),
        gr.File(label="Download Brochure")
    ],
    title="Web Brochure Generator",
    description="Enter a company name and its website URL to generate a brochure about the company for prospective customers, investors and recruits.",
    examples=[
        ["Anthropic", "https://anthropic.com", "Professional"],
        ["Patagonia", "https://www.patagonia.com", "Humorous"],
        ["Linear", "https://linear.app", "Concise"],
    ],
    theme=gr.themes.Soft()
    )

if __name__ == "__main__":
    page.launch(inbrowser=True)

