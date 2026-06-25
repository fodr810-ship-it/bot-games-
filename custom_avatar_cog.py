import discord
from discord.ext import commands
import asyncio
import io
from PIL import Image, ImageDraw, ImageFilter
import os

class DownloadCustomView(discord.ui.View):
    def __init__(self, bot, uploader: discord.Member, avatar_url: str, banner_url: str, target_channel_id: int):
        super().__init__(timeout=None)
        self.bot = bot
        self.uploader = uploader
        self.avatar_url = avatar_url
        self.banner_url = banner_url
        self.target_channel_id = target_channel_id

    @discord.ui.button(label="تنزيل", style=discord.ButtonStyle.secondary, custom_id="download_custom_btn", emoji="⬇️")
    async def download_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        target_channel = self.bot.get_channel(self.target_channel_id)
        
        if not target_channel:
            return await interaction.response.send_message("❌ لم يتم العثور على روم التنزيل، يرجى التأكد من الأيدي.", ephemeral=True)
        
        # الرسالة التي ستُرسل في روم التنزيل المحدد
        msg = (
            f"**تم سحب الصور بنجاح!** 🖼️\n"
            f"**بواسطة:** {interaction.user.mention}\n"
            f"**صاحب الصور الأصلية:** {self.uploader.mention}\n\n"
            f"**الافاتار:**\n{self.avatar_url}\n\n"
            f"**البنر:**\n{self.banner_url}"
        )
        
        await target_channel.send(content=msg)
        await interaction.response.send_message("✅ تم إرسال الصور إلى روم التنزيل المخصص!", ephemeral=True)


class CustomImageSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        # 🟢 أيدي الروم الذي سيتم إرسال الصورتين فيه لدمجها
        self.SOURCE_CHANNEL_ID = 1518210681151688794  
        
        # 🟢 أيدي الروم الذي سترسل فيه الصور عند الضغط على زر التنزيل
        self.TARGET_CHANNEL_ID = 1517015117160513726  
        
        # مسار صورة الفاصل (يجب أن تضع صورة الفاصل في نفس مجلد البوت بهذا الاسم)
        self.SEPARATOR_IMAGE_PATH = "separator.png"

    def create_image_sync(self, banner_bytes, avatar_bytes):
        canvas_w, canvas_h = 900, 850
        background = Image.new("RGBA", (canvas_w, canvas_h), (43, 45, 49, 255))

        # 1. رسم البنر الخلفي (تأثير ضبابي)
        bg_banner = Image.open(io.BytesIO(banner_bytes)).convert("RGBA").resize((canvas_w, 400), Image.Resampling.LANCZOS)
        bg_banner = bg_banner.filter(ImageFilter.GaussianBlur(radius=8))
        overlay = Image.new("RGBA", (canvas_w, 400), (0, 0, 0, 120))
        bg_banner = Image.alpha_composite(bg_banner, overlay)
        background.paste(bg_banner, (0, 0))

        # 2. رسم البنر الأمامي (مع حواف دائرية)
        fg_banner = Image.open(io.BytesIO(banner_bytes)).convert("RGBA").resize((800, 280), Image.Resampling.LANCZOS)
        banner_mask = Image.new("L", (800, 280), 0)
        ImageDraw.Draw(banner_mask).rounded_rectangle((0, 0, 800, 280), radius=25, fill=255)
        background.paste(fg_banner, (50, 50), banner_mask)

        # 3. وضع الفاصل (اللوقو/النص الشفاف)
        current_y = 360
        if os.path.exists(self.SEPARATOR_IMAGE_PATH):
            try:
                separator = Image.open(self.SEPARATOR_IMAGE_PATH).convert("RGBA")
                # تصغير/تكبير الفاصل ليتناسب مع التصميم
                sep_w = 700
                sep_h = int((sep_w / separator.width) * separator.height)
                separator = separator.resize((sep_w, sep_h), Image.Resampling.LANCZOS)
                
                # توسيط الفاصل أفقياً
                sep_x = (canvas_w - sep_w) // 2
                background.paste(separator, (sep_x, current_y), separator)
                current_y += sep_h + 20
            except Exception as e:
                print(f"Error loading separator image: {e}")
        else:
            print("⚠️ تحذير: لم يتم العثور على صورة الفاصل (separator.png)")
            current_y += 50 # مسافة افتراضية إذا لم يوجد فاصل

        # 4. رسم الأفاتار
        avatar_img = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA").resize((240, 240), Image.Resampling.LANCZOS)
        
        # إنشاء الإطار الدائري للأفاتار
        border_canvas = Image.new("RGBA", background.size, (0, 0, 0, 0))
        avatar_x = (canvas_w - 240) // 2
        
        # رسم خلفية دائرية للأفاتار (إطار)
        ImageDraw.Draw(border_canvas).ellipse(
            (avatar_x - 10, current_y - 10, avatar_x + 250, current_y + 250), 
            fill=(43, 45, 49, 255)
        )
        background = Image.alpha_composite(background, border_canvas)
        
        # قص الأفاتار بشكل دائري
        avatar_mask = Image.new("L", (240, 240), 0)
        ImageDraw.Draw(avatar_mask).ellipse((0, 0, 240, 240), fill=255)
        background.paste(avatar_img, (avatar_x, current_y), avatar_mask)

        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجاهل رسائل البوتات والرسائل التي ليست في الروم المخصص
        if message.author.bot or message.channel.id != self.SOURCE_CHANNEL_ID:
            return
        
        # التأكد من أن الرسالة تحتوي على مرفقين (صورتين)
        if len(message.attachments) == 2:
            banner_attach = message.attachments[0]
            avatar_attach = message.attachments[1]
            
            # التحقق من أن المرفقات عبارة عن صور
            if not (banner_attach.content_type.startswith('image/') and avatar_attach.content_type.startswith('image/')):
                return
            
            await message.add_reaction("⏳")
            
            try:
                banner_bytes = await banner_attach.read()
                avatar_bytes = await avatar_attach.read()

                # دمج الصور في الخلفية
                buffer = await asyncio.to_thread(self.create_image_sync, banner_bytes, avatar_bytes)
                image_file = discord.File(fp=buffer, filename="custom_showcase.png")
                
                # إنشاء الزر وإرساله
                view = DownloadCustomView(
                    bot=self.bot,
                    uploader=message.author,
                    avatar_url=avatar_attach.url,
                    banner_url=banner_attach.url,
                    target_channel_id=self.TARGET_CHANNEL_ID
                )
                
                await message.channel.send(
                    f"✨ **تم تجهيز العرض الخاص بك!** {message.author.mention}",
                    file=image_file, 
                    view=view
                )
                
                await message.remove_reaction("⏳", self.bot.user)
                await message.add_reaction("✅")
                
            except Exception as e:
                print(f"حدث خطأ: {e}")
                await message.remove_reaction("⏳", self.bot.user)
                await message.add_reaction("❌")

async def setup(bot):
    await bot.add_cog(CustomImageSystem(bot))