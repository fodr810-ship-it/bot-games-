import discord
from discord.ext import commands
import os
import sys
import asyncio
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# حل مشكلة الـ Event Loop الخاص بالـ WebSockets في أنظمة Windows لبايثون الحديث
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# ==================== إعدادات البوت والسيرفر ====================
bot.run(os.getenv("DISCORD_TOKEN"))# توكن البوت الخاص بك
GUILD_ID = 1439839910172295303  # 👈 ضع هنا آيدي سيرفرك الحقيقي لفرض المزامنة الإجبارية
# =============================================================

intents = discord.Intents.default()
intents.message_content = True  
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'======================================')
    print(f' Bot started successfully: {bot.user.name}')
    
    # 🔥 المزامنة السحرية الإجبارية القسرية للسيرفر المباشر
    try:
        guild_object = discord.Object(id=GUILD_ID)
        
        # تنظيف شجرة الأوامر الخاصة بالسيرفر أولاً لتجنب أي كاش معلق
        bot.tree.clear_commands(guild=guild_object)
        
        # نسخ كافة الأوامر من الكوجات إلى السيرفر المستهدف
        bot.tree.copy_global_to(guild=guild_object)
        
        # عمل المزامنة الفعلية وإجبار تطبيق ديسكورد على إظهارها
        synced = await bot.tree.sync(guild=guild_object)
        print(f' 🚀 Success: Force Synced {len(synced)} commands instantly to Guild!')
        for cmd in synced:
            print(f'   -> Command Loaded: /{cmd.name}')
    except Exception as e:
        print(f' ❌ Sync Error: {e}')
        
    print(f' All Cogs are loaded and active.')
    print(f'======================================')

async def main():
    async with bot:
        # شحن جميع الكوجات ونظام التحكم بالإحصائيات
        await bot.load_extension("support_cog")
        await bot.load_extension("voice_welcome_cog")
        await bot.load_extension("suggestion_cog")
        await bot.load_extension("embed_maker_cog")
        await bot.load_extension("challeng_cog")
        await bot.load_extension("stats_cog") # <--- السطر الجديد لتشغيل أمر !sts
        await bot.load_extension("say_cog")
        await bot.load_extension("antmw_cog")
        await bot.load_extension("clear_cog")
        await bot.load_extension("sts_cog")
        await bot.load_extension("apps_cog")
        await bot.load_extension("poll_cog")
        await bot.load_extension("mu_cog")
        await bot.load_extension("mute_cog")
        await bot.load_extension("tts_cog")
        await bot.start(DISCORD_TOKEN)

asyncio.run(main())