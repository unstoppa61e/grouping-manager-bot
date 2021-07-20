import discord
from discord.ext import commands
import config
import asyncio
import random
import math


class Match(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = self.init_embed()

    def init_embed(self) -> discord.Embed():
        embed = discord.Embed()
        embed.color = discord.Color.green()
        return embed

    def make_text(self, author_mention) -> str:
        return f"マッチング希望者は、✋によるリアクションをお願いします。\n\n"\
            f"{author_mention}\n:two:で２名、:three:で３名を基本としたマッチングを行います。"
    
    def make_line(self, room_num, room_members):
        return f"{room_num}号室: {' / '.join(room_members)}\n"
    
    # async def send_invitation_two_basis(self, ctx, users):
    #     USERS_NUM = len(users)
    #     ROOMS_NUM = USERS_NUM // 2
    #     capacity_per_room = [2] * ROOMS_NUM
    #     if USERS_NUM % 2 == 1:
    #         capacity_per_room[0] += 1
    #     start_i = 0
    #     for i, capacity in enumerate(capacity_per_room, start=1):
    #         end_i = start_i + capacity
    #         self.embed.description = self.make_line(i, users[start_i:end_i])
    #         await ctx.send(embed=self.embed)
    #         start_i += capacity

    # async def send_invitation_three_basis(self, ctx, users):
    #     USERS_NUM = len(users)
    #     ROOMS_NUM = math.ceil(USERS_NUM / 3.0)
    #     capacity_per_room = [2] * ROOMS_NUM
    #     REMAINDER = USERS_NUM % 3
    #     for i in range(REMAINDER):
    #         capacity_per_room[i] += 1
    #     start_i = 0
    #     for i, capacity in enumerate(capacity_per_room, start=1):
    #         end_i = start_i + capacity
    #         self.embed.description = self.make_line(i, users[start_i:end_i])
    #         await ctx.send(embed=self.embed)
    #         start_i += capacity

    
    # async def send_invitation(self, ctx, users, capacity_basis):
    #     if capacity == 2:
    #         await self.send_invitation_two_basis(ctx, users)
    #     else:
    #         await self.send_invitation_three_basis(ctx, users)
    
    def make_capacity_per_room_two_basis(self, users_num, capacity_basis):
        ROOMS_NUM = users_num // 2
        capacity_per_room = [2] * ROOMS_NUM
        if users_num % 2 == 1:
            capacity_per_room[0] += 1
        return capacity_per_room

    def make_capacity_per_room_three_basis(self, users_num, capacity_basis):
        ROOMS_NUM = math.ceil(users_num / 3.0)
        capacity_per_room = [2] * ROOMS_NUM
        REMAINDER = users_num - 2 * ROOMS_NUM
        for i in range(REMAINDER):
            capacity_per_room[i] += 1
        return capacity_per_room


    def make_capacity_per_room(self, users_num, capacity_basis):
        if capacity_basis == 2:
            return self.make_capacity_per_room_two_basis(users_num, capacity_basis)
        return self.make_capacity_per_room_three_basis(users_num, capacity_basis)

    async def send_invitation(self, ctx, users, capacity_basis):
        capacity_per_room = self.make_capacity_per_room(len(users), capacity_basis)
        start_i = 0
        for i, capacity in enumerate(capacity_per_room, start=1):
            end_i = start_i + capacity
            self.embed.description = self.make_line(i, users[start_i:end_i])
            await ctx.send(embed=self.embed)
            start_i += capacity


    @commands.command()
    async def match(self, ctx):
        await self.bot.wait_until_ready()
        self.embed.description = self.make_text(ctx.author.mention)
        channel = ctx.channel
        msg = await ctx.send(embed=self.embed)
        emojis = ['✋', '2️⃣', '3️⃣']
        for emoji in emojis:
            await msg.add_reaction(emoji)
        
        def check(reaction, user):
            are_same_messages = reaction.message.channel == msg.channel and reaction.message.id == msg.id
            return user == ctx.author and are_same_messages and (str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣')
        
        timeout = 60 * 60 * 24 * 30 * 2
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            await channel.send('募集から２カ月が経過したため、告知を締め切りました。')
        else:
            capacity_basis = 2 if str(reaction.emoji) == '2️⃣' else 3
            cached_msg = discord.utils.get(self.bot.cached_messages, id=msg.id)
            reactions = cached_msg.reactions
            users = []
            for reaction in reactions:
                if str(reaction.emoji) == '✋':
                    reaction_users = await reaction.users().flatten()
                    for user in reaction_users:
                        users.append(user.mention)
                    break
            random.shuffle(users)
            await self.send_invitation(ctx, users, capacity_basis)
                    
    
    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, module_name):
        await ctx.send(f"モジュール{module_name}の再読み込みを開始します。")
        try:
            self.bot.reload_extension(module_name)
            await ctx.send(f"モジュール{module_name}の再読み込みを終了しました。")
        except (commands.errors.ExtensionNotLoaded, commands.errors.ExtensionNotFound, commands.errors.NoEntryPointError, commands.errors.ExtensionFailed) as e:
            await ctx.send(f"モジュール{module_name}の再読み込みに失敗しました。理由: {e}")
            return
    


def setup(bot):
    bot.add_cog(Match(bot))
