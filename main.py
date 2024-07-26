from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass, QueryOrderStatus
from config import API_KEY, API_SECRET, BASE_URL
import csv, requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import time

trading_client = TradingClient(API_KEY, API_SECRET, paper=True)

account = trading_client.get_account()

if account.trading_blocked:
    print('Account is currently restricted from trading.')

def buying_power():
    print(f'${account.buying_power} is available as buying power.')
    
def balance_change():
    balance_change = float(account.equity) - float(account.last_equity)
    print(f'Today\'s portfolio balance change: ${balance_change}')

def get_tradable_assets():
    search_params = GetAssetsRequest(asset_class=AssetClass.US_EQUITY)
    assets = trading_client.get_all_assets(search_params)
    
    tradable_assets = []
    for asset in assets:
        if asset.tradable: tradable_assets.append({'Symbol': asset.symbol, 'Name': asset.name})
    
    tradable_assets.sort(key=lambda x: x['Symbol'])
    
    with open('assets.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Symbol', 'Name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for asset in tradable_assets:
            writer.writerow(asset)
#get_tradable_assets()

def market_order_buy(sym, price):
    market_order_data = MarketOrderRequest(
                    symbol=sym,
                    notional=price,
                    side=OrderSide.BUY,
                    time_in_force=TimeInForce.DAY)
    market_order = trading_client.submit_order(order_data=market_order_data)
    
def market_order_sell(sym, price):
    market_order_data = MarketOrderRequest(
                    symbol=sym,
                    notional=price,
                    side=OrderSide.SELL,
                    time_in_force=TimeInForce.DAY)
    market_order = trading_client.submit_order(order_data=market_order_data)

# Retrieve current orders
def get_orders():
    get_orders_data = GetOrdersRequest(
        status=QueryOrderStatus.CLOSED,
        limit=100,
        nested=True)
    
# Retrieve positions
def get_positions():
    portfolio = trading_client.get_all_positions()
    for position in portfolio:
        print("{} shares of {}".format(position.qty, position.symbol))
    
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
            
top10 = nlp_sentiment()
print(top10)