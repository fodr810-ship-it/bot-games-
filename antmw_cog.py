import discord
from discord.ext import commands

TARGET_CHANNEL_ID =  1518217927168622742 
# القائمة المسموحة (تم تحويلها لـ lowercase لتوحيد الفحص)
ALLOWED_WORDS = [
    "1v1", "2v2", "3v3", "4v4", "5v5", "6v6",
    "team", "need 1", "team we 4", "team we 3", "team we 2",
    "need 2", "need 3", "need 4", "need 5",
    "1", "2", "3", "4", "5", "6"
]

class MessageFilter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print(" Message Filter Cog Loaded Successfully")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 1. تجنب فحص رسائل البوتات
        if message.author.bot:
            return

        # 2. التحقق من أن الرسالة في الروم المستهدف
        if message.channel.id != TARGET_CHANNEL_ID:
            return

        content = message.content.lower().strip()

        # 3. الفحص الذكي: التحقق مما إذا كانت الرسالة تحتوي على أي كلمة من الكلمات المسموحة
        # أو إذا كانت الرسالة نفسها عبارة عن رقم مسموح أو نمط مسموح
        is_allowed = any(word in content for word in ALLOWED_WORDS)

        if is_allowed:
            return  # الرسالة سليمة وتحتوي على الكلمات المطلوبة، اتركها

        # 4. إذا كانت الرسالة مخالفة، يتم حذفها وإرسال تنبيه خاص للعضو
        try:
            await message.delete()

            # إرسال التنبيه في الخاص مباشرة دون الحاجة لـ fetch_user لضمان السرعة
            embed = discord.Embed(
                title="⚠️ تنبيه من نظام الفلترة الآلي",
                description=f"مرحباً {message.author.mention}، لقد تم حذف رسالتك في روم/البحث لأنها لا تحتوي على العبارات المسموح بها.",
                color=discord.Color.red()
            )
            
            # ترتيب الكلمات المسموحة في شكل أسطر واضحة داخل الإيمبد ليقرأها العضو بسهولة
            words_format = ", ".join([f"`{w}`" for w in ALLOWED_WORDS])
            embed.add_field(name="📌 الكلمات والأنماط المدعومة في الروم:", value=words_format, inline=False)
            embed.set_footer(text="يرجى الالتزام بنظام الروم لتجنب الحذف التلقائي.")
            
            try:
                await message.author.send(embed=embed)
            except discord.Forbidden:
                # في حال كان العضو مغلقاً للخاص لديه
                pass

        except discord.Forbidden:
            print(f"⚠️ خطأ: البوت لا يملك صلاحية حذف الرسائل (Manage Messages) في الروم: {message.channel.name}")
        except discord.NotFound:
            pass
        except Exception as err:
            print("❌ حدث خطأ غير متوقع في كوج الفلتر:", err)

async def setup(bot):
    await bot.add_cog(MessageFilter(bot))