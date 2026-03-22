import sqlite3
import re

class ProductParser:
    def __init__(self):
        self.db_path = "shop.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT, price TEXT, desc TEXT, cat TEXT, photo TEXT
                )
            ''')

    def add_item(self, text, photo):
        t = text.upper()
        # Категории
        if any(w in t for w in ['ВЕЛОСИПЕД', 'FULLBIKE', 'ФУЛБАЙК', 'В СБОРЕ', 'БАЙК']):
            cat = "Велосипеды"
        elif any(w in t for w in ['КОЛЕСО', 'ОБОД', 'ВТУЛКА', 'ВИЛЛСЕТ', 'WHEELSET', 'ВИЛСЕТ']):
            cat = "Колёса"
        elif any(w in t for w in ['ФРЕЙМСЕТ', 'FRAMESET', 'РАМА', 'FRAME', 'ВИЛКА']):
            cat = "Фреймсеты"
        else:
            cat = "Комплектующие"

        # Цена
        price = "Цена по запросу"
        match = re.search(r'(\d[\d\s,.]*)\s?(?:С|СОМ|C|СОМ)', t)
        if match:
            clean = match.group(1).strip().replace(',', '').replace(' ', '').replace('.', '')
            if clean.isdigit(): price = f"{clean} сом"

        title = text.split('\n')[0][:50]
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO items (title, price, desc, cat, photo) VALUES (?, ?, ?, ?, ?)",
                         (title, price, text, cat, photo))
        return cat

    def get_items_by_size(self, cat, size):
        items = self.get_items_by_cat(cat)
        filtered = [it for it in items if re.search(rf'\b{size}\b', it['desc'].upper())]
        return filtered if filtered else items

    def get_all_categories(self):
        with sqlite3.connect(self.db_path) as conn:
            return [r[0] for r in conn.execute("SELECT DISTINCT cat FROM items").fetchall()]

    def get_items_by_cat(self, cat):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute("SELECT * FROM items WHERE cat = ?", (cat,)).fetchall()]

    def clear_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM items")
