import sqlite3
from contextlib import contextmanager


DB_PATH = "database.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                image TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS deals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                original_price REAL NOT NULL,
                negotiated_price REAL NOT NULL,
                saving REAL NOT NULL,
                commission REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                target_price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                query TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, query)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_behavior (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                product_category TEXT,
                average_discount_preference REAL DEFAULT 0,
                deals_completed INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS funnel_stats (
                key TEXT PRIMARY KEY,
                value INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        cursor.executemany(
            """
            INSERT OR IGNORE INTO funnel_stats (key, value)
            VALUES (?, ?)
            """,
            [
                ("visits", 0),
                ("find_cheaper_clicks", 0),
                ("get_deal_clicks", 0),
                ("completed_deals", 0),
            ],
        )
        cursor.execute("PRAGMA table_info(products)")
        columns = [row[1] for row in cursor.fetchall()]
        if "user_id" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN user_id INTEGER")
        if "image" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN image TEXT")
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        if "role" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        conn.commit()


def create_user(username, hashed_password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
            """,
            (username, hashed_password, "user"),
        )
        conn.commit()
        return cursor.lastrowid


def get_user_by_username(username):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, password, role, created_at
            FROM users
            WHERE username = ?
            """,
            (username,),
        )
        return cursor.fetchone()


def get_all_users():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, role, created_at
            FROM users
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


def promote_user_to_admin(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET role = 'admin'
            WHERE id = ?
            """,
            (user_id,),
        )
        conn.commit()
        return cursor.rowcount


def delete_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount


def insert_products(products, user_id=None):
    if not products:
        return 0

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            """
            INSERT INTO products (name, price, url, source, image, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    p["name"],
                    p["price"],
                    p["url"],
                    p["source"],
                    p.get("image", ""),
                    p.get("user_id", user_id),
                )
                for p in products
            ],
        )
        conn.commit()
        return cursor.rowcount


def search_products(query, user_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        where_conditions = []
        params = []

        if query:
            where_conditions.append("name LIKE ?")
            params.append(f"%{query}%")

        if user_id is not None:
            where_conditions.append("user_id = ?")
            params.append(user_id)

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        cursor.execute(
            f"""
            SELECT id, name, price, url, source, image, user_id, created_at
            FROM products
            {where_clause}
            ORDER BY created_at DESC
            """,
            tuple(params),
        )
        return cursor.fetchall()


def get_all_products():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, price, url, source, image, user_id, created_at
            FROM products
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


def delete_product(product_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
        conn.commit()
        return cursor.rowcount


def update_product_price(product_id, new_price):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE products
            SET price = ?
            WHERE id = ?
            """,
            (new_price, product_id),
        )
        conn.commit()
        return cursor.rowcount


def create_deal(user_id, product_id, original_price, negotiated_price, saving, commission):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO deals (
                user_id,
                product_id,
                original_price,
                negotiated_price,
                saving,
                commission
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                product_id,
                original_price,
                negotiated_price,
                saving,
                commission,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_deals():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, product_id, user_id, original_price, negotiated_price, saving, commission, created_at
            FROM deals
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


def get_admin_analytics():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM deals")
        total_deals = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(commission), 0) FROM deals")
        total_revenue = cursor.fetchone()[0]
        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_deals": total_deals,
            "total_revenue": round(total_revenue, 2),
        }


def create_alert(user_id, query, target_price=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts (user_id, query, target_price)
            VALUES (?, ?, ?)
            """,
            (user_id, query, target_price),
        )
        conn.commit()
        return cursor.lastrowid


def get_user_alerts(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, query, target_price, created_at
            FROM alerts
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()


def delete_alert(alert_id, user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM alerts
            WHERE id = ? AND user_id = ?
            """,
            (alert_id, user_id),
        )
        conn.commit()
        return cursor.rowcount


def increment_funnel_stat(key, delta=1):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO funnel_stats (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = value + excluded.value
            """,
            (key, int(delta)),
        )
        conn.commit()
        return cursor.rowcount


def get_funnel_stats():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM funnel_stats")
        data = {k: int(v) for k, v in cursor.fetchall()}
        return {
            "visits": data.get("visits", 0),
            "find_cheaper_clicks": data.get("find_cheaper_clicks", 0),
            "get_deal_clicks": data.get("get_deal_clicks", 0),
            "completed_deals": data.get("completed_deals", 0),
        }


def add_user_preference(user_id, query):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO user_preferences (user_id, query)
            VALUES (?, ?)
            """,
            (user_id, query),
        )
        conn.commit()
        return cursor.rowcount


def get_user_preferences(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, query, created_at
            FROM user_preferences
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        )
        return cursor.fetchall()


def get_user_behavior(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, product_category, average_discount_preference, deals_completed, clicks, last_updated
            FROM user_behavior
            WHERE user_id = ?
            """,
            (user_id,),
        )
        return cursor.fetchone()


def update_user_behavior_click(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_behavior (user_id, clicks, last_updated)
            VALUES (?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                clicks = clicks + 1,
                last_updated = CURRENT_TIMESTAMP
            """,
            (user_id,),
        )
        conn.commit()
        return cursor.rowcount


def update_user_behavior_deal(user_id, accepted_discount_pct, product_category=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_behavior (
                user_id,
                product_category,
                average_discount_preference,
                deals_completed,
                clicks,
                last_updated
            )
            VALUES (?, ?, ?, 1, 0, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                average_discount_preference =
                    ((average_discount_preference * deals_completed) + excluded.average_discount_preference)
                    / (deals_completed + 1),
                deals_completed = deals_completed + 1,
                product_category = COALESCE(excluded.product_category, product_category),
                last_updated = CURRENT_TIMESTAMP
            """,
            (user_id, product_category, float(accepted_discount_pct)),
        )
        conn.commit()
        return cursor.rowcount
