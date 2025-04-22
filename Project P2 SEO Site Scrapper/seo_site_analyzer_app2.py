import streamlit as st
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import pandas as pd
import re
import io
from urllib.parse import urljoin  # Import urljoin here

# --- Streamlit Setup ---
st.set_page_config(page_title="SEO Toolkit", layout="wide")

st.title("🚀 SEO Scraper & Site Analyzer Toolkit")

# --- Functions ---
# ---- Phase 3: SEO Site Analyzer ----
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

    # Title & Meta
    title = soup.title.string.strip() if soup.title else ""
    meta_desc_tag = soup.find('meta', attrs={'name': 'description'})
    meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag and meta_desc_tag.get('content') else ""

    # Heading Structure (Content of each H Tag)
    heading_counts = {f'H{i}': len(soup.find_all(f'h{i}')) for i in range(1, 7)}
    heading_contents = {f'H{i} Content': list(set([h.get_text(strip=True) for h in soup.find_all(f'h{i}')])) for i in range(1, 7)}

    # Images without Alt
    images = soup.find_all('img')
    images_without_alt = [img.get('src') for img in images if not img.get('alt')]

    # Schema Markup
    has_schema = bool(soup.find_all('script', type='application/ld+json'))

    # Combine heading counts and heading contents
    page_data = {
        "URL": url,
        "Title": title,
        "Title Length": len(title),
        "Meta Description": meta_desc,
        "Meta Description Length": len(meta_desc),
        **heading_counts,
        **heading_contents,  # Added heading content for H1 to H6
        "Images without Alt": len(images_without_alt),
        "Has Schema Markup": has_schema
    }

    return page_data

# ---- Sitemap Parsing ---
def get_urls_from_sitemap(sitemap_url):
    try:
        response = requests.get(sitemap_url, timeout=10)
        if response.status_code != 200:
            return []
        
        # Parse the XML response
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        # Define the XML namespace
        namespace = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

        # Extract URLs from the <url> tags
        urls = []
        for url_elem in root.findall('ns:url', namespace):
            loc = url_elem.find('ns:loc', namespace).text
            if loc:
                urls.append(loc)
        
        return urls
    except Exception as e:
        st.error(f"Error fetching or parsing sitemap: {e}")
        return []

# --- Session State ---
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# --- Sidebar Menu ---
st.sidebar.title("🛠️ Choose Tool")
menu = st.sidebar.radio(
    "Select a Tool",
    ("🛠️ SEO Site Audit Analyzer")
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

                from concurrent.futures import ThreadPoolExecutor

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
                            # --- Basic SEO Scoring ---
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

                    # --- Visualization ---
                    st.markdown("---")
                    st.subheader("🌍 SEO Score Distribution")
                    import plotly.express as px

                    fig = px.histogram(df, x="SEO Score", nbins=10, title="SEO Score Distribution")
                    st.plotly_chart(fig, use_container_width=True)

                    st.subheader("📊 Schema Markup Presence")
                    schema_chart = df['Has Schema Markup'].value_counts().reset_index()
                    schema_chart.columns = ['Has Schema', 'Count']
                    fig2 = px.bar(schema_chart, x='Has Schema', y='Count', title='Schema Markup Presence')
                    st.plotly_chart(fig2, use_container_width=True)

                    # --- Notes Section ---
                    st.markdown("---")
                    st.subheader("📄 Full Meaning of Your Report Columns:")
                    st.markdown(""" 
                    | Field | What It Means | Example |
                    |:------|:--------------|:--------|
                    | **URL** | The webpage that was audited. This is the address of the page that was crawled and analyzed for SEO health. | `https://milestoneinternet.com/#modal-group-5` |
                    | **Title Length** | Number of characters in the `<title>` tag. Ideally, titles should be between **50–60 characters** for best SEO visibility and click-through rates. | 53 (✅ Good) |
                    | **Meta Description Length** | Number of characters in the `<meta name="description">` tag. Should ideally be **150–160 characters** for full display in search results. | 165 (⚠️ Slightly long) |
                    | **H1** | Number of `<h1>` headings. Ideally, there should be **only one H1** to define the main topic clearly for SEO and accessibility. | 0 (❗ Problem: No H1 tag) |
                    | **H2** | Number of `<h2>` headings. Used for structuring main sections under the H1, improving readability and SEO. | 18 |
                    | **H3** | Number of `<h3>` headings. Used for deeper sub-sections under H2 headings. | 39 |
                    | **H4** | Number of `<h4>` headings. Deeper level subheadings, useful for complex content structures. | 90 |
                    | **H5** | Number of `<h5>` headings. Rarely used, but available for very detailed structures. | 0 |
                    | **H6** | Number of `<h6>` headings. The smallest and deepest heading level in HTML documents. | 0 |
                    | **Images without Alt** | Counts how many `<img>` tags are missing `alt=""`. Alt text is critical for accessibility (screen readers) and SEO (image indexing). Should be minimized. | 0 (✅ Good) |
                    | **Has Schema Markup** | Indicates whether the page uses [Schema.org](https://schema.org/) structured data. Helps search engines better understand and represent your page in rich results. | TRUE (✅ Good) |
                    """, unsafe_allow_html=True)

                else:
                    st.error("No pages successfully analyzed.")

            else:
                st.error("No URLs found in sitemap.")

        else:
            st.warning("Please enter a valid sitemap URL to start the SEO audit.")
