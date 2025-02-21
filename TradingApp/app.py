from flask import Flask, request, jsonify, redirect, session
import requests
import alpaca_trade_api as tradeapi
import ccxt  # Pour Binance
from ib_insync import IB

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Config Brokers
BROKERS = {
    "alpaca": {
        "auth_url": "https://app.alpaca.markets/oauth/authorize",
        "token_url": "https://api.alpaca.markets/oauth/token",
        "client_id": "TON_ALPACA_CLIENT_ID",
        "client_secret": "TON_ALPACA_CLIENT_SECRET",
        "redirect_uri": "https://tonapp.com/auth/callback/alpaca"
    },
    "ibkr": {
        "auth_url": "https://www.interactivebrokers.com/oauth2/auth",
        "token_url": "https://www.interactivebrokers.com/oauth2/token",
        "client_id": "TON_IBKR_CLIENT_ID",
        "client_secret": "TON_IBKR_CLIENT_SECRET",
        "redirect_uri": "https://tonapp.com/auth/callback/ibkr"
    },
    "binance": {
        "api_key": "TON_BINANCE_API_KEY",
        "api_secret": "TON_BINANCE_SECRET_KEY"
    }
}

@app.route("/")
def home():
    return '''
        <h1>Choisissez votre Broker</h1>
        <a href="/login/alpaca">Se connecter avec Alpaca</a><br>
        <a href="/login/ibkr">Se connecter avec IBKR</a><br>
        <a href="/login/binance">Se connecter avec Binance (via API Key)</a>
    '''

@app.route("/login/<broker>")
def login(broker):
    if broker not in BROKERS:
        return "Broker non supporté", 400
    
    if broker == "binance":
        return "Veuillez entrer vos clés API Binance.", 400

    broker_config = BROKERS[broker]
    auth_url = f"{broker_config['auth_url']}?client_id={broker_config['client_id']}&redirect_uri={broker_config['redirect_uri']}&response_type=code"
    
    return redirect(auth_url)

@app.route("/auth/callback/<broker>")
def auth_callback(broker):
    if broker not in BROKERS:
        return "Broker non supporté", 400
    
    code = request.args.get("code")
    broker_config = BROKERS[broker]

    # Échange du code contre un token d'accès
    token_data = {
        "grant_type": "authorization_code",
        "client_id": broker_config["client_id"],
        "client_secret": broker_config["client_secret"],
        "code": code,
        "redirect_uri": broker_config["redirect_uri"]
    }
    response = requests.post(broker_config["token_url"], data=token_data)
    token_info = response.json()
    
    session[f"{broker}_access_token"] = token_info.get("access_token")
    
    return f"Connexion à {broker} réussie !"

@app.route("/trade", methods=["POST"])
def trade():
    data = request.json
    broker = data.get("broker")
    symbol = data.get("symbol")
    quantity = data.get("quantity")
    
    if broker == "alpaca":
        api = tradeapi.REST(BROKERS["alpaca"]["client_id"], BROKERS["alpaca"]["client_secret"], "https://paper-api.alpaca.markets", api_version='v2')
        order = api.submit_order(symbol=symbol, qty=quantity, side='buy', type='market', time_in_force='gtc')
        return jsonify({"status": "Trade exécuté sur Alpaca", "order_id": order.id})
    
    elif broker == "ibkr":
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=99)
        contract = tradeapi.contracts.Stock(symbol, 'SMART', 'USD')
        ib.qualifyContracts(contract)
        order = tradeapi.orders.MarketOrder('BUY', quantity)
        trade = ib.placeOrder(contract, order)
        return jsonify({"status": "Trade exécuté sur IBKR"})
    
    elif broker == "binance":
        exchange = ccxt.binance({"apiKey": BROKERS["binance"]["api_key"], "secret": BROKERS["binance"]["api_secret"]})
        order = exchange.create_market_buy_order(symbol, quantity)
        return jsonify({"status": "Trade exécuté sur Binance", "order": order})
    
    else:
        return "Broker non supporté", 400

if __name__ == "__main__":
    app.run(debug=True)
