"""
Registers commands for the bot
"""
import logging
import sys
from pathlib import Path
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv, set_key

from src.classes.database_manager import DatabaseManager
from src.classes.jokes import Jokes
from src.classes.level_manager import LevelManager
from src.utils.helper import build_setup_embed, check_perms, build_events_embed, permitted_roles
from src.utils.profile_image import create_profile_card

logger = logging.getLogger("discord")
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - [%(levelname)s] - %(message)s",
                    handlers=[
                        logging.FileHandler(filename="discord.log", encoding="utf-8", mode="a+"),
                              logging.StreamHandler(stream=sys.stdout)
                    ])

async def add_reactions(msg):
    """
    This function acts as a helper to add reactions to a message.
    :param msg: discord.ext.commands.Message object
    :return: void
    """
    emojis = ["\U0001F1FF\U0001F1E6",   #South African Flag
              "\U0001F1E8\U0001F1F3",   #Chinese Flag
              "\U0001F1E6\U0001F1FA",   #Australian Flag
              "\U0001F1EA\U0001F1FA",   #European Flag
              "\U0001F1FA\U0001F1F8",   #United States Flag
              "\U0001F1E7\U0001F1F7"]   #Brazilian Flag
    for emoji in emojis:
        await msg.add_reaction(emoji)
    return


class Commands(commands.Cog):
    """
    The Commands class is a cog implementation that acts as a wrapper for generic commands.
    More specific functionalities can be found in their own classes.
    Note: This class modifies environment variables! Check that they're present if something breaks.
    """
    def __init__(self, bot):
        """
        :param bot: discord.ext.commands.Bot object
        """
        self.bot = bot
        self.mngr = DatabaseManager()
        self.lvl_mgr = LevelManager(self.bot)

    @commands.hybrid_command(
        description="Send the embed message that will be used for reaction roles.")
    @check_perms()
    async def setup(self, ctx):
        """
        This function/command sends an embed message to a specific channel and adds reactions to it.
        These are then used to assign roles.
        :param ctx: discord.ext.commands.Context object
        :return: void
        """
        load_dotenv(override=True)
        stored_msg_id = os.getenv("REACTION_ROLES_MESSAGE_ID")

        guild = ctx.guild
        channel = guild.get_channel(int(os.getenv("REACTION_ROLES_CHANNEL_ID")))

        async for msg in channel.history():
            if msg.author == channel.guild.me:
                if msg.id == int(stored_msg_id):
                    await ctx.send("Message already exists!")
                    return

        new_msg = await channel.send(embed=await build_setup_embed())
        await add_reactions(new_msg)
        await ctx.send("Message sent successfully!")

        dotenv_path = Path(".env")
        set_key(dotenv_path,"REACTION_ROLES_MESSAGE_ID", str(new_msg.id))

    @commands.hybrid_command(
        description="Check how many and which events you have attended."
    )
    async def events(self, ctx, user: discord.User):
        is_high_rank = any(role.id in permitted_roles for role in ctx.author.roles)
        is_self = user.id == ctx.author.id

        if not (is_high_rank or is_self):
            await ctx.send("You don't have enough permissions to run this command for another user!", delete_after=5)
            return

        res = self.mngr.get_events_by_user(user.id)
        await ctx.send("An error occurred while getting events by user.") if res == -1 else await ctx.send(embed=await build_events_embed(res, user, ctx))

    @commands.hybrid_command(
        description="Get a joke. (This is from an API and randomised.)"
    )
    async def joke(self, ctx):
        joke_obj = Jokes()
        joke = joke_obj.get_joke()
        await ctx.send(joke)

    @commands.hybrid_command(
        description="Check your current level and progress towards the next one."
    )
    async def profile(self, ctx):
        user = ctx.author
        current_lvl = self.mngr.get_user_level(user.id)

        if not self.mngr.get_user(user.id):
            self.mngr.add_user(user.id)
            current_lvl = self.mngr.get_user_level(user.id)

        current_xp = self.mngr.get_user_xp(user.id)
        xp_needed = self.lvl_mgr.get_lvl_reqs()[current_lvl + 1]
        previous_xp_needed = self.lvl_mgr.get_lvl_reqs()[current_lvl]

        img_buffer = create_profile_card(user.display_name, current_lvl, current_xp, xp_needed, previous_xp_needed)
        file = discord.File(img_buffer, filename="profile.png")

        await ctx.send(file=file)

    @commands.hybrid_command(
        description="Check another user's profile"
    )
    @check_perms()
    async def uprofile(self, ctx, user: discord.User):
        current_lvl = self.mngr.get_user_level(user.id)

        if not self.mngr.get_user(user.id):
            self.mngr.add_user(user.id)
            current_lvl = self.mngr.get_user_level(user.id)

        current_xp = self.mngr.get_user_xp(user.id)
        xp_needed = self.lvl_mgr.get_lvl_reqs()[current_lvl + 1]

        img_buffer = create_profile_card(user.display_name, current_lvl, current_xp, xp_needed)
        file = discord.File(img_buffer, filename="profile.png")

        await ctx.send(file=file)

    @commands.hybrid_command(
        description="Check the bot's status."
    )
    @check_perms()
    async def status(self, ctx):
        status = os.getenv("STATUS")
        if status == "development":
            await ctx.send("This is the development version of Arryn Aid.\n"
                            "-# Not intended for public use.")
            return
        msg = "This is the production version of Baratheon Backup."
        if os.path.isfile("data/db.sqlite"):
            msg += "\nDatabase found."
        await ctx.send(msg)

async def setup(bot):
    """
    This function adds all the commands to the bot.
    :param bot: discord.ext.commands.Bot object
    :return: void
    """
    await bot.add_cog(Commands(bot))
