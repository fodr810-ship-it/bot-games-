import discord
from discord.ext import commands
import asyncio
import io
from PIL import Image, ImageDraw, ImageFilter

class DownloadCustomView(discord.ui.View):
    def __init__(self, bot, uploader: discord.Member, avatar_url: str, banner_url: str):
        super().__init__(timeout=None)
        self.bot = bot
        self.uploader = uploader
        self.avatar_url = avatar_url
        self.banner_url = banner_url

    @discord.ui.button(label="تنزيل", style=discord.ButtonStyle.secondary, custom_id="download_custom_btn", emoji="⬇️")
    async def download_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        # الرسالة التي ستظهر للشخص الذي ضغط على الزر فقط (مخفية عن البقية)
        msg = (
            f"**تم استخراج الروابط بنجاح!** 🖼️\n"
            f"**صاحب الصور الأصلية:** {self.uploader.mention}\n\n"
            f"**الافاتار:** {self.avatar_url}\n\n"
            f"**البنر:** {self.banner_url}"
        )
        
        await interaction.response.send_message(content=msg, ephemeral=True)


class CustomImageSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 🟢 أيدي الروم الذي سيتم إرسال الصورتين فيه لدمجها ومراقبته
        self.SOURCE_CHANNEL_ID = 1519058537597108407  

    def create_image_sync(self, banner_bytes, avatar_bytes):
        canvas_w, canvas_h = 900, 500
        
        # رسم الخلفية (البنر مع تأثير ضبابي)
        if banner_bytes:
            bg_img = Image.open(io.BytesIO(banner_bytes)).convert("RGBA").resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
            bg_img = bg_img.filter(ImageFilter.GaussianBlur(radius=8))
            overlay = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 120))
            background = Image.alpha_composite(bg_img, overlay)
        else:
            background = Image.new("RGBA", (canvas_w, canvas_h), (43, 45, 49, 255))

        # رسم البنر الأمامي
        if banner_bytes:
            fg_banner = Image.open(io.BytesIO(banner_bytes)).convert("RGBA").resize((800, 280), Image.Resampling.LANCZOS)
            mask = Image.new("L", (800, 280), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, 800, 280), radius=25, fill=255)
            background.paste(fg_banner, (50, 50), mask)

        # رسم الافاتار
        if avatar_bytes:
            avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((240, 240), Image.Resampling.LANCZOS)
            border_canvas = Image.new("RGBA", background.size, (0, 0, 0, 0))
            ImageDraw.Draw(border_canvas).ellipse((70, 150, 330, 410), fill=(43, 45, 49, 255))
            background = Image.alpha_composite(background, border_canvas)
            mask = Image.new("L", (240, 240), 0)
            ImageDraw.Draw(mask).ellipse((0, 0, 240, 240), fill=255)
            background.paste(avatar_img, (80, 160), mask)
            
        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل البوتات والرومات الأخرى
        if message.author.bot or message.channel.id != self.SOURCE_CHANNEL_ID:
            return
        
        # التأكد من وجود صورتين بالضبط (البنر أولاً، ثم الأفاتار ثانياً)
        if len(message.attachments) == 2:
            banner_attach = message.attachments[0]
            avatar_attach = message.attachments[1]
            
            # التحقق من أن المرفقات عبارة عن صور
            if not (banner_attach.content_type and avatar_attach.content_type):
                return
            if not (banner_attach.content_type.startswith('image/') and avatar_attach.content_type.startswith('image/')):
                return
            
            await message.add_reaction("⏳")
            
            try:
                banner_bytes = await banner_attach.read()
                avatar_bytes = await avatar_attach.read()

                # دمج الصور
                buffer = await asyncio.to_thread(self.create_image_sync, banner_bytes, avatar_bytes)
                image_file = discord.File(fp=buffer, filename="custom_showcase.png")
                
                # تم إصلاح الاستدعاء هنا وحذف المتغير الزائد الذي سبب المشكلة
                view = DownloadCustomView(
                    bot=self.bot,
                    uploader=message.author,
                    avatar_url=avatar_attach.url,
                    banner_url=banner_attach.url
                )
                
                # إرسال النص مع الصورة والزر
                await message.channel.send(
                    content=f"**From:** {message.author.mention}",
                    file=image_file, 
                    view=view
                )
                
                await message.remove_reaction("⏳", self.bot.user)
                await message.add_reaction("✅")
                
            except Exception as e:
                print(f"حدث خطأ أثناء المعالجة: {e}")
                await message.remove_reaction("⏳", self.bot.user)
                await message.add_reaction("❌")

async def setup(bot):
    await bot.add_cog(CustomImageSystem(bot))