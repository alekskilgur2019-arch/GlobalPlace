import random
import sqlite3
import database

def seed_products(n=100):
    # Убеждаемся, что база данных инициализирована
    database.init_db()

    # Сначала удаляем старые тестовые данные, чтобы не было дублирования
    with database.get_connection() as conn:
        cursor = conn.cursor()
        # Ищем тестовых продавцов, чтобы удалить их и их товары
        cursor.execute("SELECT id FROM users WHERE username LIKE 'seed_seller_%'")
        existing_sellers = [row[0] for row in cursor.fetchall()]
        
        if existing_sellers:
            placeholders = ','.join('?' for _ in existing_sellers)
            cursor.execute(f"DELETE FROM products WHERE user_id IN ({placeholders})", existing_sellers)
            cursor.execute(f"DELETE FROM users WHERE id IN ({placeholders})", existing_sellers)
        conn.commit()

    # Создаем 5 различных продавцов
    seller_ids = []
    with database.get_connection() as conn:
        cursor = conn.cursor()
        for i in range(1, 6):
            cursor.execute(
                """
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
                """,
                (f"seed_seller_{i}", "hashed_fake_pass", "seller")
            )
            seller_ids.append(cursor.lastrowid)
        conn.commit()

    categories = {
        "electronics": ["Smart Home Hub", "4K TV", "Digital Camera", "VR Headset", "Smartwatch"],
        "phones": ["iPhone 13", "iPhone 14 Pro", "Samsung Galaxy S22", "Google Pixel 6", "OnePlus 9"],
        "headphones": ["AirPods Pro", "Sony WH-1000XM4", "Bose QuietComfort", "Sennheiser Momentum", "Jabra Elite"],
        "laptops": ["MacBook Air", "MacBook Pro 14", "Dell XPS 13", "Lenovo ThinkPad", "HP Spectre"]
    }
    sources = ["eBay", "Amazon", "Willhaben"]

    products_to_insert = []
    for i in range(n):
        category = random.choice(list(categories.keys()))
        # Название (title)
        model = random.choice(categories[category])
        name = f"{model} (Condition: {random.choice(['New', 'Like New', 'Good'])})"
        
        # Цена от 20 до 1000 EUR
        price = round(random.uniform(20.0, 1000.0), 2)
        
        # URL картинки
        keyword = model.lower().split()[0]
        if category == "electronics":
            keyword = "electronic"
        elif category == "headphones":
            keyword = "headphones"
            if "airpods" in model.lower():
                keyword = "airpods"
        elif category == "phones":
            if "iphone" in model.lower():
                keyword = "iphone"
            else:
                keyword = "smartphone"
        elif category == "laptops":
            keyword = "laptop"
            
        image_url = f"https://source.unsplash.com/featured/?{keyword}"
        product_url = f"https://example.com/item/{random.randint(10000, 99999)}"
        
        # Источник (source)
        source = random.choice(sources)
        
        # Продавец (seller_id)
        seller_id = random.choice(seller_ids)

        # Описание (description) не добавляем в БД, так как в текущей схеме таблицы `products`
        # в database.py нет столбца `description`, но мы генерируем структуру согласно модели.
        description = f"Great {model} in {category} category from {source}."

        products_to_insert.append({
            "name": name,
            "price": price,
            "url": product_url,
            "source": source,
            "image": image_url,
            "user_id": seller_id
        })

    # Используем существующую функцию добавления товаров
    inserted_count = database.insert_products(products_to_insert)
    
    print(f"Seeded {inserted_count} products.")

if __name__ == "__main__":
    seed_products(100)
