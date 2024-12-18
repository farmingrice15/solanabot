import subprocess
from solana.rpc.api import Client
from solana.keypair import Keypair

# Constants
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"

# Read wallet and constants from the file
def load_wallet_and_constants(filename="wallet_info.txt"):
    wallet_info = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Remove leading/trailing whitespace and split at the '=' sign
                if '=' in line:
                    key, value = line.strip().split('=')
                    wallet_info[key] = value
    except Exception as e:
        print(f"Error loading wallet info: {e}")
    
    return wallet_info

# Load wallet details and constants from the file
wallet_info = load_wallet_and_constants()

# Parse the wallet address and constants
WALLET_ADDRESS = wallet_info.get("WALLET_ADDRESS", "")
MIN_SPEND_PER_COIN = float(wallet_info.get("MIN_SPEND_PER_COIN", 5))  # Default to 5
MAX_SPEND_PER_COIN = float(wallet_info.get("MAX_SPEND_PER_COIN", 20))  # Default to 20
TOTAL_BUDGET = float(wallet_info.get("TOTAL_BUDGET", 200))  # Default to 200

# Wallet setup (public key will be loaded from the file)
if WALLET_ADDRESS:
    public_key = WALLET_ADDRESS
else:
    print("Error: Wallet address is not set in the wallet_info.txt file.")
    public_key = None

# Solana RPC client
client = Client(SOLANA_RPC_URL)


def get_wallet_balance(sol_price):
    """
    Fetches the current SOL balance of the wallet and calculates the USD equivalent.
    :param sol_price: The current price of 1 SOL in USD.
    :return: Balance in SOL and USD.
    """
    try:
        balance = client.get_balance(public_key)
        balance_in_sol = balance["result"]["value"] / 10**9  # Convert lamports to SOL
        balance_in_usd = balance_in_sol * sol_price  # Convert SOL to USD
        return balance_in_sol, balance_in_usd
    except Exception as e:
        print(f"Error fetching wallet balance: {e}")
        return 0, 0


def open_terminal_with_wallet_info(sol_price):
    """
    Opens a new terminal window and displays wallet balance and constants.
    :param sol_price: The current price of 1 SOL in USD.
    """
    if public_key is None:
        print("Wallet address is not set. Exiting.")
        return
    
    balance_in_sol, balance_in_usd = get_wallet_balance(sol_price)

    # Information to display
    wallet_info_display = f"""
=== Wallet Info ===
Public Address: {public_key}
Bal: ${balance_in_usd:.2f}/{balance_in_sol:.4f} SOL

=== Trading Constants ===
Minimum Spend Per Coin: ${MIN_SPEND_PER_COIN}
Maximum Spend Per Coin: ${MAX_SPEND_PER_COIN}
Total Budget: ${TOTAL_BUDGET}
"""

    # Open a new terminal window and display wallet info
    try:
        # Command to open a new terminal (cross-platform support)
        if subprocess.os.name == "posix":  # macOS/Linux
            subprocess.call(["gnome-terminal", "--", "bash", "-c", f"echo '{wallet_info_display}'; exec bash"])
        elif subprocess.os.name == "nt":  # Windows
            subprocess.call(["start", "cmd", "/k", f"echo {wallet_info_display}"], shell=True)
        else:
            print("Unsupported OS for opening a new terminal.")
    except Exception as e:
        print(f"Error opening terminal: {e}")


if __name__ == "__main__":
    # Example usage: Replace with a real-time SOL price
    current_sol_price = 20  # Placeholder for the price of SOL in USD
    open_terminal_with_wallet_info(current_sol_price)
