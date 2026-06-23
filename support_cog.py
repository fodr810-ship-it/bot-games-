import discord
from discord.ext import commands

from discord.ui import Button, View

from google import genai

import sqlite3



# ==================== إعدادات الـ API والروم ====================

client = genai.Client(api_key=os.getenv("GCP_API_KEY"))

TARGET_CHANNEL_ID = 1518196896504610836  

SUPPORT_ROLE_ID = 1517019560690323516 

# =============================================================



client = genai.Client(api_key=GEMINI_API_KEY)

user_chats = {}



# 💾 إعداد قاعدة البيانات لحفظ الإحصائيات

conn = sqlite3.connect('bot_stats.db')

cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS stats (stat_name TEXT PRIMARY KEY, count INTEGER)''')

conn.commit()



def increment_stat(name):

    cursor.execute("INSERT INTO stats (stat_name, count) VALUES (?, 1) ON CONFLICT(stat_name) DO UPDATE SET count = count + 1", (name,))

    conn.commit()



def split_message(text, chunk_size=1900):

    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]



# 🔘 كلاس الأزرار التفاعلية أسفل حلول المشاكل

class SupportView(View):

    def __init__(self, author):

        super().__init__(timeout=300)

        self.author = author



    @discord.ui.button(label="✅ انحلت المشكلة", style=discord.ButtonStyle.green, custom_id="solved_btn")

    async def solved_callback(self, interaction: discord.Interaction, button: Button):

        if interaction.user != self.author:

            await interaction.response.send_message("❌ هذا الزر مخصص لصاحب المشكلة فقط.", ephemeral=True)

            return

        increment_stat("solved_by_bot")

        if self.author.id in user_chats: del user_chats[self.author.id]

        await interaction.response.edit_message(view=None)

        await interaction.channel.send(f"🎉 **الحمد لله! تم إغلاق المشكلة بنجاح بواسطة {self.author.mention}.**")



    @discord.ui.button(label="❌ ما زلت أحتاج مساعدة", style=discord.ButtonStyle.danger, custom_id="help_btn")

    async def help_callback(self, interaction: discord.Interaction, button: Button):

        if interaction.user != self.author:

            await interaction.response.send_message("❌ هذا الزر مخصص لصاحب المشكلة فقط.", ephemeral=True)

            return

        increment_stat("human_help_required")

        await interaction.response.edit_message(view=None)

        await interaction.channel.send(

            f"⚠️ **  الدعم الفني <@&{SUPPORT_ROLE_ID}>!**\n"

            f"المستخدم {self.author.mention} ما زال يواجه المشكلة ويحتاج إلى  المساعدة"

        )



# كلاس الـ Cog الرئيسي للتحكم بالأحداث والأوامر

class SupportCog(commands.Cog):

    def __init__(self, bot):

        self.bot = bot



    @commands.Cog.listener()

    async def on_message(self, message):

        if message.author == self.bot.user:

            return



        # أمر الإحصائيات !stats داخل الكوج

        if message.content.startswith('!stats'):

            cursor.execute("SELECT * FROM stats")

            rows = cursor.fetchall()

            embed = discord.Embed(title="📊 إحصائيات الدعم الفني للبوت", color=discord.Color.blue())

            if not rows:

                embed.description = "لا توجد إحصائيات مسجلة حتى الآن."

            for row in rows:

                name = "المشاكل المحلولة تلقائياً ✅" if row[0] == "solved_by_bot" else "مشاكل تدخل فيها البشر 👥" if row[0] == "human_help_required" else row[0]

                embed.add_field(name=name, value=f"**{row[1]}**", inline=False)

            await message.channel.send(embed=embed)

            return



        if message.channel.id != TARGET_CHANNEL_ID:

            return



        # التوجيه هنا مضبوط ليعطي حلاً غنياً وشاملاً ولكن دون حشو زائد ليتناسب مع الإيمبدين

        system_prompt = (

            "أنت خبير فني وعبقري في حل مشاكل ديسكورد والأنظمة والبرمجيات. "

            "صغ إجابة مفصلة، وافية وشاملة تشرح فيها المشكلة والخطوات خطوة بخطوة باللغة العربية. "

            "نسق النص باستخدام القوائم والنقاط ليكون مرتباً وجاهزاً للعرض الفوري داخل إيمبدات ديسكورد الفنية."

        )



        if message.author.id not in user_chats:

            user_chats[message.author.id] = client.aio.chats.create(

                model='gemini-2.5-flash',

                config=genai.types.GenerateContentConfig(system_instruction=system_prompt)

            )

        chat = user_chats[message.author.id]



        # 1. معالجة الصور

        if message.attachments:

            for attachment in message.attachments:

                if attachment.content_type and attachment.content_type.startswith('image/'):

                    searching_msg = await message.reply("🔍 **جاري تحليل الصورة واستخراج تفاصيل الخطأ...**")

                    try:

                        image_bytes = await attachment.read()

                        user_text = message.content if message.content else "حلل المشكلة الموجودة في هذه الصورة واكتب الحل بالتفصيل."



                        # قالب الكاش الجاهز لمشكلة Vencord

                        if "vencord" in user_text.lower() or "squirrel" in user_text.lower():

                            vencord_reply = (

                                "🛠️ **سبب المشكلة:** حدوث تضارب وتكرار في ملفات تشغيل ديسكورد الرسمية مع ملفات حقن التعديل (Vencord).\n\n"

                                "⚙️ **خطوات الحل الشاملة:**\n"

                                "1️⃣ اضغط على زر `Take me there!` الظاهر في رسالة الخطأ لديك، وسيفتح لك مسار المجلد مباشرة، قم بحذف مجلد Discord القديم بالكامل.\n"

                                "2️⃣ افتح نافذة التشغيل السريع بالنقر على أزرار `Windows + R` معاً في الكيبورد.\n"

                                "3️⃣ اكتب الأمر التالي بدقة: `%localappdata%` ثم اضغط Enter، وابحث عن مجلد باسم `Discord` واحذفه نهائياً.\n"

                                "4️⃣ كرر العملية وافتح نافذة Run واكتب الأمر: `%appdata%` ثم احذف مجلد `Discord` من هناك أيضاً.\n"

                                "5️⃣ قم بتحميل نسخة Discord الرسمية وتثبيتها من جديد، ثم أعد تشغيل مثبت Vencord واضغط على Install ليعود كل شيء للعمل بسلام."

                            )

                            embed = discord.Embed(

                                title="💡 دليل حل مشكلة ملفات Discord / Vencord المتكررة",

                                description=vencord_reply,

                                color=discord.Color.orange()

                            )

                            embed.set_footer(text=f"طلب بواسطة: {message.author.display_name}", icon_url=message.author.display_avatar.url)

                            await searching_msg.delete()

                            await message.reply(embed=embed, view=SupportView(message.author))

                            return



                        response = await chat.send_message(

                            message=[

                                user_text,

                                genai.types.Part.from_bytes(data=image_bytes, mime_type=attachment.content_type)

                            ]

                        )

                       

                        chunks = split_message(response.text)

                        await searching_msg.delete()

                       

                        # إرسال الإيمبد الأول ومرفق به الأزرار

                        embed1 = discord.Embed(title="🛠️ التقرير الفني وحل المشكلة المقترح", description=chunks[0], color=discord.Color.green())

                       

                        # إذا كان هناك جزء ثانٍ، نرسل الأول ثم نلحقه بالثاني ومعه الأزرار، وإلا نكتفي بالأول ومعه الأزرار

                        if len(chunks) > 1:

                            await message.reply(embed=embed1)

                            embed2 = discord.Embed(description=chunks[1], color=discord.Color.green())

                            embed2.set_footer(text=f"طلب بواسطة: {message.author.display_name}", icon_url=message.author.display_avatar.url)

                            await message.channel.send(embed=embed2, view=SupportView(message.author))

                        else:

                            embed1.set_footer(text=f"طلب بواسطة: {message.author.display_name}", icon_url=message.author.display_avatar.url)

                            await message.reply(embed=embed1, view=SupportView(message.author))

                        return



                    except Exception as e:

                        print(f"خطأ أثناء تحليل الصورة في الكوج: {e}")

                        await searching_msg.edit(content="❌ **عذراً، واجهت مشكلة تقنية أثناء محاولة تحليل هذه الصورة.**")

                        return



        # 2. معالجة النصوص

        if message.content:

            searching_msg = await message.reply("⚡ **جاري دراسة استفسارك وصياغة الحل الشامل...**")

            try:

                response = await chat.send_message(message=message.content)

                chunks = split_message(response.text)

                await searching_msg.delete()

               

                # إرسال الإيمبد الأول للنص

                embed1 = discord.Embed(title="🤖 الحل الفني والدليل الإرشادي", description=chunks[0], color=discord.Color.blue())

               

                # آلية الإيمبدين الأقصى

                if len(chunks) > 1:

                    await message.reply(embed=embed1)

                    embed2 = discord.Embed(description=chunks[1], color=discord.Color.blue())

                    embed2.set_footer(text=f"طلب بواسطة: {message.author.display_name}", icon_url=message.author.display_avatar.url)

                    await message.channel.send(embed=embed2, view=SupportView(message.author))

                else:

                    embed1.set_footer(text=f"طلب بواسطة: {message.author.display_name}", icon_url=message.author.display_avatar.url)

                    await message.reply(embed=embed1, view=SupportView(message.author))

            except Exception as e:

                print(f"خطأ أثناء الرد النصي في الكوج: {e}")

                await searching_msg.edit(content="❌ **عذراً، واجهت مشكلة في الاتصال بالخادم الذكي.**")



# دالة إجبارية لربط الكوج بالملف الرئيسي

async def setup(bot):

    await bot.add_cog(SupportCog(bot)) 