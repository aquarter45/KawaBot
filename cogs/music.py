import datetime
import os
import nextcord
from nextcord import FFmpegPCMAudio, guild, PCMVolumeTransformer
from nextcord.ext import commands
from nextcord.utils import get
from pytube import YouTube
from config import Mp3_Path
import glob
import asyncio

queue = {}


# play color:0x6462fe
# pause color:0xfec562
# resume color:play color
# queue color:0x62cffe


def create_embed(embed_type, **kwargs):
    embed = None
    match embed_type:
        case "playing" "resume":
            embed = nextcord.Embed(title=kwargs.get("song_name"), color=0x6462fe)
            embed.set_author(name="Now Playing:")
        case "pause":
            embed = nextcord.Embed(title=kwargs.get("song_name"), color=0xfec562)
            embed.set_author(name="Music Paused:")
        case "queue":
            embed = nextcord.Embed(title=kwargs.get("song_name"), color=0x62cffe)
            embed.set_author(name="Queue Added:")

    local_date = datetime.date.today()
    time_formatted = local_date.strftime("%Y/%m/%d|%H:%M:%S")
    footer_text = time_formatted + "|KawaBot"
    embed.set_footer(text=footer_text)

    return embed


async def check_queue(bot, ctx):
    guild_id = ctx.guild.id
    if queue[guild_id]:
        vc = get(bot.voice_clients, guild=ctx.guild)
        source = queue[guild_id].pop(0)
        print(queue[guild_id])
        coro = await vc.play(source, after=lambda x=None: check_queue(bot, ctx))
        player = asyncio.run_coroutine_threadsafe(coro, bot.loop)
        try:
            player.result()
        except nextcord.Forbidden:
            pass


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="play", description="Play music from youtube")
    async def play(self, ctx, url):
        member = ctx.user
        guild_id = ctx.guild.id

        # Find Voice Channel
        if member.voice:
            channel = member.voice.channel
            vc = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
            if vc is None:
                vc = await channel.connect()
            elif vc is not None and vc.channel == channel:
                pass
            else:
                pass

            # Check if the audio is already download
            id = str.replace(url, "https://youtu.be/", "")
            keyword = [id]
            output = ''
            for word in keyword:
                output = glob.glob(os.path.join(Mp3_Path, f'*{word}*'))
            if len(output) != 0:
                if os.path.isfile(output[0]):

                    if vc.is_playing():
                        source = PCMVolumeTransformer(FFmpegPCMAudio(output[0]), volume=float(0.2))
                        if guild_id in queue:
                            queue[guild_id].append(source)
                            print(f"Song added!:{url}")
                        else:
                            queue[guild_id] = [source]
                            print(f"Song added!:{url}")
                        return

                    source = PCMVolumeTransformer(FFmpegPCMAudio(output[0]), volume=float(0.2))
                    player = vc.play(source, after=lambda x=None: check_queue(self.bot, ctx))
                    print(f"Playing:{url}")
            else:
                target_path = Mp3_Path

                yt = YouTube(url)

                video = yt.streams.filter(only_audio=True).first()

                out_file = video.download(output_path=target_path)

                file_name = out_file.replace(Mp3_Path, "")
                song_name = file_name.replace(".mp4", "")

                new_file = f"{Mp3_Path}[{song_name}]{id}.mp3"

                os.rename(out_file, new_file)

                source = PCMVolumeTransformer(FFmpegPCMAudio(new_file), volume=float(0.1))
                player = vc.play(source)
                print(f"Playing:{url}")
        else:
            await ctx.send("Please join a voice channel to use the command")

    @nextcord.slash_command(name="resume", description="Resume the paused audio")
    async def resume(self, ctx):
        vc = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc.is_paused():
            await vc.resume()
        else:
            await ctx.send("There is no paused audio")

    @nextcord.slash_command(name="pause", description="Pause the audio that currently playing")
    async def pause(self, ctx):
        vc = nextcord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if vc.is_playing():
            await vc.pause()
        else:
            await ctx.send("There is no playing audio")


def setup(bot):
    bot.add_cog(Music(bot))
