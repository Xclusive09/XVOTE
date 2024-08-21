from solana.publickey import PublicKey
from solana.rpc.api import Client
from solana.rpc.async_api import AsyncClient
from solana.transaction import Transaction
from solana.system_program import SYS_PROGRAM_ID, CreateAccountParams, create_account
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import mint_to, initialize_mint
from spl.token.client import Token
import base64

# Solana Client Setup
SOLANA_URL = "https://api.devnet.solana.com"
client = Client(SOLANA_URL)

# Replace with your actual mint authority keypair and wallet keypair
MINT_AUTHORITY = "your_mint_authority_private_key_here"
WALLET = "your_wallet_private_key_here"

async def check_nft_in_wallet(wallet_address: str, token_mint: str) -> bool:
    """Check if the NFT (token_mint) is present in the given wallet_address."""
    wallet_pubkey = PublicKey(wallet_address)
    token_pubkey = PublicKey(token_mint)
    
    response = client.get_token_accounts_by_owner(wallet_pubkey, mint=token_pubkey)
    return len(response['result']['value']) > 0

def mint_nft(destination_wallet: str) -> str:
    """Mint an NFT to the specified wallet address."""
    wallet = PublicKey(destination_wallet)
    
    # Mint NFT logic here
    token = Token.create_mint(
        client,
        MINT_AUTHORITY,
        MINT_AUTHORITY.public_key,
        0,
        TOKEN_PROGRAM_ID,
    )
    
    token_account = token.create_account(wallet)
    token.mint_to(token_account, MINT_AUTHORITY, 1)
    
    return str(token_account)
