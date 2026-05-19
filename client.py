from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import config

def get_client() -> TelegramClient:
    """Return a configured Telethon client instance."""
    return TelegramClient(
        config.SESSION_NAME,
        config.API_ID,
        config.API_HASH,
        connection_retries=5,
        retry_delay=2,
        request_retries=3,
    )

async def start_client(client: TelegramClient) -> TelegramClient:
    """Start the client and handle 2FA if needed."""
    await client.start(phone=config.PHONE)

    if not await client.is_user_authorized():
        await client.send_code_request(config.PHONE)
        code = input("Enter the code you received on Telegram: ")
        try:
            await client.sign_in(config.PHONE, code)
        except SessionPasswordNeededError:
            pw = input("2FA enabled. Enter your password: ")
            await client.sign_in(password=pw)

    print("✅ Client connected.")
    return client
