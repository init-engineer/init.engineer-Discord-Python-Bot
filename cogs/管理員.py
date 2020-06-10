import time
import aiohttp
import discord
import importlib
import os
import sys

from discord.ext import commands
from utils import permissions, default, http, dataIO


class 管理員(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")
        self._last_result = None

    @commands.command()
    async def 我是管理者嗎(self, ctx):
        """ 我是管理者嗎？ """
        if ctx.author.id in self.config.owners:
            return await ctx.send(f"不，**{ctx.author.name}** 你是個非常好的管理者！✅")

        # Please do not remove this part.
        # I would love to be credited as the original creator of the source code.
        #   -- AlexFlipnote
        if ctx.author.id == 86477779717066752:
            return await ctx.send(f"Well kinda **{ctx.author.name}**.. you still own the source code")

        await ctx.send(f"不，真的不，**{ctx.author.name}** 你什麼都不是。")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 加載cogs(self, ctx, name: str):
        """ 加載 cogs 擴展功能。 """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(f"汪嗚 ... 窩好像失敗惹 。･ﾟ･(つд`ﾟ)･ﾟ･。 他吐ㄌ一堆窩看不懂ㄉ咚咚{default.traceback_maker(e)}")
        await ctx.send(f"窩成功ㄉ加載了 **{name}.py** 哦汪 (`・ω・´)。")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 卸載cogs(self, ctx, name: str):
        """ 卸載 cogs 擴展功能。 """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"窩成功ㄉ卸載了 **{name}.py** 哦汪 (`・ω・´)。")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 重新載入cogs(self, ctx, name: str):
        """ 重新載入 cogs 擴展功能。 """
        try:
            self.bot.reload_extension(f"cogs.{name}")
        except Exception as e:
            return await ctx.send(default.traceback_maker(e))
        await ctx.send(f"窩成功ㄉ重新載入了 **{name}.py** 哦汪 (`・ω・´)。")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 重新載入所有cogs(self, ctx):
        """ 重新載入所有的 cogs 擴展功能。 """
        error_collection = []
        for file in os.listdir("cogs"):
            if file.endswith(".py"):
                name = file[:-3]
                try:
                    self.bot.reload_extension(f"cogs.{name}")
                except Exception as e:
                    error_collection.append(
                        [file, default.traceback_maker(e, advance=False)]
                    )

        if error_collection:
            output = "\n".join([f"**{g[0]}** ```diff\n- {g[1]}```" for g in error_collection])
            return await ctx.send(
                f"汪嗚 ... 窩嘗試重新載入所有擴展功能，能夠重新載入這些咚咚 "
                f"但是有些咚咚失敗惹嗚 ... 。･ﾟ･(つд`ﾟ)･ﾟ･。\n\n{output}"
            )

        await ctx.send(f"窩已經成功重新載入所～有的 cogs 哦汪 (`・ω・´)。")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 重新載入utils(self, ctx, name: str):
        """ 重新載入 utils 模組。 """
        name_maker = f"utils/{name}.py"
        try:
            module_name = importlib.import_module(f"utils.{name}")
            importlib.reload(module_name)
        except ModuleNotFoundError:
            return await ctx.send(f"汪嗚 ... 窩找不到 **{name_maker}** 這個東西呐汪 。･ﾟ･(つд`ﾟ)･ﾟ･。")
        except Exception as e:
            error = default.traceback_maker(e)
            return await ctx.send(f"汪嗚 ... 載入模組 **{name_maker}** 的時候，好像怪怪的吶 。･ﾟ･(つд`ﾟ)･ﾟ･ 有怪怪的東西窩看不懂\n{error}")
        await ctx.send(f"窩已經成功重新載入 **{name_maker}** 哦汪 (`・ω・´)。")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 重新啟動(self, ctx):
        """ 重新啟動機器人。 """
        await ctx.send('我現在要睡覺覺惹，主人晚安汪  ... (\*´з｀\*)')
        time.sleep(1)
        sys.exit(0)

    @commands.command()
    @commands.check(permissions.is_owner)
    async def 傳訊息給(self, ctx, user_id: int, *, message: str):
        """ 傳訊息給使用者。 """
        user = self.bot.get_user(user_id)
        if not user:
            return await ctx.send(f"汪嗚、我好像找不到 **{user_id}** 是誰呢 ... ( ˘･з･)")

        try:
            await user.send(message)
            await ctx.send(f"✉️ 窩已經成功把訊息傳給了 **<@{user_id}>** 哦汪 d(`･∀･)b")
        except discord.Forbidden:
            await ctx.send("汪嗚、我好像被這個人給封鎖惹嗚 ... (´;ω;`)")

    @commands.group()
    @commands.check(permissions.is_owner)
    async def 切換(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    @切換.command(name="狀態")
    @commands.check(permissions.is_owner)
    async def 幫我換狀態(self, ctx, *, playing: str):
        """ 幫機器人換其他顯示狀態。 """
        if self.config.status_type == "閒置":
            status_type = discord.Status.idle
        elif self.config.status_type == "請勿打擾":
            status_type = discord.Status.dnd
        else:
            status_type = discord.Status.online

        if self.config.playing_type == "收聽中":
            playing_type = 2
        elif self.config.playing_type == "觀看中":
            playing_type = 3
        else:
            playing_type = 0

        try:
            await self.bot.change_presence(
                activity=discord.Activity(type=playing_type, name=playing),
                status=status_type
            )
            dataIO.change_value("config.json", "正在玩", playing)
            await ctx.send(f"我把自己的狀態換成了「**{playing}**」哦汪 (`・ω・´)")
        except discord.InvalidArgument as err:
            await ctx.send(err)
        except Exception as e:
            await ctx.send(e)

    @切換.command(name="名字")
    @commands.check(permissions.is_owner)
    async def 幫我換名字(self, ctx, *, name: str):
        """ 幫機器人換個新名字。 """
        try:
            await self.bot.user.edit(username=name)
            await ctx.send(f"嗚 ... 從今以後我的名字就叫做「**{name}**」哦汪 (`・ω・´)")
        except discord.HTTPException as err:
            await ctx.send(f"汪嗚 ... 換名字的時候，好像怪怪的吶 。･ﾟ･(つд`ﾟ)･ﾟ･ 有怪怪的東西窩看不懂\n{err}")


    @切換.command(name="暱稱")
    @commands.check(permissions.is_owner)
    async def 幫我換暱稱(self, ctx, *, name: str = None):
        """ 幫機器人換個新暱稱。 """
        try:
            await ctx.guild.me.edit(nick=name)
            if name:
                await ctx.send(f"嗚 ... 從今以後我的暱稱就叫做「**{name}**」哦汪 (`・ω・´)")
            else:
                await ctx.send("嗚 ... 從今以後還是叫窩ㄉ名字就好哦汪 (`・ω・´)")
        except Exception as err:
            await ctx.send(f"汪嗚 ... 換暱稱的時候，好像怪怪的吶 。･ﾟ･(つд`ﾟ)･ﾟ･ 有怪怪的東西窩看不懂\n{err}")

    @切換.command(name="大頭貼")
    @commands.check(permissions.is_owner)
    async def 幫我換大頭貼(self, ctx, url: str = None):
        """ 幫機器人換個新大頭貼。 """
        if url is None and len(ctx.message.attachments) == 1:
            url = ctx.message.attachments[0].url
        else:
            url = url.strip('<>') if url else None

        try:
            bio = await http.get(url, res_method="read")
            await self.bot.user.edit(avatar=bio)
            await ctx.send(f"嗚 ... 窩換了新的大頭貼哦汪 (`・ω・´) 窩換成這張:\n{url}")
        except aiohttp.InvalidURL:
            await ctx.send("汪嗚 ... 這個網址打不開啦 -`д´-")
        except discord.InvalidArgument:
            await ctx.send("汪嗚 ... 這個網址好像不是圖片啦 -`д´-")
        except discord.HTTPException as err:
            await ctx.send(f"汪嗚 ... 換大頭貼的時候，好像怪怪的吶 。･ﾟ･(つд`ﾟ)･ﾟ･ 有怪怪的東西窩看不懂\n{err}")
        except TypeError:
            await ctx.send("汪嗚 ... 尼該不會不知道怎麼幫窩換大頭貼ㄅ，科科笑 σ`∀´)σ")


def setup(bot):
    bot.add_cog(管理員(bot))
