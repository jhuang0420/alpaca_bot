from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest, MarketOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass, QueryOrderStatus
from config import API_KEY, API_SECRET, BASE_URL
from datetime import datetime,  timedelta
import csv, requests, os




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

def populate_csv(symbol,start,end):
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe=1Day&start={start}&end={end}&limit=2000&adjustment=raw&feed=sip&sort=asc"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": API_KEY,
        "APCA-API-SECRET-KEY": API_SECRET
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    bars = data.get("bars", {}).get(symbol, [])
    
    filename = os.path.join('data', f"{symbol}_{start}_{end}.csv")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['c', 'h', 'l', 'n', 'o', 't', 'v', 'vw']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for bar in bars:
            writer.writerow(bar)
            
def populate_data():
    one_day_ago = datetime.now() - timedelta(days=1)
    formatted_date = one_day_ago.strftime("%Y-%m-%d")
    with open("test.csv", 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            populate_csv(row['Symbol'], "2020-01-01",formatted_date)
    
