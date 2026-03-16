import os, csv, io, json, urllib.request, urllib.parse, base64, re
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters, ConversationHandler
)
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_DB = True
except ImportError:
    HAS_DB = False

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
GOOGLE_SERVICE_ACCOUNT = os.environ.get("GOOGLE_SERVICE_ACCOUNT", "")

def upload_to_drive(filename, file_bytes, mime_type="image/jpeg"):
    if not GOOGLE_SERVICE_ACCOUNT or not GOOGLE_DRIVE_FOLDER_ID:
        return None
    try:
        import json as _json
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        creds_info = _json.loads(GOOGLE_SERVICE_ACCOUNT)
        creds = service_account.Credentials.from_service_account_info(
            creds_info, scopes=["https://www.googleapis.com/auth/drive"])
        service = build("drive", "v3", credentials=creds)
        meta = {"name": filename, "parents": [GOOGLE_DRIVE_FOLDER_ID]}
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type)
        f = service.files().create(body=meta, media_body=media, fields="id").execute()
        file_id = f.get("id")
        service.permissions().create(fileId=file_id, body={"type": "anyone", "role": "reader"}).execute()
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    except Exception as e:
        print(f"Drive error: {e}")
        return None
CLAUDE_API_KEY = os.environ.get("CLAUDE_API_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")

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

# ── Database ──────────────────────────────────────────────────────────────────

def get_db():
    if not HAS_DB or not DATABASE_URL:
        return None
    try:
        return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    except:
        return None

def init_db():
    conn = get_db()
    if not conn:
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS invoices (
                    id SERIAL PRIMARY KEY,
                    invoice_no TEXT,
                    supplier TEXT,
                    date TEXT,
                    total NUMERIC,
                    items JSONB,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id SERIAL PRIMARY KEY,
                    invoice_id INTEGER REFERENCES invoices(id),
                    sku TEXT NOT NULL,
                    product_name TEXT,
                    color TEXT,
                    size TEXT,
                    qty INTEGER,
                    cost NUMERIC,
                    retail_price NUMERIC,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
    conn.close()

def db_save_invoice(invoice_no, supplier, date, total, items):
    conn = get_db()
    if not conn:
        return None
    with conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO invoices (invoice_no, supplier, date, total, items) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                (invoice_no, supplier, date, total, json.dumps(items))
            )
            row = cur.fetchone()
    conn.close()
    return row['id']

def db_save_variants(invoice_id, sku, variants, retail_price):
    db_save_variants_named(invoice_id, sku, variants, retail_price, None)

def db_save_variants_named(invoice_id, sku, variants, retail_price, product_name=None):
    conn = get_db()
    if not conn:
        return
    p = PRODUCTS.get(sku, {"name": sku, "cost": 0})
    name = product_name or p['name']
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM inventory WHERE sku=%s", (sku,))
            for v in variants:
                cur.execute(
                    "INSERT INTO inventory (invoice_id, sku, product_name, color, size, qty, cost, retail_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                    (invoice_id, sku, name, v['color'], v['size'], v['qty'], p['cost'], retail_price)
                )
    conn.close()

def db_get_invoices():
    conn = get_db()
    if not conn:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM invoices ORDER BY created_at DESC LIMIT 20")
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_get_inventory():
    conn = get_db()
    if not conn:
        return []
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM inventory ORDER BY sku, color, size")
        rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def db_get_inventory_as_session():
    rows = db_get_inventory()
    sess = {}
    for r in rows:
        sku = r['sku']
        if sku not in sess:
            sess[sku] = {"variants": [], "retail_price": float(r['retail_price'] or 0)}
        sess[sku]["variants"].append({"color": r['color'], "size": r['size'], "qty": r['qty']})
    return sess

# in-memory fallback
mem_sessions = {}
def get_session(cid):
    conn = get_db()
    if conn:
        conn.close()
        return db_get_inventory_as_session()
    if cid not in mem_sessions:
        mem_sessions[cid] = {}
    return mem_sessions[cid]

# ── Claude API ────────────────────────────────────────────────────────────────

def call_claude(prompt, system_prompt):
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}]
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
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    raw = data["content"][0]["text"].strip()
    raw = raw.replace("```json","").replace("```","").strip()
    raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', "", raw)
    if raw.startswith("["):
        end = raw.rfind("]")
        if end != -1: raw = raw[:end+1]
    elif raw.startswith("{"):
        end = raw.rfind("}")
        if end != -1: raw = raw[:end+1]
    return raw

def parse_invoice_with_claude(pdf_text):
    system = """Sen bir fatura analiz asistanısın. Verilen fatura metninden ürün bilgilerini çıkar.
SADECE JSON döndür:
{
  "invoice_no": "1013",
  "supplier": "VAV New York",
  "date": "03/14/2026",
  "total": 10487.10,
  "items": [
    {"sku": "1308", "description": "DRESS EMBROIDERY", "qty": 12, "unit_price": 8.00, "amount": 96.00}
  ]
}"""
    raw = call_claude(pdf_text, system)
    return json.loads(raw)

def parse_delivery_with_claude(text):
    system = """Sen bir moda perakende stok yönetim asistanısın. Her girdi Türkçe olacak, her çıktı İngilizce olmalı.

RENK KODLARI (Türkçe → kısa kod):
siyah→BLK, beyaz→WHT, kırmızı→RED, mavi→BLU, lacivert→NVY, bej/bege→BGE,
yeşil→GRN, pembe→PNK, gri→GRY, kahve→BRN, sarı→YLW, mor→PRP,
turuncu→ORG, krem→CRM, ekru→ECR, camel→CML, multi/çok renkli→MLT,
leopar→LEO, çiçekli print→FLR, çizgili→STR, kareli→PLD

BEDEN DAĞILIMI:
- "2s2m2l" = asorti oran, renk adedi beden sayısına bölünür
  Örnek: 6mavi 2s2m2l → BLU:2S,2M,2L | 3siyah 2s2m2l → BLK:1S,1M,1L
- "one size" / "tek beden" / beden yok → OS
- "S/M" → S ve M eşit bölünür | "L/XL" → L ve XL eşit
- Sayısal bedenler (27,28,29,30) olduğu gibi bırak

ÜRÜN ADI ÇEVİRİSİ - Türkçe açıklamayı İngilizce ürün adına çevir:
nakışlı→Embroidery, çizgili→Striped, keten→Linen, örme/örgü→Knit,
baskılı→Printed, dantel→Lace, kadife→Velvet, denim→Denim, çiçekli→Floral,
düz renk→Solid, saten→Satin, şifon→Chiffon, fitilli→Ribbed, tığ işi/kroşe→Crochet,
elbise→Dress, bluz→Blouse, pantolon→Pants, şort→Shorts, etek→Skirt,
hırka→Cardigan, yelek→Vest, üst/top→Top, takım→Set, kazak→Sweater, palto→Coat

SADECE JSON döndür:
[{"sku":"1308","product_name":"Embroidery Dress","retail_price":24.00,"variants":[{"color":"BLK","size":"S","qty":1}]}]"""
    raw = call_claude(text, system)
    return json.loads(raw)

# ── Keyboards ─────────────────────────────────────────────────────────────────

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📄 Invoice Yukle", callback_data="menu_invoice"),
         InlineKeyboardButton("📦 Urun Teslim Al", callback_data="menu_delivery")],
        [InlineKeyboardButton("📸 Fotograf Ekle", callback_data="menu_photo"),
         InlineKeyboardButton("🗂 Envanter", callback_data="menu_inventory")],
        [InlineKeyboardButton("📋 Invoice Listesi", callback_data="menu_invoices"),
         InlineKeyboardButton("📤 CSV Indir", callback_data="menu_csv")],
        [InlineKeyboardButton("🗑 Envanteri Sifirla", callback_data="menu_reset_inventory")],
    ])

def back_keyboard():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Ana Menü", callback_data="menu_main")]])

# ── Handlers ──────────────────────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    conn = get_db()
    db_ok = "🟢 Veritabanı bağlı" if conn else "🟡 Geçici hafıza (DB yok)"
    if conn: conn.close()
    inv_count = len(db_get_invoices()) if HAS_DB and DATABASE_URL else 0
    stock_count = len(db_get_inventory()) if HAS_DB and DATABASE_URL else 0
    await update.message.reply_text(
        f"👗 *GAVA New York — Stok Yönetimi*\n"
        f"{db_ok}\n"
        f"📄 {inv_count} invoice · 📦 {stock_count} variant kayıtlı\n\n"
        f"Ne yapmak istersiniz?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def show_main_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    inv_count = len(db_get_invoices()) if HAS_DB and DATABASE_URL else 0
    stock_count = len(db_get_inventory()) if HAS_DB and DATABASE_URL else 0
    query = update.callback_query
    await query.edit_message_text(
        f"👗 *GAVA New York — Ana Menü*\n"
        f"📄 {inv_count} invoice · 📦 {stock_count} variant\n\n"
        f"Ne yapmak istersiniz?",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

async def menu_invoice(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📄 *Invoice Yükleme*\n\n"
        "Invoice PDF'ini buraya gönderin.\n"
        "Claude faturayı okuyup sisteme kaydeder.\n\n"
        "_Şimdi PDF dosyasını gönderin..._",
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )
    ctx.user_data['mode'] = 'invoice'

async def menu_delivery(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "📦 *Ürün Teslim Al*\n\n"
        "Türkçe serbest yazın, Claude anlar:\n\n"
        "`1308 3siyah 6mavi 3kırmızı 2s2m2l 24$`\n"
        "`1309 6kırmızı 6yeşil one size 35$`\n"
        "`V331 12kırmızı S/M 18$`\n"
        "`SS4278 20multi 2s2m2l 15$`\n\n"
        "Birden fazla ürünü aynı anda da girebilirsiniz.",
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )
    ctx.user_data['mode'] = 'delivery'

async def menu_invoices(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    invoices = db_get_invoices()
    if not invoices:
        await query.edit_message_text(
            "📋 *Invoice Listesi*\n\nHenüz invoice yüklenmedi.",
            parse_mode="Markdown", reply_markup=back_keyboard()
        )
        return
    lines = ["📋 *Yüklenen Invoice'lar:*\n"]
    for inv in invoices:
        items = inv.get('items') or []
        if isinstance(items, str):
            items = json.loads(items)
        date = inv.get('date','?')
        lines.append(
            f"🧾 *#{inv['invoice_no']}* — {inv['supplier']}\n"
            f"   📅 {date} · {len(items)} ürün · ${inv['total'] or '?'}\n"
            f"   🕐 {str(inv['created_at'])[:16]}"
        )
    keyboard = []
    for inv in invoices[:5]:
        keyboard.append([
            InlineKeyboardButton(f"#{inv['invoice_no']} — {inv['supplier']}", callback_data=f"inv_detail_{inv['id']}"),
            InlineKeyboardButton("🗑", callback_data=f"inv_delete_{inv['id']}")
        ])
    keyboard.append([InlineKeyboardButton("🏠 Ana Menü", callback_data="menu_main")])
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def invoice_detail(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inv_id = int(query.data.split("_")[-1])
    conn = get_db()
    if not conn:
        await query.edit_message_text("DB bağlantısı yok.", reply_markup=back_keyboard())
        return
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM invoices WHERE id=%s", (inv_id,))
        inv = dict(cur.fetchone())
    conn.close()
    items = inv.get('items') or []
    if isinstance(items, str):
        items = json.loads(items)
    lines = [f"🧾 *Invoice #{inv['invoice_no']}*\n"
             f"📦 {inv['supplier']} · {inv['date']}\n"
             f"💰 Toplam: ${inv['total']}\n\n"
             f"*Ürünler ({len(items)}):*"]
    for it in items[:20]:
        lines.append(f"  `{it.get('sku','')}` {it.get('description','')} — {it.get('qty','')} adet @ ${it.get('unit_price','')}")
    if len(items) > 20:
        lines.append(f"  _...ve {len(items)-20} ürün daha_")
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=back_keyboard()
    )

async def menu_inventory(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rows = db_get_inventory()
    if not rows:
        await query.edit_message_text(
            "🗂 *Envanter*\n\nHenüz ürün teslim alınmadı.",
            parse_mode="Markdown", reply_markup=back_keyboard()
        )
        return
    # group by sku
    by_sku = {}
    for r in rows:
        sku = r['sku']
        if sku not in by_sku:
            by_sku[sku] = {"name": r['product_name'], "variants": [], "retail": r['retail_price']}
        by_sku[sku]["variants"].append(r)
    total_items = sum(sum(v['qty'] for v in d['variants']) for d in by_sku.values())
    lines = [f"🗂 *Envanter — {len(by_sku)} ürün, {total_items} adet*\n"]
    for sku, d in list(by_sku.items())[:15]:
        total = sum(v['qty'] for v in d['variants'])
        colors = {}
        for v in d['variants']:
            colors.setdefault(v['color'], 0)
            colors[v['color']] += v['qty']
        color_str = " ".join([f"{c}:{q}" for c,q in colors.items()])
        lines.append(f"`{sku}` {d['name']}\n  {color_str} · {total} adet · ${d['retail']}")
    if len(by_sku) > 15:
        lines.append(f"\n_...ve {len(by_sku)-15} ürün daha. CSV ile tam listeye bakın._")
    keyboard = [
        [InlineKeyboardButton("📤 Shopify CSV", callback_data="menu_shopify"),
         InlineKeyboardButton("📤 Square CSV", callback_data="menu_square")],
        [InlineKeyboardButton("🏠 Ana Menü", callback_data="menu_main")]
    ]
    await query.edit_message_text(
        "\n".join(lines),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def menu_csv(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Hangi platform icin CSV?",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Shopify CSV", callback_data="menu_shopify"),
             InlineKeyboardButton("Square CSV", callback_data="menu_square")],
            [InlineKeyboardButton("Ana Menu", callback_data="menu_main")]
        ])
    )

async def menu_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "Fotograf Ekle\n\nUrun fotografini gonderin, caption olarak SKU yazin.\nOrnek caption: 1308",
        reply_markup=back_keyboard()
    )
    ctx.user_data['mode'] = 'photo'

async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo
    if not photo:
        return
    caption = (update.message.caption or "").strip().upper()
    if not caption:
        await update.message.reply_text("Caption olarak SKU yazin! Ornek: 1308", reply_markup=main_menu_keyboard())
        return
    sku = caption.split()[0]
    if sku not in PRODUCTS:
        matches = [k for k in PRODUCTS if k.startswith(sku)]
        if len(matches) == 1:
            sku = matches[0]
        else:
            await update.message.reply_text(f"SKU bulunamadi: {sku}", reply_markup=main_menu_keyboard())
            return
    p = PRODUCTS[sku]
    await update.message.reply_text(f"Yukleniyor: {sku} - {p['name']}...")
    file = await ctx.bot.get_file(photo[-1].file_id)
    file_bytes = bytes(await file.download_as_bytearray())
    filename = f"{sku}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
    url = upload_to_drive(filename, file_bytes)
    if not url:
        await update.message.reply_text("Drive yuklemesi basarisiz. Variables kontrol edin.", reply_markup=main_menu_keyboard())
        return
    conn = get_db()
    if conn:
        with conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("ALTER TABLE inventory ADD COLUMN IF NOT EXISTS image_url TEXT")
                except Exception:
                    pass
                cur.execute("UPDATE inventory SET image_url=%s WHERE sku=%s", (url, sku))
        conn.close()
    await update.message.reply_text(
        f"Fotograf yuklendi!\nSKU: {sku}\nURL: {url}\n\nShopify CSV indirince Image Src dolu gelecek.",
        reply_markup=main_menu_keyboard()
    )

async def export_csv(update: Update, ctx: ContextTypes.DEFAULT_TYPE, platform: str):
    query = update.callback_query
    await query.answer()
    sess = db_get_inventory_as_session() if HAS_DB and DATABASE_URL else mem_sessions.get(update.effective_chat.id, {})
    if not sess:
        await query.edit_message_text("Henüz ürün girilmedi.", reply_markup=back_keyboard())
        return
    total_v = sum(len(e["variants"]) for e in sess.values())
    if platform == "shopify":
        csv_bytes = build_shopify_csv(sess)
        fname = f"gava_shopify_{datetime.now().strftime('%Y%m%d')}.csv"
        caption = f"✅ Shopify CSV — {len(sess)} ürün, {total_v} variant"
    else:
        csv_bytes = build_square_csv(sess)
        fname = f"gava_square_{datetime.now().strftime('%Y%m%d')}.csv"
        caption = f"✅ Square CSV — {len(sess)} ürün, {total_v} variant"
    await query.message.reply_document(
        document=io.BytesIO(csv_bytes),
        filename=fname,
        caption=caption
    )
    await query.edit_message_text(
        "Fotograf Ekle\n\nUrun fotografini gonderin.\nCaption olarak SKU yazin.\nOrnek: 1308",
        reply_markup=back_keyboard()
    )

def build_shopify_csv(sess_data):
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Handle","Title","Body (HTML)","Vendor","Type","Tags","Published",
                "Option1 Name","Option1 Value","Option2 Name","Option2 Value",
                "Variant SKU","Variant Inventory Qty","Variant Price","Cost per item","Status"])
    for sku, entry in sess_data.items():
        p = PRODUCTS.get(sku, {"name": sku, "type": "Other", "cost": 0})
        handle = f"{p['name'].lower().replace(' ','-').replace('&','and')}-{sku.lower()}"
        retail = entry.get("retail_price") or round(p['cost'] * 2.5, 2)
        for i, v in enumerate(entry["variants"]):
            w.writerow([
                handle,
                f"{p['name']} - {sku}" if i==0 else "",
                f"<p>{p['type']}</p>" if i==0 else "",
                "VAV New York" if i==0 else "",
                p['type'] if i==0 else "",
                p['type'].lower() if i==0 else "",
                "TRUE" if i==0 else "",
                "Color", v['color'], "Size", v['size'],
                f"{sku}-{v['color']}-{v['size']}",
                v['qty'], retail, p['cost'],
                "active" if i==0 else ""
            ])
    return output.getvalue().encode('utf-8')

def build_square_csv(sess_data):
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(["Item Name","Variation Name","SKU","Category","Price","Current Quantity","Track Inventory"])
    for sku, entry in sess_data.items():
        p = PRODUCTS.get(sku, {"name": sku, "type": "Other", "cost": 0})
        retail = entry.get("retail_price") or round(p['cost'] * 2.5, 2)
        for v in entry["variants"]:
            w.writerow([
                f"{p['name']} - {sku}",
                f"{v['color']} / {v['size']}",
                f"{sku}-{v['color']}-{v['size']}",
                p['type'], retail, v['qty'], "Y"
            ])
    return output.getvalue().encode('utf-8')

async def handle_pdf(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    doc = update.message.document
    if not doc or doc.mime_type != 'application/pdf':
        return
    await update.message.reply_text("📄 Invoice okunuyor, Claude analiz ediyor...")
    file = await ctx.bot.get_file(doc.file_id)
    file_bytes = await file.download_as_bytearray()
    # Extract text from PDF using base64 + Claude vision
    pdf_b64 = base64.b64encode(bytes(file_bytes)).decode()
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 8000,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
                {"type": "text", "text": """Faturadaki TUM urunleri eksiksiz listele, hicbirini atlama. Shipping/handling satirini items'a ekleme. SADECE JSON dondur:
{
  "invoice_no": "1013",
  "supplier": "VAV New York LLC",
  "date": "03/14/2026",
  "total": 10487.10,
  "items": [
    {"sku": "1308", "description": "DRESS EMBROIDERY", "qty": 12, "unit_price": 8.00, "amount": 96.00}
  ]
}"""}
            ]
        }]
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={"Content-Type":"application/json","x-api-key":CLAUDE_API_KEY,"anthropic-version":"2023-06-01"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read())
        raw = data["content"][0]["text"].strip()
        # Robust JSON extraction - find the JSON object boundaries
        raw = raw.replace("```json","").replace("```","").strip()
        # Find first { and last } to extract valid JSON
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end+1]
        # Fix common issues: remove control characters, fix newlines in strings
        raw = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
        invoice = json.loads(raw)
    except json.JSONDecodeError as e:
        # Fallback: ask Claude to fix the JSON
        try:
            fix_payload = json.dumps({
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 4000,
                "messages": [{"role": "user", "content": f"Bu JSON'u düzelt, SADECE geçerli JSON döndür:\n{raw[:3000]}"}]
            }).encode()
            fix_req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=fix_payload,
                headers={"Content-Type":"application/json","x-api-key":CLAUDE_API_KEY,"anthropic-version":"2023-06-01"}
            )
            with urllib.request.urlopen(fix_req, timeout=30) as resp2:
                data2 = json.loads(resp2.read())
            raw2 = data2["content"][0]["text"].strip().replace("```json","").replace("```","").strip()
            start = raw2.find('{')
            end = raw2.rfind('}')
            if start != -1 and end != -1:
                raw2 = raw2[start:end+1]
            invoice = json.loads(raw2)
        except Exception as e2:
            await update.message.reply_text(f"❌ PDF okunamadı: {e2}\n\nPDF'i tekrar göndermeyi deneyin.")
            return
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")
        return
    items = invoice.get("items", [])
    inv_id = db_save_invoice(
        invoice.get("invoice_no","?"),
        invoice.get("supplier","?"),
        invoice.get("date","?"),
        invoice.get("total",0),
        items
    )
    # İlk mesaj: özet
    supplier = invoice.get('supplier','')
    inv_date = invoice.get('date','')
    inv_total = invoice.get('total','?')
    inv_no = invoice.get('invoice_no','?')
    await update.message.reply_text(
        f"✅ *Invoice #{inv_no} kaydedildi!*\n"
        f"📦 {supplier} · {inv_date}\n"
        f"💰 Toplam: ${inv_total}\n"
        f"📋 *{len(items)} ürün* bulundu:",
        parse_mode="Markdown"
    )
    # Ürünleri 20'şer gönder
    chunk_size = 20
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i+chunk_size]
        end = min(i+chunk_size, len(items))
        lines = [f"📋 *{i+1}–{end} / {len(items)}:*\n"]
        for it in chunk:
            sku = str(it.get('sku',''))
            desc = str(it.get('description',''))
            qty = str(it.get('qty',''))
            price = str(it.get('unit_price',''))
            lines.append(f"`{sku}` {desc} — {qty} adet @ ${price}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    await update.message.reply_text(
        "📦 Ürünleri teslim almak için *Ürün Teslim Al* butonunu kullanın.",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )
    ctx.user_data['mode'] = None

async def handle_text(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cid = update.effective_chat.id
    text = update.message.text.strip()
    mode = ctx.user_data.get('mode')

    # auto-detect: if starts with a SKU-like pattern → delivery
    if re.match(r'^[A-Za-z0-9]+\s+\d*[A-Za-zğüşıöçĞÜŞİÖÇ]', text):
        mode = 'delivery'

    if mode == 'delivery' or mode is None:
        await update.message.reply_text("⏳ Analiz ediliyor...")
        try:
            results = parse_delivery_with_claude(text)
        except Exception as e:
            await update.message.reply_text(f"❌ Hata: {e}", reply_markup=main_menu_keyboard())
            return

        reply_lines = []
        for item in results:
            sku = str(item.get("sku","")).upper()
            variants = item.get("variants", [])
            retail = float(item.get("retail_price") or 0)
            if not sku or not variants:
                continue
            p = PRODUCTS.get(sku, {"name": sku, "type":"Other","cost":0})
            if retail == 0:
                retail = round(p['cost'] * 2.5, 2)
            # Use Claude's translated product name if provided
            claude_name = item.get("product_name")
            if claude_name:
                p = dict(p)
                p['name'] = claude_name
            # Check qty mismatch with invoice
            total_delivered = sum(v['qty'] for v in variants)
            warning = ""
            if HAS_DB and DATABASE_URL:
                conn_check = get_db()
                if conn_check:
                    with conn_check.cursor() as cur:
                        cur.execute("""
                            SELECT (item->>'qty')::int as invoice_qty
                            FROM invoices,
                            jsonb_array_elements(items) AS item
                            WHERE item->>'sku' = %s
                            ORDER BY created_at DESC LIMIT 1
                        """, (sku,))
                        inv_row = cur.fetchone()
                    conn_check.close()
                    if inv_row:
                        invoice_qty = int(inv_row['invoice_qty'])
                        if total_delivered != invoice_qty:
                            diff = total_delivered - invoice_qty
                            sign = "+" if diff > 0 else ""
                            warning = f"\n⚠️ *Fark:* Invoice {invoice_qty} adet, girilen {total_delivered} adet ({sign}{diff})"
            if HAS_DB and DATABASE_URL:
                db_save_variants_named(None, sku, variants, retail, p['name'])
            else:
                sess = mem_sessions.setdefault(cid, {})
                existing = sess.get(sku, {"variants":[], "retail_price": retail})
                existing["retail_price"] = retail
                for nv in variants:
                    found = any(ev['color']==nv['color'] and ev['size']==nv['size'] for ev in existing["variants"])
                    if not found:
                        existing["variants"].append(nv)
                    else:
                        for ev in existing["variants"]:
                            if ev['color']==nv['color'] and ev['size']==nv['size']:
                                ev['qty'] = nv['qty']
                sess[sku] = existing
            total_qty = sum(v['qty'] for v in variants)
            colors = {}
            for v in variants:
                colors.setdefault(v['color'], []).append(f"{v['qty']}{v['size']}")
            lines = [f"✅ *{p['name']}* `{sku}` — ${retail}"]
            for color, sizes in colors.items():
                lines.append(f"  🎨 {color}: {' '.join(sizes)}")
            lines.append(f"  📦 {total_qty} adet, {len(variants)} variant{warning}")
            reply_lines.append("\n".join(lines))

        if reply_lines:
            reply_lines.append("\n_/shopify veya /square ile CSV alın_")
            await update.message.reply_text(
                "\n\n".join(reply_lines),
                parse_mode="Markdown",
                reply_markup=main_menu_keyboard()
            )
        else:
            await update.message.reply_text("❌ Anlayamadım.", reply_markup=main_menu_keyboard())
    else:
        await update.message.reply_text(
            "Ana menüden bir işlem seçin:",
            reply_markup=main_menu_keyboard()
        )

async def menu_reset_inventory(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    rows = db_get_inventory()
    count = len(rows)
    total_qty = sum(r['qty'] for r in rows) if rows else 0
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑 Evet, sıfırla", callback_data="confirm_reset_inventory"),
        InlineKeyboardButton("İptal", callback_data="menu_main")
    ]])
    await query.edit_message_text(
        "Envanter Sifirla\n\nSu an: " + str(count) + " variant, " + str(total_qty) + " adet\nTumü silinecek, invoiceler korunur.\nEmin misiniz?",
        reply_markup=keyboard
    )

async def confirm_reset_inventory(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    conn = get_db()
    if conn:
        with conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM inventory")
        conn.close()
    else:
        mem_sessions.clear()
    await query.edit_message_text(
        "Envanter sifirlandi! Invoiceler korundu.",
        reply_markup=main_menu_keyboard()
    )

async def invoice_delete(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inv_id = int(query.data.split("_")[-1])
    conn = get_db()
    if not conn:
        await query.edit_message_text("DB bağlantısı yok.", reply_markup=back_keyboard())
        return
    with conn.cursor() as cur:
        cur.execute("SELECT invoice_no, supplier FROM invoices WHERE id=%s", (inv_id,))
        row = cur.fetchone()
    conn.close()
    if not row:
        await query.edit_message_text("Invoice bulunamadı.", reply_markup=back_keyboard())
        return
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑 Evet, sil", callback_data=f"inv_confirm_delete_{inv_id}"),
        InlineKeyboardButton("İptal", callback_data="menu_invoices")
    ]])
    await query.edit_message_text(
        f"⚠️ *Invoice #{row['invoice_no']}* ({row['supplier']}) silinsin mi?\n"
        f"Bu işlem geri alınamaz.",
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def invoice_confirm_delete(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inv_id = int(query.data.split("_")[-1])
    conn = get_db()
    if not conn:
        await query.edit_message_text("DB bağlantısı yok.", reply_markup=back_keyboard())
        return
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM invoices WHERE id=%s", (inv_id,))
    conn.close()
    await query.edit_message_text(
        "✅ Invoice silindi.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Invoice Listesi", callback_data="menu_invoices"), InlineKeyboardButton("🏠 Ana Menü", callback_data="menu_main")]])
    )

async def callback_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "menu_main":
        await show_main_menu(update, ctx)
    elif data == "menu_invoice":
        await menu_invoice(update, ctx)
    elif data == "menu_delivery":
        await menu_delivery(update, ctx)
    elif data == "menu_invoices":
        await menu_invoices(update, ctx)
    elif data == "menu_inventory":
        await menu_inventory(update, ctx)
    elif data == "menu_shopify":
        await export_csv(update, ctx, "shopify")
    elif data == "menu_square":
        await export_csv(update, ctx, "square")
    elif data.startswith("inv_detail_"):
        await invoice_detail(update, ctx)
    elif data.startswith("inv_delete_"):
        await invoice_delete(update, ctx)
    elif data.startswith("inv_confirm_delete_"):
        await invoice_confirm_delete(update, ctx)
    elif data == "menu_photo":
        await menu_photo(update, ctx)
    elif data == "menu_csv":
        await menu_csv(update, ctx)
    elif data == "menu_reset_inventory":
        await menu_reset_inventory(update, ctx)
    elif data == "confirm_reset_inventory":
        await confirm_reset_inventory(update, ctx)

async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    inv_count = len(db_get_invoices()) if HAS_DB and DATABASE_URL else 0
    stock_count = len(db_get_inventory()) if HAS_DB and DATABASE_URL else 0
    await update.message.reply_text(
        f"👗 *GAVA New York — Ana Menü*\n"
        f"📄 {inv_count} invoice · 📦 {stock_count} variant",
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard()
    )

def main():
    if HAS_DB and DATABASE_URL:
        init_db()
        print("Veritabani baslatildi")
    else:
        print("Veritabani yok, gecici hafiza")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("shopify", lambda u,c: export_csv_cmd(u,c,"shopify")))
    app.add_handler(CommandHandler("square", lambda u,c: export_csv_cmd(u,c,"square")))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")
    PORT = int(os.environ.get("PORT", 8443))
    if WEBHOOK_URL:
        print(f"Webhook modu: {WEBHOOK_URL}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=WEBHOOK_URL,
            drop_pending_updates=True,
        )
    else:
        print("Polling modu")
        app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
