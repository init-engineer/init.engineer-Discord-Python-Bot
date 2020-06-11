import time
import discord
import psutil
import os

from datetime import datetime
from discord.ext import commands
from utils import default


class Information(commands.Cog, name="資訊"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def ping(self, ctx):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        message = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command(name="邀請", aliases=['invite', 'joinme', 'join', 'botinvite'])
    async def invite(self, ctx):
        """ 邀請我到你的伺服器 """
        await ctx.send(f"**{ctx.author.name}**, use this URL to invite me\n<{discord.utils.oauth_url(self.bot.user.id)}>")

    @commands.command(name="程式碼", aliases=['source'])
    async def source(self, ctx):
        """ Check out my source code <3 """
        # Do not remove this command, this has to stay due to the GitHub LICENSE.
        # TL:DR, you have to disclose source according to MIT.
        # Reference: https://github.com/AlexFlipnote/discord_bot.py/blob/master/LICENSE
        await ctx.send(f"**{ctx.bot.user}** is powered by this source code:\nhttps://github.com/AlexFlipnote/discord_bot.py")

    @commands.command(name="伺服器", aliases=['supportserver', 'feedbackserver'])
    async def botserver(self, ctx):
        """ 獲取伺服器的邀請連結! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 86484642730885120:
            return await ctx.send(f"**Here you go {ctx.author.name} 🍻\n<{self.config.botserver}>**")

        await ctx.send(f"**{ctx.author.name}** this is my home you know :3")

    @commands.command(name="關於", aliases=['about', 'info', 'stats', 'status'])
    async def about(self, ctx):
        """ 關於機器人 """
        ram_usage = self.process.memory_full_info().rss / 1024 ** 2
        avg_members = round(len(self.bot.users) / len(self.bot.guilds))

        embed_colour = discord.Embed.Empty
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            embed_colour = ctx.me.top_role.colour

        embed = discord.Embed(colour=embed_colour)
        embed.set_thumbnail(url=ctx.bot.user.avatar_url)
        embed.add_field(name="Last boot", value=default.timeago(datetime.now() - self.bot.uptime), inline=True)
        embed.add_field(
            name=f"Developer{'' if len(self.config.owners) == 1 else 's'}",
            value=', '.join([str(self.bot.get_user(x)) for x in self.config.owners]),
            inline=True)
        embed.add_field(name="Library", value="discord.py", inline=True)
        embed.add_field(name="Servers", value=f"{len(ctx.bot.guilds)} ( avg: {avg_members} users/server )", inline=True)
        embed.add_field(name="Commands loaded", value=str(len([x.name for x in self.bot.commands])), inline=True)
        embed.add_field(name="RAM", value=f"{ram_usage:.2f} MB", inline=True)

        await ctx.send(content=f"ℹ About **{ctx.bot.user}** | **{self.config.version}**", embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
