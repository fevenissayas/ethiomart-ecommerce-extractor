from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os
import pandas as pd
import asyncio

load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
client = TelegramClient('anon', api_id, api_hash)

channels = [
    '@EthioMarketPlace',
    '@MerttEka',
    '@Shewabrand',
    '@ethio_brand_collection',
    '@ZemenExpress'
]

async def fetch_messages(channel, limit=200):
    await client.start()
    messages = []
    async for message in client.iter_messages(channel, limit=limit):
        if message.text:
            messages.append({
                'channel': channel,
                'text': message.text,
                'date': message.date,
                'sender_id': message.sender_id,
                'id': message.id
            })
    return messages

async def run():
    all_data = []
    for ch in channels:
        print(f"Fetching from {ch}")
        messages = await fetch_messages(ch)
        all_data.extend(messages)

    df = pd.DataFrame(all_data)
    df.to_csv("data/raw/telegram_messages.csv", index=False)
    print("Data saved to data/raw/telegram_messages.csv")

with client:
    client.loop.run_until_complete(run())
