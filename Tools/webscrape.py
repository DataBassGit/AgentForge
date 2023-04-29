import requests
from bs4 import BeautifulSoup


class WebScraper:
    def __init__(self):
        pass

    def get_plain_text(self, url):
        # Send a GET request to the URL
        url2 = url
        response = requests.get(url2)

        # Create a BeautifulSoup object with the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the plain text from the HTML content
        plain_text = soup.get_text()

        # print(plain_text)

        # Return the plain text
        return plain_text
