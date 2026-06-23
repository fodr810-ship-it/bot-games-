import discord
from discord import app_commands
from discord.ext import commands

class ServerSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ================== SERVER STATS ==================
    @app_commands.command(name="sts", description="عرض احصائيات السيرفر")
    async def sts(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild:
            return await interaction.response.send_message("❌ هذا الأمر داخل سيرفر فقط.", ephemeral=True)

        total = guild.member_count
        bots = sum(m.bot for m in guild.members)
        humans = total - bots
        online = sum(m.status != discord.Status.offline for m in guild.members)

        embed = discord.Embed(
            title=f"📊 احصائيات {guild.name}",
            color=discord.Color.blurple()
        )

        embed.add_field(name="👥 إجمالي الأعضاء", value=total, inline=True)
        embed.add_field(name="🙂 الأعضاء", value=humans, inline=True)
        embed.add_field(name="🤖 البوتات", value=bots, inline=True)

        embed.add_field(name="🟢 الأونلاين", value=online, inline=True)
        embed.add_field(name="💬 رومات كتابية", value=len(guild.text_channels), inline=True)
        embed.add_field(name="🔊 رومات صوتية", value=len(guild.voice_channels), inline=True)

        embed.add_field(name="🎭 عدد الرتب", value=len(guild.roles), inline=True)
        embed.add_field(name="🚀 عدد البوستات", value=guild.premium_subscription_count, inline=True)
        embed.add_field(name="⭐ مستوى البوست", value=guild.premium_tier, inline=True)

        embed.add_field(name="🆔 آيدي السيرفر", value=guild.id, inline=False)
        embed.add_field(
            name="📅 تاريخ الإنشاء",
            value=f"<t:{int(guild.created_at.timestamp())}:F>",
            inline=False
        )

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)

    # ================== MEMBER INFO ==================
    @app_commands.command(name="memberinfo", description="عرض معلومات عضو")
    async def memberinfo(self, interaction: discord.Interaction, member: discord.Member):
        roles = [role.mention for role in member.roles if role.name != "@everyone"]

        embed = discord.Embed(
            title=f"👤 معلومات {member}",
            color=discord.Color.green()
        )

        embed.add_field(name="🆔 ID", value=member.id, inline=False)
        embed.add_field(
            name="📅 انضم للسيرفر",
            value=f"<t:{int(member.joined_at.timestamp())}:F>",
            inline=False
        )
        embed.add_field(
            name="📅 إنشاء الحساب",
            value=f"<t:{int(member.created_at.timestamp())}:F>",
            inline=False
        )
        embed.add_field(
            name="🎭 الرتب",
            value=", ".join(roles) if roles else "لا يوجد",
            inline=False
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    # ================== SERVER ICON ==================
    @app_commands.command(name="servericon", description="عرض صورة السيرفر")
    async def servericon(self, interaction: discord.Interaction):
        guild = interaction.guild
        if not guild or not guild.icon:
            return await interaction.response.send_message("❌ لا توجد صورة للسيرفر.", ephemeral=True)

        embed = discord.Embed(
            title=f"🖼️ صورة {guild.name}",
            color=discord.Color.orange()
        )
        embed.set_image(url=guild.icon.url)

        await interaction.response.send_message(embed=embed)

    # ================== ROLES ==================
    @app_commands.command(name="roles", description="عرض جميع رتب السيرفر")
    async def roles(self, interaction: discord.Interaction):
        guild = interaction.guild
        roles = [role.mention for role in guild.roles if role.name != "@everyone"]

        embed = discord.Embed(
            title=f"🎭 رتب {guild.name}",
            description="\n".join(roles[:50]) if roles else "لا يوجد رتب",
            color=discord.Color.red()
        )

        embed.set_footer(text=f"عدد الرتب: {len(guild.roles)}")

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerSystem(bot))