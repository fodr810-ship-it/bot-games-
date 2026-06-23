import discord
from discord.ext import commands
from discord.ui import Button, View
import sqlite3
import time
import os
import sys

# وقت تشغيل البوت لحساب الـ Uptime
start_time = time.time()

# 🔘 كلاس الأزرار التفاعلية للتحكم بالبوت
class StatsView(View):
    def __init__(self, bot):
        super().__init__(timeout=60)
        self.bot = bot

    @discord.ui.button(label="🔄 تحديث", style=discord.ButtonStyle.blurple, custom_id="refresh_stats")
    async def refresh_callback(self, interaction: discord.Interaction, button: Button):
        # جلب الإحصائيات المحدثة وإعادة إرسال الإيمبد
        embed = gen_stats_embed(self.bot)
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⚠️ إعادة تشغيل البوت", style=discord.ButtonStyle.danger, custom_id="restart_bot")
    async def restart_callback(self, interaction: discord.Interaction, button: Button):
        # التحقق من أن الشخص الذي ضغط الزر لديه صلاحيات إدارية
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ هذا الزر مخصص لإدارة السيرفر العليا فقط.", ephemeral=True)
            return

        await interaction.response.send_message("🔄 **جاري إعادة تشغيل نظام البوت الآن...**", ephemeral=False)
        
        # إغلاق اتصال قاعدة البيانات بأمان وإعادة تشغيل العملية عبر الـ Script
        try:
            conn = sqlite3.connect('bot_stats.db')
            conn.close()
        except:
            pass
            
        os.execv(sys.executable, ['python'] + sys.argv)

# دالة مساعدة لإنشاء وبناء إيمبد الإحصائيات لتسهيل تحديثه
def gen_stats_embed(bot):
    # 1. حساب عمر التشغيل (Uptime)
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{hours} ساعة، {minutes} دقيقة، {seconds} ثانية"

    # 2. جلب إحصائيات الدعم من قاعدة البيانات
    solved_by_bot = 0
    human_help = 0
    try:
        conn = sqlite3.connect('bot_stats.db')
        cursor = conn.cursor()
        cursor.execute("SELECT count FROM stats WHERE stat_name='solved_by_bot'")
        row1 = cursor.fetchone()
        if row1: solved_by_bot = row1[0]

        cursor.execute("SELECT count FROM stats WHERE stat_name='human_help_required'")
        row2 = cursor.fetchone()
        if row2: human_help = row2[0]
        conn.close()
    except Exception as e:
        print(f"خطأ أثناء قراءة قاعدة البيانات في كوج الإحصائيات: {e}")

    # 3. بناء الإيمبد المنظم
    embed = discord.Embed(
        title="📊 لوحة تحكم وإحصائيات البوت الكاملة",
        color=discord.Color.dark_magenta()
    )
    embed.add_field(name="📶 سرعة الاستجابة (Ping):", value=f"`{round(bot.latency * 1000)}ms`", inline=True)
    embed.add_field(name="⏳ مدة التشغيل المستمر:", value=f"`{uptime_str}`", inline=False)
    embed.add_field(name="✅ مشاكل حُلت تلقائياً بالذكاء الاصطناعي:", value=f"**{solved_by_bot} مشكلة**", inline=True)
    embed.add_field(name="👥 مشاكل تحولت للدعم البشري:", value=f"**{human_help} مشكلة**", inline=True)
    
    # حساب الإجمالي
    total = solved_by_bot + human_help
    embed.add_field(name="📈 إجمالي التذاكر والمطالبات:", value=f"`{total}`", inline=False)
    
    embed.set_footer(text="نظام مراقبة الأداء الآلي الخاص بـ Echo")
    return embed

class StatsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🛠️ الأمر المختصر الحاسم !sts
    @commands.command(name="sts")
    @commands.has_permissions(manage_messages=True)
    async def sts_command(self, ctx):
        embed = gen_stats_embed(self.bot)
        await ctx.send(embed=embed, view=StatsView(self.bot))

    @sts_command.error
    async def sts_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ عذراً، هذا الأمر مخصص لطاقم الإدارة والدعم الفني فقط.")

async def setup(bot):
    await bot.add_cog(StatsCog(bot))