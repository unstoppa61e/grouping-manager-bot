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
            ":two:で２名、:three:で３名を基本としたマッチングを行います。\n"\
            f"{author_mention} {Role.make_how_to_destruct_role_message()}"

    def make_line(self, channel_name, room_member_ids, guild):
        room_members_mentions = []
        for member_id in room_member_ids:
            member = guild.get_member(member_id)
            room_members_mentions.append(member.mention)
        return f"{channel_name}: {' / '.join(room_members_mentions)}\n"

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

    async def send_invitation(self, channel, channel_name, user_ids):
        invitation_line = self.make_line(channel_name, user_ids, channel.guild)
        await channel.send(invitation_line)

    async def send_introduction(self, channel, reactioner_mention):
        embed = discord.Embed(
            description=f"{reactioner_mention}さんがマッチングを実施しました。\n"
                        "各自、割り当てられたボイスチャンネルへ入室してください。",
            color=discord.Color.gold()
        )
        await channel.send(embed=embed)

    def channel_already_exists(self, channels, channel_name):
        for channel in channels:
            if channel.name == channel_name:
                return True
        return False

    async def send_invitations_creating_channels(
        self,
        channel,
        user_ids,
        capacity_basis,
        reactioner_mention,
        role_index_str
    ):
        await self.send_introduction(channel, reactioner_mention)
        capacity_per_room = self.make_capacity_per_room(
            len(user_ids),
            capacity_basis
        )
        start_i = 0
        category = channel.category
        for i, capacity in enumerate(capacity_per_room, start=1):
            end_i = start_i + capacity
            channel_name = f"room{role_index_str}-{i}"
            await self.send_invitation(
                channel,
                channel_name,
                user_ids[start_i:end_i]
            )
            start_i += capacity
            if self.channel_already_exists(
                channel.guild.channels,
                channel_name
            ):
                continue
            await channel.guild.create_voice_channel(
                channel_name,
                category=category
            )

    @commands.command()
    async def match(self, ctx):
        await self.bot.wait_until_ready()
        channel = ctx.channel
        embed = discord.Embed(
            description=self.make_text(ctx.author.mention),
            color=discord.Color.blue()
        )
        role_name = Role.make_role_name_with_index(ctx.guild.roles)
        role = await ctx.guild.create_role(name=role_name)
        embed.add_field(name="New role", value=role_name)
        embed.add_field(name="Called by", value=ctx.author.name)
        msg = await ctx.send(embed=embed)
        emojis = [
            self.WILLING_EMOJI,
            self.TWO_EMOJI,
            self.THREE_EMOJI,
            Role.REMOVER_EMOJI
        ]
        for emoji in emojis:
            await msg.add_reaction(emoji)

    async def get_user_ids_for_matching(self, reactions):
        users = []
        for reaction in reactions:
            if str(reaction.emoji) == self.WILLING_EMOJI:
                reaction_users = await reaction.users().flatten()
                for user in reaction_users:
                    if user.bot:
                        continue
                    users.append(user.id)
                break
        return users

    async def handle_matching_result(self, payload, emoji_name):
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        try:
            capacity_basis = 2 if emoji_name == self.TWO_EMOJI else 3
            reactioned_msg = await channel.fetch_message(
                payload.message_id
            )
            if reactioned_msg.author.id != self.bot.user.id:
                return
            user_ids = await self.get_user_ids_for_matching(
                reactioned_msg.reactions
            )
            reactioner_mention = payload.member.mention
            if len(user_ids) < 2:
                embed = discord.Embed(
                    description="マッチングに必要な人数が集まっていません。",
                    color=discord.Color.red()
                )
                await channel.send(embed=embed)
                return
            random.shuffle(user_ids)
            role_index_str = reactioned_msg.embeds[0].fields[0].value[5:]
            await self.send_invitations_creating_channels(
                channel,
                user_ids,
                capacity_basis,
                reactioner_mention,
                role_index_str
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
