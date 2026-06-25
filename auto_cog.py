import discord
from discord.ext import commands

class DownloadButton(discord.ui.View):
    def __init__(self, image_url: str):
        super().__init__(timeout=None)
        # إضافة زر رابط لفتح الصورة الأصلية مباشرة
        self.add_item(discord.ui.Button(label="تنزيل الصورة", url=image_url, style=discord.ButtonStyle.link))

class ImageRepostSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # ضع هنا أيدي الروم الذي تريد مراقبته
        self.TARGET_CHANNEL_ID = 1519725913045078056

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل رسائل البوت والتأكد من الروم
        if message.author.bot or message.channel.id != self.TARGET_CHANNEL_ID:
            return

        # التحقق إذا كانت الرسالة تحتوي على صورة
        if message.attachments:
            attachment = message.attachments[0]
            if attachment.content_type and attachment.content_type.startswith("image/"):
                
                # إنشاء الرسالة الجديدة
                content = f"**From:** {message.author.mention}"
                
                # إرسال الصورة الجديدة مع الزر
                await message.channel.send(
                    content=content,
                    file=await attachment.to_file(),
                    view=DownloadButton(attachment.url)
                )
                
                # حذف الرسالة الأصلية
                try:
                    await message.delete()
                except Exception as e:
                    print(f"لم أتمكن من حذف الرسالة: {e}")

async def setup(bot):
    await bot.add_cog(ImageRepostSystem(bot))