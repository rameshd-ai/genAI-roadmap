import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter
import re
import csv
import xml.etree.ElementTree as ET
import streamlit as st
import os

# Define stop words
stop_words = set([
    "the", "and", "to", "for", "in", "of", "with", "on", "is", "are", "at", "as", "by", "an", "be", "this", "that"
])

visited_links = set()
max_pages = 30  # Limit to avoid crawling entire giant sites

def clean_text(text):
    words = re.findall(r'\b\w+\b', text.lower())
    return [word for word in words if word not in stop_words and len(word) > 2]

def scrape_page(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        elements = []

        title = soup.title.string if soup.title else ''
        elements.append(title)

        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            elements.append(meta_desc['content'])

        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings:
            elements.append(heading.get_text())

        # Find internal links
        page_links = set()
        base_url = "{0.scheme}://{0.netloc}".format(urlparse(url))
        for link_tag in soup.find_all('a', href=True):
            href = link_tag['href']
            full_url = urljoin(base_url, href)
            if base_url in full_url and full_url not in visited_links:
                page_links.add(full_url)

        return elements, page_links

    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return [], set()

def fetch_sitemap_urls(base_url):
    sitemap_url = urljoin(base_url, '/sitemap.xml')
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        root = ET.fromstring(response.text)

        urls = set()
        for url in root.findall(".//url/loc"):
            urls.add(url.text)

        return urls
    except Exception as e:
        print(f"Error fetching sitemap: {e}")
        return set()

def crawl_website(start_url):
    to_visit = set([start_url])
    all_texts = []

    # Fetch and crawl URLs from sitemap
    sitemap_urls = fetch_sitemap_urls(start_url)
    to_visit.update(sitemap_urls)

    while to_visit and len(visited_links) < max_pages:
        url = to_visit.pop()
        if url in visited_links:
            continue

        print(f"Crawling: {url}")
        visited_links.add(url)

        texts, links = scrape_page(url)
        all_texts.extend(texts)
        to_visit.update(links)

    return all_texts

def generate_keywords_csv(start_url):
    texts = crawl_website(start_url)
    
    keywords = clean_text(' '.join(texts))
    keyword_counter = Counter(keywords)

    # Ensure the output directory exists
    output_dir = "reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, 'multi_page_keywords_output.csv')

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Keyword", "Frequency"])
        for keyword, freq in keyword_counter.most_common():
            writer.writerow([keyword, freq])

    return output_path

# Streamlit GUI interface
def main():
    st.title("SEO Keyword Scraper")

    # User input for the URL
    start_url = st.text_input("Enter the competitor website URL (like https://example.com):")
    
    if st.button("Scrape Keywords"):
        if start_url:
            with st.spinner('Scraping website...'):
                try:
                    output_file = generate_keywords_csv(start_url)
                    st.success(f"Scraping complete! Results saved in {output_file}")

                    # Provide download link for the CSV file
                    with open(output_file, 'r') as f:
                        st.download_button(
                            label="Download CSV",
                            data=f,
                            file_name="keywords_output.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Error during scraping: {e}")
        else:
            st.error("Please enter a valid URL.")

if __name__ == "__main__":
    main()
