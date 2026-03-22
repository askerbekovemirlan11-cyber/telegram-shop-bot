import sqlite3

class BotExtensions:
    def __init__(self):
        self.db_path = "shop.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    user_id INTEGER,
                    item_id INTEGER
                )
            ''')

    def add_to_fav(self, user_id, item_id):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT * FROM favorites WHERE user_id=? AND item_id=?", (user_id, item_id))
            if not cur.fetchone():
                conn.execute("INSERT INTO favorites (user_id, item_id) VALUES (?, ?)", (user_id, item_id))

    def get_favs(self, user_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT items.* FROM items 
                JOIN favorites ON items.id = favorites.item_id 
                WHERE favorites.user_id = ?
            """
            return [dict(row) for row in conn.execute(query, (user_id,)).fetchall()]
