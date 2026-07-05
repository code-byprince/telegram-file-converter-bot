# 🤖 Telegram File Converter Bot

Advance File Converter Bot — Image, PDF, Word, Video/Audio sab convert karta hai.
Free Render hosting ke liye optimized (heavy tools jaise LibreOffice avoid kiye gaye hain).

---

## 📁 File Structure (kya file kis liye hai)

```
telegram-file-converter-bot/
├── bot.py                       # Main entry point - bot yahin se start hota hai
├── config.py                    # Environment variables (BOT_TOKEN etc) load karta hai
├── requirements.txt             # Saari Python libraries ki list
├── Dockerfile                   # Render ke liye - ffmpeg/poppler system tools install karta hai
├── render.yaml                  # Render blueprint (auto-config, optional)
├── .env.example                 # BOT_TOKEN kaise set karna hai uska template
├── .gitignore                   # GitHub pe junk files (temp/, __pycache__) avoid karta hai
├── handlers/
│   ├── start.py                 # /start command + main menu
│   ├── callback_handler.py      # Button clicks (Image/Document/Video/Excel menu) handle karta hai
│   ├── file_handler.py          # User ki bheji file ko convert karke wapas bhejta hai
│   ├── admin.py                 # /stats command - sirf admin ke liye usage report
│   ├── language.py              # /language command - Hindi/English switch
│   └── history.py               # /history command - last 5 conversions dikhata hai
├── converters/
│   ├── image_converter.py       # Image↔Image, Resize, Images→PDF, PDF→Images
│   ├── document_converter.py    # PDF↔Word, Text↔PDF, Merge/Split, Password, Excel↔CSV
│   └── video_converter.py       # Video→Audio, Video Compress
└── utils/
    ├── helpers.py                # Common helper functions (temp folder, file size etc)
    ├── stats.py                   # SQLite database - users, language, feature usage, history
    ├── rate_limit.py               # Spam rokne ke liye rate limiting
    └── i18n.py                     # Hindi/English text translations
```

---

## 🚀 STEP 1: Telegram Bot Token Lena

1. Telegram me `@BotFather` ko open karo
2. `/newbot` bhejo
3. Bot ka naam do (e.g. `Prince File Converter`)
4. Username do (must end with `bot`, e.g. `prince_file_converter_bot`)
5. BotFather tumhe ek **token** dega, jaise: `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`
6. Yeh token safe rakho — kisi ko mat dena

---

## 🚀 STEP 2: Code GitHub Pe Upload Karna

1. [github.com](https://github.com) pe login karo
2. Top right `+` → **New repository** click karo
3. Repository name do: `telegram-file-converter-bot` → **Create repository**
4. Apne computer pe terminal/cmd khol ke is project folder me jao, phir:

```bash
git init
git add .
git commit -m "File converter bot - initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/telegram-file-converter-bot.git
git push -u origin main
```

> `YOUR_USERNAME` apna GitHub username daalna. `.env` file **kabhi upload mat karna** — `.gitignore` usko automatically skip kar dega.

**Ya phir GitHub website se seedha:** "Add file" → "Upload files" → sari files drag-drop karo → Commit.

---

## 🚀 STEP 3: Render Pe Deploy Karna

1. [render.com](https://render.com) pe jao, GitHub se sign up/login karo
2. Dashboard → **New +** → **Web Service**
3. Apna GitHub repo (`telegram-file-converter-bot`) select karo
4. Settings me:
   - **Name**: kuch bhi (e.g. `file-converter-bot`)
   - **Runtime**: `Docker` (auto-detect ho jayega Dockerfile se)
   - **Instance Type**: `Free`
5. **Environment Variables** section me add karo:
   - Key: `BOT_TOKEN` → Value: (apna BotFather wala token)
   - Key: `MAX_FILE_SIZE_MB` → Value: `20`
   - Key: `ADMIN_ID` → Value: (apna Telegram numeric user ID — neeche "Admin Stats" section me batya hai kaise nikale)
6. **Create Web Service** click karo
7. Build/deploy me 3-5 minute lagega (pehli baar). Logs me `Bot polling shuru ho raha hai...` dikhna chahiye — matlab bot live hai

---

## 🚀 STEP 4: Bot Ko 24/7 Zinda Rakhna (Free Plan Trick)

Render ka **free** Web Service 15 minute tak koi HTTP request na aane par "sleep" ho jata hai. Usse bachne ke liye:

1. [UptimeRobot.com](https://uptimerobot.com) pe free account banao
2. **Add New Monitor** → Type: `HTTP(s)`
3. URL: tumhara Render app URL (e.g. `https://file-converter-bot.onrender.com`)
4. Interval: `5 minutes`
5. Save kar do

Ab UptimeRobot har 5 minute me tumhare bot ko "ping" karega, aur woh sona nahi (approx 24/7 rahega). Free plan me kabhi 1-2 second ka cold-start delay ho sakta hai, woh normal hai.

---

## ✅ Bot Test Karna

1. Telegram me apna bot open karo, `/start` bhejo
2. Category choose karo (Image / Document / Video)
3. Option choose karo (e.g. "→ JPG")
4. File bhejo — bot process karke wapas bhej dega

---

## 📊 Admin Stats (`/stats` command)

Bot me full website wala admin panel nahi hai, uski jagah ek simple `/stats` command hai jo sirf tumhe (admin) dikhta hai — kitne total users hain, aaj kitne active the, aur kaunsa feature kitni baar use hua.

**Apna Telegram numeric ID nikalna:**
1. Telegram me `@userinfobot` search karke open karo
2. `/start` bhejo — woh tumhara numeric ID bhej dega (jaise `123456789`)
3. Yeh ID Render ke `ADMIN_ID` environment variable me daal do (Step 3 me upar batya hai)

**Use karna:**
Apne bot ko `/stats` bhejo (sirf tumhare ADMIN_ID wale account se kaam karega, baaki users ko "sirf admin ke liye hai" dikhega).

> ⚠️ Note: Yeh data ek SQLite file me store hota hai jo Render ke container ke andar hi rehti hai. Jab bhi tum naya **deploy/redeploy** karoge (naya code push), yeh data reset ho jayega — sirf normal restart/sleep-wake se data safe rehta hai. Agar permanent data chahiye, toh Render ka paid **Persistent Disk** add karna padega.

---

## 📱 Mini App Menu Button Setup (BotFather)

Bot me ab ek proper **Mini App** (Web App) hai jo Telegram ke andar hi khulti hai — jaisa BotFather ka "Open" button hota hai. Isko enable karna hai:

1. `@BotFather` → `/mybots` → apna bot select karo
2. **Bot Settings** → **Menu Button** → **Edit Menu Button URL**
3. Yeh URL bhejo (apna Render URL use karke):
   ```
   https://tumhara-app-name.onrender.com/webapp
   ```
4. Fir button ka naam poochega — kuch bhi de do, jaise: `Menu`
5. Done! Ab chat ke andar bottom-left me ek button dikhega, dabate hi Mini App khul jayegi

**Kaise kaam karta hai:** Mini App me category (Image/Document/Excel/Video) choose karo, phir specific option dabao — Mini App band ho jayegi aur bot turant tumse file maangega, jaise normal button flow me hota hai. Yeh sirf ek alag, zyada modern tarika hai wahi purane menu ko access karne ka.

---

## 🆕 Naye Features (v2)

- 🔒 **Donation Gate** — naya user pehle 5/10+ ⭐ Stars donate karta hai, tabhi bot unlock hota hai. Admin (`ADMIN_ID`) ke liye yeh gate nahi hai, seedha use kar sakte ho.
- ⭐ **Telegram Stars Donation** — `/donate` command se koi bhi user Stars donate kar sakta hai (bank/UPI ki zaroorat nahi)

- 📐 **Image Resize** — custom width x height
- 📎 **PDF Merge** — multiple PDFs ek me jodo
- ✂️ **PDF Split** — page range se naya PDF banao
- 🔒 **PDF Password** — add ya remove karo
- 📊 **Excel ↔ CSV** — dono taraf convert
- 🌐 **Language toggle** — `/language` se Hindi/English switch karo
- 🕘 **History** — `/history` se apni last 5 conversions dekho
- ⏱️ **Rate limiting** — 1 minute me max 5 files (spam se bachne ke liye, khud-ba-khud kaam karta hai)

**Naye Commands:**
| Command | Kaam |
|---|---|
| `/language` | Hindi/English choose karo |
| `/history` | Last 5 conversions dekho |
| `/done` | Multi-file collection (Images→PDF, PDF Merge) finalize karo |

---

## ⚠️ Free Plan Limitations (Important)

- **Max file size 20MB** rakha hai (free plan ki 512MB RAM ke hisaab se). `.env` me `MAX_FILE_SIZE_MB` badha sakte ho, but bade video files se bot crash ho sakta hai.
- **Word → PDF** lightweight method use karta hai (text/paragraphs), complex tables/images wale Word docs me formatting simple ho sakti hai.
- Agar zyada heavy usage chahiye (bade videos, perfect Word formatting), toh Render ka paid plan (Starter, ~$7/month) better rahega.

---

## 🔧 Local Testing (Optional, deploy karne se pehle)

```bash
pip install -r requirements.txt
# Windows: choco install poppler ffmpeg  |  Mac: brew install poppler ffmpeg  |  Linux: apt install poppler-utils ffmpeg
cp .env.example .env   # phir .env me apna BOT_TOKEN daalo
python bot.py
```
