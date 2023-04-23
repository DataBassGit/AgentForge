import requests
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self, url):
        self.url = url
        
    def get_plain_text(self):
        # Send a GET request to the URL
        response = requests.get(self.url)
        
        # Create a BeautifulSoup object with the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the plain text from the HTML content
        plain_text = soup.get_text()
        
        # Return the plain text
        return plain_text
