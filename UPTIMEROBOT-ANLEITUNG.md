# 🤖 UPTIMEROBOT - 24/7 ANLEITUNG

## ✅ WAS IST FERTIG:

✅ **keep_alive.py** - Webserver für Bot
✅ **requirements.txt** - Mit Flask
✅ **bot.py** - Mit keep_alive() Integration

---

## 🚀 SCHRITT-FÜR-SCHRITT:

### **1. Dateien hochladen in Replit**

Lade ALLE Dateien in dein Replit-Projekt hoch:
- bot.py (ERSETZE die alte Datei!)
- keep_alive.py (NEU!)
- requirements.txt (ERSETZE!)
- .env (dein Token drin)

---

### **2. Bot starten**

Klicke auf **Run** in Replit

Du solltest sehen:
```
Bot is alive! 🐼
✅ Bot ist online!
✅ Commands synchronisiert!
```

**Oben in Replit** erscheint eine URL wie:
```
https://dein-bot-name.deinusername.repl.co
```

**Diese URL kopieren!** 📋

---

### **3. Im Browser testen**

Öffne die URL im Browser.
Du solltest sehen: **"Bot is alive! 🐼"**

✅ Wenn ja → Weiter zu Schritt 4!
❌ Wenn nicht → Bot neu starten!

---

### **4. UptimeRobot Account erstellen**

1. Gehe zu: https://uptimerobot.com
2. **Sign Up** (kostenlos!)
3. Bestätige deine E-Mail
4. Login

---

### **5. Monitor erstellen**

Im Dashboard:

1. Klicke **+ Add New Monitor**

2. **Einstellungen:**
   ```
   Monitor Type: HTTP(s)
   Friendly Name: Panda's Paradise Bot
   URL (or IP): https://dein-bot-name.deinusername.repl.co
   Monitoring Interval: 5 minutes
   ```

3. **Create Monitor** klicken

---

### **6. FERTIG! 🎉**

UptimeRobot pingt jetzt alle 5 Minuten deinen Bot!

**Bot bleibt 24/7 wach!** ✅

---

## 📊 UPTIMEROBOT DASHBOARD:

Zeigt dir:
- ✅ **Uptime %** (sollte ~100% sein)
- ✅ **Response Time**
- ✅ **Status** (UP/DOWN)
- ✅ **Logs**

---

## ⚠️ WICHTIG:

**Replit FREE Limits:**
- Kann nach ~12-24 Stunden trotzdem "einschlafen"
- Bei zu vieler Last stoppt Replit den Bot

**Wenn das passiert:**
→ Nutze **Railway.app** stattdessen! (echter 24/7)

---

## 🔧 TROUBLESHOOTING:

### **Bot schläft trotzdem?**
- ✅ URL richtig in UptimeRobot?
- ✅ Monitor ist aktiv (nicht pausiert)?
- ✅ Bot läuft in Replit?

### **"Bot is alive!" erscheint nicht?**
- keep_alive.py richtig hochgeladen?
- requirements.txt hat Flask?
- Bot neu starten!

### **Nach 12h offline?**
- Replit FREE hat Limits
- Zeit für Railway.app! (siehe RAILWAY-ANLEITUNG.md)

---

## 🌐 ALTERNATIVE: RAILWAY.APP

**Bessere Option für echten 24/7:**

Railway.app bietet:
- ✅ Echter 24/7 Betrieb
- ✅ 500 Stunden/Monat kostenlos
- ✅ Kein "Wachhalten" nötig
- ✅ Professionelles Hosting

**Anleitung:** Siehe RAILWAY-ANLEITUNG.md

---

**Viel Erfolg! 🐼✨**
