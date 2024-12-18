import requests
import time
from datetime import datetime
from solana.rpc.api import Client
from solana.keypair import Keypair
from decouple import config

# Constants
DEXSCREENER_API = "https://api.dexscreener.io/latest/dex/pairs/solana"
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"
client = Client(SOLANA_RPC_URL)

# Wallet details
PRIVATE_KEY = list(map(int, config("PRIVATE_KEY").split(",")))  # Private key stored in environment
wallet = Keypair.from_secret_key(bytes(PRIVATE_KEY))
public_key = wallet.public_key

# Configuration
MAX_SPEND_PER_MEMECOIN = 10  # USD to spend per memecoin
STOP_LOSS_PERCENTAGE = 30  # Stop loss at 30% drop
TAKE_PROFIT_MULTIPLIER = 2  # Take profit at 2x
POLL_INTERVAL = 600  # Poll every 10 minutes (600 seconds)

# Files for logging
PROFIT_FILE = "profit.txt"
LOSS_FILE = "loss.txt"
BALANCE_LOG_FILE = "balance_log.txt"

# Track purchases
purchases = []

# Utility functions
def log_to_file(filename, content):
    """Appends content to a log file."""
    with open(filename, "a") as file:
        file.write(content + "\n")


def get_trending_memecoins():
    """
    Fetches trending memecoins from Dexscreener.
    """
    response = requests.get(DEXSCREENER_API)
    if response.status_code == 200:
        pairs = response.json()["pairs"]
        trending = []

        for pair in pairs:
            liquidity = pair["liquidity"]["usd"]
            market_cap = pair.get("fdv", 0)  # Fully diluted valuation
            creation_time = pair.get("createdAt")
            timestamp = time.time()

            # Apply filters
            if (
                liquidity >= 50000
                and market_cap <= 1000000
                and (timestamp - creation_time / 1000) <= 6 * 60 * 60  # Within 6 hours
            ):
                trending.append(pair)

        return trending
    else:
        print("Failed to fetch data from Dexscreener.")
        return []


def trade_on_raydium(pair, amount_in_usd):
    """
    Executes a swap on Raydium.
    :param pair: Dexscreener token pair data.
    :param amount_in_usd: Amount of USD to spend on the token.
    """
    token_address = pair["baseToken"]["address"]
    token_name = pair["baseToken"]["symbol"]
    price_per_token = pair["priceUsd"]

    # Calculate amount of token to buy
    amount_of_token = amount_in_usd / price_per_token

    # Placeholder for actual Raydium swap logic
    print(f"Purchased {amount_of_token} {token_name} for {amount_in_usd} USD.")

    # Record the purchase
    purchases.append({
        "token": token_name,
        "amount": amount_of_token,
        "price": price_per_token,
        "spent": amount_in_usd,
        "pair": pair,
        "bought_at": datetime.now(),
    })


def monitor_purchases():
    """
    Monitors the purchased memecoins for stop-loss and take-profit conditions.
    """
    global purchases
    for purchase in purchases:
        current_price = float(purchase["pair"]["priceUsd"])
        initial_price = purchase["price"]
        spent = purchase["spent"]
        token_name = purchase["token"]

        # Calculate current value and thresholds
        current_value = current_price * purchase["amount"]
        stop_loss_value = spent * (1 - STOP_LOSS_PERCENTAGE / 100)
        take_profit_value = spent * TAKE_PROFIT_MULTIPLIER

        if current_value <= stop_loss_value:
            print(f"Stop-loss triggered for {token_name}. Selling...")
            sell_on_raydium(purchase, "stop-loss")
            purchases.remove(purchase)
        elif current_value >= take_profit_value:
            print(f"Take-profit triggered for {token_name}. Selling...")
            sell_on_raydium(purchase, "take-profit")
            purchases.remove(purchase)


def sell_on_raydium(purchase, reason):
    """
    Placeholder for selling tokens on Raydium.
    :param purchase: The purchase record to sell.
    :param reason: Reason for selling (stop-loss or take-profit).
    """
    token_name = purchase["token"]
    amount = purchase["amount"]
    sold_at = datetime.now()

    # Placeholder for actual selling logic
    print(f"Sold {amount} {token_name} due to {reason}.")

    # Log the result
    bought_at = purchase["bought_at"]
    spent = purchase["spent"]
    initial_price = purchase["price"]
    sold_price = purchase["pair"]["priceUsd"]
    trade_duration = (sold_at - bought_at).seconds // 60  # in minutes
    pnl = (sold_price * amount) - spent

    if pnl > 0:
        log_to_file(PROFIT_FILE, f"[{sold_at}] {token_name}: +${pnl:.2f} (Duration: {trade_duration} min)")
    else:
        log_to_file(LOSS_FILE, f"[{sold_at}] {token_name}: -${abs(pnl):.2f} (Duration: {trade_duration} min)")

    # Log balance details
    sol_balance = client.get_balance(public_key)["result"]["value"] / 10**9
    log_to_file(
        BALANCE_LOG_FILE,
        f"[{sold_at}] {token_name} | PnL: ${pnl:.2f} | SOL Balance: {sol_balance:.4f} | "
        f"Bought at: {bought_at}, Sold at: {sold_at}"
    )


def check_wallet_balances():
    """
    Checks the balances of the Phantom wallet.
    """
    balance = client.get_balance(public_key)
    usd_balance = random.uniform(100, 500)  # Mock USD balance
    sol_balance = balance['result']['value'] / 10**9
    print(f"Current Balance: ${usd_balance:.2f} | {sol_balance:.4f} SOL")


# Main bot workflow
def main():
    print("Starting memecoin trading bot...")

    while True:
        # Step 1: Display wallet balances
        check_wallet_balances()

        # Step 2: Fetch trending memecoins
        print("Fetching trending memecoins...")
        trending_tokens = get_trending_memecoins()
        print(f"Found {len(trending_tokens)} potential memecoins.")

        # Step 3: Trade new tokens
        for token in trending_tokens:
            if len(purchases) >= 10:  # Limit to 10 active trades
                break
            trade_on_raydium(token, MAX_SPEND_PER_MEMECOIN)

        # Step 4: Monitor purchases for stop-loss or take-profit
        print("Monitoring purchases for price changes...")
        monitor_purchases()

        # Step 5: Wait before polling for new coins
        print(f"Sleeping for {POLL_INTERVAL / 60} minutes...")
        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    main()
