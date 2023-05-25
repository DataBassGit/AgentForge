import Tools.google_search as google
from Tools.webscrape import WebScraper
import Tools.intelligent_chunk as smart_chunk
from bs4 import BeautifulSoup

web_scrape = WebScraper()

search_results = google.google_search("spaceships", 5)
url = search_results[2][0]
scrapped = web_scrape.get_plain_text(url)
chunks = smart_chunk.intelligent_chunk(scrapped, chunk_size=0)

print(f"\nURL: {url}")
print(f"\nURL: {url}")
print(f"\n\nChunks:\n{chunks}")


