import asyncio
from client import get_client, start_client

async def main():
    client = get_client()
    async with client:
        await start_client(client)
        me = await client.get_me()
        print(f"Logged in as: {me.first_name} (@{me.username})")
        print(f"User ID: {me.id}")

if __name__ == "__main__":
    asyncio.run(main())
