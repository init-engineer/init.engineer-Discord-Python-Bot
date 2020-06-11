import discord

from io import BytesIO
from utils import default
from discord.ext import commands


class 基本功能(commands.Cog, name="基本功能"):
    def __init__(self, bot):
        self.bot = bot
        self.config = default.get("config.json")

    @commands.command(name="我的大頭貼", aliases=['avatar'])
    @commands.guild_only()
    async def avatar(self, ctx, *, user: discord.Member = None):
        """ 讓機器人告訴你，你的大頭貼是什麼？ """
        user = user or ctx.author
        await ctx.send(f"嗨嗨汪、**{user.name}**\r\n你的大頭貼是這張哦 ٩(｡・ω・｡)و！\r\n{user.avatar_url_as(size=1024)}")

    @commands.command(name="角色列表報告")
    @commands.guild_only()
    async def 角色列表報告(self, ctx):
        """ 獲得頻道當中所有角色詳細資訊的報告。 """
        allroles = "```\r\nNUM | USERS |         ID         |       NAME\r\n----+-------+--------------------+------------------------\r\n"
        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            if role.name != '@everyone':
                allroles += f"{str(num).rjust(3)} | {str(len(role.members)).rjust(5)} | {role.id} | {role.name}\r\n"
            else:
                allroles += f"----+-------+--------------------+------------------------\r\n{str(num).rjust(3)} | {str(len(role.members)).rjust(5)} | {role.id} |  全部```"
        await ctx.send(allroles)
        # data = BytesIO(allroles.encode('utf-8'))
        # await ctx.send(content=f"**{ctx.guild.name}**頻道內所有角色的詳細資訊：", file=discord.File(data, filename=f"{default.timetext('Roles')}"))

    @commands.command(name="角色列表資料", aliases=["roles"])
    @commands.guild_only()
    async def roles(self, ctx):
        """ 獲得頻道當中所有角色詳細資訊的資料。 """
        all_roles = ""

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            all_roles += f"[{str(num).zfill(2)}] {role.id}\t{role.name}\t[ Users: {len(role.members)} ]\r\n"

        data = BytesIO(all_roles.encode('utf-8'))
        await ctx.send(content=f"Roles in **{ctx.guild.name}**", file=discord.File(data, filename=f"{default.timetext('Roles')}"))

    @commands.command(name="我什麼時候加入的", aliases=["joindat", "joined"])
    @commands.guild_only()
    async def join_date(self, ctx, *, user: discord.Member = None):
        """ 讓機器人告訴你，你什麼時候加入頻道的？ """
        user = user or ctx.author

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar_url)
        embed.description = f'嗨嗨汪、**{user}**\n你是從 {default.date(user.joined_at)} 開始加入 **{ctx.guild.name}** 這頻道的唷 ٩(｡・ω・｡)و！'
        await ctx.send(embed=embed)

    @commands.command(name="確認使用者上線狀態", aliases=["mods"])
    @commands.guild_only()
    async def mods(self, ctx):
        """ 檢查當前伺服器當中，有哪些管理員還在線上。 """
        message = ""
        online, idle, dnd, offline = [], [], [], []

        for user in ctx.guild.members:
            if ctx.channel.permissions_for(user).kick_members or \
               ctx.channel.permissions_for(user).ban_members:
                if not user.bot and user.status is discord.Status.online:
                    online.append(f"**{user}**")
                if not user.bot and user.status is discord.Status.idle:
                    idle.append(f"**{user}**")
                if not user.bot and user.status is discord.Status.dnd:
                    dnd.append(f"**{user}**")
                if not user.bot and user.status is discord.Status.offline:
                    offline.append(f"**{user}**")

        if online:
            message += f"🟢 {', '.join(online)}\n"
        if idle:
            message += f"🟡 {', '.join(idle)}\n"
        if dnd:
            message += f"🔴 {', '.join(dnd)}\n"
        if offline:
            message += f"⚫ {', '.join(offline)}\n"

        await ctx.send(f"**{ctx.guild.name}**\n{message}")

    @commands.group(name="查看頻道詳細資訊")
    @commands.guild_only()
    async def server(self, ctx):
        """ 查看頻道的資訊。 """
        if ctx.invoked_subcommand is None:
            findbots = sum(1 for member in ctx.guild.members if member.bot)

            embed = discord.Embed()

            if ctx.guild.icon:
                embed.set_thumbnail(url=ctx.guild.icon_url)
            if ctx.guild.banner:
                embed.set_image(url=ctx.guild.banner_url_as(format="png"))

            embed.add_field(name="頻道名稱", value=ctx.guild.name, inline=True)
            embed.add_field(name="頻道 ID", value=ctx.guild.id, inline=True)
            embed.add_field(name="會員人數", value=ctx.guild.member_count, inline=True)
            embed.add_field(name="機器人數量", value=str(findbots), inline=True)
            embed.add_field(name="管理員", value=ctx.guild.owner, inline=True)
            embed.add_field(name="位址", value=ctx.guild.region, inline=True)
            embed.add_field(name="建立於", value=default.date(ctx.guild.created_at), inline=True)
            await ctx.send(content=f"ℹ 這是 **{ctx.guild.name}** 頻道的基本資訊哦汪嗚 ٩(｡・ω・｡)و", embed=embed)

    @server.command(name="大頭貼", aliases=["icon"])
    async def server_avatar(self, ctx):
        """ 取得當前伺服器的大頭貼。 """
        if not ctx.guild.icon:
            return await ctx.send(f"嗚 ... **{ctx.guild.name}**好像還沒放大頭貼呢汪 _(:3 」∠ )_")
        await ctx.send("{ctx.guild.icon_url_as(size=1024)}")

    @server.command(name="橫幅", aliases=["banner"])
    async def server_banner(self, ctx):
        """ 取得當前伺服器的橫幅圖片。 """
        if not ctx.guild.banner:
            return await ctx.send(f"嗚 ... **{ctx.guild.name}**好像還沒放橫幅圖片呢汪 _(:3 」∠ )_")
        await ctx.send("{ctx.guild.banner_url_as(format='png')}")

    @commands.command(name="我想看看我自己", aliases=["user"])
    @commands.guild_only()
    async def user_info(self, ctx, *, user: discord.Member = None):
        """ 取得使用者自己的資訊 """
        user = user or ctx.author

        show_roles = ', '.join(
            [f"<@&{x.id}>" for x in sorted(user.roles, key=lambda x: x.position, reverse=True) if x.id != ctx.guild.default_role.id]
        ) if len(user.roles) > 1 else '空空如也'

        embed = discord.Embed(colour=user.top_role.colour.value)
        embed.set_thumbnail(url=user.avatar_url)

        embed.add_field(name="名字", value=user, inline=True)
        embed.add_field(name="暱稱", value=user.nick if hasattr(user, "nick") else "無", inline=True)
        embed.add_field(name="建立帳號於", value=default.date(user.created_at), inline=True)
        embed.add_field(name="加入伺服器於", value=default.date(user.joined_at), inline=True)

        embed.add_field(
            name="身份組",
            value=show_roles,
            inline=False
        )

        await ctx.send(content=f"ℹ 汪嗚！窩找到了<@{user.id}>的名片哦 ٩(｡・ω・｡)و", embed=embed)


def setup(bot):
    bot.add_cog(基本功能(bot))
