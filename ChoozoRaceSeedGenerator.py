import asyncio
import os
from os import system
from DiscordGenerator import discord_get_bot
from DiscordGenerator import discord_start_bot


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    discordbot = discord_get_bot()
    loop.create_task(discord_start_bot(discordbot))
    loop.run_forever()

