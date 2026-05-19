import asyncio
from datetime import datetime
from telethon import TelegramClient
from telethon.tl.types import (
    User, Channel, Chat,
    UserStatusOnline, UserStatusRecently,
    UserStatusOffline, UserStatusLastWeek, UserStatusLastMonth
)
from telethon.errors import UsernameNotOccupiedError, FloodWaitError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

console = Console()

def parse_last_seen(status) -> str:
    if isinstance(status, UserStatusOnline):
        return "🟢 Online now"
    if isinstance(status, UserStatusRecently):
        return "Recently"
    if isinstance(status, UserStatusLastWeek):
        return "Within last week"
    if isinstance(status, UserStatusLastMonth):
        return "Within last month"
    if isinstance(status, UserStatusOffline):
        return status.was_online.strftime('%Y-%m-%d %H:%M UTC') if \
            status.was_online else "Unknown"
    return "Hidden"


async def lookup_target(client: TelegramClient, target: str) -> dict:
    try:
        entity = await client.get_entity(target)
    except UsernameNotOccupiedError:
        console.print(f"[red] '{target}' does not exist.[/red]")
        return {}
    except FloodWaitError as e:
        console.print(f"[yellow] Rate limited. Waiting {e.seconds} s... [/yellow]")
        await asyncio.sleep(e.seconds)
        return await lookup_target(client, target)

    result = {
        "queried_target": target,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    if isinstance(entity, User):
        result.update({
            "entity_type": "Bot" if entity.bot else "User",
            "id": entity.id,
            "first_name": entity.first_name or "",
            "last_name": entity.last_name or "",
            "username": entity.username or "None",
            "phone": entity.phone or "hidden",
            "is_bot": entity.bot,
            "is_verified": entity.verified,
            "is_scam": entity.scam,
            "is_premium": entity.premium,
            "last_seen": parse_last_seen(entity.status),
        })
    elif isinstance(entity, (Channel, Chat)):
        result.update({
            "entity_type": "Channel" if isinstance(entity, Channel) else "Group",
            "id": entity.id,
            "title": entity.title,
            "username": entity.username or "None",
            "participants_count": getattr(entity, 'participants_count', None),
        })

    return result


def display_profile(data: dict):
    """Beautifully display the profile using Rich"""
    if not data:
        return

    console.print(Panel(f"[bold cyan]Profile Lookup: {data.get('queried_target')}[/bold cyan]",
                        border_style="blue"))

    table = Table(title=" Entity Information", box=box.ROUNDED, show_header=False)
    table.add_column("Field", style="bold cyan", width=20)
    table.add_column("Value", style="white")

    fields = [
        ("Type", data.get("entity_type")),
        ("ID", str(data.get("id"))),
        ("Title / Name", f"{data.get('first_name', '')} {data.get('last_name', '')}".strip() or data.get("title")),
        ("Username", f"@{data.get('username')}" if data.get("username") != "None" else "None"),
        ("Participants", data.get("participants_count")),
        ("Verified", "Yes" if data.get("is_verified") else "No"),
        ("Scam", "Yes" if data.get("is_scam") else "No"),
        ("Premium", "Yes" if data.get("is_premium") else "No"),
        ("Last Seen", data.get("last_seen")),
        ("Bio / Description", data.get("bio") or data.get("description") or "-"),
        ("Phone", data.get("phone")),
        ("Profile Photo", data.get("profile_photo", "-")),
    ]

    for field, value in fields:
        if value is not None and value != "":
            table.add_row(field, str(value))

    console.print(table)
