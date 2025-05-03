import streamlit as st
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import pandas as pd
import re
import io
import os
import json
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
import openai
import plotly.express as px

# --- Load OpenAI API Key ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
key_path = os.path.join(parent_dir, 'key.json')

with open(key_path) as f:
    key_data = json.load(f)

openai.api_key = key_data["openai_api_key"]

# --- Streamlit Setup ---
st.set_page_config(page_title="SEO Toolkit", layout="wide")
st.title("🚀 SEO Scraper & Site Analyzer Toolkit")

# --- Functions ---
def fetch_page(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.text
    except:
        pass
    return None

def analyze_page(url):
    html = fetch_page(url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'html.parser')

    title = soup.title.string.strip() if soup.title else ""
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag and meta_desc_tag.get('content') else ""

    heading_counts = {f'H{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    heading_contents = {f'H{i} Content': list(set([h.get_text(strip=True) for h in soup.find_all(f'h{i}')])) for i in range(1, 7)}

    images = soup.find_all('img')
    images_without_alt = [img.get('src') for img in images if not img.get('alt')]

    has_schema = bool(soup.find_all('script', type='application/ld+json'))

    page_data = {
        "URL": url,
        "Title": title,
        "Title Length": len(title),
        "Meta Description": meta_desc,
        "Meta Description Length": len(meta_desc),
        **heading_counts,
        **heading_contents,
        "Images without Alt": len(images_without_alt),
        "Has Schema Markup": has_schema
    }

    return page_data

def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code != 200:
            return []

        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        urls = []
        for url_elem in root.findall('ns:url', namespace):
            loc = url_elem.find('ns:loc', namespace).text
            if loc:
                urls.append(loc)

        return urls
    except Exception as e:
        st.error(f"Error fetching or parsing sitemap: {e}")
        return []

def get_gpt_recommendations(page_data):
    prompt = f"""
You are an expert SEO consultant.
Analyze the following webpage SEO report and suggest improvements.
Report:
Title Length: {page_data['Title Length']}
Meta Description Length: {page_data['Meta Description Length']}
H1 Count: {page_data.get('H1', 0)}
Images without Alt: {page_data['Images without Alt']}
Has Schema Markup: {page_data['Has Schema Markup']}

Suggest improvements step-by-step.
"""
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error fetching recommendation: {e}"

# --- Session State ---
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# --- Sidebar Menu ---
st.sidebar.title("🛠️ Choose Tool")
menu = st.sidebar.radio(
    "Select a Tool",
    ("🛠️ SEO Site Audit Analyzer",)
)

# --- SEO Site Audit Analyzer ---
if menu == "🛠️ SEO Site Audit Analyzer":
    st.subheader("🛠️ SEO Site Audit Analyzer")

    sitemap_url = st.text_input("Enter Sitemap URL (usually `https://example.com/sitemap.xml`):")
    max_pages = st.slider("Max Pages to Audit", min_value=5, max_value=50, value=10)

    if st.button("Start SEO Audit"):
        if sitemap_url:
            with st.spinner("Fetching URLs from sitemap..."):
                internal_links = get_urls_from_sitemap(sitemap_url)[:max_pages]

            if internal_links:
                st.info(f"Found {len(internal_links)} URLs. Starting audit...")

                progress = st.progress(0)
                all_pages_data = []

                def safe_analyze(url):
                    try:
                        return analyze_page(url)
                    except:
                        return None

                with ThreadPoolExecutor(max_workers=5) as executor:
                    futures = {executor.submit(safe_analyze, link): link for link in internal_links}
                    for i, future in enumerate(futures):
                        result = future.result()
                        if result:
                            seo_score = 100
                            if result['Title Length'] == 0:
                                seo_score -= 20
                            if result['Meta Description Length'] == 0:
                                seo_score -= 20
                            if result['Images without Alt'] > 3:
                                seo_score -= 10
                            if not result['Has Schema Markup']:
                                seo_score -= 10
                            h1_count = result.get('H1', 0)
                            if h1_count != 1:
                                seo_score -= 10

                            result['SEO Score'] = max(seo_score, 0)

                            if seo_score < 100:
                                result['GPT Recommendation'] = get_gpt_recommendations(result)
                            else:
                                result['GPT Recommendation'] = "All Good ✅"

                            all_pages_data.append(result)

                        progress.progress((i+1)/len(futures))

                if all_pages_data:
                    df = pd.DataFrame(all_pages_data)
                    st.dataframe(df, use_container_width=True)

                    csv_buffer = io.StringIO()
                    df.to_csv(csv_buffer, index=False)

                    st.download_button(
                        label="📂 Download SEO Site Audit Report",
                        data=csv_buffer.getvalue(),
                        file_name="seo_site_audit_report.csv",
                        mime="text/csv"
                    )

                    st.markdown("---")
                    st.subheader("🌍 SEO Score Distribution")
                    fig = px.histogram(df, x="SEO Score", nbins=10, title="SEO Score Distribution")
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("📊 Schema Markup Presence")
                    schema_chart = df['Has Schema Markup'].value_counts().reset_index()
                    schema_chart.columns = ['Has Schema', 'Count']
                    fig2 = px.bar(schema_chart, x='Has Schema', y='Count', title='Schema Markup Presence')
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.error("No pages successfully analyzed.")
            else:
                st.error("No URLs found in sitemap.")
        else:
            st.warning("Please enter a valid sitemap URL to start the SEO audit.")
