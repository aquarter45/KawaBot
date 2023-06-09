import datetime

from nextcord import slash_command, Embed
from nextcord.ext import commands

from config import Version


class Essential(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command("status", "To show status of the bot")
    async def status(self, ctx):
        embed = Embed(title="KawaBOT have response!", color=0x31502b)
        embed.add_field(name="Bot Version", value=Version, inline=True)
        embed.add_field(name="Current Latency", value=round(self.bot.latency * 1000), inline=True)
        local_date = datetime.date.today()
        time_formatted = local_date.strftime("%Y/%m/%d")
        embed.set_footer(text=time_formatted + " | KawaBOT [Made by KawaKawa]")
        await ctx.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(Essential(bot))
