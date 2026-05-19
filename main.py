import asyncio
import click
import config
from client import get_client, start_client
import utils
from modules.profile import lookup_target, display_profile
from modules.members import get_group_members
from modules.messages import get_messages
from modules.media import download_media

@click.group()
def cli():
    """Telegram OSINT Toolkit"""
    pass

@cli.command()
@click.option('--target', required=True, help='Target username or ID')
async def profile(target):
    """Lookup profile information"""
    client = get_client()
    async with client:
        await start_client(client)
        data = await lookup_target(client, target)
        if data:
            display_profile(data)
            await utils.save_to_json(data, f"profile_{target.strip('@')}.json")

@cli.command()
@click.option('--target', required=True, help='Group/Channel username')
@click.option('--max-members', default=200, help='Maximum members to fetch')
async def members(target, max_members):
    """Scrape group members"""
    await utils.init_db()
    client = get_client()
    async with client:
        await start_client(client)
        await get_group_members(client, target, max_members)

@cli.command()
@click.option('--target', required=True, help='Group/Channel username')
@click.option('--limit', default=50, help='Number of messages')
async def messages(target, limit):
    """Fetch recent messages"""
    await utils.init_db()
    client = get_client()
    async with client:
        await start_client(client)
        await get_messages(client, target, limit)

@cli.command()
@click.option('--target', required=True, help='Group/Channel username')
@click.option('--limit', default=10, help='Number of media files')
@click.option('--output-dir', default='output/media', help='Output directory')
async def media(target, limit, output_dir):
    """Download media and extract metadata"""
    await utils.init_db()
    client = get_client()
    async with client:
        await start_client(client)
        await download_media(client, target, limit, output_dir)

if __name__ == "__main__":
    asyncio.run(cli())
