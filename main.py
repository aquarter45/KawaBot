import nextcord
from nextcord.ext import commands
import os
from config import *

intents = nextcord.Intents.all()
bot = commands.Bot(intents=intents)

TESTING_GUILD_ID = 1048586597244870687


@bot.event
async def on_ready():
    await bot.change_presence(activity=nextcord.Game(f"KawaBot|Version:{Version}"))
    print(f"KawaBot|Version:{Version}")
    print(f'The Bot Is Online!')

initial_extensions = []


def add_external_component():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            bot.load_extension(f'cogs.{filename[:-3]}')


if __name__ == '__main__':
    add_external_component()
    for extensions in initial_extensions:
        bot.load_extension(extensions)

    bot.run(Token)
