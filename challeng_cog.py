import discord
from discord.ext import commands
from discord import app_commands
import asyncio

ALLOWED_CHANNEL_ID = 1518217927168622742
CATEGORY_NAME = "〢𝐋𝐎𝐆"

challenges = [
    "1v1","2v2","3v3","4v4","5v5","6v6",
    "Team","team","Need 1",
    "1","team we 4","team we 3","Team we 2",
    "4","3","2","5","6","Need 2 ",
    "Need 3","Need 4","Need 5",
]

class ChallengeButton(discord.ui.View):
    def __init__(self, author_id, guild_id, message_id):
        super().__init__(timeout=120)
        self.author_id = author_id
        self.guild_id = guild_id
        self.message_id = message_id
    async def on_timeout(self):
        # عندما لا يتم ضغط الزر خلال 120 ثانية سيعمل هذا
        # تعطيل كل الأزرار في الـ view
        for item in self.children:
            item.disabled = True

        try:
            # عدّل الرسالة الأصلية لتعكس أن الوقت انتهى
            await self.original_message.edit(content="⏱️ انتهى وقت التحدي!", view=self)
        except Exception as e:
            print("❌ خطأ عند انتهاء المدة:", e)
            
    @discord.ui.button(label="تحدي اللاعب ⚔️ ", style=discord.ButtonStyle.danger)
    async def challenge(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.author_id:
            return await interaction.response.send_message("❌ لا يمكنك تحدي نفسك!", ephemeral=True)

        button.disabled = True
        button.label = "✅ تم أخذ التحدي"
        button.style = discord.ButtonStyle.secondary
        await interaction.message.edit(view=self)

        target_user = await interaction.client.fetch_user(self.author_id)

        view = AcceptDeclineView(interaction.user.id, self.author_id, self.guild_id, interaction.message, self)

        embed = discord.Embed(
            title="⚔️ تحدي جديد!",
            description=f"لقد تم تحديك من قبل <@{interaction.user.id}>",
            color=discord.Color.dark_red()
        )

        await target_user.send(embed=embed, view=view)
        await interaction.response.send_message("✅ تم إرسال الطلب في الخاص", ephemeral=True)


class AcceptDeclineView(discord.ui.View):
    def __init__(self, challenger_id, challenged_id, guild_id, original_message, original_view):
        super().__init__(timeout=None)
        self.challenger_id = challenger_id
        self.challenged_id = challenged_id
        self.guild_id = guild_id
        self.original_message = original_message
        self.original_view = original_view

    @discord.ui.button(label="✅ قبول", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.client.get_guild(self.guild_id)

        category = discord.utils.get(guild.categories, name=CATEGORY_NAME)
        if not category:
            category = await guild.create_category(CATEGORY_NAME)

        channel = await guild.create_text_channel(
            name=f"challenge-{interaction.user.name}",
            category=category,
            overwrites={
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.get_member(self.challenger_id): discord.PermissionOverwrite(view_channel=True, send_messages=True),
                guild.get_member(self.challenged_id): discord.PermissionOverwrite(view_channel=True, send_messages=True),
            }
        )

        await interaction.response.edit_message(
            content=f"✅ تم قبول التحدي!\n\n📍 روم التحدي: {channel.mention}",
            view=None
        )

        challenger_user = await interaction.client.fetch_user(self.challenger_id)

        room_link = f"https://discord.com/channels/{guild.id}/{channel.id}"

        embed = discord.Embed(
            title="✅ تم قبول التحدي!",
            description=f"""تم قبول التحدي 🎉

🔗 رابط الروم:
{room_link}""",
            color=discord.Color.green()
        )

        await challenger_user.send(embed=embed)
        await channel.send(f"<@{self.challenger_id}> <@{self.challenged_id}>")

        welcome = discord.Embed(
            title="🎮 مرحباً بكم في روم التحدي",
            description="""أهلاً بكم في روم التحدي ⚔️

📌 القوانين:
• يمنع السب أو الإساءة
• يمنع التخريب
• الالتزام بوقت الروم
• احترام الخصم

⏳ مدة الروم: 3 دقائق
""",
            color=discord.Color.blue()
        )

        await channel.send(embed=welcome)
        await asyncio.sleep(180)
        await channel.delete()

    @discord.ui.button(label="❌ رفض", style=discord.ButtonStyle.danger)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        challenger_user = await interaction.client.fetch_user(self.challenger_id)

        embed = discord.Embed(
            title="❌ تم رفض التحدي",
            description=f"تم رفض التحدي من قبل <@{interaction.user.id}>",
            color=discord.Color.red()
        )

        await challenger_user.send(embed=embed)

        await interaction.response.edit_message(
            content="❌ تم رفض التحدي",
            view=None
        )

        # ✨ إعادة تفعيل زر التحدي في الرسالة الأصلية
        try:
            # استرجاع الـ view الأصلي وإعادة تفعيل الزر
            new_view = ChallengeButton(self.challenger_id, self.guild_id, self.original_message.id)
            await self.original_message.edit(view=new_view)
        except Exception as e:
            print("❌ خطأ بإعادة تفعيل زر التحدي:", e)

class Challenges(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.channel.id != ALLOWED_CHANNEL_ID:
            return

        content = message.content.lower()
        found = next((c for c in challenges if content == c.lower()), None)
        if not found:
            return

        reply = await message.reply(f"⚔️ تم الكشف عن تحدي {found}!")
        view = ChallengeButton(message.author.id, message.guild.id, reply.id)
        await reply.edit(view=view)
        view.original_message = reply 

async def setup(bot):
    await bot.add_cog(Challenges(bot))