import discord
from discord.ext import commands
import asyncio
import random
import math
from cogs.role import Role


class Match(commands.Cog):
    WILLING_EMOJI = '✋'
    TWO_EMOJI = '2️⃣'
    THREE_EMOJI = '3️⃣'

    def __init__(self, bot):
        self.bot = bot

    def make_text(self, author_mention) -> str:
        return f"マッチング希望者は、{self.WILLING_EMOJI}によるリアクションをお願いします"\
            "（通知用の新ロールが付与されます）。\n"\
            f"{author_mention}\n"\
            ":two:で２名、:three:で３名を基本としたマッチングを行います。\n"\
            f"{Role.make_how_to_destruct_role_message()}"

    def make_line(self, channel_name, room_members):
        return f"{channel_name}: {' / '.join(room_members)}\n"

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
            return self.make_capacity_per_room_two_basis(
                users_num,
                capacity_basis
            )
        return self.make_capacity_per_room_three_basis(
            users_num,
            capacity_basis
        )

    async def send_invitation(self, channel, channel_name, users):
        embed = discord.Embed(
            description=self.make_line(channel_name, users),
            color=discord.Color.random()
        )
        await channel.send(embed=embed)

    async def send_invitations_creating_channels(
        self,
        channel,
        users,
        capacity_basis
    ):
        capacity_per_room = self.make_capacity_per_room(
            len(users),
            capacity_basis
        )
        start_i = 0
        for i, capacity in enumerate(capacity_per_room, start=1):
            end_i = start_i + capacity
            channel_name = f"room{i}"
            await self.send_invitation(
                channel,
                channel_name,
                users[start_i:end_i]
            )
            await channel.guild.create_voice_channel(
                channel_name,
                category=channel.category
            )
            start_i += capacity

    @commands.command()
    async def match(self, ctx):
        await self.bot.wait_until_ready()
        channel = ctx.channel
        embed = discord.Embed(
            description=self.make_text(ctx.author.mention),
            color=discord.Color.blue()
        )
        role_name = Role.make_role_name(ctx.guild.roles)
        role = await ctx.guild.create_role(name=role_name)
        embed.add_field(name="new_role_name", value=role_name)
        msg = await ctx.send(embed=embed)
        emojis = [
            self.WILLING_EMOJI,
            self.TWO_EMOJI,
            self.THREE_EMOJI,
            Role.REMOVER_EMOJI
        ]
        for emoji in emojis:
            await msg.add_reaction(emoji)

    async def get_users_for_matching(self, reactions):
        users = []
        for reaction in reactions:
            if str(reaction.emoji) == self.WILLING_EMOJI:
                reaction_users = await reaction.users().flatten()
                for user in reaction_users:
                    if user.bot:
                        continue
                    users.append(user.mention)
                break
        return users

    async def handle_matching_result(self, payload, emoji_name):
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        try:
            capacity_basis = 2 if emoji_name == self.TWO_EMOJI else 3
            reactioned_message = await channel.fetch_message(
                payload.message_id
            )
            if reactioned_message.author.id != self.bot.user.id:
                return
            users = await self.get_users_for_matching(
                reactioned_message.reactions
            )
            if len(users) < 2:
                embed = discord.Embed(
                    description='マッチングに必要な人数が集まっていません。',
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)
                return
            random.shuffle(users)
            await self.send_invitations_creating_channels(
                channel,
                users,
                capacity_basis
            )
        except Exception as e:
            print(e)
            print(type(e))

    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, module_name):
        await ctx.send(f"モジュール{module_name}の再読み込みを開始します。")
        try:
            self.bot.reload_extension(module_name)
            await ctx.send(f"モジュール{module_name}の再読み込みを終了しました。")
        except (
            commands.errors.ExtensionNotLoaded,
            commands.errors.ExtensionNotFound,
            commands.errors.NoEntryPointError,
            commands.errors.ExtensionFailed
        ) as e:
            await ctx.send(f"モジュール{module_name}の再読み込みに失敗しました。理由: {e}")
            return

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        emoji_name = payload.emoji.name
        if emoji_name == self.WILLING_EMOJI:
            await Role.handle_role_toggling_reaction(self, payload, True)
        elif emoji_name == self.TWO_EMOJI or emoji_name == self.THREE_EMOJI:
            await self.handle_matching_result(payload, emoji_name)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.emoji.name != self.WILLING_EMOJI:
            return
        if payload.user_id == self.bot.user.id:
            return
        await Role.handle_role_toggling_reaction(self, payload, False)


def setup(bot):
    bot.add_cog(Match(bot))
