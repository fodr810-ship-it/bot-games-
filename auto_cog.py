import discord
from discord.ext import commands

class DownloadButton(discord.ui.View):
    def __init__(self, image_url: str):
        super().__init__(timeout=None)
        # زر "تنزيل" شفاف (رابط) يفتح الصورة مباشرة بجودتها الأصلية
        self.add_item(discord.ui.Button(label="تنزيل الصورة", url=image_url, style=discord.ButtonStyle.link))

class ImageRepostSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # آيدي روم المنتدى/البوستات الرئيسي الخاص بك
        self.TARGET_CHANNEL_ID = 1519725913045078056

    @commands.Cog.listener()
    async def on_message(self, message):
        # 1. تجاهل رسائل البوتات تماماً
        if message.author.bot:
            return

        # 2. حل مشكلة البوستات (Threads): 
        # إذا كانت الرسالة داخل بوست، جلب آيدي الروم الرئيسي (المنتدى) الذي يحتوي على هذا البوست
        channel_id = message.channel.id
        if isinstance(message.channel, discord.Thread):
            channel_id = message.channel.parent_id

        # التحقق من مطابقة آيدي الروم
        if channel_id != self.TARGET_CHANNEL_ID:
            return

        # 3. التحقق من وجود مرفقات (صور)
        if message.attachments:
            attachment = message.attachments[0]
            
            # التحقق الذكي من أن الملف صورة (عن طريق النوع أو امتداد الملف)
            is_image = False
            if attachment.content_type and attachment.content_type.startswith("image/"):
                is_image = True
            elif attachment.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                is_image = True

            if is_image:
                try:
                    # إرسال الصورة الجديدة مع المنشن والزر الشفاف تحتها بنفس البوست
                    await message.channel.send(
                        content=f"**From:** {message.author.mention}",
                        file=await attachment.to_file(),
                        view=DownloadButton(attachment.url)
                    )
                    
                    # حذف الرسالة الأصلية التي أرسلها العضو للتنظيف
                    await message.delete()
                    
                except discord.Forbidden:
                    print("خطأ: البوت لا يمتلك صلاحية [Manage Messages] أو [Send Messages] في هذا الروم/البوست.")
                except Exception as e:
                    print(f"حدث خطأ غير متوقع: {e}")

async def setup(bot):
    await bot.add_cog(ImageRepostSystem(bot))