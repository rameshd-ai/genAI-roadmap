# own_keywords.py - Scrape keywords from your website
from sitemap_scraper import generate_keywords_csv  # Assuming this is your existing scraper function

def scrape_own_website():
    # Replace with your website's URL
    start_url = "https://www.wildnettechnologies.com/"
    output_file = generate_keywords_csv(start_url)
    print(f"Keywords scraped and saved in {output_file}")

if __name__ == "__main__":
    scrape_own_website()
