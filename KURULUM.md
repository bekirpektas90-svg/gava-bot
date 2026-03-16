# GAVA New York Telegram Botu — Kurulum Rehberi

## Adım 1: Telegram'dan Bot Token Alın (2 dakika)

1. Telegram'da @BotFather'ı arayın
2. `/newbot` yazın
3. Bot adı: `GAVA New York`
4. Bot kullanıcı adı: `gava_newyork_bot` (benzersiz olmalı, sonuna rakam ekleyin)
5. BotFather size bir TOKEN verecek → kopyalayın (şuna benzer: `7123456789:AAF...`)

## Adım 2: Railway'e Yükleyin (5 dakika)

1. **railway.app** adresine gidin → GitHub ile giriş yapın
2. **New Project** → **Deploy from GitHub repo** tıklayın
3. Bu klasörü GitHub'a yüklemeniz gerekiyor:
   - github.com adresine gidin → New repository → `gava-bot` adıyla oluşturun
   - Bu klasördeki tüm dosyaları yükleyin (bot.py, requirements.txt, railway.json, Procfile)
4. Railway'de repo'yu seçin

## Adım 3: Environment Variable Ekleyin

Railway'de projenizi açın:
1. **Variables** sekmesine tıklayın
2. **New Variable** ekleyin:
   - Key: `BOT_TOKEN`
   - Value: BotFather'dan aldığınız token
3. **Deploy** tıklayın — bot 1 dakika içinde çalışır!

## Adım 4: Botu Test Edin

Telegram'da botunuzu açın ve `/start` yazın.

---

## Bot Kullanımı

### Ürün Girme Formatı:
```
1308 BLK 2S 2M 2L
1308 BLK 2S 2M 2L WHT 2S 2M 2L
V331 RED 3S 3M BLUE 3S 3M
SS4278 MULTI 10S 10M 10L
```

### Komutlar:
- `/start` — hoşgeldin mesajı
- `/liste` — tüm ürün SKU'ları
- `/ozet` — girilen ürünler özeti
- `/shopify` — Shopify CSV dosyası indir
- `/square` — Square CSV dosyası indir
- `/sil 1308` — tek ürün sil
- `/temizle` — tümünü sıfırla

---
