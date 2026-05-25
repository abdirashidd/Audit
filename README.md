# ⚡ ALSHAMS SOLAR — Energo-Audit Tizimi

Professional energiya auditi uchun Telegram Bot + Streamlit veb ilova.

---

## 📁 Loyiha tuzilmasi

```
energo_audit_project/
├── bot.py           ← Telegram bot (mahalliy kompyuterda ishlaydi)
├── app.py           ← Streamlit veb ilova (GitHub + Streamlit Cloud)
├── shablon.docx     ← Word shablon (o'zgartirmang!)
├── requirements.txt ← Kutubxonalar ro'yxati
└── README.md        ← Shu fayl
```

---

## 🚀 Ishga tushirish — Qadam-baqadam

### 1-QADAM: Python o'rnatish
https://python.org dan Python 3.10 yoki yuqorisini yuklab o'rnating.
O'rnatishda **"Add Python to PATH"** katagini belgilang!

### 2-QADAM: Kutubxonalarni o'rnatish
CMD (buyruqlar qatori) ni oching va yozing:
```
pip install -r requirements.txt
```

### 3-QADAM: Telegram botni ishga tushirish
```
python bot.py
```
Ekranda `🤖 ALSHAMS bot ishga tushdi` chiqsa — bot ishlayapti.
**Bu oynani yopmang!**

### 4-QADAM: Streamlit saytni ulash (GitHub orqali)

1. GitHub.com da yangi repository oching
2. `app.py` va `shablon.docx` ni yuklang (ikkalasi root papkada)
3. https://streamlit.io/cloud ga kiring
4. "New app" → o'z reponi tanlang → Deploy

### 5-QADAM: Telegram botni sinash

1. Telegramda botingizni toping
2. `/start` yozing
3. Matn yuboring (ism, manzil, xona maydoni, jihozlar...)
4. Xona rasmlarini yuboring
5. `/analyze` yozing
6. Bot tugma yuboradi → bosing → sayt ochiladi
7. Ma'lumotlarni tekshiring → **"WORD HUJJAT YARATISH"** tugmasini bosing
8. Hujjat yuklanadi ✅

---

## ⚙️ Sozlamalar (bot.py)

```python
TELEGRAM_TOKEN = "sizning_token"     # @BotFather dan olingan
GEMINI_API_KEY = "sizning_kalit"     # aistudio.google.com dan
WEB_APP_URL    = "sizning_streamlit_url"
```

---

## ❗ Muammolar va yechimlari

| Muammo | Yechim |
|--------|--------|
| `shablon.docx topilmadi` | GitHub repoga `app.py` bilan bir joyga yuklang |
| Bot javob bermaydi | CMD da bot.py ishlayotganini tekshiring |
| Gemini xatosi | API kalitni yangilang (aistudio.google.com) |
| Word hujjat bo'sh | Streamlit da barcha maydonlar to'ldirilganini tekshiring |
