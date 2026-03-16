import os, csv, io, re, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

TOKEN = os.environ.get("BOT_TOKEN", "")

PRODUCTS = {
  "1308":{"name":"Dress Embroidery","type":"Dress","cost":8.00,"qty":12},
  "1309":{"name":"Dress Embroidery","type":"Dress","cost":8.00,"qty":12},
  "1310":{"name":"Dress Embroidery","type":"Dress","cost":8.00,"qty":12},
  "3701":{"name":"Mini Dress","type":"Dress","cost":5.75,"qty":12},
  "3707":{"name":"Mini Dress","type":"Dress","cost":5.75,"qty":12},
  "3519":{"name":"Dress Oversized","type":"Dress","cost":7.00,"qty":12},
  "3672":{"name":"Printed Long Dress","type":"Dress","cost":8.00,"qty":12},
  "3680":{"name":"Printed Long Dress","type":"Dress","cost":8.00,"qty":12},
  "3673":{"name":"Solid Long Dress","type":"Dress","cost":8.00,"qty":12},
  "3669":{"name":"Solid Long Dress","type":"Dress","cost":8.00,"qty":12},
  "3668":{"name":"Solid Long Dress","type":"Dress","cost":8.00,"qty":12},
  "3653":{"name":"Vest & Pant Set","type":"Set","cost":12.00,"qty":12},
  "1321":{"name":"Skirt & Top Set","type":"Set","cost":8.25,"qty":12},
  "3712":{"name":"Top & Pant Set","type":"Set","cost":11.50,"qty":12},
  "3620":{"name":"Vest & Top Set","type":"Set","cost":10.25,"qty":12},
  "3633":{"name":"Top & Pant Set","type":"Set","cost":10.25,"qty":12},
  "3618":{"name":"Vest & Pant Set","type":"Set","cost":11.00,"qty":12},
  "3621":{"name":"Vest & Top Set","type":"Set","cost":10.25,"qty":12},
  "789":{"name":"Cotton Skirt","type":"Skirt","cost":5.00,"qty":24},
  "786":{"name":"Cotton Skirt","type":"Skirt","cost":5.00,"qty":24},
  "7292":{"name":"Solid Pant","type":"Pant","cost":5.00,"qty":24},
  "7291":{"name":"Solid Pant","type":"Pant","cost":5.00,"qty":24},
  "SS0648":{"name":"Cotton Printed Pants","type":"Pant","cost":4.50,"qty":216},
  "SS4278":{"name":"Cotton Printed Shorts","type":"Shorts","cost":3.60,"qty":216},
  "SS3542":{"name":"Cotton Printed Skirt","type":"Skirt","cost":5.00,"qty":108},
  "1114":{"name":"Solid Palazzo Pant","type":"Pant","cost":6.00,"qty":24},
  "1199":{"name":"Solid Palazzo Pant","type":"Pant","cost":6.00,"qty":24},
  "V166":{"name":"Crochet Set","type":"Set","cost":12.75,"qty":12},
  "V331":{"name":"Crochet Top","type":"Top","cost":7.50,"qty":12},
  "V313":{"name":"Crochet Cardigan","type":"Cardigan","cost":8.00,"qty":12},
  "V328":{"name":"Crochet Vest","type":"Vest","cost":7.50,"qty":12},
  "V162":{"name":"Crochet Long Sleeve","type":"Top","cost":9.00,"qty":12},
  "V136":{"name":"Crochet Cardigan","type":"Cardigan","cost":12.00,"qty":12},
  "V135":{"name":"Crochet Top Multi","type":"Top","cost":9.50,"qty":12},
  "V119":{"name":"Crochet Vest","type":"Vest","cost":7.50,"qty":12},
  "V3321":{"name":"Crochet Cardigan","type":"Cardigan","cost":7.50,"qty":12},
  "V104":{"name":"Crochet Long","type":"Top","cost":10.00,"qty":12},
  "V107":{"name":"Crochet Top","type":"Top","cost":7.50,"qty":12},
  "V101":{"name":"Crochet Top","type":"Top","cost":7.50,"qty":12},
  "V137":{"name":"Denim Vest","type":"Vest","cost":8.50,"qty":12},
  "914":{"name":"Denim Short","type":"Shorts","cost":8.50,"qty":12},
  "9113":{"name":"Denim Short","type":"Shorts","cost":8.50,"qty":12},
  "9105":{"name":"Denim Short","type":"Shorts","cost":8.50,"qty":12},
  "912":{"name":"Denim Shirt","type":"Top","cost":8.50,"qty":12},
  "25008":{"name":"Maxi Knit Dress","type":"Dress","cost":9.00,"qty":6},
  "1978":{"name":"Knit Set Pant & Top","type":"Set","cost":10.00,"qty":6},
  "1147":{"name":"Crochet Top","type":"Top","cost":6.75,"qty":12},
  "2128":{"name":"Crochet Cardigan","type":"Cardigan","cost":6.75,"qty":6},
  "3211":{"name":"Soft Knit Poncho","type":"Poncho","cost":10.00,"qty":6},
  "1949":{"name":"Soft Knit Dress","type":"Dress","cost":10.00,"qty":6},
  "9358":{"name":"Knit Pant Wide Leg","type":"Pant","cost":9.00,"qty":24},
  "4403":{"name":"Crepe Palazzo Pant","type":"Pant","cost":4.00,"qty":54},
  "4478":{"name":"Knitwear Cardigan & Sweater","type":"Cardigan","cost":7.50,"qty":54},
  "1533":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50,"qty":12},
  "1530":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50,"qty":12},
  "1529":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50,"qty":12},
  "1658":{"name":"Knit Cardigan Elegant","type":"Cardigan","cost":11.50,"qty":12},
  "4694":{"name":"Knit Skirt Pleated","type":"Skirt","cost":8.50,"qty":12},
  "4685":{"name":"Crystal Knit Pant","type":"Pant","cost":8.50,"qty":12},
  "SS4110-ATL":{"name":"Printed Crop Top Atlanta","type":"Top","cost":3.75,"qty":36},
  "SS4110-CAR":{"name":"Printed Crop Top Caramel","type":"Top","cost":3.75,"qty":36},
  "SS4110-USA":{"name":"Printed Crop Top USA","type":"Top","cost":3.75,"qty":36},
  "SS4110-BLM":{"name":"Printed Crop Top Bloom","type":"Top","cost":3.75,"qty":36},
  "SS4110-NYC":{"name":"Printed Crop Top New York","type":"Top","cost":3.75,"qty":36},
  "SS4034":{"name":"Polo Neck Crop Top","type":"Top","cost":4.00,"qty":36},
  "SS2465":{"name":"Tank Top","type":"Top","cost":3.75,"qty":36},
  "SS3501":{"name":"Cotton Tank Top","type":"Top","cost":3.75,"qty":36},
  "SS3538":{"name":"Ribbed Top","type":"Top","cost":3.75,"qty":36},
}

# In-memory session store  { chat_id: { sku: [ {color, size, qty} ] } }
sessions = {}

def get_session(cid):
    if cid not in sessions:
        sessions[cid] = {}
    return sessions[cid]

def parse_entry(text):
    """
    Parse entries like:
      1308 BLK 2S 2M 2L WHT 2S 2M 2L
      1308 BLK S:2 M:2 L:2
      V331 RED 3S 3M 3L BLUE 3S 3M 3L
    Returns list of {sku, color, size, qty} or None on error.
    """
    text = text.strip().upper()
    tokens = text.split()
    if not tokens:
        return None, "Mesaj boş."

    sku = tokens[0]
    if sku not in PRODUCTS:
        # try partial match
        matches = [k for k in PRODUCTS if k.startswith(sku)]
        if len(matches) == 1:
            sku = matches[0]
        elif len(matches) > 1:
            return None, f"'{sku}' için birden fazla eşleşme: {', '.join(matches[:5])}\nDaha spesifik yazın."
        else:
            return None, f"'{sku}' ürün bulunamadı. /liste komutu ile ürünleri görebilirsiniz."

    variants = []
    current_color = None
    i = 1
    while i < len(tokens):
        tok = tokens[i]
        # size:qty format like S:2 or M:3
        if re.match(r'^[A-Z0-9]+:\d+$', tok):
            if not current_color:
                return None, "Beden girmeden önce renk belirtin. Örnek: 1308 BLK 2S 2M 2L"
            size, qty = tok.split(':')
            variants.append({"color": current_color, "size": size, "qty": int(qty)})
        # qty+size format like 2S 3M or just S M L (qty=1)
        elif re.match(r'^\d+[A-Z]+$', tok):
            if not current_color:
                return None, "Beden girmeden önce renk belirtin. Örnek: 1308 BLK 2S 2M 2L"
            m = re.match(r'^(\d+)([A-Z]+)$', tok)
            qty, size = int(m.group(1)), m.group(2)
            variants.append({"color": current_color, "size": size, "qty": qty})
        # plain size like S M L XL OS
        elif re.match(r'^(XS|S|M|L|XL|XXL|OS|\d{1,2})$', tok):
            if not current_color:
                return None, "Beden girmeden önce renk belirtin. Örnek: 1308 BLK 2S 2M 2L"
            variants.append({"color": current_color, "size": tok, "qty": 1})
        else:
            # treat as color
            current_color = tok
        i += 1

    if not variants:
        return None, "Hiç variant girilmedi. Örnek:\n`1308 BLK 2S 2M 2L WHT 2S 2M 2L`"

    return {"sku": sku, "variants": variants}, None

def build_shopify_csv(data):
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Handle","Title","Body (HTML)","Vendor","Type","Tags","Published",
                "Option1 Name","Option1 Value","Option2 Name","Option2 Value",
                "Variant SKU","Variant Inventory Qty","Variant Price","Cost per item","Status"])
    for sku, variants in data.items():
        p = PRODUCTS[sku]
        handle = f"{p['name'].lower().replace(' ','-').replace('&','and')}-{sku.lower()}"
        retail = round(p['cost'] * 2.5, 2)
        for i, v in enumerate(variants):
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

def build_square_csv(data):
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Item Name","Variation Name","SKU","Category","Price","Current Quantity","Track Inventory"])
    for sku, variants in data.items():
        p = PRODUCTS[sku]
        retail = round(p['cost'] * 2.5, 2)
        for v in variants:
            w.writerow([
                f"{p['name']} - {sku}",
                f"{v['color']} / {v['size']}",
                f"{sku}-{v['color']}-{v['size']}",
                p['type'], retail, v['qty'], "Y"
            ])
    return output.getvalue().encode('utf-8')

# ── Handlers ──────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👗 *GAVA New York — Ürün Giriş Botu*\n\n"
        "Ürün girmek için şu formatta yazın:\n"
        "`SKU RENK ADETbeden ADETbeden ...`\n\n"
        "📌 *Örnekler:*\n"
        "`1308 BLK 2S 2M 2L`\n"
        "`1308 BLK 2S 2M 2L WHT 2S 2M 2L`\n"
        "`V331 RED 3S 3M BLUE 3S 3M`\n\n"
        "📋 *Komutlar:*\n"
        "/liste — tüm ürün SKU'ları\n"
        "/ozet — girilen ürünler\n"
        "/shopify — Shopify CSV indir\n"
        "/square — Square CSV indir\n"
        "/sil SKU — bir ürünü sil\n"
        "/temizle — tümünü sıfırla",
        parse_mode="Markdown"
    )

async def cmd_liste(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lines = []
    for sku, p in PRODUCTS.items():
        lines.append(f"`{sku}` — {p['name']} ({p['type']}) ${p['cost']}")
    # split into chunks of 30
    chunks = [lines[i:i+30] for i in range(0, len(lines), 30)]
    for chunk in chunks:
        await update.message.reply_text("\n".join(chunk), parse_mode="Markdown")

async def cmd_ozet(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sess = get_session(cid)
    if not sess:
        await update.message.reply_text("Henüz ürün girilmedi.")
        return
    lines = [f"📦 *{len(sess)} ürün girildi:*\n"]
    total_variants = 0
    for sku, variants in sess.items():
        p = PRODUCTS[sku]
        total_variants += len(variants)
        colors = {}
        for v in variants:
            colors.setdefault(v['color'], []).append(f"{v['qty']}{v['size']}")
        color_str = "  ".join([f"{c}: {' '.join(sizes)}" for c, sizes in colors.items()])
        lines.append(f"`{sku}` {p['name']}\n  {color_str}")
    lines.append(f"\n📊 Toplam {total_variants} variant")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def cmd_shopify(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sess = get_session(cid)
    if not sess:
        await update.message.reply_text("Henüz ürün girilmedi.")
        return
    csv_bytes = build_shopify_csv(sess)
    await update.message.reply_document(
        document=io.BytesIO(csv_bytes),
        filename="gava_shopify.csv",
        caption=f"✅ Shopify CSV — {len(sess)} ürün, {sum(len(v) for v in sess.values())} variant"
    )

async def cmd_square(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    sess = get_session(cid)
    if not sess:
        await update.message.reply_text("Henüz ürün girilmedi.")
        return
    csv_bytes = build_square_csv(sess)
    await update.message.reply_document(
        document=io.BytesIO(csv_bytes),
        filename="gava_square.csv",
        caption=f"✅ Square CSV — {len(sess)} ürün, {sum(len(v) for v in sess.values())} variant"
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
        await update.message.reply_text(f"'{sku}' oturumda bulunamadı.")

async def cmd_temizle(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    keyboard = [[
        InlineKeyboardButton("Evet, sıfırla", callback_data="confirm_clear"),
        InlineKeyboardButton("İptal", callback_data="cancel_clear")
    ]]
    await update.message.reply_text(
        "Tüm girilen ürünler silinecek. Emin misiniz?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cid = query.message.chat_id
    if query.data == "confirm_clear":
        sessions[cid] = {}
        await query.edit_message_text("✅ Tüm veriler temizlendi.")
    elif query.data == "cancel_clear":
        await query.edit_message_text("İptal edildi.")

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    text = update.message.text.strip()
    sess = get_session(cid)

    result, error = parse_entry(text)
    if error:
        await update.message.reply_text(f"❌ {error}", parse_mode="Markdown")
        return

    sku = result['sku']
    p = PRODUCTS[sku]
    new_variants = result['variants']

    # Merge with existing
    existing = sess.get(sku, [])
    for nv in new_variants:
        found = False
        for ev in existing:
            if ev['color'] == nv['color'] and ev['size'] == nv['size']:
                ev['qty'] = nv['qty']
                found = True
                break
        if not found:
            existing.append(nv)
    sess[sku] = existing

    # Build confirmation message
    colors = {}
    for v in existing:
        colors.setdefault(v['color'], []).append(f"{v['qty']}{v['size']}")

    lines = [f"✅ *{p['name']}* (`{sku}`) kaydedildi\n"]
    for color, sizes in colors.items():
        skus_preview = ", ".join([f"`{sku}-{color}-{s.replace(str(q),'')}`" 
                                  for v in existing if v['color']==color 
                                  for q,s in [(v['qty'],v['size'])]])
        lines.append(f"🎨 *{color}*: {' '.join(sizes)}")

    total_qty = sum(v['qty'] for v in existing)
    lines.append(f"\n📦 Toplam: {total_qty} adet, {len(existing)} variant")
    lines.append(f"💰 Maliyet: ${p['cost']} | Satış: ${p['cost']*2.5:.2f}")
    lines.append(f"\n_Tüm oturum: {len(sess)} ürün girildi_")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("liste", cmd_liste))
    app.add_handler(CommandHandler("ozet", cmd_ozet))
    app.add_handler(CommandHandler("shopify", cmd_shopify))
    app.add_handler(CommandHandler("square", cmd_square))
    app.add_handler(CommandHandler("sil", cmd_sil))
    app.add_handler(CommandHandler("temizle", cmd_temizle))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot başlatıldı...")
    app.run_polling()

if __name__ == "__main__":
    main()
