import json
import logging
import math
import os
import sys
import time

from pathlib import Path

from dotenv import load_dotenv

from src.classes.database_manager import DatabaseManager
from discord.ext import commands, tasks
from src.utils.helper import qualifies_for_xp

load_dotenv()

logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - %(message)s",
                    handlers=[
                        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
                              logging.StreamHandler(stream=sys.stdout)
                    ])

def _lvl_reqs():
    lvl_rqs = {}
    base_xp = 100
    for i in range(0, 200):
        req = math.ceil((base_xp * (i ** 1.5)) / 100) * 100
        lvl_rqs[i] = req

    return lvl_rqs

class LevelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self._cooldowns = {}
        self.lvl_reqs = _lvl_reqs()
        with open(Path("data/level_roles.json"), "r") as f:
            self.lvl_roles = json.load(f)

    def get_lvl_reqs(self):
        return self.lvl_reqs

    @tasks.loop(hours=1)
    async def clean_cooldown_dict(self):
        current_time = time.time()
        self._cooldowns = {uid: exp for uid, exp in self._cooldowns.items() if exp > current_time}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != os.getenv("XP_EARNABLE_CHANNEL_ID"):
            return

        if not qualifies_for_xp(message.content):
            return

        author_id = message.author.id
        current_time = time.time()
        cooldown_expiry = self._cooldowns.get(author_id, 0)

        if current_time < cooldown_expiry:
            return

        try:
            if not self.db.get_user(author_id):
                self.db.add_user(author_id)

            self.db.add_user_xp(author_id, 5)
            user_xp = self.db.get_user_xp(author_id)
            current_lvl = self.db.get_user_level(author_id)
            next_lvl = current_lvl + 1

            if user_xp > self.lvl_reqs[next_lvl]:
                self.db.add_user_level(author_id, 1)

                if str(next_lvl) in self.lvl_roles:
                    guild = message.guild
                    role = guild.get_role(self.lvl_roles[str(next_lvl)])
                    await message.author.add_roles(role)

                logger.info(f"User {message.author} has achieved level {next_lvl}")

            self._cooldowns[author_id] = current_time + 1
        except Exception as e:
            logger.error(e)

async def setup(bot):
    await bot.add_cog(LevelManager(bot))
