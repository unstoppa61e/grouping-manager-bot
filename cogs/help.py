import discord
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def make_embed(self):
        embed = discord.Embed(
            color=discord.Color.orange(),
        )
        embed.add_field(
            name="match",
            value="マッチング募集用メッセージの送信",
            inline=False
        )
        embed.add_field(
            name="role",
            value="ロール付与用メッセージの送信",
            inline=False
        )
        embed.set_footer(
            text="ご要望・不具合のご報告は monoue までお願いします。"
        )
        return embed

    @commands.command()
    async def help(self, ctx):
        embed = self.make_embed()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Help(bot))
