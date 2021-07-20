from discord.ext import commands
from utils.check_privilege import executed_by_privileged_member


class ChNick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def chnick(self, ctx):
        if not executed_by_privileged_member(ctx):
            return
        await ctx.guild.me.edit(nick="マッチングアプリ")


def setup(bot):
    bot.add_cog(ChNick(bot))
