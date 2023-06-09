import random
import nextcord
from nextcord import slash_command
from nextcord.ext import commands


class game(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @slash_command("dice", "To dice a number")
    async def dice(self, ctx):
        guild = ctx.guild
        channel_id = ctx.channel_id

        await ctx.response.send_message("正在擲骰子...")

        channel = guild.get_channel(channel_id)

        playerA = random.randint(1, 6)
        playerB = random.randint(1, 6)

        await channel.send(f"你擲到了 {playerA} 和 {playerB}")

        botA = random.randint(1, 6)
        botB = random.randint(1, 6)

        await channel.send(f"機器人擲到了 {botA} 和 {botB}")

        if playerA + playerB > botA + botB:
            await channel.send(f"你贏了!")
        else:
            await channel.send(f"你輸了!")

    @slash_command("luck", "To make a divine to show your luck now")
    async def luck(self, ctx):
        luck = random.randint(100, 10000)/100



def setup(bot):
    bot.add_cog(game(bot))
