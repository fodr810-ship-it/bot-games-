import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from gtts import gTTS
import os

# الرموز للتقييم
RATING_EMOJIS = {"⭐": 1, "⭐⭐": 2, "⭐⭐⭐": 3, "⭐⭐⭐⭐": 4, "⭐⭐⭐⭐⭐": 5}

class RatingView(View):
    def __init__(self, original_message, staff_member):
        super().__init__(timeout=60)
        self.original_message = original_message
        self.staff_member = staff_member

    @discord.ui.select(placeholder="اختر تقييمك للخدمة...", options=[discord.SelectOption(label=k, value=str(v)) for k, v in RATING_EMOJIS.items()])
    async def select_callback(self, interaction: discord.Interaction, select: Select):
        rating = select.values[0]
        await interaction.response.send_message(f"شكراً لتقييمك! (التقييم: {rating}/5)", ephemeral=True)
        
        # تحديث الرسالة الأصلية
        embed = self.original_message.embeds[0]
        embed.add_field(name="📊 التقييم النهائي", value=f"{'⭐' * int(rating)} ({rating}/5)", inline=False)
        embed.color = discord.Color.gold()
        await self.original_message.edit(embed=embed, view=None)
        self.stop()

class SupportView(View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

    @discord.ui.button(label="استلام", style=discord.ButtonStyle.green, custom_id="take_case")
    async def take_callback(self, interaction: discord.Interaction, button: Button):
        embed = interaction.message.embeds[0]
        embed.add_field(name="👤 تم الخدمة بواسطة", value=interaction.user.mention, inline=False)
        embed.color = discord.Color.blue()
        
        button.disabled = True
        finish_view = View()
        finish_btn = Button(label="✅ تمت الخدمة", style=discord.ButtonStyle.blurple)
        
        async def finish_callback(i: discord.Interaction):
            await i.response.edit_message(content="تم إرسال طلب التقييم للعضو.", view=None)
            # إرسال تقييم خاص
            try:
                await self.member.send("نرجو تقييم الخدمة التي تلقيتها:", view=RatingView(interaction.message, interaction.user))
            except:
                await i.channel.send(f"{self.member.mention} لم أستطع إرسال التقييم (الخاص مغلق).")

        finish_btn.callback = finish_callback
        finish_view.add_item(finish_btn)
        await interaction.response.edit_message(embed=embed, view=finish_view)

class VoiceWelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot or after.channel is None or after.channel.id != 1518204868920348802: return

        # 1. الترحيب الصوتي (ويلكم فقط)
        voice_client = await after.channel.connect() if not member.guild.voice_client else member.guild.voice_client
        if voice_client.channel != after.channel: await voice_client.move_to(after.channel)
        
        tts = gTTS(text="Welcome", lang="en")
        tts.save("w.mp3")
        voice_client.play(discord.FFmpegPCMAudio("w.mp3"), after=lambda e: os.remove("w.mp3"))

        # 2. الإيمبد المرتب
        channel = self.bot.get_channel(1518275391494819900) 
        embed = discord.Embed(title="🔔 طلب دعم جديد", description=f"العضو: {member.mention}", color=discord.Color.green())
        embed.set_footer(text=f"ID: {member.id}")
        await channel.send(embed=embed, view=SupportView(member))

async def setup(bot):
    await bot.add_cog(VoiceWelcomeCog(bot))