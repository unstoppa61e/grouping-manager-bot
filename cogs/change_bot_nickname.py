from discord.ext import commands


class ChNick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def chnick(self, ctx):
        await ctx.guild.me.edit(nick="マッチングアプリ")


def setup(bot):
    bot.add_cog(ChNick(bot))
