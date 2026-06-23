import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class EmbedMakerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🛠️ أمر السلاش القياسي
    @app_commands.command(name="send_embed", description="إرسال إيمبد مخصص ومطور في الروم الحالي")
    @app_commands.describe(
        title="عنوان الإيمبد الرئيسي",
        description="النص الداخلي للإيمبد (يدعم الـ Markdown والأسطر الجديدة عبر \\n)",
        color="اختر لون الإيمبد من القائمة الجاهزة",
        image="ارفع صورة لتظهر داخل الإيمبد (اختياري)"
    )
    @app_commands.choices(color=[
        app_commands.Choice(name="🔵 أزرق", value="blue"),
        app_commands.Choice(name="🟢 أخضر", value="green"),
        app_commands.Choice(name="🔴 أحمر", value="red"),
        app_commands.Choice(name="🟡 أصفر", value="yellow"),
        app_commands.Choice(name="🟠 برتقالي", value="orange"),
        app_commands.Choice(name="⚫ أسود", value="black"),
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def send_embed(
        self, 
        interaction: discord.Interaction, 
        title: str, 
        description: str, 
        color: app_commands.Choice[str], 
        image: Optional[discord.Attachment] = None
    ):
        # 1. معالجة خريطة الألوان
        color_map = {
            "blue": discord.Color.blue(),
            "green": discord.Color.green(),
            "red": discord.Color.red(),
            "yellow": discord.Color.from_rgb(255, 215, 0),
            "orange": discord.Color.orange(),
            "black": discord.Color.from_rgb(1, 1, 1)
        }
        chosen_color = color_map.get(color.value, discord.Color.default())

        # 2. تهيئة وتنسيق النص والأسطر
        formatted_description = description.replace("\\n", "\n")
        
        embed = discord.Embed(
            title=title,
            description=formatted_description,
            color=chosen_color
        )
        embed.set_footer(text=f"بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # 3. التحقق من الصور وإضافتها
        if image:
            if image.content_type and image.content_type.startswith("image/"):
                embed.set_image(url=image.url)
            else:
                await interaction.response.send_message("❌ الملف المرفق ليس صورة صالحة!", ephemeral=True)
                return

        # 4. إرسال الإيمبد واستجابة مخفية
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ تم إرسال الإيمبد بنجاح!", ephemeral=True)

    # معالجة صلاحيات الأعضاء
    @send_embed.error
    async def embed_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ هذا الأمر مخصص للإدارة فقط (صلاحية إدارة الرسائل).", ephemeral=True)

# الدالة القياسية النقية لربط الكوج
async def setup(bot):
    await bot.add_cog(EmbedMakerCog(bot))