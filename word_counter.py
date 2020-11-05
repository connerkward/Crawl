import ctoken
import requests
from bs4 import BeautifulSoup
url = "https://wics.ics.uci.edu/events/category/wics-meeting-2/2018-12-16/"
page = requests.get(url=url)
text = BeautifulSoup(page.text, features="lxml").text
tokens = ctoken.tokenize_page(page_text=text, ignore_stop_words=False)
print(text)
print(len(tokens))