import requests 
from bs4 import BeautifulSoup 
import pandas as pd

for url_id in pd.read_csv("Input.csv")["URL_ID"]:
    text_file = f"{url_id}.txt"
    URL = pd.read_csv("Input.csv")[pd.read_csv("Input.csv")["URL_ID"] == url_id]["URL"].values[0]
    r = requests.get(URL) 
    text = ""
    soup = BeautifulSoup(r.content, 'html5lib') 
    target_div = soup.find_all("div", attrs={"class":"td-post-content tagdiv-type"})
    for i in target_div:
        text += i.text
    with open(f"scraping/{text_file}", 'w') as f:
        f.write(text)