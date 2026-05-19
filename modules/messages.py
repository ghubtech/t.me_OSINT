import asyncio
from datetime import datetime
from telethon import TelegramClient
import utils

async def get_messages(client: TelegramClient, target: str, limit: int = 50):
    """Fetch recent messages from a chat"""
    await utils.log_action("messages_scrape", target, f"limit={limit}")
    
    try:
        entity = await client.get_entity(target)
        messages = []
        
        async for message in client.iter_messages(entity, limit=limit):
            messages.append({
                "id": message.id,
                "date": message.date.isoformat() if message.date else None,
                "sender_id": message.sender_id,
                "text": message.text,
                "views": message.views,
                "forwards": message.forwards,
            })
        
        data = {
            "target": target,
            "total_messages": len(messages),
            "timestamp": datetime.utcnow().isoformat(),
            "messages": messages
        }
        
        await utils.save_to_json(data, f"messages_{target.strip('@')}.json")
        return data
        
    except Exception as e:
        utils.logger.error(f"Error fetching messages: {e}")
        return {"error": str(e)}
