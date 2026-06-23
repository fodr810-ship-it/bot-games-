import discord
from discord.ext import commands

class Say(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        # يتأكد أن الرسالة تبدأ بـ say
        if message.content.startswith("say "):
            content = message.content[4:]  # يأخذ الكلام بعد say

            if content.strip() == "":
                return

            try:
                await message.delete()  # حذف الرسالة الأصلية
            except:
                pass  # إذا ما عنده صلاحية حذف

            await message.channel.send(content)

async def setup(bot):
    await bot.add_cog(Say(bot))