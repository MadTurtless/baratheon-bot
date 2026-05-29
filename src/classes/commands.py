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
from src.utils.helper import build_setup_embed, check_perms, build_events_embed
from src.utils.helper import permitted_roles

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

    @commands.hybrid_command()
    async def events(self, ctx, user: discord.User):
        is_high_rank = any(role.id in permitted_roles for role in ctx.author.roles)
        is_self = user.id == ctx.author.id

        if not (is_high_rank or is_self):
            await ctx.send("You don't have enough permissions to run this command for another user!", delete_after=5)
            return

        res = self.mngr.get_events_by_user(user.id)
        await ctx.send("An error occurred while getting events by user.") if res == -1 else await ctx.send(embed=await build_events_embed(res, user, ctx))

    @commands.hybrid_command()
    async def joke(self, ctx):
        joke_obj = Jokes()
        joke = joke_obj.get_joke()
        await ctx.send(joke)

    @commands.hybrid_command()
    @check_perms()
    async def status(self, ctx):
        status = os.getenv("STATUS")
        if status == "development":
            await ctx.send("This is the development version of Arryn Aid.\n"
                            "-# Not intended for public use.")
            return
        await ctx.send("This is the production version of Arryn Aid.")

async def setup(bot):
    """
    This function adds all the commands to the bot.
    :param bot: discord.ext.commands.Bot object
    :return: void
    """
    await bot.add_cog(Commands(bot))
