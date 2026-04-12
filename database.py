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
                telegram_chat_id TEXT UNIQUE,
                email_verified INTEGER NOT NULL DEFAULT 0,
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
                family_key TEXT,
                display_name TEXT,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                price REAL,
                detected_at TIMESTAMP,
                source TEXT,
                average_price REAL,
                discount_pct REAL,
                score REAL,
                is_auto_detected INTEGER NOT NULL DEFAULT 0
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
                excluded_category TEXT,
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
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notification_type TEXT NOT NULL,
                sent_for_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(notification_type, sent_for_date)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_delivery_state (
                recipient_key TEXT PRIMARY KEY,
                last_sent_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS telegram_interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                telegram_chat_id TEXT NOT NULL,
                interaction_type TEXT NOT NULL,
                query TEXT,
                raw_text TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alert_notification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                alert_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, alert_id, product_id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS telegram_connect_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                connect_token TEXT UNIQUE NOT NULL,
                is_used INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                used_at TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS behavior_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                product_family_key TEXT NOT NULL,
                offer_id INTEGER,
                price REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_behavior_events_user_family
            ON behavior_events(user_id, product_family_key)
            """
        )
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_behavior_events_type
            ON behavior_events(event_type)
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
        if "family_key" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN family_key TEXT")
        if "display_name" not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN display_name TEXT")
        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_products_family_key
            ON products(family_key)
            """
        )
        cursor.execute("PRAGMA table_info(users)")
        user_columns = [row[1] for row in cursor.fetchall()]
        if "role" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
        if "telegram_chat_id" not in user_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN telegram_chat_id TEXT")
        if "email_verified" not in user_columns:
            cursor.execute(
                "ALTER TABLE users ADD COLUMN email_verified INTEGER NOT NULL DEFAULT 0"
            )
        cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_users_telegram_chat_id
            ON users(telegram_chat_id)
            WHERE telegram_chat_id IS NOT NULL
            """
        )
        cursor.execute("PRAGMA table_info(deals)")
        deal_columns = [row[1] for row in cursor.fetchall()]
        if "price" not in deal_columns:
            cursor.execute("ALTER TABLE deals ADD COLUMN price REAL")
        if "detected_at" not in deal_columns:
            cursor.execute("ALTER TABLE deals ADD COLUMN detected_at TIMESTAMP")
        if "source" not in deal_columns:
            cursor.execute("ALTER TABLE deals ADD COLUMN source TEXT")
        if "average_price" not in deal_columns:
            cursor.execute("ALTER TABLE deals ADD COLUMN average_price REAL")
        if "discount_pct" not in deal_columns:
            cursor.execute("ALTER TABLE deals ADD COLUMN discount_pct REAL")
        if "score" not in deal_columns:
            cursor.execute("ALTER TABLE deals ADD COLUMN score REAL")
        if "is_auto_detected" not in deal_columns:
            cursor.execute(
                "ALTER TABLE deals ADD COLUMN is_auto_detected INTEGER NOT NULL DEFAULT 0"
            )
        cursor.execute("PRAGMA table_info(user_behavior)")
        behavior_columns = [row[1] for row in cursor.fetchall()]
        if "excluded_category" not in behavior_columns:
            cursor.execute("ALTER TABLE user_behavior ADD COLUMN excluded_category TEXT")
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


def get_user_by_telegram_chat_id(telegram_chat_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, password, telegram_chat_id, role, created_at
            FROM users
            WHERE telegram_chat_id = ?
            """,
            (str(telegram_chat_id),),
        )
        return cursor.fetchone()


def get_or_create_telegram_user(telegram_chat_id):
    telegram_chat_id = str(telegram_chat_id)
    existing_user = get_user_by_telegram_chat_id(telegram_chat_id)
    if existing_user:
        return existing_user

    username = f"tg_{telegram_chat_id}"
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO users (username, password, telegram_chat_id, role)
            VALUES (?, ?, ?, ?)
            """,
            (username, "", telegram_chat_id, "user"),
        )
        conn.commit()

    return get_user_by_telegram_chat_id(telegram_chat_id)


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


def insert_behavior_event(
    user_id,
    event_type,
    product_family_key,
    offer_id=None,
    price=None,
):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO behavior_events (
                user_id,
                event_type,
                product_family_key,
                offer_id,
                price
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                int(user_id),
                str(event_type),
                str(product_family_key),
                None if offer_id is None else int(offer_id),
                None if price is None else float(price),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_behavior_event_counts(user_id, product_family_key):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT event_type, COUNT(*)
            FROM behavior_events
            WHERE user_id = ? AND product_family_key = ?
            GROUP BY event_type
            """,
            (int(user_id), str(product_family_key)),
        )
        return cursor.fetchall()


def clear_behavior_events(user_id=None, product_family_key=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        where_conditions = []
        params = []

        if user_id is not None:
            where_conditions.append("user_id = ?")
            params.append(int(user_id))
        if product_family_key is not None:
            where_conditions.append("product_family_key = ?")
            params.append(str(product_family_key))

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        cursor.execute(
            f"""
            DELETE FROM behavior_events
            {where_clause}
            """,
            params,
        )
        conn.commit()
        return cursor.rowcount


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


def set_user_role(username, role):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET role = ?
            WHERE username = ?
            """,
            (role, username),
        )
        conn.commit()
        return cursor.rowcount


def set_user_password(username, hashed_password):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET password = ?
            WHERE username = ?
            """,
            (hashed_password, username),
        )
        conn.commit()
        return cursor.rowcount


def set_user_telegram_chat_id(user_id, telegram_chat_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET telegram_chat_id = ?
            WHERE id = ?
            """,
            (str(telegram_chat_id), int(user_id)),
        )
        conn.commit()
        return cursor.rowcount


def clear_user_telegram_chat_id(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET telegram_chat_id = NULL
            WHERE id = ?
            """,
            (int(user_id),),
        )
        conn.commit()
        return cursor.rowcount


def get_user_telegram_chat_id(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT telegram_chat_id
            FROM users
            WHERE id = ?
            """,
            (int(user_id),),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def get_user_email_verified(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT email_verified
            FROM users
            WHERE id = ?
            """,
            (int(user_id),),
        )
        row = cursor.fetchone()
        return bool(row[0]) if row else False


def create_telegram_connect_token(user_id, connect_token):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO telegram_connect_tokens (user_id, connect_token, is_used)
            VALUES (?, ?, 0)
            """,
            (int(user_id), str(connect_token)),
        )
        conn.commit()
        return cursor.lastrowid


def get_telegram_connect_token(connect_token):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, connect_token, is_used, created_at, used_at
            FROM telegram_connect_tokens
            WHERE connect_token = ?
            """,
            (str(connect_token),),
        )
        return cursor.fetchone()


def get_latest_active_telegram_connect_token_for_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, user_id, connect_token, is_used, created_at, used_at
            FROM telegram_connect_tokens
            WHERE user_id = ? AND is_used = 0
            ORDER BY created_at DESC, id DESC
            LIMIT 1
            """,
            (int(user_id),),
        )
        return cursor.fetchone()


def mark_telegram_connect_token_used(connect_token):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE telegram_connect_tokens
            SET is_used = 1, used_at = CURRENT_TIMESTAMP
            WHERE connect_token = ? AND is_used = 0
            """,
            (str(connect_token),),
        )
        conn.commit()
        return cursor.rowcount


def expire_unused_telegram_connect_tokens_for_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE telegram_connect_tokens
            SET is_used = 1, used_at = CURRENT_TIMESTAMP
            WHERE user_id = ? AND is_used = 0
            """,
            (int(user_id),),
        )
        conn.commit()
        return cursor.rowcount


def set_user_email_verified(user_id, email_verified):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE users
            SET email_verified = ?
            WHERE id = ?
            """,
            (1 if email_verified else 0, int(user_id)),
        )
        conn.commit()
        return cursor.rowcount


def clear_admin_roles(except_username=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if except_username:
            cursor.execute(
                """
                UPDATE users
                SET role = 'user'
                WHERE role = 'admin' AND username != ?
                """,
                (except_username,),
            )
        else:
            cursor.execute(
                """
                UPDATE users
                SET role = 'user'
                WHERE role = 'admin'
                """
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
            INSERT INTO products (name, price, url, source, image, family_key, display_name, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    p["name"],
                    p["price"],
                    p["url"],
                    p["source"],
                    p.get("image", ""),
                    p.get("family_key"),
                    p.get("display_name"),
                    p.get("user_id", user_id),
                )
                for p in products
            ],
        )
        conn.commit()
        return cursor.rowcount


def insert_products_if_missing(products, user_id=None):
    if not products:
        return 0

    with get_connection() as conn:
        cursor = conn.cursor()
        urls = [str(product.get("url", "")).strip() for product in products if product.get("url")]
        existing_urls = set()
        if urls:
            placeholders = ",".join("?" for _ in urls)
            cursor.execute(
                f"""
                SELECT url
                FROM products
                WHERE url IN ({placeholders})
                """,
                urls,
            )
            existing_urls = {row[0] for row in cursor.fetchall()}

        products_to_insert = [
            product
            for product in products
            if str(product.get("url", "")).strip() not in existing_urls
        ]
        if not products_to_insert:
            return 0

        cursor.executemany(
            """
            INSERT INTO products (name, price, url, source, image, family_key, display_name, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    product["name"],
                    product["price"],
                    product["url"],
                    product["source"],
                    product.get("image", ""),
                    product.get("family_key"),
                    product.get("display_name"),
                    product.get("user_id", user_id),
                )
                for product in products_to_insert
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
            SELECT id, name, price, url, source, image, family_key, display_name, user_id, created_at
            FROM products
            {where_clause}
            ORDER BY created_at DESC
            """,
            tuple(params),
        )
        return cursor.fetchall()


def get_product_by_id(product_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, price, url, source, image, family_key, display_name, user_id, created_at
            FROM products
            WHERE id = ?
            """,
            (product_id,),
        )
        return cursor.fetchone()


def get_all_products():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name, price, url, source, image, family_key, display_name, user_id, created_at
            FROM products
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


def get_offers_by_family_key(family_key, user_id=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        where_conditions = ["family_key = ?"]
        params = [str(family_key)]

        if user_id is not None:
            where_conditions.append("(user_id = ? OR user_id IS NULL)")
            params.append(int(user_id))

        where_clause = "WHERE " + " AND ".join(where_conditions)
        cursor.execute(
            f"""
            SELECT id, name, price, url, source, image, family_key, display_name, user_id, created_at
            FROM products
            {where_clause}
            ORDER BY created_at DESC
            """,
            tuple(params),
        )
        return cursor.fetchall()


def get_products_missing_family():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, name
            FROM products
            WHERE family_key IS NULL OR family_key = '' OR display_name IS NULL OR display_name = ''
            ORDER BY id ASC
            """
        )
        return cursor.fetchall()


def update_product_family_fields(product_id, family_key, display_name):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE products
            SET family_key = ?, display_name = ?
            WHERE id = ?
            """,
            (str(family_key), str(display_name), int(product_id)),
        )
        conn.commit()
        return cursor.rowcount


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


def update_product_url(product_id, new_url):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE products
            SET url = ?
            WHERE id = ?
            """,
            (str(new_url).strip(), int(product_id)),
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
                commission,
                price,
                source,
                is_auto_detected
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
            """,
            (
                user_id,
                product_id,
                original_price,
                negotiated_price,
                saving,
                commission,
                negotiated_price,
                None,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def create_detected_deal(
    product_id,
    price,
    source,
    average_price,
    discount_pct,
    score,
    duplicate_window_hours=24,
):
    saving = round(max(float(average_price) - float(price), 0.0), 2)
    original_price = float(average_price)
    negotiated_price = float(price)
    recent_window = f"-{int(duplicate_window_hours)} hours"

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id
            FROM deals
            WHERE is_auto_detected = 1
              AND product_id = ?
              AND COALESCE(detected_at, created_at) >= DATETIME('now', ?)
            """,
            (product_id, recent_window),
        )
        existing = cursor.fetchone()
        if existing:
            return None

        cursor.execute(
            """
            INSERT INTO deals (
                user_id,
                product_id,
                original_price,
                negotiated_price,
                saving,
                commission,
                price,
                detected_at,
                source,
                average_price,
                discount_pct,
                score,
                is_auto_detected
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, 1)
            """,
            (
                0,
                product_id,
                original_price,
                negotiated_price,
                saving,
                0.0,
                float(price),
                source,
                float(average_price),
                float(discount_pct),
                float(score),
            ),
        )
        conn.commit()
        return cursor.lastrowid


def create_detected_deals(deals, duplicate_window_hours=24):
    if not deals:
        return []

    inserted_deals = []
    for deal in deals:
        deal_id = create_detected_deal(
            product_id=deal["product_id"],
            price=deal["price"],
            source=deal["source"],
            average_price=deal["average_price"],
            discount_pct=deal["discount_pct"],
            score=deal["score"],
            duplicate_window_hours=duplicate_window_hours,
        )
        if deal_id is not None:
            inserted_deals.append({**deal, "deal_id": deal_id})
    return inserted_deals


def get_all_deals():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, product_id, user_id, original_price, negotiated_price, saving, commission, created_at
            FROM deals
            WHERE is_auto_detected = 0
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


def get_detected_deals():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                id,
                product_id,
                price,
                source,
                average_price,
                discount_pct,
                score,
                detected_at
            FROM deals
            WHERE is_auto_detected = 1
            ORDER BY detected_at DESC, id DESC
            """
        )
        return cursor.fetchall()


def get_detected_deals_for_date(target_date=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        if target_date is None:
            date_expression = "DATE('now', 'localtime')"
            params = ()
        else:
            date_expression = "DATE(?)"
            params = (target_date,)

        cursor.execute(
            f"""
            SELECT
                d.id,
                d.product_id,
                p.name,
                d.price,
                d.source,
                d.score,
                p.url,
                d.detected_at
            FROM deals d
            JOIN products p ON p.id = d.product_id
            WHERE d.is_auto_detected = 1
              AND DATE(COALESCE(d.detected_at, d.created_at), 'localtime') = {date_expression}
            ORDER BY d.score DESC, d.detected_at DESC, d.id DESC
            """,
            params,
        )
        return cursor.fetchall()


def has_notification_been_sent(notification_type, sent_for_date):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM notification_logs
            WHERE notification_type = ? AND sent_for_date = ?
            LIMIT 1
            """,
            (notification_type, sent_for_date),
        )
        return cursor.fetchone() is not None


def mark_notification_sent(notification_type, sent_for_date):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO notification_logs (notification_type, sent_for_date)
            VALUES (?, ?)
            """,
            (notification_type, sent_for_date),
        )
        conn.commit()
        return cursor.rowcount


def has_alert_notification_been_sent(user_id, alert_id, product_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT 1
            FROM alert_notification_logs
            WHERE user_id = ? AND alert_id = ? AND product_id = ?
            LIMIT 1
            """,
            (int(user_id), int(alert_id), int(product_id)),
        )
        return cursor.fetchone() is not None


def mark_alert_notification_sent(user_id, alert_id, product_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO alert_notification_logs (user_id, alert_id, product_id)
            VALUES (?, ?, ?)
            """,
            (int(user_id), int(alert_id), int(product_id)),
        )
        conn.commit()
        return cursor.rowcount


def get_last_notification_time(recipient_key):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT last_sent_at
            FROM notification_delivery_state
            WHERE recipient_key = ?
            """,
            (str(recipient_key),),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def update_last_notification_time(recipient_key):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO notification_delivery_state (recipient_key, last_sent_at, updated_at)
            VALUES (?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON CONFLICT(recipient_key) DO UPDATE SET
                last_sent_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            """,
            (str(recipient_key),),
        )
        conn.commit()
        return cursor.rowcount


def get_notification_setting(key):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT value
            FROM notification_settings
            WHERE key = ?
            """,
            (str(key),),
        )
        row = cursor.fetchone()
        return row[0] if row else None


def set_notification_setting(key, value):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO notification_settings (key, value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = CURRENT_TIMESTAMP
            """,
            (str(key), None if value is None else str(value)),
        )
        conn.commit()
        return cursor.rowcount


def get_admin_analytics():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM deals WHERE is_auto_detected = 0")
        total_deals = cursor.fetchone()[0]
        cursor.execute(
            "SELECT COALESCE(SUM(commission), 0) FROM deals WHERE is_auto_detected = 0"
        )
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


def get_user_alert_by_query(user_id, query):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, query, target_price, created_at
            FROM alerts
            WHERE user_id = ? AND query = ?
            LIMIT 1
            """,
            (user_id, query),
        )
        return cursor.fetchone()


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


def delete_all_alerts_for_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM alerts
            WHERE user_id = ?
            """,
            (int(user_id),),
        )
        conn.commit()
        return cursor.rowcount


def clear_alert_notification_logs_for_user(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM alert_notification_logs
            WHERE user_id = ?
            """,
            (int(user_id),),
        )
        conn.commit()
        return cursor.rowcount


def clear_notification_delivery_state(recipient_key):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            DELETE FROM notification_delivery_state
            WHERE recipient_key = ?
            """,
            (str(recipient_key),),
        )
        conn.commit()
        return cursor.rowcount


def update_alert_target_price(alert_id, user_id, target_price):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE alerts
            SET target_price = ?
            WHERE id = ? AND user_id = ?
            """,
            (target_price, alert_id, user_id),
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


def log_telegram_interaction(user_id, telegram_chat_id, interaction_type, query=None, raw_text=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO telegram_interactions (
                user_id,
                telegram_chat_id,
                interaction_type,
                query,
                raw_text
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                int(user_id),
                str(telegram_chat_id),
                interaction_type,
                query,
                raw_text,
            ),
        )
        conn.commit()
        return cursor.lastrowid


def get_all_telegram_users():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, username, telegram_chat_id, role, created_at
            FROM users
            WHERE telegram_chat_id IS NOT NULL
            ORDER BY created_at DESC
            """
        )
        return cursor.fetchall()


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


def get_recent_user_searches(user_id, limit=10):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT query
            FROM user_preferences
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (user_id, int(limit)),
        )
        return [row[0] for row in cursor.fetchall()]


def get_recent_user_interactions(user_id, limit=10):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT interaction_type, query, raw_text, created_at
            FROM telegram_interactions
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (user_id, int(limit)),
        )
        return cursor.fetchall()


def get_user_behavior(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT
                id,
                user_id,
                product_category,
                average_discount_preference,
                deals_completed,
                clicks,
                last_updated,
                excluded_category
            FROM user_behavior
            WHERE user_id = ?
            """,
            (user_id,),
        )
        return cursor.fetchone()


def update_user_behavior_click(user_id, product_category=None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO user_behavior (user_id, product_category, clicks, last_updated)
            VALUES (?, ?, 1, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                clicks = clicks + 1,
                product_category = COALESCE(excluded.product_category, product_category),
                last_updated = CURRENT_TIMESTAMP
            """,
            (user_id, product_category),
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


def update_user_behavior_feedback(user_id, product_category=None, liked=True):
    with get_connection() as conn:
        cursor = conn.cursor()
        if liked:
            cursor.execute(
                """
                INSERT INTO user_behavior (
                    user_id,
                    product_category,
                    excluded_category,
                    clicks,
                    last_updated
                )
                VALUES (?, ?, NULL, 1, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    product_category = COALESCE(excluded.product_category, product_category),
                    clicks = clicks + 1,
                    last_updated = CURRENT_TIMESTAMP
                """,
                (user_id, product_category),
            )
        else:
            cursor.execute(
                """
                INSERT INTO user_behavior (
                    user_id,
                    product_category,
                    excluded_category,
                    clicks,
                    last_updated
                )
                VALUES (?, NULL, ?, 0, CURRENT_TIMESTAMP)
                ON CONFLICT(user_id) DO UPDATE SET
                    excluded_category = COALESCE(excluded.excluded_category, excluded_category),
                    last_updated = CURRENT_TIMESTAMP
                """,
                (user_id, product_category),
            )
        conn.commit()
        return cursor.rowcount
