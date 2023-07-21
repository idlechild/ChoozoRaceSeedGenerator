import asyncio
import os
from os import system
from DiscordGenerator import discord_start_bot


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(discord_start_bot())
    loop.run_forever()

