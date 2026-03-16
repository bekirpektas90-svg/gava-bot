import os, csv, io, json
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
import urllib.request

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")

PRODUCTS = {
  "1308":{"name":"Dress Embroidery","type":"Dress","cost":8.00},
  "1309":{"name":"Dress Embroidery","type":"Dress","cost":8.00},
  "1310":{"name":"Dress Embroidery","type":"Dress","cost":8.00},
  "3701":{"name":"Mini Dress","type":"Dress","cost":5.75},
  "3707":{"name":"Mini Dress","type":"Dress","cost":5.75},
  "3519":{"name":"Dress Oversized","type":"Dress","cost":7.00},
  "3672":{"name":"Printed Long Dress","type":"Dress","cost":8.00},
  "3680":{"name":"Printed Long Dress","type":"Dress","cost":8.00},
  "3673":{"name":"Solid Long Dress","type":"Dress","cost":8.00},
  "3669":{"name":"Solid Long Dress","type":"Dress","cost":8.00},
  "3668":{"name":"Solid Long Dress","type":"Dress","cost":8.00},
  "3653":{"name":"Vest & Pant Set","type":"Set","cost":12.00},
  "1321":{"name":"Skirt & Top Set","type":"Set","cost":8.25},
  "3712":{"name":"Top & Pant Set","type":"Set","cost":11.50},
  "3620":{"name":"Vest & Top Set","type":"Set","cost":10.25},
  "3633":{"name":"Top & Pant Set","type":"Set","cost":10.25},
  "3618":{"name":"Vest & Pant Set","type":"Set","cost":11.00},
  "3621":{"name":"Vest & Top Set","type":"Set","cost":10.25},
  "789":{"name":"Cotton Skirt","type":"Skirt","cost":5.00},
  "786":{"name":"Cotton Skirt","type":"Skirt","cost":5.00},
  "7292":{"name":"Solid Pant","type":"Pant","cost":5.00},
  "7291":{"name":"Solid Pant","type":"Pant","cost":5.00},
  "SS0648":{"name":"Cotton Printed Pants","type":"Pant","cost":4.50},
  "SS4278":{"name":"Cotton Printed Shorts","type":"Shorts","cost":3.60},
  "SS3542":{"name":"Cotton Printed Skirt","type":"Skirt","cost":5.00},
  "1114":{"name":"Solid Palazzo Pant","type":"Pant","cost":6.00},
  "1199":{"name":"Solid Palazzo Pant","type":"Pant","cost":6.00},
  "V166":{"name":"Crochet Set","type":"Set","cost":12.75},
  "V331":{"name":"Crochet Top","type":"Top","cost":7.50},
  "V313":{"name":"Crochet Cardigan","type":"Cardigan","cost":8.00},
  "V328":{"name":"Crochet Vest","type":"Vest","cost":7.50},
  "V162":{"name":"Crochet Long Sleeve","type":"Top","cost":9.00},
  "V136":{"name":"Crochet Cardigan","type":"Cardigan","cost":12.00},
  "V135":{"name":"Crochet Top Multi","type":"Top","cost":9.50},
  "V119":{"name":"Crochet Vest","type":"Vest","cost":7.50},
  "V3321":{"name":"Crochet Cardigan","type":"Cardigan","cost":7.50},
  "V104":{"name":"Crochet Long","type":"Top","cost":10.00},
  "V107":{"name":"Crochet Top","type":"Top","cost":7.50},
  "V101":{"name":"Crochet Top","type":"Top","cost":7.50},
  "V137":{"name":"Denim Vest","type":"Vest","cost":8.50},
  "914":{"name":"Denim Short","type":"Shorts","cost":8.50},
  "9113":{"name":"Denim Short","type":"Shorts","cost":8.50},
  "9105":{"name":"Denim Short","type":"Shorts","cost":8.50},
  "912":{"name":"Denim Shirt","type":"Top","cost":8.50},
  "25008":{"name":"Maxi Knit Dress","type":"Dress","cost":9.00},
  "1978":{"name":"Knit Set Pant & Top","type":"Set","cost":10.00},
  "1147":{"name":"Crochet Top","type":"Top","cost":6.75},
  "2128":{"name":"Crochet Cardigan","type":"Cardigan","cost":6.75},
  "3211":{"name":"Soft Knit Poncho","type":"Poncho","cost":10.00},
  "1949":{"name":"Soft Knit Dress","type":"Dress","cost":10.00},
  "9358":{"name":"Knit Pant Wide Leg","type":"Pant","cost":9.00},
  "4403":{"name":"Crepe Palazzo Pant","type":"Pant","cost":4.00},
  "4478":{"name":"Knitwear Cardigan & Sweater","type":"Cardigan","cost":7.50},
  "1533":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50},
  "1530":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50},
  "1529":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50},
  "1658":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50},
  "4694":{"name":"Knit Skirt Pleated","type":"Skirt","cost":8.50},
  "4685":{"name":"Crystal Knit Pant","type":"Pant","cost":8.50},
  "SS4110-ATL":{"name":"Printed Crop Top Atlanta","type":"Top","cost":3.75},
  "SS4110-CAR":{"name":"Printed Crop Top Caramel","type":"Top","cost":3.75},
  "SS4110-USA":{"name":"Printed Crop Top USA","type":"Top","cost":3.75},
  "SS4110-BLM":{"name":"Printed Crop Top Bloom","type":"Top","cost":3.75},
  "SS4110-NYC":{"name":"Printed Crop Top New York","type":"Top","cost":3.75},
  "SS4034":{"name":"Polo Neck Crop Top","type":"Top","cost":4.00},
  "SS2465":{"name":"Tank Top","type":"Top","cost":3.75},
  "SS3501":{"name":"Cotton Tank Top","type":"Top","cost":3.75},
  "SS3538":{"name":"Ribbed Top","type":"Top","cost":3.75},
}

COLOR_MAP = {
    "siyah":"BLK","beyaz":"WHT","kırmızı":"RED","kirmizi":"RED",
    "mavi":"BLUE","lacivert":"NAVY","bej":"BEIGE","bege":"BEIGE",
    "yeşil":"GREEN","yesil":"GREEN","pembe":"PINK","gri":"GREY",
    "kahve":"BROWN","kahverengi":"BROWN","sarı":"YELLOW","sari":"YELLOW",
    "mor":"PURPLE","turuncu":"ORANGE","krem":"CREAM","ekru":"ECRU",
    "camel":"CAMEL","multi":"MULTI","çok renkli":"MULTI","cok renkli":"MULTI",
}

sessions = {}

def get_session(cid):
    if cid not in sessions:
        sessions[cid] = {}
    return sessions[cid]

def call_claude(user_text):
    system = """Sen bir moda perakende stok yönetim asistanısın. 
Kullanıcı Türkçe serbest formatta ürün bilgisi girer, sen bunu JSON'a çevirirsin.

Renk çevirme kuralları (Türkçe → İngilizce kısa kod):
siyah→BLK, beyaz→WHT, kırmızı→RED, mavi→BLUE, lacivert→NAVY, bej/bege→BEIGE,
yeşil→GREEN, pembe→PINK, gri→GREY, kahve→BROWN, sarı→YELLOW, mor→PURPLE,
turuncu→ORANGE, krem→CREAM, ekru→ECRU, camel→CAMEL, multi/çok renkli→MULTI

Beden dağılımı kuralları:
- "2s2m2l" = her bedenden o oran kadar → renk adedi ÷ beden sayısı = her bedenden kaç adet
  Örnek: 6mavi 2s2m2l → 6÷3=2 → BLUE: 2S, 2M, 2L
  Örnek: 3siyah 2s2m2l → 3÷3=1 → BLK: 1S, 1M, 1L
- "one size" veya "tek beden" → OS bedeni
- "S/M" → S ve M bedenleri eşit bölünür
- "L/XL" → L ve XL bedenleri eşit bölünür
- Beden belirtilmemişse → OS

Kullanıcı birden fazla ürünü aynı anda girebilir, her satır/ürün ayrı işle.

SADECE JSON döndür, başka hiçbir şey yazma. Format:
[
  {
    "sku": "1308",
    "retail_price": 24.00,
    "variants": [
      {"color": "BLK", "size": "S", "qty": 1},
      {"color": "BLK", "size": "M", "qty": 1},
      {"color": "BLK", "size": "L", "qty": 1}
    ]
  }
]"""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": system,
        "messages": [{"role": "user", "content": user_text}]
    }).encode()

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01"
        }
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    raw = data["content"][0]["text"].strip()
    raw = raw.replace("```json","").replace("```","").strip()
    return json.loads(raw)

def build_shopify_csv(sess_data):
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Handle","Title","Body (HTML)","Vendor","Type","Tags","Published",
                "Option1 Name","Option1 Value","Option2 Name","Option2 Value",
                "Variant SKU","Variant Inventory Qty","Variant Price","Cost per item","Status"])
    for sku, entry in sess_data.items():
        p = PRODUCTS.get(sku, {"name": sku, "type": "Other", "cost": 0})
        handle = f"{p['name'].lower().replace(' ','-').replace('&','and')}-{sku.lower()}"
        retail = entry.get("retail_price", round(p['cost'] * 2.5, 2))
        for i, v in enumerate(entry["variants"]):
            w.writerow([
                handle,
                f"{p['name']} - {sku}" if i == 0 else "",
                f"<p>{p['type']}</p>" if i == 0 else "",
                "VAV New York" if i == 0 else "",
                p['type'] if i == 0 else "",
                p['type'].lower() if i == 0 else "",
                "TRUE" if i == 0 else "",
                "Color", v['color'],
                "Size", v['size'],
                f"{sku}-{v['color']}-{v['size']}",
                v['qty'], retail, p['cost'],
                "active" if i == 0 else ""
            ])
    return output.getvalue().encode('utf-8')

def build_square_csv(sess_data):
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Item Name","Variation Name","SKU","Category","Price","Current Quantity","Track Inventory"])
    for sku, entry in sess_data.items():
        p = PRODUCTS.get(sku, {"name": sku, "type": "Other", "cost": 0})
        retail = entry.get("retail_price", round(p['cost'] * 2.5, 2))
        for v in entry["variants"]:
            w.writerow([
                f"{p['name']} - {sku}",
                f"{v['color']} / {v['size']}",
                f"{sku}-{v['color']}-{v['size']}",
                p['type'], retail, v['qty'], "Y"
            ])
    return output.getvalue().encode('utf-8')

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👗 *GAVA New York — Ürün Giriş Botu*\n\n"
        "İstediğiniz gibi Türkçe yazın:\n\n"
        "`1308 3siyah 6mavi 3kırmızı 2s2m2l 24$`\n"
        "`1309 6kırmızı 6yeşil one size 35$`\n"
        "`V331 12kırmızı S/M 18$`\n"
        "`SS4278 20multi 2s2m2l 15$`\n\n"
        "📋 *Komutlar:*\n"
        "/ozet — girilen ürünler\n"
        "/shopify — Shopify CSV\n"
        "/square — Square CSV\n"
        "/sil 1308 — ürün sil\n"
        "/temizle — sıfırla",
        parse_mode="Markdown"
    )

async def cmd_ozet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sess = get_session(cid)
    if not sess:
        await update.message.reply_text("Henüz ürün girilmedi.")
        return
    lines = [f"📦 *{len(sess)} ürün:*\n"]
    total_v = 0
    for sku, entry in sess.items():
        p = PRODUCTS.get(sku, {"name": sku})
        variants = entry["variants"]
        total_v += len(variants)
        total_qty = sum(v['qty'] for v in variants)
        colors = {}
        for v in variants:
            colors.setdefault(v['color'], []).append(f"{v['qty']}{v['size']}")
        color_str = "  ".join([f"{c}:{' '.join(s)}" for c, s in colors.items()])
        price = entry.get("retail_price", "?")
        lines.append(f"`{sku}` {p['name']} — ${price}\n  {color_str} ({total_qty} adet)")
    lines.append(f"\n📊 Toplam {total_v} variant")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_shopify(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sess = get_session(cid)
    if not sess:
        await update.message.reply_text("Henüz ürün girilmedi.")
        return
    total_v = sum(len(e["variants"]) for e in sess.values())
    csv_bytes = build_shopify_csv(sess)
    await update.message.reply_document(
        document=io.BytesIO(csv_bytes),
        filename="gava_shopify.csv",
        caption=f"✅ Shopify CSV — {len(sess)} ürün, {total_v} variant"
    )

async def cmd_square(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sess = get_session(cid)
    if not sess:
        await update.message.reply_text("Henüz ürün girilmedi.")
        return
    total_v = sum(len(e["variants"]) for e in sess.values())
    csv_bytes = build_square_csv(sess)
    await update.message.reply_document(
        document=io.BytesIO(csv_bytes),
        filename="gava_square.csv",
        caption=f"✅ Square CSV — {len(sess)} ürün, {total_v} variant"
    )

async def cmd_sil(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sess = get_session(cid)
    args = ctx.args
    if not args:
        await update.message.reply_text("Kullanım: /sil 1308")
        return
    sku = args[0].upper()
    if sku in sess:
        del sess[sku]
        await update.message.reply_text(f"✅ {sku} silindi.")
    else:
        await update.message.reply_text(f"'{sku}' bulunamadı.")

async def cmd_temizle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sessions[cid] = {}
    await update.message.reply_text("✅ Tüm veriler temizlendi.")

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    text = update.message.text.strip()
    sess = get_session(cid)

    await update.message.reply_text("⏳ Analiz ediliyor...")

    try:
        results = call_claude(text)
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {str(e)}\n\nTekrar deneyin.")
        return

    if not results:
        await update.message.reply_text("❌ Anlayamadım. Örnek:\n`1308 3siyah 6mavi 2s2m2l 24$`", parse_mode="Markdown")
        return

    reply_lines = []
    for item in results:
        sku = item.get("sku", "").upper()
        variants = item.get("variants", [])
        retail = item.get("retail_price")

        if not sku or not variants:
            continue

        p = PRODUCTS.get(sku, {"name": sku, "type": "Other", "cost": 0})
        if retail is None:
            retail = round(p['cost'] * 2.5, 2)

        # merge into session
        existing = sess.get(sku, {"variants": [], "retail_price": retail})
        existing["retail_price"] = retail
        for nv in variants:
            found = False
            for ev in existing["variants"]:
                if ev['color'] == nv['color'] and ev['size'] == nv['size']:
                    ev['qty'] = nv['qty']
                    found = True
                    break
            if not found:
                existing["variants"].append(nv)
        sess[sku] = existing

        total_qty = sum(v['qty'] for v in existing["variants"])
        colors = {}
        for v in existing["variants"]:
            colors.setdefault(v['color'], []).append(f"{v['qty']}{v['size']}")

        lines = [f"✅ *{p['name']}* `{sku}` — ${retail}"]
        for color, sizes in colors.items():
            lines.append(f"  🎨 {color}: {' '.join(sizes)}")
        lines.append(f"  📦 {total_qty} adet, {len(existing['variants'])} variant")
        reply_lines.append("\n".join(lines))

    if reply_lines:
        reply_lines.append(f"\n_Oturum: {len(sess)} ürün. /shopify veya /square ile CSV al._")
        await update.message.reply_text("\n\n".join(reply_lines), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Hiç ürün işlenemedi.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ozet", cmd_ozet))
    app.add_handler(CommandHandler("shopify", cmd_shopify))
    app.add_handler(CommandHandler("square", cmd_square))
    app.add_handler(CommandHandler("sil", cmd_sil))
    app.add_handler(CommandHandler("temizle", cmd_temizle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot başlatıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
