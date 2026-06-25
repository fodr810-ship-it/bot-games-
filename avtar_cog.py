import discord
from discord.ext import commands
import asyncio
import io
import aiohttp
from PIL import Image, ImageDraw, ImageFilter
import os

class DownloadAvatarView(discord.ui.View):
    def __init__(self, member_name: str, avatar_url: str, banner_url: str = None):
        super().__init__(timeout=None)
        self.member_name = member_name
        self.avatar_url = avatar_url
        self.banner_url = banner_url

    @discord.ui.button(label="تنزيل", style=discord.ButtonStyle.secondary, custom_id="download_avatar_btn")
    async def download_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        msg = f"**الصور الخاصة بـ {self.member_name}** 🖼️\n\n**الافاتار:**\n{self.avatar_url}\n"
        msg += f"\n**البنر:**\n{self.banner_url}" if self.banner_url else "\n**البنر:** لا يوجد بنر."
        await interaction.response.send_message(msg, ephemeral=True)

class AvatarSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.AVATAR_CHANNEL_ID = 1519058537597108407

    def create_image_sync(self, avatar_bytes, banner_bytes):
        canvas_w, canvas_h = 900, 500
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

    async def generate_profile_image(self, avatar_url, banner_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(avatar_url) as resp: avatar_bytes = await resp.read()
            banner_bytes = None
            if banner_url:
                async with session.get(banner_url) as resp: banner_bytes = await resp.read()
        buffer = await asyncio.to_thread(self.create_image_sync, avatar_bytes, banner_bytes)
        return discord.File(fp=buffer, filename="profile.png")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = self.bot.get_channel(self.AVATAR_CHANNEL_ID)
        if not channel: return
        user = await self.bot.fetch_user(member.id)
        avatar_url = user.avatar.with_size(512).url if user.avatar else user.default_avatar.with_size(512).url
        banner_url = user.banner.with_size(1024).url if user.banner else None
        image_file = await self.generate_profile_image(avatar_url, banner_url)
        await channel.send(file=image_file, view=DownloadAvatarView(user.name, avatar_url, banner_url))

    @commands.command(name="عرض")
    async def show_avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        msg = await ctx.send("⏳ جاري التصميم...")
        user = await self.bot.fetch_user(member.id)
        avatar_url = user.avatar.with_size(512).url if user.avatar else user.default_avatar.with_size(512).url
        banner_url = user.banner.with_size(1024).url if user.banner else None
        image_file = await self.generate_profile_image(avatar_url, banner_url)
        await msg.delete()
        await ctx.send(file=image_file, view=DownloadAvatarView(user.name, avatar_url, banner_url))

    @commands.command(name="ارشيف")
    @commands.has_permissions(administrator=True)
    async def archive_server(self, ctx):
        await ctx.send("⏳ جاري أرشفة الأعضاء الذين يمتلكون بنر فقط...")
        
        count = 0
        for member in [m for m in ctx.guild.members if not m.bot]:
            try:
                user = await self.bot.fetch_user(member.id)
                
                # الشرط: هل البنر موجود؟
                if user.banner:
                    avatar_url = user.avatar.with_size(512).url if user.avatar else user.default_avatar.with_size(512).url
                    banner_url = user.banner.with_size(1024).url
                    
                    image_file = await self.generate_profile_image(avatar_url, banner_url)
                    view = DownloadAvatarView(user.name, avatar_url, banner_url)

                    await ctx.send(file=image_file, view=view)
                    count += 1
                    
                    # تأخير لمنع حظر الـ API
                    await asyncio.sleep(2.5)
            except Exception as e:
                print(f"حدث خطأ مع {member.name}: {e}")
                continue
        
        await ctx.send(f"✅ تمت أرشفة {count} عضواً يمتلكون بنر بنجاح!")

async def setup(bot):
    await bot.add_cog(AvatarSystem(bot))