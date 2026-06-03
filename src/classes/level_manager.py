import logging
import sys
import time

import math

from src.classes.database_manager import DatabaseManager
from discord.ext import commands, tasks

from src.utils.helper import qualifies_for_xp

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
    for i in range(1, 200):
        req = math.ceil((base_xp * (i ** 1.5)) / 100) * 100
        lvl_rqs[i] = req

    return lvl_rqs

class LevelManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = DatabaseManager()
        self._cooldowns = {}
        self.lvl_reqs = _lvl_reqs()

    @tasks.loop(hours=1)
    async def clean_cooldown_dict(self):
        current_time = time.time()
        self._cooldowns = {uid: exp for uid, exp in self._cooldowns.items() if exp > current_time}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
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

            if user_xp > self.lvl_reqs[current_lvl + 1]:
                self.db.add_user_level(author_id, 1)
                logger.info(f"User {message.author} has achieved level {current_lvl + 1}")

            self._cooldowns[author_id] = current_time + 1
        except Exception as e:
            logger.error(e)

async def setup(bot):
    await bot.add_cog(LevelManager(bot))
