import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from typing import List

# كلاس الأزرار التفاعلية لحساب وتحديث الأصوات فوراً
class PollButton(Button):
    def __init__(self, label: str, custom_id: str):
        # نضع الـ label الأولي مع رقم 0 للأصوات
        super().__init__(style=discord.ButtonStyle.blurple, label=f"{label} (0)", custom_id=custom_id)
        self.option_name = label
        self.votes = 0
        self.voted_users = set() # لمنع العضو من التصويت لنفس الخيار أكثر من مرة

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        
        # إذا كان العضو قد صوت بالفعل لهذا الخيار، نقوم بإزالة صوته (إلغاء التصويت)
        if user_id in self.voted_users:
            self.voted_users.remove(user_id)
            self.votes -= 1
            await interaction.response.send_message(f"🔄 تم إلغاء تصويتك لـ: **{self.option_name}**", ephemeral=True)
        else:
            # إضافة الصوت
            self.voted_users.add(user_id)
            self.votes += 1
            await interaction.response.send_message(f"✅ تم تسجيل تصويتك لـ: **{self.option_name}**", ephemeral=True)

        # تحديث الاسم الظاهر على الزر بالرقم الجديد
        self.label = f"{self.option_name} ({self.votes})"
        
        # تحديث الرسالة الأصلية بالإيمبد والأزرار الجديدة
        await interaction.message.edit(view=self.view)


class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 📊 أمر السلاش لإنشاء التصويت المخصص
    @app_commands.command(name="create_poll", description="إنشاء تصويت تفاعلي بأزرار في روم محدد")
    @app_commands.describe(
        channel="اختر الروم الذي تريد إرسال التصويت فيه",
        question="اكتب عنوان أو سؤال التصويت",
        options="اكتب الخيارات وافصل بينها بـ فاصلة (مثال: نعم, لا, ربما)"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def create_poll(
        self, 
        interaction: discord.Interaction, 
        channel: discord.TextChannel, 
        question: str, 
        options: str
    ):
        # تحويل نص الخيارات إلى مصفوفة عبر الفاصلة وتنظيف الفراغات
        raw_options = [opt.strip() for opt in options.split(",") if opt.strip()]
        
        # التأكد من أن عدد الخيارات منطقي (ديسكورد يدعم حتى 25 زر في الرسالة، لكن نكتفي بـ 5 للمظهر)
        if len(raw_options) < 2 or len(raw_options) > 5:
            await interaction.response.send_message("❌ يجب أن تحتوى الخيارات على خيارين كحد أدنى و 5 خيارات كحد أقصى.", ephemeral=True)
            return

        # بناء الإيمبد الخاص بالتصويت
        embed = discord.Embed(
            title="📊 تصويت  ",
            description=f"**{question}**\n\nاضغط على الأزرار بالأسفل للإدلاء بصوتك فوراُ! (يمكنك الضغط مرة أخرى لإلغاء الصوت).",
            color=discord.Color.brand_green()
        )
        embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)
        embed.set_footer(text=f"أنشئ بواسطة: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)

        # إنشاء الـ View وإضافة الأزرار التفاعلية له ديناميكياً
        view = View(timeout=None) # تظل تعمل دائماً بدون توقف
        
        for index, option in enumerate(raw_options):
            # نضع custom_id فريد لكل زر لضمان عدم التداخل
            custom_id = f"poll_{interaction.id}_{index}"
            view.add_item(PollButton(label=option, custom_id=custom_id))

        try:
            # إرسال التصويت في الروم المحدد
            await channel.send(embed=embed, view=view)
            await interaction.response.send_message(f"✅ تم إرسال التصويت بنجاح في روم {channel.mention}!", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ لا أملك صلاحية إرسال رسائل في ذلك الروم.", ephemeral=True)
        except Exception as e:
            print(f"خطأ أثناء إنشاء التصويت: {e}")
            await interaction.response.send_message("❌ حدث خطأ غير متوقع أثناء إرسال التصويت.", ephemeral=True)

    # معالجة صلاحيات استخدام الأمر
    @create_poll.error
    async def poll_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ هذا الأمر مخصص لطاقم الإدارة فقط.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(PollCog(bot))