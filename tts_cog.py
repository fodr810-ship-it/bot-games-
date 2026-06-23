import discord
from discord.ext import commands
from discord import app_commands
from elevenlabs.client import ElevenLabs
import asyncio
import os

# ==================== إعدادات ELEVENLABS ====================
ELEVEN_API_KEY = "ac6b0c3a91d3278256b438754b06d1b9bedf028ac2f444f2d301c4549217d971"
CHOSEN_VOICE_ID = "pNInz6obpgDQGcFmaJgB"
# ============================================================

# تهيئة عميل ElevenLabs
try:
    el_client = ElevenLabs(api_key=ELEVEN_API_KEY)
except Exception as e:
    print(f"⚠️ خطأ في تهيئة ElevenLabs: {e}")

class TTSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="speak", description="🗣️ نطق الكلام بلهجة حجازية فعلية وطبيعية 100% عبر ElevenLabs")
    @app_commands.describe(text="اكتب النص بالعامية الحجازية الفصحى أو الحرة")
    async def speak(self, interaction: discord.Interaction, text: str):
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.response.send_message("❌ يجب أن تكون متواصلاً بروم صوتي أولاً!", ephemeral=True)
            return

        voice_channel = interaction.user.voice.channel
        await interaction.response.defer(ephemeral=True)

        filename = f"tts_eleven_{interaction.id}.mp3"

        try:
            # ✅ تحديث دالة التوليد لتتوافق مع إصدار المكتبة الجديد والمستقر
            audio_generator = el_client.text_to_speech.convert(
                voice_id=CHOSEN_VOICE_ID,
                text=text,
                model_id="eleven_multilingual_v2",
                output_format="mp3_44100_128"
            )

            # كتابة البيانات الصوتية الحية إلى ملف MP3
            with open(filename, "wb") as f:
                for chunk in audio_generator:
                    f.write(chunk)

            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                raise Exception("فشل السيرفر في تمرير الصوت التوليدي")

        except Exception as e:
            print(f"❌ خطأ ElevenLabs API: {e}")
            if os.path.exists(filename): 
                try: 
                    os.remove(filename)
                except: 
                    pass
            await interaction.followup.send("❌ فشل جلب الصوت الواقعي من خوادم ElevenLabs الفنية.", ephemeral=True)
            return

        # 3. الاتصال بالروم وتشغيل الصوت عبر FFmpeg
        try:
            if interaction.guild.voice_client:
                vc = interaction.guild.voice_client
                if vc.channel != voice_channel:
                    await vc.move_to(voice_channel)
            else:
                vc = await voice_channel.connect()
        except Exception as e:
            print(f"❌ خطأ اتصال الروم: {e}")
            if os.path.exists(filename): 
                try:
                    os.remove(filename)
                except:
                    pass
            await interaction.followup.send("❌ تعذر دخول البوت إلى الروم الصوتي.", ephemeral=True)
            return

        try:
            source = discord.FFmpegPCMAudio(executable="ffmpeg", source=filename)
            vc.play(source)
            await interaction.followup.send(f"🎙️ جاري نطق العبارة بذكاء اصطناعي واقعي وحقيقي في: {voice_channel.name}", ephemeral=True)

            while vc.is_playing():
                await asyncio.sleep(0.5)
        except Exception as e:
            print(f"❌ خطأ تشغيل FFmpeg: {e}")
        finally:
            if vc and vc.is_connected():
                await vc.disconnect()
            if os.path.exists(filename):
                try: 
                    os.remove(filename)
                except: 
                    pass

async def setup(bot):
    await bot.add_cog(TTSCog(bot))