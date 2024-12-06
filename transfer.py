from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.rpc.types import TxOpts
from solana.system_program import transfer, TransferParams

# Solana RPC Endpoint (Mainnet or Devnet)
RPC_URL = "https://api.mainnet-beta.solana.com"  # Use Devnet for testing
solana_client = Client(RPC_URL)

def transfer_sol(from_wallet: Keypair, to_wallet_address: str, amount_sol: float):
    """Transfer SOL from one wallet to another."""
    try:
        # Convert SOL to lamports (1 SOL = 1_000_000_000 lamports)
        lamports = int(amount_sol * 1_000_000_000)
        
        # Create transaction
        transaction = Transaction().add(
            transfer(
                TransferParams(
                    from_pubkey=from_wallet.public_key,
                    to_pubkey=to_wallet_address,
                    lamports=lamports,
                )
            )
        )
        
        # Send transaction
        response = solana_client.send_transaction(
            transaction, from_wallet, opts=TxOpts(skip_preflight=True)
        )
        print(f"Transaction successful! Signature: {response['result']}")
        return response["result"]
    except Exception as e:
        print(f"Error transferring SOL: {e}")
        return None
