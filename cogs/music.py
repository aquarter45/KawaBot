import pafy
import yt_dlp as youtube_dl
from nextcord.ext import commands
from nextcord import slash_command, FFmpegPCMAudio, PCMVolumeTransformer, SlashOption, utils, Embed,Interaction
import datetime
import urllib
import re
import asyncio

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

# 'guild_id': {song_info,song_list}
queue = {}


# youtube api key setup
pafy.set_api_key("AIzaSyDE-vBYEBJLQBvsA6WIZJcKWC16DZCQa0I")

async def platform_checker(search):
    if "https://open.spotify.com/" in search:
        return "spotify"
    elif "https://www.youtube.com/" in search or "https://youtu.be/" in search:
        return "youtube"
    else:
        return None


async def create_embed(embed_type, **kwargs):
    embed = None
    match embed_type:
        case "errors":
            embed = Embed(title=kwargs.get("title"), color=0xac2f2f)
        case "status":
            embed = Embed(title=kwargs.get("title"), color=0x2f93ac)
        case "playing":
            song_info = kwargs.get("song_info")
            embed = Embed(title=song_info['title'], color=0x376d4e)
            embed.set_author(name=f"正在從{song_info['platform']}播放", url=song_info['url'],icon_url=get_author(song_info['url']))
            embed.set_thumbnail(url=song_info['thumbnail'])
            embed.add_field(name="時長", value= song_info['duration'])
            embed.add_field(name="觀看次數", value= f"{song_info['viewcount']}次")
            embed.add_field(name="作者", value= song_info['author'])
            embed.add_field(name="上傳時間", value= song_info['published'])
        case "queued":
            song_info = kwargs.get("song_info")
            embed = Embed(title=song_info['title'], color=0xddb936)
            embed.set_author(name=f"正在從{song_info['platform']}新增歌曲", url=song_info['url'],icon_url=get_author(song_info['url']))
            embed.set_thumbnail(url=song_info['thumbnail'])
            embed.add_field(name="時長", value= song_info['duration'])
            embed.add_field(name="觀看次數", value= f"{song_info['viewcount']}次")
            embed.add_field(name="作者", value= song_info['author'])
            embed.add_field(name="上傳時間", value= song_info['published'])




    local_date = datetime.date.today()
    time_formatted = local_date.strftime("%Y/%m/%d")
    embed.set_footer(text=time_formatted + " | KawaBOT [Made by KawaKawa]")

    return embed

def get_author(uri):
    html = urllib.request.urlopen(uri)
    author_image = re.search(r'yt3\.ggpht\.com/[^"]+', html.read().decode())
    if author_image:
        return f"https://{author_image.group()}"
    return None 


async def add_queue(guild_id,original_message,url):
    video = pafy.new(url)
    audio = video.getbestaudio()
    source = FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
    volume_fixed_source = PCMVolumeTransformer(source, volume=float(0.15))
    song_info = {
                'title': video.title,
                'platform': "Youtube",
                'url': url,
                'thumbnail': video.bigthumbhd,
                'duration': video.duration,
                'viewcount': video.viewcount,
                'author': video.author,
                'published': video.published,
            }

    if guild_id in queue:
        queue[guild_id].append({'song_info':song_info,'source':volume_fixed_source})
    else:
        queue[guild_id] = [{'song_info':song_info,'source':volume_fixed_source}]

    embed = await create_embed("queued",song_info=song_info)
    await original_message.edit(embed=embed)
    await asyncio.sleep(10)
    await original_message.delete()



async def check_queue(guild_id, bot, original_message):
    guild = bot.get_guild(guild_id)
    if guild_id in queue and len(queue[guild_id]) > 0:
        vc = utils.get(bot.voice_clients, guild=guild)

        song_info = queue[guild_id][0]['song_info']
        source = queue[guild_id][0]['source']
        queue[guild_id].pop(0)

        play_coro = vc.play(source, after=lambda x=None: check_queue(guild_id=guild_id, bot=bot, original_message=original_message))
        embed = await create_embed("playing", song_info=song_info)
        await original_message.edit(embed=embed)
        player = asyncio.run_coroutine_threadsafe(play_coro, bot.loop)
        try:
            player.result()
        except nextcord.Forbidden:
            pass
    else:
        await original_message.delete()
        





class Music(commands.Cog):

    def __init__(self,bot):
        self.bot = bot


    @slash_command("play", "播放音樂")
    async def play(self, ctx:Interaction,search:str=SlashOption(required=True)):

        guild = ctx.guild
        channel_id = ctx.channel_id
        channel = guild.get_channel(channel_id)
        user_vc = ctx.user.voice.channel
        bot_vc = utils.get(self.bot.voice_clients, guild=guild) 

        # 使用者未加入語音頻道
        if user_vc == None:
            embed = await create_embed("errors", title=":x: 你必須先加入一個語音頻道")
            await ctx.response.send_message(embed=embed)
            return
        
        # 機器人未加入語音頻道
        if bot_vc == None:
            bot_vc =await user_vc.connect()
        elif bot_vc.channel != user_vc:
            embed = await create_embed("errors", title="我無法自由切換語音頻道!")
            await ctx.response.send_message(embed=embed)
            return
        elif bot_vc.channel == user_vc:
            pass

        embed = await create_embed("status", title=f"正在搜尋{search}")
        original_message = await ctx.response.send_message(embed=embed)

        if bot_vc.is_playing():
            await add_queue(guild_id=guild.id,original_message=original_message,url=search)
            return

        

        platform = await platform_checker(search=search)

        if platform == "youtube":

            # 取得音源
            video = pafy.new(search)
            audio = video.getbestaudio()
            source = FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
            volume_fixed_source = PCMVolumeTransformer(source, volume=float(0.15)) # 修正聲音

            #播放音源
            await asyncio.sleep(1)
            bot_vc.play(volume_fixed_source, after=lambda x=None: check_queue(guild_id=guild.id,bot=self.bot,original_message=original_message))

            # 載入歌曲資訊
            song_info = {
                'title': video.title,
                'platform': "Youtube",
                'url': search,
                'thumbnail': video.bigthumbhd,
                'duration': video.duration,
                'viewcount': video.viewcount,
                'author': video.author,
                'published': video.published,
            }
            #生成正在播放訊息
            embed = await create_embed(embed_type="playing",song_info=song_info)
            # 編輯訊息
            await original_message.edit(embed=embed)
    
    @slash_command("playlist", "顯示當前的清單內容")
    async def playlist(self, ctx:Interaction):

        embed = await create_embed("status", title="正在查詢清單...")
        original_message = await ctx.response.send_message(embed=embed)

        guild_id = ctx.guild_id

        if guild_id not in queue:
            embed = await create_embed("errors", title="查無任何待播放的清單")
            await original_message.edit(embed=embed)
            return

        embed = Embed(title=f"下個播放:{queue[guild_id][0]['song_info']['title']}", color=0xddb936)
        embed.set_author(name="-當前的播放清單- (10秒後將會刪除該訊息)")
        embed.set_thumbnail(queue[guild_id][0]['song_info']['thumbnail'])

        description = ""
        for i in range(len(queue[guild_id])):
            description += f"{i}. {queue[guild_id][i]['song_info']['title']} - {queue[guild_id][i]['song_info']['duration']}\n"
        
        embed.add_field(name="清單列表",value=description)

        await original_message.edit(embed=embed)
        await asyncio.sleep(10)
        await original_message.delete()


def setup(bot):
    bot.add_cog(Music(bot))