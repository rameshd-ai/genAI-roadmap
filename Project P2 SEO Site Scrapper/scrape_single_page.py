import requests
from bs4 import BeautifulSoup
from collections import Counter
import re
import csv
import os

# Define stop words
stop_words = set([
    "the", "and", "to", "for", "in", "of", "with", "on", "is", "are", "at", "as", "by", "an", "be", "this", "that"
])

def scrape_keywords(url):
    try:
        # Make a GET request to the website
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title, meta description, headings
        elements = []

        # Extract title
        title = soup.title.string if soup.title else 'No Title'
        elements.append(title)

        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and 'content' in meta_desc.attrs:
            elements.append(meta_desc['content'])
        else:
            elements.append('No Meta Description')

        # Extract headings (h1, h2, h3)
        headings = soup.find_all(['h1', 'h2', 'h3'])
        for heading in headings:
            elements.append(heading.get_text())

        # Clean and tokenize
        text = ' '.join(elements)
        words = re.findall(r'\b[\w\'-]+\b', text.lower())  # This regex handles words with apostrophes and hyphens
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        # Count frequency of keywords
        keyword_counter = Counter(keywords)

        # Create a reports directory if it doesn't exist
        if not os.path.exists('reports'):
            os.makedirs('reports')

        # Save the results to a CSV file
        with open('reports/keywords_output.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Keyword", "Frequency"])
            for keyword, freq in keyword_counter.most_common():
                writer.writerow([keyword, freq])

        print(f"✅ Scraping complete! Found {len(keyword_counter)} unique keywords.")
        print("Results saved in 'reports/keywords_output.csv'.")

    except Exception as e:
        print(f"Error: {e}")

# Example usage
scrape_keywords("https://www.milestoneinternet.com")  # Replace with any competitor site
