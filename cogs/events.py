import discord
import psutil
import os

from datetime import datetime
from discord.ext import commands
from discord.ext.commands import errors
from utils import default

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            await ctx.send_help(helper)

        elif isinstance(err, errors.CommandInvokeError):
            error = default.traceback_maker(err.original)

            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send(
                    f"You attempted to make the command display more than 2,000 characters...\n"
                    f"Both error and command will be ignored."
                )

            await ctx.send(f"There was an error processing the command ;-;\n{error}")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send(f"You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown... try again in {err.retry_after:.2f} seconds.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if not self.config.join_message:
            return

        try:
            to_send = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
        except IndexError:
            pass
        else:
            await to_send.send(self.config.join_message)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        try:
            print(f"{ctx.guild.name} > {ctx.author} > {ctx.message.clean_content}")
        except AttributeError:
            print(f"私人訊息 > {ctx.author} > {ctx.message.clean_content}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ 機器人啟動完成後會執行的功能。 """
        if not hasattr(self.bot, 'uptime'):
            self.bot.uptime = datetime.utcnow()

        # Indicate that the bot has successfully booted up
        print(f'準備就緒: {self.bot.user} | 服務數量: {len(self.bot.guilds)}')

        # Check if user desires to have something other than online
        if self.config.status_type == "閒置":
            status_type = discord.Status.idle
        elif self.config.status_type == "請勿打擾":
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        # Check if user desires to have a different type of playing status
        if self.config.playing_type == "收聽中":
            playing_type = 2
        elif self.config.playing_type == "觀看中":
            playing_type = 3
        else:
            playing_type = 0

        await self.bot.change_presence(
            activity=discord.Activity(type=playing_type, name=self.config.playing),
            status=status_type
        )

    # Author by @bbb543123
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        get_roles = 基本功能.角色列表資料()

        if payload.message_id == 705286880920338535:

            guild_id = payload.guild_id
            guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
            roles = []
            for role in guild.roles:
                if not role.permissions.administrator:
                    roles.append(role.name)

            if payload.emoji.name == "t_":
                role = discord.utils.get(guild.roles, name="yellow_man")
                print(role)
            # if role != None:
            #     member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
            #     if member != None:
            #         await member.add_roles(role)
            # if role_name = emoji_name
            # role = discord.utils.find(lambda r: r.name == payload.emoji.name, guild.roles)
            #
            # if role is not None:
            #     member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
            #     await member.add_roles(role)


def setup(bot):
    bot.add_cog(Events(bot))
