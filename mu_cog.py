import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp
import asyncio

# خيارات yt_dlp
yt_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
    'extractaudio': True,
    'audioformat': 'mp3',
    'default_search': 'ytsearch',
    'source_address': '0.0.0.0'
}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    # JOIN
    @app_commands.command(name="join", description="⛔ يدخل البوت روم الصوت")
    async def join(self, interaction: discord.Interaction):
        vc = interaction.user.voice
        if not vc:
            return await interaction.response.send_message("⚠️ أنت مو داخل روم صوت!", ephemeral=True)

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            return await interaction.response.send_message(
                f"⚠️ البوت بالفعل داخل روم: **{voice_client.channel.name}**", ephemeral=True
            )

        await vc.channel.connect()
        await interaction.response.send_message(f"🔊 تم دخول الروم: **{vc.channel.name}**")

    # PLAY
    @app_commands.command(name="play", description="▶️ تشغيل أغنية من اليوتيوب")
    @app_commands.describe(query="اسم الأغنية أو رابط اليوتيوب")
    async def play(self, interaction: discord.Interaction, query: str):
        # تأكد أن المستخدم داخل روم
        if not interaction.user.voice:
            return await interaction.response.send_message("⚠️ لازم تكون داخل روم صوت أولاً!", ephemeral=True)

        # تأكد أن البوت داخل روم
        voice_client = interaction.guild.voice_client
        if not voice_client or not voice_client.is_connected():
            return await interaction.response.send_message("⚠️ البوت مو داخل روم! استخدم /join", ephemeral=True)

        # تأكد أن البوت غير مشغول
        if voice_client.is_playing():
            return await interaction.response.send_message("🎵 البوت يشغل شي حاليًا!", ephemeral=True)

        await interaction.response.send_message(f"🔎 جارٍ البحث عن: **{query}**")

        # تحميل الصوت من YouTube
        loop = asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                None,
                lambda: yt_dlp.YoutubeDL(yt_opts).extract_info(query, download=False)
            )
        except Exception as e:
            return await interaction.followup.send(f"❌ خطأ أثناء البحث: {e}")

        if not data:
            return await interaction.followup.send("❌ ما قدرنا نلقى الأغنية!")

        info = data['entries'][0] if 'entries' in data else data
        url = info['url']
        title = info.get("title", "Unknown Title")

        # تشغيل الصوت مع FFmpeg من PATH
        source = discord.FFmpegPCMAudio(
            url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            executable="ffmpeg"
        )
        voice_client.play(source)
        await interaction.followup.send(f"🎶 الآن شغال: **{title}**")

    # STOP
    @app_commands.command(name="stop", description="⏹️ إيقاف التشغيل")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("⚠️ البوت مو داخل روم!", ephemeral=True)
        vc.stop()
        await interaction.response.send_message("⏹️ توقفت الموسيقى!")

    # LEAVE
    @app_commands.command(name="leave", description="❌ يطلع البوت من روم الصوت")
    async def leave(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if not vc or not vc.is_connected():
            return await interaction.response.send_message("⚠️ البوت مو داخل روم!", ephemeral=True)
        await vc.disconnect()
        await interaction.response.send_message("👋 البوت طلع من الروم!")

async def setup(bot):
    await bot.add_cog(Music(bot))