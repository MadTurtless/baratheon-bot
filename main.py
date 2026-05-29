"""
Arryn Bot - v1.0.1
Description:
This Discord bot is used for administrative tasks in the House Arryn server within the EOV genre.
Current functionality:
Reaction Roles
Planned functionality:
Event logging
"""

import asyncio
import os
import logging
import sys

import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()

token = os.getenv("DISCORD_TOKEN")

logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - %(message)s",
                    handlers=[
                        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
                              logging.StreamHandler(stream=sys.stdout)
                    ])

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(intents=intents, command_prefix="!")

@bot.event
async def on_ready():
    """
    This function is called when the bot is online.
    It attempts to synchronise all commands
    :return:
    """
    logger.info(f"{bot.user} has connected to Discord!")

    try:
        synced = await bot.tree.sync()
        logger.info(f"{bot.user} has synced {len(synced)} commands")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

async def main():
    """
    This is the entry point for the bot.
    It makes sure to add all cogs and then starts it.
    :return:
    """
    extensions = ["src.classes.commands", "src.classes.reaction_roles", "src.classes.join_manager", "src.classes.event_logs_manager"]

    async with bot:
        for e in extensions:
            await bot.load_extension(e)
        await bot.start(token)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    logger.info("Shutting down...\n"
                "================================================================\n")
