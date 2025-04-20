import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import re
import io

st.set_page_config(page_title="SEO Scraper & Analyzer", layout="wide")

st.title("🔎 SEO Keyword Scraper & Analyzer")

# --- Functions ---
def scrape_keywords(url, max_pages=20):
    visited_urls = set()
    all_keywords = set()

    def crawl(page_url):
        if len(visited_urls) >= max_pages:
            return
        try:
            response = requests.get(page_url, timeout=10)
            if response.status_code != 200:
                return
            visited_urls.add(page_url)

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract keywords
            title = soup.title.string if soup.title else ""
            if title:
                all_keywords.update(re.findall(r'\b\w+\b', title.lower()))

            metas = soup.find_all("meta", attrs={"name": "keywords"})
            for meta in metas:
                if meta.get("content"):
                    all_keywords.update(re.findall(r'\b\w+\b', meta["content"].lower()))

            headers = soup.find_all(re.compile('^h[1-6]$'))
            for header in headers:
                all_keywords.update(re.findall(r'\b\w+\b', header.get_text().lower()))

            # Crawl internal links
            links = soup.find_all("a", href=True)
            for link in links:
                link_url = urljoin(page_url, link['href'])
                if urlparse(link_url).netloc == urlparse(url).netloc:
                    if link_url not in visited_urls:
                        crawl(link_url)
        except Exception as e:
            st.error(f"Error scraping {page_url}: {e}")

    crawl(url)
    return all_keywords

def compare_keywords(own_keywords, competitor_keywords):
    only_in_own = own_keywords - competitor_keywords
    only_in_competitor = competitor_keywords - own_keywords
    common_keywords = own_keywords & competitor_keywords

    return only_in_own, only_in_competitor, common_keywords

# --- Streamlit App ---

# Initialize session state
if 'own_keywords' not in st.session_state:
    st.session_state.own_keywords = set()
if 'competitor_keywords' not in st.session_state:
    st.session_state.competitor_keywords = set()
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

tab1, tab2 = st.tabs(["🔎 Scrape Websites", "📊 Analyze SEO"])

with tab1:
    st.header("Scrape Keywords from Websites")

    own_url = st.text_input("Enter Your Website URL (Own Site):")
    competitor_url = st.text_input("Enter Competitor Website URL:")

    max_pages = st.slider("Max Pages to Crawl per Site", min_value=5, max_value=100, value=20)

    if st.button("Scrape Keywords"):
        if own_url:
            with st.spinner("Scraping your website..."):
                st.session_state.own_keywords = scrape_keywords(own_url, max_pages=max_pages)
        if competitor_url:
            with st.spinner("Scraping competitor website..."):
                st.session_state.competitor_keywords = scrape_keywords(competitor_url, max_pages=max_pages)
        
        st.success("Scraping Completed!")
        st.session_state.analysis_done = False

with tab2:
    st.header("Compare and Analyze Keywords")

    if (st.session_state.own_keywords and st.session_state.competitor_keywords):

        if st.button("Generate Analysis Report"):
            only_in_own, only_in_competitor, common_keywords = compare_keywords(
                st.session_state.own_keywords,
                st.session_state.competitor_keywords
            )

            report_data = {
                "Keyword Type": [],
                "Keyword": []
            }

            for kw in only_in_own:
                report_data["Keyword Type"].append("Only in Own Site")
                report_data["Keyword"].append(kw)
            for kw in only_in_competitor:
                report_data["Keyword Type"].append("Only in Competitor Site")
                report_data["Keyword"].append(kw)
            for kw in common_keywords:
                report_data["Keyword Type"].append("Common")
                report_data["Keyword"].append(kw)

            df_report = pd.DataFrame(report_data)

            st.dataframe(df_report, use_container_width=True)

            # Save to CSV
            buffer = io.BytesIO()
            df_report.to_csv(buffer, index=False)
            buffer.seek(0)

            st.download_button(
                label="Download SEO Analysis Report",
                data=buffer,
                file_name="seo_analysis_report.csv",
                mime="text/csv",
            )

            st.success("Report Generated!")
            st.session_state.analysis_done = True

    else:
        st.warning("Please scrape both websites first to generate the analysis.")

