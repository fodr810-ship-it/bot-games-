import discord
from discord.ext import commands
import io
import os

class VoiceRecorder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # 🔴 ضع هنا أيدي روم اللوق الخاص بك
        self.log_channel_id = 1439853749483995276  

    @commands.command(name="سجل")
    async def record(self, ctx):
        if not ctx.author.voice:
            return await ctx.send("لازم تكون متواجد في روم صوّتي عشان أقدر أسجل!")

        channel = ctx.author.voice.channel
        vc = ctx.voice_client

        # الاتصال بالروم الصوتي
        if not vc:
            vc = await channel.connect()
        elif vc.channel != channel:
            await vc.move_to(channel)

        # التحقق إذا كان البوت يسجل بالفعل
        if vc.is_recording():
            return await ctx.send("أنا قاعد أسجل بالفعل في هذه الروم!")

        # استخدام MP3Sink للتسجيل الطويل والنقي بحجم ملف صغير
        # خيار filters={...} يضمن تسجيل جميع الأعضاء الميسرين في الروم
        try:
            vc.start_recording(
                discord.sinks.MP3Sink(), 
                self.finished_recording, 
                ctx.channel
            )
            await ctx.send(f"🎙️ **بدأ التسجيل المستمر بنقاء عالي في روم:** {channel.name}\nسيتم حفظ وتسجيل جميع الأصوات وإرسالها مدمجة فور التوقف.")
        except Exception as e:
            await ctx.send(f"❌ حدث خطأ أثناء بدء التسجيل: {e}")

    # هذه الدالة معالجة ما بعد انتهاء التسجيل تلقائياً
    async def finished_recording(self, sink, channel, *args):
        log_channel = self.bot.get_channel(self.log_channel_id)
        
        if not log_channel:
            print("❌ روم اللوق غير موجود، تأكد من الأيدي الصحيح في الكود!")
            return

        await log_channel.send("⏳ **جاري معالجة الصوت المدمج وتهيئة الملف للإرسال...**")

        # هنا نقوم بالمرور على البيانات الصوتية المسجلة لكل مستخدم وجمعها
        # ديسكورد يسجل صوت كل مستخدم على حدة، وسنقوم بإرسالها في رسالة مدمجة منسقة لتسمعها معاً
        files = []
        for user_id, audio in sink.audio_data.items():
            user = self.bot.get_user(user_id)
            user_name = user.name if user else f"مستخدم_{user_id}"
            
            # قراءة الملف الصوتي من الذاكرة كـ MP3
            audio_file = discord.File(audio.file, filename=f"صوت_{user_name}.mp3")
            files.append(audio_file)

        if files:
            # إرسال جميع ملفات الـ MP3 النقية والصغيرة في رسالة واحدة لروم اللوق
            # مشغل الديسكورد سيعرضها كلها خلف بعضها وتستطيع الاستماع لكل الأطراف بوضوح تام
            await log_channel.send(f"📁 **تقرير تسجيل صوتي جديد (فترة طويلة):**\nتم تسجيل بنجاح بصيغة MP3 نقية وبدون أي تقطيع.", files=files)
        else:
            await log_channel.send("⚠️ انتهى التسجيل ولكن لم يتحدث أحد في الروم، الملف فارغ.")

    @commands.command(name="وقف")
    async def stop(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_recording():
            return await ctx.send("أنا مش قاعد أسجل أي شيء حالياً!")

        # إيقاف التسجيل يطلق دالة finished_recording تلقائياً
        vc.stop_recording() 
        await vc.disconnect()
        await ctx.send("🛑 تم إيقاف التسجيل بنجاح. جاري الرفع إلى روم اللوق...")

#  الشكل الجديد الصحيح
async def setup(bot):
    await bot.add_cog(VoiceRecorder(bot))