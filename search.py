import Tools.google_search as google
from Tools.webscrape import WebScraper as ws
import Tools.intelligent_chunk as ic
from bs4 import BeautifulSoup

var = google.google_search("spaceships",5)
print(var[2][0])
# var2 = ws.get_plain_text(var[2][0])
var2 = ws.get_plain_text("https://www.space.com/coolest-spaceships-in-sci-fi")
print(f"\n\n{var2}")
