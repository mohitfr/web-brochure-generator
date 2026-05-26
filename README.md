# Web Brochure Generator

My first LLM project. You give it a company name and a URL — it scrapes the website, figures out which pages are actually worth reading, and uses AI to write a clean markdown brochure about the company. There's a simple Gradio interface so you don't have to touch the terminal once it's running.

I built this to learn how LLMs fit into a real pipeline, not just as a chatbot. It's not complex, but it does something complete — input goes in, a useful thing comes out.

---

## What it does

1. Scrapes the text content of the given URL
2. Pulls all the links from the page
3. Uses GPT-4o-mini to filter down to only the relevant ones — about pages, careers, products, that kind of thing
4. Fetches the content from those pages too
5. Passes everything to GPT-4o-mini to write a brochure
6. Streams the output live so you're not just staring at a spinner
7. Lets you download the result as a `.md` file when it's done

You can also pick a tone — Professional, Humorous, or Concise.

---

## Project structure

```
web-brochure-generator/
├── scraper.py           # scrapes page text and extracts links
├── link_filter.py       # uses GPT-4o-mini to filter links down to relevant ones
├── brochure.py          # core logic — builds the prompt and generates the brochure
├── brochure_local.py    # same as brochure.py but uses a local Ollama model
├── link_filter_local.py # same as link_filter.py but uses a local Ollama model
├── app.py               # Gradio UI — run this for the OpenAI version
├── app_local.py         # Gradio UI for the local Ollama version
├── .env.example         # template for your API key
├── requirements.txt
├── .gitignore
└── README.md
```

The separation is intentional — scraping, filtering, and generating are three different jobs and keeping them in different files made debugging a lot easier than I expected.

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/mohitfr/web-brochure-generator.git
cd web-brochure-generator
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Add your API key**
```bash
cp .env.example .env
# open .env and add your OpenAI API key
```

---

## Usage

**OpenAI version**
```bash
python app.py
```

**Local Ollama version — free, no API key needed**
```bash
ollama pull llama3.2    # first time only
ollama serve            # start the local server
python app_local.py
```

Open the URL Gradio gives you, enter a company name and URL, pick a tone, hit Submit. That's it.

---

## Tones

| Tone | What it does |
|---|---|
| Professional | Clean, structured brochure for customers and investors |
| Humorous | Witty and entertaining — try it on Patagonia |
| Concise | Bullet points only, no more than 20 |

---

## Tech stack

- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) — HTML parsing
- [Requests](https://requests.readthedocs.io/) — HTTP requests
- [OpenAI Python SDK](https://github.com/openai/openai-python) — GPT-4o-mini calls
- [Gradio](https://www.gradio.app/) — web UI
- [python-dotenv](https://github.com/theskumar/python-dotenv) — API key management
- [Ollama](https://ollama.com/) — local LLM support (optional)

---

## Requirements

- Python 3.10+
- An OpenAI API key — or Ollama installed if you want to run it locally

---

## What I learned

This was my first time working with LLMs outside of just chatting with them. Going in, I knew Python but had no idea how to plug an LLM into an actual pipeline.

A few things that stuck with me — prompt engineering matters way more than I thought. The same model gives completely different output depending on how you phrase the instructions, and that took some trial and error to get right. Streaming the response instead of waiting for the full reply also felt like a small thing until I tried waiting — then it felt essential.

The most useful thing I did structurally was keep scraping, filtering, and generating in separate files. When something broke, I knew exactly where to look. And when I wanted to add the Ollama version, I could swap just the client without touching the rest.

Simple project, but it covers the full loop. Good enough to build on.