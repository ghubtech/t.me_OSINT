import asyncio
from pathlib import Path
from telethon import TelegramClient
from PIL import Image
import piexif
import utils

async def download_media(client: TelegramClient, target: str, limit: int = 10, output_dir: str = "output/media"):
    """Download media and extract EXIF metadata"""
    await utils.log_action("media_download", target)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        entity = await client.get_entity(target)
        downloaded = []
        
        async for message in client.iter_messages(entity, limit=limit):
            if message.photo or message.video or message.document:
                file_path = await client.download_media(message, file=output_path)
                if file_path:
                    metadata = extract_exif(file_path) if str(file_path).lower().endswith(('.jpg', '.jpeg')) else {}
                    downloaded.append({
                        "file": str(file_path),
                        "message_id": message.id,
                        "metadata": metadata
                    })
        
        data = {
            "target": target,
            "downloaded_count": len(downloaded),
            "timestamp": datetime.utcnow().isoformat(),
            "files": downloaded
        }
        
        await utils.save_to_json(data, f"media_{target.strip('@')}.json")
        return data
        
    except Exception as e:
        utils.logger.error(f"Error downloading media: {e}")
        return {"error": str(e)}

def extract_exif(image_path):
    """Extract EXIF data from image"""
    try:
        img = Image.open(image_path)
        exif_data = piexif.load(img.info.get('exif', b''))
        return {tag: str(val) for ifd in exif_data for tag, val in exif_data[ifd].items()}
    except:
        return {}
