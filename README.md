# Qurilish Mollari Market — Telegram bot

Shikoyat, taklif va admin bilan bog'lanish uchun Telegram bot.

## Mahalliy ishga tushirish

```bash
pip install -r requirements.txt
```

`.env` faylini yarating (yoki mavjudini tahrirlang):

```
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_user_id
```

```bash
python bot.py
```

Bot ham Telegram polling qiladi, ham `http://localhost:8080/` manzilida health-check server ko'taradi.

## Render'da joylashtirish

1. Bu repository'ni GitHub'ga push qiling.
2. [render.com](https://render.com) da hisob oching va **New +** → **Web Service** ni tanlang.
3. GitHub repo'ni ulang.
4. Sozlamalar:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Plan**: Free
5. **Environment** bo'limida quyidagi o'zgaruvchilarni qo'shing:
   - `BOT_TOKEN` — bot tokeningiz
   - `ADMIN_ID` — sizning Telegram ID raqamingiz
6. **Create Web Service** tugmasini bosing. Deploy tugagach, Render sizga bir URL beradi (masalan `https://qmbot.onrender.com`).

## Botni uxlab qolishdan saqlash

Render'ning bepul tarifidagi web xizmatlar ~15 daqiqa HTTP so'rov kelmasa, uxlab qoladi. Buni oldini olish uchun:

1. [cron-job.org](https://cron-job.org) yoki [UptimeRobot](https://uptimerobot.com) da bepul hisob oching.
2. Render URL'ingizni (masalan `https://qmbot.onrender.com`) har 5–10 daqiqada bir marta "ping" qiladigan monitor/cron job sozlang.

Shu tarzda bot doimiy uyg'oq turadi.
