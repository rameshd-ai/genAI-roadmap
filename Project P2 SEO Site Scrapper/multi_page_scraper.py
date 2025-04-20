import requests
from bs4 import BeautifulSoup
import csv
import os
from collections import Counter
from urllib.parse import urlparse, urljoin
import re

# List of common stopwords to exclude from the analysis
STOPWORDS = {
    "i", "me", "my", "you", "your", "yours", "he", "him", "his", "she", "her", "hers", "it", "its", "we", "our", "ours",
    "they", "them", "their", "theirs", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are",
    "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the",
    "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between",
    "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off",
    "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both",
    "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
    "very", "s", "t", "can", "will", "just", "don", "should", "now", "d", "ll", "m", "o", "re", "ve", "y", "ain", "aren",
    "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn",
    "weren", "won", "wouldn"
}

# Function to get all links from a page
def get_links_from_page(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all anchor tags with href
        links = set()
        for link in soup.find_all('a', href=True):
            absolute_url = urljoin(url, link['href'])
            if urlparse(absolute_url).netloc == urlparse(url).netloc:  # Same domain
                links.add(absolute_url)
        return links
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return set()

# Function to crawl the website and gather texts from all pages
def crawl_website(start_url):
    visited_links = set()
    all_texts = []

    def crawl(url):
        if url in visited_links or len(visited_links) >= 10:  # Limit to 10 pages for demo
            return
        print(f"Crawling {url}...")
        visited_links.add(url)

        # Get the page content and extract text
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract text only from meaningful tags like <h1>, <h2>, <p>, etc.
            page_text = ' '.join([text.get_text() for text in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'meta'])])
            all_texts.append(page_text)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")

        # Get the links from the current page
        links = get_links_from_page(url)
        for link in links:
            crawl(link)

    crawl(start_url)
    return visited_links, all_texts

# Function to clean and split the text into words for keyword extraction
def clean_text(text):
    words = text.split()
    cleaned_words = [word.strip().lower() for word in words if word.isalpha() and word.lower() not in STOPWORDS]
    return cleaned_words

# Function to create timestamped file names for the output CSV
def get_timestamped_filename():
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"reports/multi_page_keywords_output_{timestamp}.csv"

# Main function to start the scraping
def main():
    start_url = input("Enter the competitor website URL (like https://example.com): ").strip()
    
    # Get all page texts and visited links by crawling the website
    visited_links, texts = crawl_website(start_url)
    
    # Clean the text and get keywords
    keywords = clean_text(' '.join(texts))
    keyword_counter = Counter(keywords)

    # 🚀 Make sure 'reports/' folder exists
    os.makedirs('reports', exist_ok=True)

    # Get the timestamped filename for CSV
    output_filename = get_timestamped_filename()

    # Save keywords to CSV file
    with open(output_filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Keyword", "Frequency"])
        for keyword, freq in keyword_counter.most_common():
            writer.writerow([keyword, freq])

    print(f"\n✅ Scraping complete! {len(visited_links)} pages scanned.")
    print(f"✅ Found {len(keyword_counter)} unique keywords.")
    print(f"📂 Results saved in '{output_filename}'.")

if __name__ == "__main__":
    main()
