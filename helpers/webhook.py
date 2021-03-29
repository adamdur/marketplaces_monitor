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


async def send_invalid_channel_webhook(guild_id, guild_name, channel):
    url = settings.INVALID_CHANNELS_WEBHOOK
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
        timestamp = int(round(time.time() * 1000))
        await webhook.send(f"INVALID CHANNEL WARNING!\n"
                           f"guild_name: {guild_name}\n"
                           f"guild_id: {guild_id}\n"
                           f"channel: {channel}", username=f"{settings.BOT_NAME} [{timestamp}]", avatar_url=settings.BOT_ICON)


async def sotm_webhook(embed):
    url = settings.STATE_OF_THE_MARKET_WEBHOOK
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(url, adapter=AsyncWebhookAdapter(session))
        timestamp = int(round(time.time() * 1000))
        await webhook.send(embed=embed, username=f"MFNF State of the Market", avatar_url="https://pbs.twimg.com/profile_images/1348329578981421058/kGKg351L.jpg")
