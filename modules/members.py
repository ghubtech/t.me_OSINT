import asyncio
from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from rich.progress import Progress
import utils

async def get_group_members(client: TelegramClient, target: str, max_members: int = 200):
    """Fetch members from a public group/channel"""
    await utils.log_action("members_scrape", target)

    try:
        entity = await client.get_entity(target)
        members = []
        
        with Progress() as progress:
            task = progress.add_task("[cyan]Fetching members...", total=max_members)
            
            offset = 0
            limit = 200
            
            while len(members) < max_members:
                participants = await client(GetParticipantsRequest(
                    entity, ChannelParticipantsSearch(''), offset, limit, hash=0
                ))
                
                if not participants.users:
                    break
                    
                for user in participants.users:
                    members.append({
                        "id": user.id,
                        "username": user.username,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                    })
                    progress.update(task, advance=1)
                    if len(members) >= max_members:
                        break
                
                offset += len(participants.users)
        
        data = {
            "target": target,
            "total_members_fetched": len(members),
            "timestamp": datetime.utcnow().isoformat(),
            "members": members
        }
        
        await utils.save_to_json(data, f"members_{target.strip('@')}.json")
        return data
        
    except Exception as e:
        utils.logger.error(f"Error fetching members: {e}")
        return {"error": str(e)}
