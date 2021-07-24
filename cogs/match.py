import discord
from discord.ext import commands
import asyncio
import random
import math
from cogs.role import Role


class Match(commands.Cog):
    REMOVER_EMOJI = '❌'
    WILLING_EMOJI = '✋'

    def __init__(self, bot):
        self.bot = bot

    def make_text(self, author_mention) -> str:
        return f"マッチング希望者は、{self.WILLING_EMOJI}によるリアクションをお願いします。\n"\
            f"{author_mention}\n:two:で２名、:three:で３名を基本としたマッチングを行います。"
    
    def make_line(self, room_num, room_members):
        return f"room{room_num}: {' / '.join(room_members)}\n"
    
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
        embed = discord.Embed()
        for i, capacity in enumerate(capacity_per_room, start=1):
            end_i = start_i + capacity
            embed.description = self.make_line(i, users[start_i:end_i])
            await ctx.send(embed=embed)
            start_i += capacity


    @commands.command()
    async def match(self, ctx):
        await self.bot.wait_until_ready()
        channel = ctx.channel
        embed = discord.Embed(
            description = self.make_text(ctx.author.mention),
            color = discord.Color.blue()
        )
        msg = await ctx.send(embed=embed)
        emojis = [self.WILLING_EMOJI, '2️⃣', '3️⃣']
        for emoji in emojis:
            await msg.add_reaction(emoji)
        
        def check(reaction, user):
            are_same_messages = reaction.message.channel == msg.channel and reaction.message.id == msg.id
            return user == ctx.author and are_same_messages and (str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣')
        
        timeout = 60 * 60 * 24 * 30 * 2
        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            embed.description = '募集から２カ月が経過したため、告知を締め切りました。'
            embed.color = discord.Color.red()
            await channel.send(embed=embed)
        else:
            capacity_basis = 2 if str(reaction.emoji) == '2️⃣' else 3
            cached_msg = discord.utils.get(self.bot.cached_messages, id=msg.id)
            reactions = cached_msg.reactions
            users = []
            for reaction in reactions:
                if str(reaction.emoji) == self.WILLING_EMOJI:
                    reaction_users = await reaction.users().flatten()
                    for user in reaction_users:
                        if user.bot:
                            continue
                        users.append(user.mention)
                    break
            if len(users) < 2:
                embed.color = discord.Color.red()
                embed.description = 'マッチングに必要な人数が集まりませんでした。'
                await ctx.send(embed=embed)
                return
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
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.name != self.WILLING_EMOJI:
            return
        if payload.user_id == self.bot.user.id:
            return
        await Role.handle_role_toggling_reaction(self, payload, False)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.emoji.name != self.WILLING_EMOJI:
            return
        if payload.user_id == self.bot.user.id:
            return
        await Role.handle_role_toggling_reaction(self, payload, True)


def setup(bot):
    bot.add_cog(Match(bot))
