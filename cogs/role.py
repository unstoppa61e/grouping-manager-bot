import discord
from discord.ext import commands
import asyncio


class Role(commands.Cog):
    REGISTER_EMOJI = '✅'
    REMOVER_EMOJI = '❌'
    ROLE_NAME_HEAD = 'role_'

    def __init__(self, bot):
        self.bot = bot

    def make_how_to_destruct_role_message():
        message = f"このロールが不要になりましたら、{Role.REMOVER_EMOJI}にて、サーバーから削除できます。"
        return message

    def make_text(self, author_mention) -> str:
        return f"各自、{self.REGISTER_EMOJI}にて、新ロールのオン・オフが可能です。\n"\
            f"{author_mention} {Role.make_how_to_destruct_role_message()}"

    def get_role_index_not_used(roles):
        num = 0
        while True:
            found = False
            for role in roles:
                if role.name == f"{Role.ROLE_NAME_HEAD}{num}":
                    found = True
                    break
            if found is False:
                break
            num += 1
        return num

    def make_role_name_with_index(roles):
        role_index = Role.get_role_index_not_used(roles)
        return f"{Role.ROLE_NAME_HEAD}{role_index}"

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id:
            return
        if payload.emoji.name == self.REGISTER_EMOJI:
            await self.handle_role_toggling_reaction(payload, True)
        elif payload.emoji.name == self.REMOVER_EMOJI:
            await self.handle_role_destroying_reaction(payload)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if not payload.emoji.name == self.REGISTER_EMOJI:
            return
        if payload.user_id == self.bot.user.id:
            return
        await self.handle_role_toggling_reaction(payload, False)

    def get_role_corresponding_to_message(guild, message):
        role_name = message.embeds[0].fields[0].value
        role = discord.utils.get(guild.roles, name=role_name)
        return role

    async def handle_role_toggling_reaction(self, payload, adding):
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        try:
            reactioned_msg = await channel.fetch_message(payload.message_id)
            if reactioned_msg.author.id != self.bot.user.id:
                return
            guild = reactioned_msg.guild
            member = discord.utils.find(
                lambda m: m.id == payload.user_id,
                guild.members
            )
            if member.bot:
                return
            role = Role.get_role_corresponding_to_message(
                guild,
                reactioned_msg
            )
            if role is None:
                return
            if adding:
                await member.add_roles(role)
            else:
                await member.remove_roles(role)
        except Exception as e:
            print(e)
            print(type(e))

    async def send_role_destroying_msg(self, user_mention, role_name, channel):
        embed = discord.Embed(
            description=f"{user_mention}さんにより、`{role_name}`ロールが削除されました。",
            color=discord.Color.green()
        )
        await channel.send(embed=embed)

    async def send_error_msg_via_dm(self, member, msg, text):
        msg_url = msg.jump_url
        text_to_jump_back = f"[こちらのリンク]({msg_url})から、元のメッセージに戻れます。"
        embed = discord.Embed(
            color=discord.Color.red(),
            description=f"{text}\n{text_to_jump_back}"
        )
        await member.send(embed=embed)
        return

    async def handle_role_destroying_reaction(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        if not isinstance(channel, discord.TextChannel):
            return
        try:
            reactioned_msg = await channel.fetch_message(payload.message_id)
            if reactioned_msg.author.id != self.bot.user.id:
                return
            guild = reactioned_msg.guild
            member = discord.utils.find(
                lambda m: m.id == payload.user_id,
                guild.members
            )
            if member.bot:
                return
            role = Role.get_role_corresponding_to_message(
                guild,
                reactioned_msg
            )
            if role is None:
                role_name = reactioned_msg.embeds[0].fields[0].value
                text = f"`{role_name}`ロールは既に削除済みです。"
                await self.send_error_msg_via_dm(member, reactioned_msg, text)
                return
            command_user_name = reactioned_msg.embeds[0].fields[1].value
            if command_user_name != member.name:
                text = f"{self.REMOVER_EMOJI}によるロールの削除は、"\
                    f"元のコマンドを実行した`{command_user_name}`さんのみに許可されています。"
                await self.send_error_msg_via_dm(member, reactioned_msg, text)
                return
            await self.send_role_destroying_msg(
                payload.member.mention,
                role.name,
                channel
            )
            await role.delete()
        except Exception as e:
            print(e)
            print(type(e))

    def role_name_exists(self, role_name, roles):
        for role in roles:
            if role.name == role_name:
                return True
        return False

    def make_role_name_error_message(self, role_name):
        embed = discord.Embed(
            description=f"`{role_name}`という名前のロールは既に存在します。",
            color=discord.Color.red()
        )
        return embed

    def make_role_name(self, role_name_tail, roles):
        role_name = None
        if role_name_tail is None:
            role_name = Role.make_role_name_with_index(roles)
        else:
            role_name = f"{self.ROLE_NAME_HEAD}{role_name_tail}"
        return role_name

    @commands.command()
    async def role(self, ctx, role_name_tail=None):
        await self.bot.wait_until_ready()
        roles = ctx.guild.roles
        role_name = self.make_role_name(role_name_tail, roles)
        if role_name_tail and self.role_name_exists(role_name, roles):
            embed = self.make_role_name_error_message(role_name)
            await ctx.send(embed=embed)
            return
        embed = discord.Embed(
            description=self.make_text(ctx.author.mention),
            color=discord.Color.blue()
        )
        await ctx.guild.create_role(name=role_name)
        embed.add_field(name="New Role", value=role_name)
        embed.add_field(name="Called by", value=ctx.author.name)
        msg = await ctx.send(embed=embed)
        await msg.add_reaction(self.REGISTER_EMOJI)
        await msg.add_reaction(self.REMOVER_EMOJI)

    @commands.command()
    async def rm(self, ctx, role_name_tail):
        embed = discord.Embed()
        role_name = f"{self.ROLE_NAME_HEAD}{role_name_tail}"
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role is None:
            embed.color = discord.Color.red()
            embed.description = f"{ctx.author.mention}"\
                f" `{role_name}`というロールは存在しません。"
            await ctx.send(embed=embed)
        else:
            embed.color = discord.Color.green()
            embed.description = f"{ctx.author.mention}さんが"\
                f"`{role.name}`ロールを削除しました。"
            await ctx.send(embed=embed)
            await role.delete()


def setup(bot):
    bot.add_cog(Role(bot))
