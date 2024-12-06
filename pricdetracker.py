import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
API_URL = "https://api.coingecko.com/api/v3/coins/markets"
PARAMS = {
    "vs_currency": "usd",
    "order": "volume_desc",
    "per_page": 50,  # Fetch top 50 coins for broader selection
    "page": 1,
    "sparkline": False,
    "price_change_percentage": "7d",
}
MAX_MARKET_CAP = 5000000  # Market cap threshold ($5 million)
MIN_PRICE_CHANGE = 5  # Minimum 7-day price change percentage for bullish momentum
MIN_VOLUME_SURGE = 1.5  # Minimum trading volume increase multiplier (e.g., 1.5 = 50%)

def fetch_memecoins():
    """Fetch and filter memecoins with low market cap, bullish momentum, and volume surge."""
    response = requests.get(API_URL, params=PARAMS)
    if response.status_code != 200:
        raise Exception("API request failed!")
    
    data = response.json()
    memecoins = []
    for coin in data:
        # Calculate volume surge as a proxy for bullish interest
        if "meme" in coin.get("categories", []) or "dog" in coin["name"].lower():
            market_cap = coin.get("market_cap", float("inf"))
            price_change = coin.get("price_change_percentage_7d_in_currency", 0)
            current_volume = coin.get("total_volume", 0)
            avg_volume = coin.get("market_cap") / (coin["current_price"] if coin["current_price"] > 0 else 1)
            
            # Calculate volume surge and filter conditions
            if (
                market_cap < MAX_MARKET_CAP
                and price_change >= MIN_PRICE_CHANGE
                and (current_volume / avg_volume) >= MIN_VOLUME_SURGE
            ):
                memecoins.append(coin)
    return memecoins[:5]  # Top 5 memecoins

def evaluate_risk(coin):
    """Assign a risk level based on market cap and volatility."""
    market_cap = coin["market_cap"]
    price_change = coin["price_change_percentage_7d_in_currency"]
    if market_cap < 1000000 or abs(price_change) > 50:
        return "High"
    elif market_cap < 3000000:
        return "Medium"
    else:
        return "Low"

def calculate_investment(memecoins, budget):
    """Allocate investment and estimate profits for the bullish coins."""
    investment_per_coin = budget / len(memecoins)
    results = []
    for coin in memecoins:
        # Assume weekly profit estimate is based on 7-day percentage change
        weekly_change = coin.get("price_change_percentage_7d_in_currency", 0) / 100
        current_price = coin["current_price"]
        expected_profit = investment_per_coin * weekly_change
        risk_level = evaluate_risk(coin)
        
        results.append({
            "Coin": coin["name"],
            "Current Price (USD)": current_price,
            "Market Cap (USD)": coin["market_cap"],
            "Volume (USD)": coin["total_volume"],
            "7-Day Change (%)": coin.get("price_change_percentage_7d_in_currency", 0),
            "Risk Level": risk_level,
            "Investment (USD)": round(investment_per_coin, 2),
            "Expected Weekly Profit (USD)": round(expected_profit, 2),
        })
    return results

def plot_graphs(results):
    """Visualize data with graphs."""
    df = pd.DataFrame(results)
    
    # Bar chart: Investment vs. Expected Weekly Profit
    plt.figure(figsize=(10, 6))
    sns.barplot(x="Coin", y="Investment (USD)", data=df, color="blue", label="Investment")
    sns.barplot(x="Coin", y="Expected Weekly Profit (USD)", data=df, color="green", label="Expected Profit")
    plt.title("Investment vs. Expected Weekly Profit")
    plt.xlabel("Coin")
    plt.ylabel("Amount (USD)")
    plt.legend()
    plt.show()
    
    # Scatter plot: Market Cap vs. 7-Day Change
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x="Market Cap (USD)", y="7-Day Change (%)", hue="Risk Level", size="Volume (USD)", data=df, sizes=(50, 300))
    plt.title("Market Cap vs. 7-Day Change with Risk Levels")
    plt.xlabel("Market Cap (USD)")
    plt.ylabel("7-Day Change (%)")
    plt.legend()
    plt.show()
    
    # Line chart: Investment breakdown
    plt.figure(figsize=(10, 6))
    df.set_index("Coin")[["Investment (USD)", "Expected Weekly Profit (USD)"]].plot(kind="line", marker="o")
    plt.title("Investment Breakdown")
    plt.ylabel("Amount (USD)")
    plt.grid()
    plt.show()

def display_results(results):
    """Display results in a table format and show graphical analysis."""
    df = pd.DataFrame(results)
    print(df)
    plot_graphs(results)

# Main Execution
if __name__ == "__main__":
    try:
        # Get budget input from user
        budget = float(input("Enter your daily investment budget (USD): "))
        
        memecoins = fetch_memecoins()
        if not memecoins:
            print("No bullish memecoins found!")
        else:
            investment_results = calculate_investment(memecoins, budget)
            display_results(investment_results)
    except Exception as e:
        print(f"Error: {e}")
