import os
import requests
from flask import Flask, render_template, request, jsonify
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# List of cryptocurrencies
crypto_list = ['bitcoin', 'ethereum', 'litecoin', 'dogecoin']

@app.route('/', methods=['GET', 'POST'])
def index():
    selected_crypto = 'bitcoin'  # Default cryptocurrency
    time_period = '12h'  # Default time period
    plot_img = None

    if request.method == 'POST':
        selected_crypto = request.form['crypto_symbol']
        time_period = request.form['time_period']
        
        # Fetch cryptocurrency data based on selected symbol and time period
        data = fetch_crypto_data(selected_crypto, time_period)
        
        # Create the plot
        plot_img = create_crypto_plot(data)

    return render_template('index.html', crypto_list=crypto_list, selected_crypto=selected_crypto, time_period=time_period, plot_img=plot_img)

def fetch_crypto_data(crypto_symbol, time_period):
    # API to fetch historical data for cryptocurrency (example API)
    url = f'https://api.coingecko.com/api/v3/coins/{crypto_symbol}/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': time_period  # can be '1', '7', '30', etc.
    }
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        return data['prices']  # List of [timestamp, price] pairs
    else:
        return []

def create_crypto_plot(data):
    if not data:
        return None
    
    # Extract timestamps and prices
    timestamps = [x[0] for x in data]
    prices = [x[1] for x in data]
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, prices, label="Price over Time")
    plt.xlabel('Time')
    plt.ylabel('Price (USD)')
    plt.title(f"Cryptocurrency Price over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Save the plot as an image in a BytesIO object
    img_io = io.BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    
    # Encode the image as base64
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')
    return img_base64

@app.route('/get_real_time_price', methods=['GET'])
def get_real_time_price():
    crypto_symbol = request.args.get('crypto_symbol', 'bitcoin')  # Default to Bitcoin if no symbol is provided
    price = fetch_real_time_price(crypto_symbol)
    return jsonify({'current_price': price})

def fetch_real_time_price(crypto_symbol):
    # Fetch real-time price for cryptocurrency (CoinGecko API)
    url = f'https://api.coingecko.com/api/v3/simple/price'
    params = {'ids': crypto_symbol, 'vs_currencies': 'usd'}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data[crypto_symbol]['usd']
    else:
        return 0.0  # Return 0 if there's an error

if __name__ == '__main__':
    app.run(debug=True)
