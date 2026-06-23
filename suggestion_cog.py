import discord
from discord.ext import commands
from discord.ui import Button, View

# ==================== إعدادات رومات الاقتراحات ====================
SUGGESTION_INPUT_CHANNEL_ID = 1518210739851104368  # آيدي الروم الذي يكتب فيه الأعضاء اقتراحاتهم
SUGGESTION_LOG_CHANNEL_ID = 1518210681151688794  # آيدي روم اللوق الذي ستترحل إليه الاقتراحات في إيمبد
# =================================================================

# 🔘 كلاس أزرار التصويت أسفل الاقتراح
class SuggestionView(View):
    def __init__(self):
        super().__init__(timeout=None) # لتظل الأزرار تعمل دائماً حتى بعد إعادة تشغيل البوت
        self.upvotes = 0
        self.downvotes = 0

    @discord.ui.button(label="👍 0", style=discord.ButtonStyle.green, custom_id="vote_up")
    async def upvote_callback(self, interaction: discord.Interaction, button: Button):
        # زيادة عدد الأصوات المؤيدة وتحديث الزر
        self.upvotes += 1
        button.label = f"👍 {self.upvotes}"
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label="👎 0", style=discord.ButtonStyle.danger, custom_id="vote_down")
    async def downvote_callback(self, interaction: discord.Interaction, button: Button):
        # زيادة عدد الأصوات المعارضة وتحديث الزر
        self.downvotes += 1
        button.label = f"👎 {self.downvotes}"
        await interaction.response.edit_message(view=self)

# كلاس الكوج الرئيسي للاقتراحات
class SuggestionCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # تجنب قراءة رسائل البوتات
        if message.author.bot:
            return

        # التحقق مما إذا كانت الرسالة مكتوبة في روم الاقتراحات المحدد
        if message.channel.id == SUGGESTION_INPUT_CHANNEL_ID:
            suggestion_content = message.content
            member = message.author

            # 1. حذف رسالة العضو الأصلية فوراً لتنظيف الروم
            try:
                await message.delete()
            except discord.Forbidden:
                print("⚠️ البوت لا يملك صلاحية حذف الرسائل (Manage Messages) في هذا الروم.")
            except discord.NotFound:
                pass

            # التحقق من أن الاقتراح ليس فارغاً (مثلاً لو أرسل ملف أو صورة فقط)
            if not suggestion_content:
                return

            # 2. جلب روم اللوق المخصص لترحيل الاقتراحات إليه
            log_channel = self.bot.get_channel(SUGGESTION_LOG_CHANNEL_ID)
            if log_channel is None:
                print(f"❌ لم يتم العثور على روم اللوق بالآيدي المحدد: {SUGGESTION_LOG_CHANNEL_ID}")
                return

            # 3. بناء الإيمبد المنظم للاقتراح
            embed = discord.Embed(
                title="💡 اقتراح جديد !",
                description=f"```{suggestion_content}```",
                color=discord.Color.purple()
            )
            embed.add_field(name="👤 صاحب الاقتراح:", value=member.mention, inline=False)
            embed.add_field(name="🆔 آيدي الحساب:", value=f"`{member.id}`", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            embed.set_footer(text=f"سيرفر: {message.guild.name} • نظام الاقتراحات الآلي")

            # 4. ترحيل الإيمبد إلى روم اللوق مع منشن العضو في الرسالة وتفعيل الأزرار
            await log_channel.send(content=f"🔔 اقتراح جديد مقدم من {member.mention}", embed=embed, view=SuggestionView())

# دالة ربط الكوج بالملف الرئيسي
async def setup(bot):
    await bot.add_cog(SuggestionCog(bot))