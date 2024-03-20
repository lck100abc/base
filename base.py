import telepot
import requests
import time

# Replace with your Telegram Bot Token
BOT_TOKEN = '6855817314:AAGdE5XBJ1y7QMkEkfx8N3NUU6LdBXgzmCg'

# Define the chat ID where you want to send notifications
CHAT_ID = '6613211769'

# Blastscan API Key
API_KEY = 'B5W1DPSDVXKJWRWNAJQ5BBDMMMJRIWKUWF'

# Blastscan API URL - assuming similar functionality, replace with actual endpoints
API_URL = 'https://api.basescan.io/api'

# Dictionary to store the last checked block number for each wallet address
last_checked_blocks = {}

def get_current_block_number():
    # Assuming there's a similar endpoint in Blastscan to get the current block number
    params = {'module': 'proxy', 'action': 'eth_blockNumber', 'apikey': API_KEY}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        current_block = int(response.json().get('result', '0x0'), 16)
        return current_block
    else:
        print(f"Error fetching current block number: HTTP {response.status_code}")
        return None

def get_latest_token_transfer(address):
    # Assuming Blastscan has a similar API endpoint for token transfers
    params = {
        'module': 'account',
        'action': 'tokentx',
        'address': address,
        'page': 1,
        'offset': 1,
        'startblock': last_checked_blocks.get(address, 0) + 1,
        'endblock': 'latest',
        'sort': 'asc',
        'apikey': API_KEY
    }
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        result = response.json().get('result', [])
        if result:
            return result[0]
        else:
            return None
    else:
        print(f"Error fetching transactions: HTTP {response.status_code}")
        return None

bot = telepot.Bot(BOT_TOKEN)

def send_notification(chat_id, message):
    bot.sendMessage(chat_id, message, parse_mode="Markdown")

def monitor_wallet_addresses():
    wallet_addresses = [
        "0x67ab0E84C7f9e399a67037F94a08e5C664DC1C66"
    ]

    current_block = get_current_block_number()
    if current_block:
        for address in wallet_addresses:
            last_checked_blocks[address] = current_block

    while True:
        time.sleep(30)  # Delay for API rate limit considerations
        for address in wallet_addresses:
            latest_tx = get_latest_token_transfer(address)
            if latest_tx and isinstance(latest_tx, dict) and 'blockNumber' in latest_tx:
                block_number = int(latest_tx['blockNumber'], 16)
                if address not in last_checked_blocks or block_number > last_checked_blocks[address]:
                    # Adjust the message as needed based on Blastscan's response structure
                    message = (
                        f"🚀 *New Transaction on Blast L2* 🚀\n\n"
                        f"🔹 *Address*: [{address}](https://blastscan.io/address/{address})\n"
                        f"🔹 *Direction*: {'Received' if address.lower() == latest_tx.get('to', '').lower() else 'Sent'}\n"
                        f"🔹 *Token*: {latest_tx.get('tokenName', 'Unknown Token')} ({latest_tx.get('tokenSymbol', 'N/A')})\n"
                        f"🔹 *Value*: {latest_tx.get('value', 'N/A')}\n"
                        f"🔹 *Block Number*: {block_number}\n"
                    )
                    send_notification(CHAT_ID, message)
                    last_checked_blocks[address] = block_number

if __name__ == '__main__':
    monitor_wallet_addresses()
