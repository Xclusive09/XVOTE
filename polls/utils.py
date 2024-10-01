import requests
import json

# Solana-specific constants
SOLANA_RPC_URL = "https://api.mainnet-beta.solana.com"  # Mainnet Solana RPC URL
SOLANA_HEADERS = {
    "Content-Type": "application/json"
}

def solana_request(payload):
    """
    Sends a request to the Solana blockchain RPC.
    Args:
        payload (dict): The request payload.

    Returns:
        dict: The response from the Solana RPC server.
    """
    try:
        response = requests.post(SOLANA_RPC_URL, headers=SOLANA_HEADERS, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error communicating with Solana RPC: {e}")
        return None

def get_tokens_in_wallet(wallet_address):
    """
    Retrieves all the tokens in a specific Solana wallet.
    Args:
        wallet_address (str): The public address of the Solana wallet.

    Returns:
        list: A list of token accounts in the wallet, including mint addresses.
    """
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet_address,
            {
                "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"  # Solana token program ID
            },
            {
                "encoding": "jsonParsed"
            }
        ]
    }

    result = solana_request(payload)

    if result and 'result' in result:
        return result['result']['value']
    else:
        print("No tokens found in wallet.")
        return []

def check_nft_in_wallet(wallet_address, nft_mint_address):
    """
    Checks if a specific NFT (mint address) exists in a given Solana wallet.
    Args:
        wallet_address (str): The public address of the Solana wallet.
        nft_mint_address (str): The mint address of the NFT to check.

    Returns:
        bool: True if the NFT is found in the wallet, False otherwise.
    """
    tokens = get_tokens_in_wallet(wallet_address)
    
    for token in tokens:
        token_info = token.get('account', {}).get('data', {}).get('parsed', {}).get('info', {})
        if token_info.get('mint') == nft_mint_address:
            return True
    return False

wallet_address = "YOUR_WALLET_ADDRESS_HERE"
nft_mint_address = "YOUR_NFT_MINT_ADDRESS_HERE"

if check_nft_in_wallet(wallet_address, nft_mint_address):
    print("NFT is in the wallet.")
else:
    print("NFT not found in the wallet.")
