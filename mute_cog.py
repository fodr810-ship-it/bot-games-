import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class MuteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="mute", description="حظر مؤقت لعضو من السيرفر")
    @app_commands.describe(member="العضو المراد حظره", duration="المدة بالدقائق", reason="سبب الحظر")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int, reason: str):
        
        # ⚠️ ضع الأرقام الصحيحة هنا
        MUTE_ROLE_ID = 1518295982041731283  # ID رتبة الميوت
        LOG_CHANNEL_ID = 1439853749483995276 # ID روم اللوق
        
        role = interaction.guild.get_role(MUTE_ROLE_ID)
        log_channel = interaction.guild.get_channel(LOG_CHANNEL_ID)

        if not role:
            await interaction.response.send_message("لم يتم العثور على رتبة الميوت، تأكد من ID الرتبة.", ephemeral=True)
            return

        # إضافة الرتبة
        await member.add_roles(role, reason=reason)
        
        # رسالة العضو
        embed_user = discord.Embed(
            title="تم حظرك مؤقتاً",
            description=f"لقد تم حظرك في {interaction.guild.name}",
            color=discord.Color.red()
        )
        embed_user.add_field(name="السبب", value=reason, inline=False)
        embed_user.add_field(name="المدة", value=f"{duration} دقيقة", inline=False)
        try:
            await member.send(embed=embed_user)
        except:
            pass 

        # رسالة اللوق
        embed_log = discord.Embed(title="سجل الحظر المؤقت", color=discord.Color.orange())
        embed_log.add_field(name="العضو", value=member.mention, inline=True)
        embed_log.add_field(name="المشرف", value=interaction.user.mention, inline=True)
        embed_log.add_field(name="المدة", value=f"{duration} دقيقة", inline=False)
        embed_log.add_field(name="السبب", value=reason, inline=False)
        
        if log_channel:
            await log_channel.send(embed=embed_log)

        await interaction.response.send_message(f"تم حظر {member.name} لمدة {duration} دقيقة.", ephemeral=True)

        # انتظار المدة ثم إزالة الرتبة
        await asyncio.sleep(duration * 60)
        await member.remove_roles(role, reason="انتهاء مدة الميوت")
        
        if log_channel:
            await log_channel.send(f"انتهت مدة حظر {member.mention}")

async def setup(bot):
    await bot.add_cog(MuteCog(bot))
    print("MuteCog Loaded Successfully")