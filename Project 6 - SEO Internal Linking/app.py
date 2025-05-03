import openai
import os
import json
import pandas as pd
import requests
import xml.etree.ElementTree as ET
import streamlit as st
from typing import List
from bs4 import BeautifulSoup
from io import BytesIO
from sentence_transformers import SentenceTransformer, util

# Load OpenAI API Key
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

client = openai.OpenAI(api_key=key_data["openai_api_key"])

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def fetch_urls_from_sitemap(sitemap_url: str) -> List[str]:
    response = requests.get(sitemap_url)
    if response.status_code != 200:
        raise Exception("Failed to fetch sitemap")
    root = ET.fromstring(response.content)
    return [url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url')]


def fetch_page_text(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")
        return "\n".join([p.get_text() for p in paragraphs])
    except:
        return ""


def find_relevant_urls(content: str, all_urls: List[str], page_texts: dict, top_k=5) -> List[str]:
    content_embedding = embedder.encode(content, convert_to_tensor=True)
    candidates = []
    for url in all_urls:
        if url not in page_texts:
            page_texts[url] = fetch_page_text(url)
        if not page_texts[url]:
            continue
        url_embedding = embedder.encode(page_texts[url], convert_to_tensor=True)
        score = util.cos_sim(content_embedding, url_embedding).item()
        candidates.append((url, score))

    candidates.sort(key=lambda x: x[1], reverse=True)
    return [url for url, _ in candidates[:top_k]]


def suggest_internal_links(content: str, relevant_urls: List[str]) -> List[str]:
    prompt = (
        "You are an SEO assistant. Given this page content and internal site URLs, suggest 3–5 relevant internal links with anchor text."
        " Return results in the format: \nTitle: ...\nAnchor: ...\nTarget URL: ...\n"
        f"Content:\n{content[:2000]}\n\nURLs:\n" + "\n".join(relevant_urls)
    )
    try:
        response = client.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful internal linking optimizer."},
                {"role": "user", "content": prompt}
            ]
        )
        suggestions = response.choices[0].message['content'].strip()
        return suggestions.split("\n\n")
    except Exception as e:
        return [f"Error: {e}"]


def process_urls(url_list: List[str]) -> pd.DataFrame:
    data = []
    page_texts = {}
    for url in url_list:
        text = fetch_page_text(url)
        if not text.strip():
            continue
        page_texts[url] = text
        relevant_urls = find_relevant_urls(text, [u for u in url_list if u != url], page_texts)
        suggestions = suggest_internal_links(text, relevant_urls)
        for s in suggestions:
            data.append({"Page URL": url, "Suggestion": s})
    return pd.DataFrame(data)


# Streamlit App
st.set_page_config(page_title="Internal Linking Optimizer", layout="wide")
st.title("🔗 GenAI Internal Linking Assistant (Token Optimized)")

input_mode = st.radio("Choose Input Method", ["Sitemap URL", "Manual URL Entry"])

urls = []
if input_mode == "Sitemap URL":
    sitemap_url = st.text_input("Enter sitemap URL")
    if st.button("Fetch URLs") and sitemap_url:
        try:
            urls = fetch_urls_from_sitemap(sitemap_url)
            st.success(f"Fetched {len(urls)} URLs from sitemap")
            st.write(urls[:10])
        except Exception as e:
            st.error(f"Failed to fetch sitemap: {e}")
else:
    url_input = st.text_area("Enter URLs (one per line)")
    if url_input:
        urls = [line.strip() for line in url_input.splitlines() if line.strip()]

if urls and st.button("Generate Internal Linking Suggestions"):
    with st.spinner("Processing pages and generating suggestions using vector search..."):
        df = process_urls(urls)
        st.success("✅ Suggestions generated!")
        st.dataframe(df)

        # Prepare Excel file in memory
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine='openpyxl')
        excel_buffer.seek(0)

        # Download link
        st.download_button(
            label="📥 Download Excel",
            data=excel_buffer,
            file_name="internal_link_suggestions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
