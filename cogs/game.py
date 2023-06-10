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

        guild = ctx.guild
        channel_id = ctx.channel_id
        channel = guild.get_channel(channel_id)

        await ctx.response.send_message("你正在抽籤...")

        luckList = ["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"]
        await channel.send("正在幫您解籤...")
        for i in range(len(luckList)):
            get = random.randint(1, 700)
            if get < 100:
                await channel.send(f"您今天的運勢是`{luckList[i]}`")
                return
        else:
            await channel.send(f"您今天的運勢是`{luckList[6]}`")



def setup(bot):
    bot.add_cog(game(bot))
