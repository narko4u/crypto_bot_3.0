import ccxt
import numpy as np
import pandas as pd
import time
import os

# Load Binance API keys from environment variables
binance = ccxt.binance({
    'apiKey': os.getenv('BINANCE_API_KEY'),
    'secret':os.getenv('BINANCE_SECRET_KEY'),
    'options': {'defaultType': 'spot'}
})

# Trading parameters
symbol = 'ETH/USDT'  # Trading pair
grid_size = 10  # Number of grid levels
grid_spacing = 0.5  # Percentage between levels
trade_amount = 0.01  # Amount per order

# Take profit and stop loss
take_profit_percentage = 1.5  # 1.5% profit target
stop_loss_percentage = 2.0  # 2.0% stop loss

def get_price():
    try:
        ticker = binance.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        print("Error fetching price:", e)
        return None

def create_grid():
    price = get_price()
    if price is None:
        return []
    grid = [price * (1 + (i - grid_size / 2) * grid_spacing / 100) for i in range(grid_size)]
    return sorted(grid)

def place_orders(grid):
    for level in grid:
        try:
            binance.create_limit_buy_order(symbol, trade_amount, level)
            binance.create_limit_sell_order(symbol, trade_amount, level * (1 + take_profit_percentage / 100))
        except Exception as e:
            print(f"Error placing order at {level}: {e}")
    print("Grid orders placed successfully!")

def monitor_orders():
    while True:
        try:
            open_orders = binance.fetch_open_orders(symbol)
            current_price = get_price()
            
            for order in open_orders:
                if order['side'] == 'buy' and current_price <= order['price'] * (1 - stop_loss_percentage / 100):
                    binance.cancel_order(order['id'], symbol)
                    print(f"Stop-loss triggered: Canceled buy order at {order['price']}")
                elif order['side'] == 'sell' and current_price >= order['price']:
                    print(f"Take-profit reached: Sell order at {order['price']} executed")
            
            time.sleep(30)
        except Exception as e:
            print("Error monitoring orders:", e)
            time.sleep(10)

# Main trading loop
def run_bot():
    while True:
        try:
            grid = create_grid()
            if grid:
                place_orders(grid)
                monitor_orders()
        except Exception as e:
            print("Error:", e)
            time.sleep(10)

if __name__ == "__main__":
    run_bot()
