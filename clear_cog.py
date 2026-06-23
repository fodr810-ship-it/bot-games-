import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import asyncio

class ClearCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🧹 أمر السلاش لمسح الرسائل
    @app_commands.command(name="clear", description="مسح عدد معين من الرسائل من هذا الروم")
    @app_commands.describe(
        amount="عدد الرسائل المراد مسحها (الحد الأقصى 100)",
        member="اختر عضواً لمسح رسائله فقط (اختياري)"
    )
    # حصر الأمر للإدارة فقط ممن يملكون صلاحية إدارة الرسائل
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear_messages(
        self, 
        interaction: discord.Interaction, 
        amount: int, 
        member: Optional[discord.Member] = None
    ):
        # التأكد من أن العدد منطقي ومسموح به في ديسكورد
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ يرجى إدخال عدد رسائل بين 1 و 100 فقط.", ephemeral=True)
            return

        # تأكيد استلام الأمر بشكل مخفي لتجنب انتهاء وقت التفاعل (Defer)
        await interaction.response.defer(ephemeral=True)

        # دالة الفلترة: إذا تم تحديد عضو، يمسح رسائله فقط، وإلا يمسح كل شيء
        def check_filter(msg):
            if member:
                return msg.author.id == member.id
            return True

        try:
            # القيام بعملية الحذف الذكي (بحد أقصى مقدار الرقم المحدد)
            deleted = await interaction.channel.purge(limit=amount, check=check_filter)
            
            # صياغة رسالة النجاح حسب نوع الحذف
            if member:
                success_msg = f"✅ تم مسح `{len(deleted)}` رسالة خاصة بالعضو {member.mention} بنجاح."
            else:
                success_msg = f"✅ تم مسح `{len(deleted)}` رسالة من الروم بنجاح."

            # إرسال رسالة التأكيد للمشرف (مخفية)
            await interaction.followup.send(success_msg, ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send("⚠️ لا أملك صلاحية `إدارة الرسائل` أو صلاحيات كافية للحذف في هذا الروم.", ephemeral=True)
        except Exception as e:
            print(f"خطأ أثناء تنفيذ أمر مسح الرسائل: {e}")
            await interaction.followup.send("❌ حدث خطأ غير متوقع أثناء محاولة مسح الرسائل.", ephemeral=True)

    # معالجة أخطاء الصلاحيات للأعضاء العاديين
    @clear_messages.error
    async def clear_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.errors.MissingPermissions):
            await interaction.response.send_message("❌ هذا الأمر مخصص لطاقم الإدارة فقط (يتطلب صلاحية `إدارة الرسائل`).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(ClearCog(bot))