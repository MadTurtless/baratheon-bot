import asyncio
import time

from src.classes.database_manager import DatabaseManager

import threading

from discord.ext import commands
from discord.ext.commands import Cog


class LevelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        # A dictionary to hold user_id: expiry_timestamp
        self._cooldowns = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        author_id = message.author.id
        current_time = time.time()

        # 1. Check RAM cache first
        cooldown_expiry = self._cooldowns.get(author_id, 0)

        if current_time < cooldown_expiry:
            return  # Rate limited! Drop it instantly.

        # 2. Immediately update the RAM cache BEFORE doing DB operations
        self._cooldowns[author_id] = current_time + 1

        # 3. Proceed with your database operations
        try:
            self.db.add_user_xp(author_id, 5)
            print(f"Added xp for user {message.author}")
        except Exception as e:
            # If the DB fails, optionally remove them from cooldown
            # del self._cooldowns[author_id]
            print(f"Database error: {e}")

async def setup(bot):
    await bot.add_cog(LevelManager(bot))
