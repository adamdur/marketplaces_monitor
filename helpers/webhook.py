import aiohttp
import settings
import time
from discord import Webhook, AsyncWebhookAdapter


async def send_webhook(message, test=False):
    url = settings.TEST_LOG_WEBHOOK if test else settings.LOG_WEBHOOK
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
        timestamp = int(round(time.time() * 1000))
        await webhook.send(message, username=f"{settings.BOT_NAME} [{timestamp}]{' [TEST_MODE]' if test else ''}", avatar_url=settings.BOT_ICON)
