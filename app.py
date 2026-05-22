import gradio as gr
from brochure import create_brochure

def generate_brochure(company_name, url):

    if not company_name or not url:
        yield "Please provide both a company name and website links."
        return
    
    if not url.startswith("http"):
        yield "Please provide valid website links starting with http or https."    
        return 
    
    yield from create_brochure(company_name, url)

page = gr.Interface(
    fn=generate_brochure,
    inputs=[gr.Textbox(label="Company Name",placeholder="Enter company name:"),
            gr.Textbox(label="Company Website URL",placeholder="Enter website URL:")],
    outputs=gr.Markdown(label="Generated Brochure"),
    title="Web Brochure Generator",
    description="Enter a company name and its website URL to generate a brochure about the company for prospective customers, investors and recruits.",
    examples=[["Acme Inc.", "https://www.acme.com"], ["Globex Corp.", "https://www.globex.com"]],
    theme=gr.themes.Soft()
)

if __name__ == "__main__":
    page.launch(inbrowser=True)

