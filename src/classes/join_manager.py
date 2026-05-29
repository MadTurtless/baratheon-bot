import os

from discord.ext import commands
from dotenv import load_dotenv

class JoinManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        load_dotenv()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member:
            return

        guild = member.guild
        print(guild)
        role_id = int(os.getenv("JOIN_ROLE_ID"))
        print(role_id)
        role = guild.get_role(role_id)
        print(role)
        await member.add_roles(role)

async def setup(bot):
    await bot.add_cog(JoinManager(bot))