import telebot
from telebot import types
from tg_parser import ProductParser
from extensions import BotExtensions

# --- НАСТРОЙКИ ---
TOKEN = "8757913413:AAHPre0ss0isrVrj_j3NaX3I_v18sgj09I4"
ADMIN_ID = 1826944290 
ADMIN_USERNAME = "@SAYSUBA" 

bot = telebot.TeleBot(TOKEN)
parser = ProductParser()
ext = BotExtensions()

def main_kb(uid):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🎁 Каталог", "⭐ Избранное")
    markup.add("🧠 Консультант", "ℹ️ Полезное")
    markup.add("🆘 Связь и Поддержка")
    if uid == ADMIN_ID:
        markup.add("📘 Массовая загрузка", "📕 Очистить всё")
    return markup

@bot.message_handler(commands=['start'])
def start(m):
    welcome = (
        f"🚲 **FIXIE SHOP KG**\n"
        f"━━━━━━━━━━━━━━\n"
        f"Привет, {m.from_user.first_name}! 👋\n\n"
        f"Я твой личный гид по фикс-культуре Бишкека.\n"
        f"Ищи байки, рамы и запчасти в пару кликов."
    )
    bot.send_message(m.chat.id, welcome, reply_markup=main_kb(m.from_user.id), parse_mode="Markdown")

@bot.message_handler(content_types=['text'])
def handle_text(m):
    uid = m.from_user.id

    if m.text == "🎁 Каталог":
        cats = parser.get_all_categories()
        if not cats:
            return bot.send_message(m.chat.id, "📭 *Каталог пока пуст.*", parse_mode="Markdown")
        kb = types.InlineKeyboardMarkup(row_width=1)
        for c in cats:
            kb.add(types.InlineKeyboardButton(f"📁 {c.upper()}", callback_data=f"cat_{c}"))
        bot.send_message(m.chat.id, "📂 **ВЫБЕРИТЕ КАТЕГОРИЮ:**", reply_markup=kb, parse_mode="Markdown")

    elif m.text == "🧠 Консультант":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🚲 Велосипеды в сборе", callback_data="cons_Велосипеды"),
               types.InlineKeyboardButton("🖼 Фреймсеты (Рамы)", callback_data="cons_Фреймсеты"),
               types.InlineKeyboardButton("🎡 Виллсеты (Колеса)", callback_data="cons_Колёса"))
        bot.send_message(m.chat.id, "🧠 **УМНЫЙ ПОДБОР**\nВыбери тип товара, и я подберу его под твой рост:", reply_markup=kb, parse_mode="Markdown")

    elif m.text == "ℹ️ Полезное":
        info = (
            "ℹ️ **ИНФОРМАЦИЯ**\n"
            "━━━━━━━━━━━━━━\n"
            "📍 **ГОРОД:** Бишкек, Кыргызстан\n"
            "🚚 **ДОСТАВКА:** СДЭК / Курьер / Самовывоз\n"
            "🛠 **СЕРВИС:** Проверка всех узлов перед продажей\n\n"
            "Все объявления актуальны на момент публикации."
        )
        bot.send_message(m.chat.id, info, parse_mode="Markdown")

    elif m.text == "🆘 Связь и Поддержка":
        contact = (
            "🆘 **ПОДДЕРЖКА**\n"
            "━━━━━━━━━━━━━━\n"
            f"По вопросам покупки, обмена или рекламы пиши нашему менеджеру:\n\n"
            f"👤 **CONTACT:** {ADMIN_USERNAME}"
        )
        bot.send_message(m.chat.id, contact, parse_mode="Markdown")

    elif m.text == "⭐ Избранное":
        items = ext.get_favs(uid)
        if items: send_card(m, items, 0, "fav")
        else: bot.send_message(m.chat.id, "🌟 *Список избранного пуст.*", parse_mode="Markdown")

    elif m.text == "📘 Массовая загрузка" and uid == ADMIN_ID:
        kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
        kb.add("❌ Отменить загрузку")
        msg = bot.send_message(m.chat.id, "📥 **РЕЖИМ ЗАГРУЗКИ**\nПросто пересылай посты из канала сюда:", reply_markup=kb, parse_mode="Markdown")
        bot.register_next_step_handler(msg, mass_upload)

    elif m.text == "📕 Очистить всё" and uid == ADMIN_ID:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✅ ДА, УДАЛИТЬ", callback_data="db_clear_confirm"),
               types.InlineKeyboardButton("❌ НЕТ, ОТМЕНА", callback_data="db_clear_cancel"))
        bot.send_message(m.chat.id, "⚠️ **ПОДТВЕРЖДЕНИЕ**\nВы уверены, что хотите полностью очистить базу данных?", reply_markup=kb, parse_mode="Markdown")

def mass_upload(m):
    if m.text == "❌ Отменить загрузку":
        return bot.send_message(m.chat.id, "✅ Режим загрузки выключен.", reply_markup=main_kb(m.from_user.id))
    
    try:
        text = m.caption or m.text
        photo = m.photo[-1].file_id if m.photo else None
        if text:
            cat = parser.add_item(text, photo)
            bot.send_message(m.chat.id, f"✅ Добавлено в: *{cat}*", parse_mode="Markdown")
    except: pass
    bot.register_next_step_handler(m, mass_upload)

def send_card(m, items, idx, mode, edit=False):
    it = items[idx]
    cap = (
        f"🏷 **{it['title'].upper()}**\n"
        f"━━━━━━━━━━━━━━\n"
        f"💰 ЦЕНА: `{it['price']}`\n"
        f"📍 ЛОКАЦИЯ: `Бишкек`\n\n"
        f"📝 **ОПИСАНИЕ:**\n{it['desc']}\n"
        f"━━━━━━━━━━━━━━\n"
        f"🔎 #{it['cat']}"
    )
    kb = types.InlineKeyboardMarkup(row_width=2)
    nav = []
    if idx > 0: nav.append(types.InlineKeyboardButton("⬅️", callback_data=f"nav_{mode}_{idx-1}"))
    if idx < len(items)-1: nav.append(types.InlineKeyboardButton("➡️", callback_data=f"nav_{mode}_{idx+1}"))
    if nav: kb.row(*nav)
    
    kb.add(types.InlineKeyboardButton("💬 КУПИТЬ / СВЯЗЬ", url=f"https://t.me/{ADMIN_USERNAME[1:]}"))
    kb.add(types.InlineKeyboardButton("⭐️ В ИЗБРАННОЕ", callback_data=f"fav_{it['id']}"))

    if edit:
        try: bot.edit_message_media(types.InputMediaPhoto(it['photo'], caption=cap, parse_mode="Markdown"), m.chat.id, m.message_id, reply_markup=kb)
        except: pass
    else:
        if it['photo']: bot.send_photo(m.chat.id, it['photo'], caption=cap, reply_markup=kb, parse_mode="Markdown")
        else: bot.send_message(m.chat.id, cap, reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: True)
def cb(c):
    uid = c.from_user.id

    if c.data.startswith("cat_"):
        cat = c.data.split('_')[1]
        items = parser.get_items_by_cat(cat)
        if items: send_card(c.message, items, 0, cat)

    elif c.data.startswith("cons_"):
        cat = c.data.split('_')[1]
        kb = types.InlineKeyboardMarkup()
        for h, s in [("📏 160-175см", "S"), ("📏 175-185см", "M"), ("📏 185+см", "L")]:
            kb.add(types.InlineKeyboardButton(h, callback_data=f"h_{cat}_{s}"))
        bot.edit_message_text(f"🔍 **ПОДБОР: {cat.upper()}**\nУкажи свой рост:", c.message.chat.id, c.message.message_id, reply_markup=kb, parse_mode="Markdown")

    elif c.data.startswith("h_"):
        _, cat, size = c.data.split('_')
        items = parser.get_items_by_size(cat, size)
        if items:
            bot.send_message(c.message.chat.id, f"💡 Тебе подойдет размер **{size}**. Вот что мы нашли:", parse_mode="Markdown")
            send_card(c.message, items, 0, f"h_{cat}_{size}")
        else:
            bot.send_message(c.message.chat.id, f"❌ Размера **{size}** сейчас нет в наличии.")

    elif c.data.startswith("nav_"):
        _, mode, idx = c.data.split('_')
        if mode == "fav": items = ext.get_favs(uid)
        elif mode.startswith("h_"):
            m_parts = mode.split('_')
            items = parser.get_items_by_size(m_parts[1], m_parts[2])
        else: items = parser.get_items_by_cat(mode)
        
        if items: send_card(c.message, items, int(idx), mode, edit=True)

    elif c.data.startswith("fav_"):
        ext.add_to_fav(uid, c.data.split('_')[1])
        bot.answer_callback_query(c.id, "🌟 Добавлено в избранное!")

    elif c.data == "db_clear_confirm":
        parser.clear_db()
        bot.edit_message_text("✅ **БАЗА ДАННЫХ ОЧИЩЕНА**", c.message.chat.id, c.message.message_id, parse_mode="Markdown")

    elif c.data == "db_clear_cancel":
        bot.delete_message(c.message.chat.id, c.message.message_id)

# Хэндлер канала
@bot.channel_post_handler(content_types=['photo', 'text'])
def channel_listener(m):
    try:
        text = m.caption or m.text
        photo = m.photo[-1].file_id if m.photo else None
        if text:
            cat = parser.add_item(text, photo)
            print(f"✅ Канал: добавлено в {cat}")
    except: pass

print("\n" + "="*30)
print("🚀 БОТ ЗАПУЩЕН УСПЕШНО!")
print("Слушаю сообщения...")
print("="*30 + "\n")

bot.infinity_polling(allowed_updates=["message", "callback_query", "channel_post"])
