import asyncio
import random
import re
import secrets
from io import BytesIO
from urllib.parse import quote

import aiohttp
import discord
from discord.ext import commands
from discord.ext.commands import clean_content

from utils import (
    argparser,
    default,
    http,
    permissions,
)


async def random_image_api(ctx, url, endpoint):
    try:
        r = await http.get(url, res_method="json", no_cache=True)
    except aiohttp.ClientConnectorError:
        return await ctx.send("The API seems to be down...")
    except aiohttp.ContentTypeError:
        return await ctx.send("The API returned an error or didn't return JSON...")

    await ctx.send(r[endpoint])


async def api_img_creator(ctx, url, filename, content=None):
    async with ctx.channel.typing():
        req = await http.get(url, res_method="read")

        if req is None:
            return await ctx.send("I couldn't create the image ;-;")

        bio = BytesIO(req)
        bio.seek(0)
        await ctx.send(content=content, file=discord.File(bio, filename=filename))


class FunCommands(commands.Cog, name="有趣指令"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command(name="貓", aliases=["cat"])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def cat(self, ctx):
        """ 發送一張隨機的貓照片 """
        await random_image_api(ctx, 'https://api.alexflipnote.dev/cats', 'file')

    @commands.command(name="狗", aliases=["dog"])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dog(self, ctx):
        """ 發送一張隨機的狗照片 """
        await random_image_api(ctx, 'https://api.alexflipnote.dev/dogs', 'file')

    @commands.command(name="鳥", aliases=["bird", "birb"])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def bird(self, ctx):
        """ 發送一張隨機的鳥照片 """
        await random_image_api(ctx, 'https://api.alexflipnote.dev/birb', 'file')

    @commands.command(name="鴨子", aliases=["duck"])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, ctx):
        """ 發送一張隨機的鴨子照 """
        await random_image_api(ctx, 'https://random-d.uk/api/v1/random', 'url')

    @commands.command(name="翻硬幣", aliases=['flip', 'coin'])
    async def coin_flip(self, ctx):
        """ 翻硬幣! """
        coin_sides = ['Heads', 'Tails']
        await ctx.send(f"**{ctx.author.name}** flipped a coin and got **{random.choice(coin_sides)}**!")

    @commands.command()
    async def f(self, ctx, *, text: clean_content = None):
        """ Press F to pay respect """
        hearts = ['❤', '💛', '💚', '💙', '💜']
        reason = f"for **{text}** " if text else ""
        await ctx.send(f"**{ctx.author.name}** has paid their respect {reason}{random.choice(hearts)}")

    @commands.command()
    async def supreme(self, ctx, *, text: clean_content(fix_channel_mentions=True)):
        """ 製作一個假的 Supreme logo

        Arguments:
            --dark | Make the background to dark colour
            --light | Make background to light and text to dark colour
        """
        parser = argparser.Arguments()
        parser.add_argument('input', nargs="+", default=None)
        parser.add_argument('-d', '--dark', action='store_true')
        parser.add_argument('-l', '--light', action='store_true')

        args, valid_check = parser.parse_args(text)
        if not valid_check:
            return await ctx.send(args)

        input_text = quote(' '.join(args.input))
        if len(input_text) > 500:
            return await ctx.send(f"**{ctx.author.name}**, the Supreme API is limited to 500 characters, sorry.")

        dark_or_light = ""
        if args.dark:
            dark_or_light = "dark=true"
        if args.light:
            dark_or_light = "light=true"
        if args.dark and args.light:
            return await ctx.send(f"**{ctx.author.name}**, you can't define both --dark and --light, sorry..")

        await api_img_creator(ctx, f"https://api.alexflipnote.dev/supreme?text={input_text}&{dark_or_light}", "supreme.png")

    @commands.command(name="顏色", aliases=['colour', 'color'])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def colour(self, ctx, colour: str):
        """ 查看顏色的 HEX 詳細資訊 """
        async with ctx.channel.typing():
            if not permissions.can_embed(ctx):
                return await ctx.send("I can't embed in this channel ;-;")

            if colour == "random":
                colour = "%06x" % random.randint(0, 0xFFFFFF)

            if colour[:1] == "#":
                colour = colour[1:]

            if not re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', colour):
                return await ctx.send("You're only allowed to enter HEX (0-9 & A-F)")

            try:
                r = await http.get(f"https://api.alexflipnote.dev/colour/{colour}", res_method="json", no_cache=True)
            except aiohttp.ClientConnectorError:
                return await ctx.send("The API seems to be down...")
            except aiohttp.ContentTypeError:
                return await ctx.send("The API returned an error or didn't return JSON...")

            embed = discord.Embed(colour=r["int"])
            embed.set_thumbnail(url=r["image"])
            embed.set_image(url=r["image_gradient"])

            embed.add_field(name="HEX", value=r['hex'], inline=True)
            embed.add_field(name="RGB", value=r['rgb'], inline=True)
            embed.add_field(name="Int", value=r['int'], inline=True)
            embed.add_field(name="Brightness", value=r['brightness'], inline=True)

            await ctx.send(embed=embed, content=f"{ctx.invoked_with.title()} name: **{r['name']}**")

    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def urban(self, ctx, *, search: clean_content):
        """ 尋找你字的『最佳』定義 """
        async with ctx.channel.typing():
            try:
                url = await http.get(f'https://api.urbandictionary.com/v0/define?term={search}', res_method="json")
            except Exception:
                return await ctx.send("Urban API returned invalid data... might be down atm.")

            if not url:
                return await ctx.send("I think the API broke...")

            if not len(url['list']):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(url['list'], reverse=True, key=lambda g: int(g["thumbs_up"]))[0]

            definition = result['definition']
            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(' ', 1)[0]
                definition += '...'

            await ctx.send(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")

    @commands.command(name="反轉", aliases=["reverse"])
    async def reverse(self, ctx, *, text: str):
        """ !轉反會都入輸有所
        Everything you type after reverse will of course, be reversed
        """
        t_rev = text[::-1].replace("@", "@\u200B").replace("&", "&\u200B")
        await ctx.send(f"🔁 {t_rev}")

    @commands.command(name="密碼", aliases=["password"])
    async def password(self, ctx, n_bytes: int = 18):
        """ 為你生成一串隨機的密碼字串

        This returns a random URL-safe text string, containing nbytes random bytes.
        The text is Base64 encoded, so on average each byte results in approximately 1.3 characters.
        """
        if n_bytes not in range(3, 1401):
            return await ctx.send("I only accept any numbers between 3-1400")
        if hasattr(ctx, 'guild') and ctx.guild is not None:
            await ctx.send(f"Sending you a private message with your random generated password **{ctx.author.name}**")
        await ctx.author.send(f"🎁 **Here is your password:**\n{secrets.token_urlsafe(n_bytes)}")

    @commands.command()
    async def rate(self, ctx, *, thing: clean_content):
        """ Rates what you desire """
        rate_amount = random.uniform(0.0, 100.0)
        await ctx.send(f"I'd rate `{thing}` a **{round(rate_amount, 4)} / 100**")

    @commands.command(name="啤酒", aliases=["beer"])
    async def beer(self, ctx, user: discord.Member = None, *, reason: clean_content = ""):
        """ 給某人一杯啤酒! 🍻 """
        if not user or user.id == ctx.author.id:
            return await ctx.send(f"**{ctx.author.name}**: paaaarty!🎉🍺")
        if user.id == self.bot.user.id:
            return await ctx.send("*drinks beer with you* 🍻")
        if user.bot:
            return await ctx.send(f"I would love to give beer to the bot **{ctx.author.name}**, but I don't think it will respond to you :/")

        beer_offer = f"**{user.name}**, you got a 🍺 offer from **{ctx.author.name}**"
        beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
        msg = await ctx.send(beer_offer)

        def reaction_check(m):
            if m.message_id == msg.id and m.user_id == user.id and str(m.emoji) == "🍻":
                return True
            return False

        try:
            await msg.add_reaction("🍻")
            await self.bot.wait_for('raw_reaction_add', timeout=30.0, check=reaction_check)
            await msg.edit(content=f"**{user.name}** and **{ctx.author.name}** are enjoying a lovely beer together 🍻")
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.send(f"well, doesn't seem like **{user.name}** wanted a beer with you **{ctx.author.name}** ;-;")
        except discord.Forbidden:
            # Yeah so, bot doesn't have reaction permission, drop the "offer" word
            beer_offer = f"**{user.name}**, you got a 🍺 from **{ctx.author.name}**"
            beer_offer = beer_offer + f"\n\n**Reason:** {reason}" if reason else beer_offer
            await msg.edit(content=beer_offer)

    @commands.command(aliases=['howhot', 'hot'])
    async def hot_calc(self, ctx, *, user: discord.Member = None):
        """ 隨機回傳一個百分比來代表一個人有多 hot """
        user = user or ctx.author

        random.seed(user.id)
        r = random.randint(1, 100)
        hot = r / 1.17

        emoji = "💔"
        if hot > 25:
            emoji = "❤"
        if hot > 50:
            emoji = "💖"
        if hot > 75:
            emoji = "💞"

        await ctx.send(f"**{user.name}** is **{hot:.2f}%** hot {emoji}")

    @commands.command(aliases=['noticemesenpai'])
    async def notice_me(self, ctx):
        """ Notice me senpai! owo """
        if not permissions.can_upload(ctx):
            return await ctx.send("I cannot send images here ;-;")

        bio = BytesIO(await http.get("https://i.alexflipnote.dev/500ce4.gif", res_method="read"))
        await ctx.send(file=discord.File(bio, filename="noticeme.gif"))

    @commands.command(name="老虎機", aliases=['slots', 'bet'])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def slot(self, ctx):
        """ Roll the slot machine """
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        slotmachine = f"**[ {a} {b} {c} ]\n{ctx.author.name}**,"

        if a == b == c:
            await ctx.send(f"{slotmachine} All matching, you won! 🎉")
        elif (a == b) or (a == c) or (b == c):
            await ctx.send(f"{slotmachine} 2 in a row, you won! 🎉")
        else:
            await ctx.send(f"{slotmachine} No match, you lost 😢")


def setup(bot):
    bot.add_cog(FunCommands(bot))
