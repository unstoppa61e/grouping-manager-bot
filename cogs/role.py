import discord
from discord.ext import commands
import asyncio


class Role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = self.init_embed()

    def init_embed(self) -> discord.Embed():
        embed = discord.Embed()
        return embed

    def make_text(self, role_mention, author_mention) -> str:
        emoji = self.get_emoji()
        return f"新ロール、 {role_mention} が作成されました。\n\n"\
            f"各自、{emoji}にて、本ロールのオン・オフが可能です。\n\n"\
            f"{author_mention}\nこのロールが不要になりましたら、`!rm_role` コマンドを実行してください"\
            "（サーバとメンバーから、本ロールが削除されます）"
    
    def get_role_index_not_used(self, roles):
        num = 0
        while True:
            found = False
            for role in roles:
                if role.name == f"role{num}":
                    found = True
                    break
            if found == False:
                break
            num += 1
        return num
    
    def make_role_name(self, roles):
        role_index = self.get_role_index_not_used(roles)
        return f"role{role_index}"
    
    def get_emoji(self):
        return '✅'

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if not payload.emoji.name == self.get_emoji():
            return
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        await member.add_roles(self.role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.emoji.name == self.get_emoji():
            return
        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g: g.id == guild_id, self.bot.guilds)
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        await member.remove_roles(self.role)

    @commands.command()
    async def role(self, ctx):
        await self.bot.wait_until_ready()
        role_name = self.make_role_name(ctx.guild.roles)
        self.role = await ctx.guild.create_role(name=role_name)
        self.embed.description = self.make_text(self.role.mention, ctx.author.mention)
        self.embed.color = discord.Color.green()
        channel = ctx.channel
        msg = await ctx.send(embed=self.embed)
        self.msg_id = msg.id
        await msg.add_reaction(self.get_emoji())
        
        def check(reaction, user):
            are_same_messages = reaction.message.channel == msg.channel and reaction.message.id == msg.id
            return user == ctx.author and are_same_messages and (str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣')
        
        # timeout = 60 * 60 * 24 * 30 * 2
        # try:
        #     reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)
        # except asyncio.TimeoutError:
        #     self.embed.description = '募集から２カ月が経過したため、告知を締め切りました。'
        #     self.embed.color = discord.Color.red()
        #     await channel.send(embed=self.embed)
        # else:
        #     capacity_basis = 2 if str(reaction.emoji) == '2️⃣' else 3
        #     cached_msg = discord.utils.get(self.bot.cached_messages, id=msg.id)
        #     reactions = cached_msg.reactions
        #     users = []
        #     for reaction in reactions:
        #         if str(reaction.emoji) == '✋':
        #             reaction_users = await reaction.users().flatten()
        #             for user in reaction_users:
        #                 if user.bot:
        #                     continue
        #                 users.append(user.mention)
        #             break
        #     if len(users) < 2:
        #         self.embed.color = discord.Color.red()
        #         self.embed.description = 'マッチングに必要な人数が集まりませんでした。'
        #         await ctx.send(embed=self.embed)
        #         return
        #     random.shuffle(users)
        #     await self.send_invitation(ctx, users, capacity_basis)
                    
    
    


def setup(bot):
    bot.add_cog(Role(bot))
