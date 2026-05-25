"""
ALSHAMS SOLAR — Energo-Audit Telegram Bot
Ishlab chiqarish uchun tayyor versiya. Python 3.9+
"""
import time
import json
import zlib
import base64
import io
import re
import logging

import telebot
from google import genai
from PIL import Image

# ─── LOGGING ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("bot.log", encoding="utf-8"),
    ],
)
log = logging.getLogger(__name__)

# ─── SOZLAMALAR — faqat shu yerda o'zgartiring ───────────────────────────────
TELEGRAM_TOKEN = "8287973493:AAHmW_oztCG8QzX9bWu9lvHyGXcNv5PWN80"
GEMINI_API_KEY = "AIzaSyAU3hDmEAVdIA0LHUPUZVpry4tUHSjRn9w"
WEB_APP_URL    = "https://5purdnz3t2jbvoddmlsxmw.streamlit.app/"

# ─── MIJOZLAR VA GEMINI ───────────────────────────────────────────────────────
bot    = telebot.TeleBot(TELEGRAM_TOKEN, threaded=False)
client = genai.Client(api_key=GEMINI_API_KEY)

# ─── HAR BIR FOYDALANUVCHI UCHUN XOTIRA ──────────────────────────────────────
user_store: dict = {}

def _init(cid: int):
    if cid not in user_store:
        user_store[cid] = {"texts": [], "photos": []}

# ─── AI PROMPT ───────────────────────────────────────────────────────────────
AI_PROMPT = """
Sen professional Energo-Audit AI agentisan. Sanga auditor tomonidan yuborilgan
tartibsiz matnlar va obyekt rasmlari beriladi.

QATTIQ QOIDALAR:
1. Faqat toza JSON qaytarish — hech qanday ``` yoki tushuntirish yozma.
2. Har bir massiv ROPPA-ROSA 12 ta son (yanvar–dekabr tartibida).
3. Aniq ma'lumot bo'lmasa, mantiqiy taxminiy qiymat yoz.
4. Barcha raqamli qiymatlar — son turi (string emas).

Faqat quyidagi JSON tuzilmasini qaytargin:
{
  "mijoz_ismi": "To'liq ismi sharifi",
  "manzil": "Shahar, ko'cha, uy",
  "kadastr_raqami": "",
  "elektr_raqami": "",
  "gaz_raqami": "",
  "kenglik": "41.2995",
  "uzunlik": "69.2401",
  "qurilgan_yili": "1990",
  "oxirgi_remont": "2015",
  "umumiy_m": 120.0,
  "qavat_soni": 1,
  "bolimlar_soni": 3,
  "odam_soni": 4,
  "oyna_soni": 5,
  "eshik_soni": 1,
  "solar_kw": 5.0,
  "lampa_soni": 10,
  "kond_soni": 1,
  "boyler_soni": 1,
  "dazmol_soni": 1,
  "muzlat_soni": 1,
  "tv_soni": 1,
  "pech_soni": 1,
  "kir_soni": 1,
  "nasos_soni": 1,
  "temp_1": 26.3, "hum_1": 27.6,
  "temp_2": 21.2, "hum_2": 31.5,
  "temp_3": 22.0, "hum_3": 30.0,
  "temp_4": 23.5, "hum_4": 28.0,
  "e_vals_y1": [150,160,140,130,180,220,250,240,190,150,160,170],
  "g_vals_y1": [300,280,200,100,50,20,10,15,40,120,250,350],
  "e_vals_y2": [155,165,145,135,185,225,255,245,195,155,165,175],
  "g_vals_y2": [310,290,210,105,55,25,15,20,45,125,255,360],
  "e_vals_y3": [160,170,150,140,190,230,260,250,200,160,170,180],
  "g_vals_y3": [320,300,220,110,60,30,20,25,50,130,260,370]
}
"""

# ─── JSON TOZALAGICH (Gemini markdown chiqarsa ham ishlaydi) ──────────────────
def extract_json(raw: str) -> dict:
    text = raw.strip()
    # Barcha ``` fences ni o'chirish
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).strip()
    text = text.replace("```", "").strip()

    # Birinchi { dan oxirgi } gacha topish
    start = text.find("{")
    if start == -1:
        raise ValueError("JSON topilmadi. Gemini javobi: " + text[:200])

    depth, end = 0, start
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i
                break

    parsed = json.loads(text[start:end + 1])
    return parsed

# ─── PAYLOAD ZICHLASHTIRISH ───────────────────────────────────────────────────
def compress(data: dict) -> str:
    raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
    return base64.urlsafe_b64encode(zlib.compress(raw, level=9)).decode("utf-8")

# ─── MASSIVNI TEKSHIRISH (12 ta bo'lishi shart) ───────────────────────────────
def fix_array(arr, default_val=100):
    if not isinstance(arr, list):
        arr = []
    arr = [int(x) if isinstance(x, (int, float)) else default_val for x in arr]
    return (arr + [default_val] * 12)[:12]

# ═══════════════════════════════════════════════════════════════════════════════
#                              HANDLER'LAR
# ═══════════════════════════════════════════════════════════════════════════════

@bot.message_handler(commands=["start"])
def cmd_start(message):
    cid = message.chat.id
    user_store[cid] = {"texts": [], "photos": []}
    bot.reply_to(
        message,
        "🏢 *ALSHAMS SOLAR* — Energo-Audit tizimiga xush kelibsiz!\n\n"
        "📋 *Qanday ishlaydi:*\n"
        "1️⃣ Obyekt haqida matn yuboring (istalgan tartibda)\n"
        "2️⃣ Xona rasmlarini yuboring\n"
        "3️⃣ /analyze buyrug'ini bosing\n\n"
        "📌 Buyruqlar:\n"
        "/status — yig'ilgan ma'lumotlar\n"
        "/clear — tozalash\n"
        "/analyze — tahlil qilish",
        parse_mode="Markdown",
    )

@bot.message_handler(commands=["clear"])
def cmd_clear(message):
    cid = message.chat.id
    user_store[cid] = {"texts": [], "photos": []}
    bot.reply_to(message, "🧹 Barcha ma'lumotlar tozalandi. Yangidan boshlashingiz mumkin.")

@bot.message_handler(commands=["status"])
def cmd_status(message):
    cid = message.chat.id
    _init(cid)
    d = user_store[cid]
    bot.reply_to(
        message,
        f"📊 *Hozirgi holat:*\n"
        f"📝 Matnlar: *{len(d['texts'])}* ta\n"
        f"📸 Rasmlar: *{len(d['photos'])}* ta\n\n"
        f"Tayyor bo'lsa /analyze bosing.",
        parse_mode="Markdown",
    )

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text.startswith("/"):
        return
    cid = message.chat.id
    _init(cid)
    user_store[cid]["texts"].append(message.text)
    n = len(user_store[cid]["texts"])
    bot.reply_to(message, f"📥 Matn qabul qilindi ({n}-matn). Yana matn yoki rasm yuboring, yoki /analyze.")

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    cid = message.chat.id
    _init(cid)
    # Eng yuqori sifatli versiyasini olish
    user_store[cid]["photos"].append(message.photo[-1].file_id)
    n = len(user_store[cid]["photos"])
    bot.reply_to(message, f"📸 Rasm qabul qilindi ({n}-rasm). Yana rasm yuboring yoki /analyze.")

@bot.message_handler(content_types=["document"])
def handle_document(message):
    bot.reply_to(message, "⚠️ Faqat matn va rasm qabul qilinadi. Hujjat formati qo'llab-quvvatlanmaydi.")

@bot.message_handler(commands=["analyze"])
def cmd_analyze(message):
    cid = message.chat.id
    _init(cid)
    data = user_store[cid]

    if not data["texts"] and not data["photos"]:
        bot.reply_to(
            message,
            "❌ Hech qanday ma'lumot yo'q!\n"
            "Avval matn va/yoki rasmlar yuboring, keyin /analyze bosing."
        )
        return

    total = len(data["photos"])
    status_msg = bot.send_message(cid, "⏳ Boshlandi... Rasmlar yuklanmoqda.")
    log.info(f"[{cid}] Tahlil boshlandi: {len(data['texts'])} matn, {total} rasm")

    try:
        # ── 1. Gemini uchun tarkib yig'ish ──────────────────────────────
        contents = [AI_PROMPT]

        if data["texts"]:
            combined = "\n---\n".join(data["texts"])
            contents.append(f"MATNLI MA'LUMOTLAR:\n{combined}")

        for idx, file_id in enumerate(data["photos"]):
            bot.edit_message_text(
                f"⏳ Rasmlar yuklanmoqda... ({idx + 1}/{total})",
                cid, status_msg.message_id
            )
            info = bot.get_file(file_id)
            raw  = bot.download_file(info.file_path)

            # Siqish va o'lchamni kamaytirish
            img = Image.open(io.BytesIO(raw))
            img.thumbnail((1280, 1280), Image.LANCZOS)
            buf = io.BytesIO()
            img.convert("RGB").save(buf, format="JPEG", quality=82, optimize=True)
            buf.seek(0)
            contents.append(Image.open(buf))

        # ── 2. Gemini API chaqiruvi ──────────────────────────────────────
        bot.edit_message_text(
            "🧠 AI tahlil qilmoqda... (10-30 soniya kutiladi)",
            cid, status_msg.message_id
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )
        log.info(f"[{cid}] Gemini javobi keldi ({len(response.text)} belgi)")

        # ── 3. JSON tozalash va tekshirish ───────────────────────────────
        parsed = extract_json(response.text)
        log.info(f"[{cid}] JSON muvaffaqiyatli parsing: {list(parsed.keys())[:5]}...")

        # Massivlarni 12 ta elementga keltirish
        for key in ("e_vals_y1","g_vals_y1","e_vals_y2","g_vals_y2","e_vals_y3","g_vals_y3"):
            parsed[key] = fix_array(parsed.get(key, []))

        # ── 4. Zichlashtirish va URL yaratish ────────────────────────────
        payload   = compress(parsed)
        final_url = f"{WEB_APP_URL}?audit_data={payload}"

        log.info(f"[{cid}] URL uzunligi: {len(final_url)} belgi")

        # URL juda uzun bo'lsa ogohlantirish (Telegram 4096 limit)
        if len(final_url) > 4000:
            log.warning(f"[{cid}] URL juda uzun: {len(final_url)}")

        # ── 5. Natijani yuborish ─────────────────────────────────────────
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(
            telebot.types.InlineKeyboardButton(
                text="🖥️ SAYTGA O'TISH VA WORD YUKLAB OLISH",
                url=final_url
            )
        )

        # Keshni tozalash
        user_store[cid] = {"texts": [], "photos": []}

        bot.delete_message(cid, status_msg.message_id)
        bot.send_message(
            cid,
            "✅ *Tahlil muvaffaqiyatli yakunlandi!*\n\n"
            "Quyidagi tugmani bosib saytga o'ting:\n"
            "• Ma'lumotlar avtomatik to'ldiriladi\n"
            "• Tekshirib, Word hujjatni yuklab oling",
            reply_markup=markup,
            parse_mode="Markdown",
        )
        log.info(f"[{cid}] Muvaffaqiyatli yakunlandi.")

    except json.JSONDecodeError as e:
        log.error(f"[{cid}] JSON xatosi: {e}")
        bot.edit_message_text(
            f"❌ AI javobi noto'g'ri formatda.\n"
            f"Iltimos, /clear bosib qaytadan urinib ko'ring.",
            cid, status_msg.message_id
        )
    except Exception as e:
        log.exception(f"[{cid}] Kutilmagan xato")
        try:
            bot.edit_message_text(
                f"❌ Xatolik: {str(e)[:200]}\n\nIltimos, qayta urinib ko'ring.",
                cid, status_msg.message_id
            )
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════════════════════════
#                            ASOSIY TSIKL
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    log.info("=" * 60)
    log.info("🤖 ALSHAMS SOLAR bot ishga tushdi!")
    log.info(f"   Web URL: {WEB_APP_URL}")
    log.info("=" * 60)

    RETRY_DELAY = 5

    while True:
        try:
            # threaded=False — Python 3.11+ da muzlab qolish muammosini hal qiladi
            bot.polling(none_stop=True, interval=0, timeout=25)
        except telebot.apihelper.ApiException as e:
            log.warning(f"Telegram API xatosi: {e}. {RETRY_DELAY}s kutilmoqda...")
            time.sleep(RETRY_DELAY)
        except ConnectionError as e:
            log.warning(f"Internet uzildi: {e}. {RETRY_DELAY}s kutilmoqda...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            log.error(f"Kutilmagan xato: {e}. {RETRY_DELAY}s kutilmoqda...")
            time.sleep(RETRY_DELAY)
