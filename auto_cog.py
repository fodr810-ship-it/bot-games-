import discord
from discord.ext import commands

class DownloadButton(discord.ui.View):
    def __init__(self, image_url: str):
        super().__init__(timeout=None)
        # زر "تنزيل" كـ Link يفتح الصورة مباشرة في المتصفح
        self.add_item(discord.ui.Button(label="تنزيل الصورة", url=image_url, style=discord.ButtonStyle.link))

class ImageRepostSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.TARGET_CHANNEL_ID = 1519725913045078056

    @commands.Cog.listener()
    async def on_message(self, message):
        # 1. تجاهل رسائل البوت
        # 2. التأكد أن الرسالة في الروم المطلوب
        # 3. التأكد أن الرسالة تحتوي على مرفق (صورة)
        if message.author.bot or message.channel.id != self.TARGET_CHANNEL_ID:
            return

        if message.attachments:
            attachment = message.attachments[0]
            
            # التأكد أن المرفق هو صورة
            if attachment.content_type and attachment.content_type.startswith("image/"):
                
                # إرسال النسخة الجديدة من الرسالة
                try:
                    await message.channel.send(
                        content=f"**From:** {message.author.mention}",
                        file=await attachment.to_file(),
                        view=DownloadButton(attachment.url)
                    )
                    
                    # حذف الرسالة الأصلية بعد نجاح الإرسال
                    await message.delete()
                except discord.Forbidden:
                    print("البوت لا يملك صلاحية حذف الرسائل في هذا الروم.")
                except Exception as e:
                    print(f"حدث خطأ: {e}")

async def setup(bot):
    await bot.add_cog(ImageRepostSystem(bot))