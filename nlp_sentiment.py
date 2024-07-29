import csv, requests
from bs4 import BeautifulSoup
from textblob import TextBlob

def nlp_sentiment():
    lis = []
    with open('test.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader: 
            titles = scrape_google_news_titles(row['Symbol'])
            analysis = TextBlob(titles)
            polarity = analysis.sentiment.polarity
            lis.append({"Symbol": row['Symbol'], "Rating":polarity})
        top_10 = sorted(lis, key=lambda x: x['Rating'], reverse=True)[:10]
    return top_10
            
def scrape_google_news_titles(keyword):
    url = f"https://news.google.com/search?q={keyword}+stock"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    if response.status_code != 200:
        print("Failed to retrieve the page")
        return ""
    
    titles = ""
    for item in soup.find_all('c-wiz', class_='PO9Zff Ccj79 kUVvS'): 
        title = item.find('a', class_ = 'JtKRv').text
        titles += title + ". "
    return titles