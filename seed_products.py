from database import init_db, insert_products_if_missing


QA_PRODUCTS = [
    {
        "name": "AirPods Pro 2nd Gen",
        "price": 219.0,
        "url": "https://qa.globalplace.local/audio/airpods-pro-2",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "Sony WH-1000XM5",
        "price": 289.0,
        "url": "https://qa.globalplace.local/audio/sony-wh-1000xm5",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "Bose QuietComfort 45",
        "price": 199.0,
        "url": "https://qa.globalplace.local/audio/bose-quietcomfort-45",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "JBL Tune 510BT",
        "price": 39.0,
        "url": "https://qa.globalplace.local/audio/jbl-tune-510bt",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "iPhone 13 128GB",
        "price": 499.0,
        "url": "https://qa.globalplace.local/phones/iphone-13-128gb",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "Samsung Galaxy S21",
        "price": 349.0,
        "url": "https://qa.globalplace.local/phones/samsung-galaxy-s21",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "Google Pixel 7",
        "price": 379.0,
        "url": "https://qa.globalplace.local/phones/google-pixel-7",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "Xiaomi Redmi Note 11",
        "price": 179.0,
        "url": "https://qa.globalplace.local/phones/xiaomi-redmi-note-11",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "MacBook Air M1",
        "price": 799.0,
        "url": "https://qa.globalplace.local/laptops/macbook-air-m1",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "Dell XPS 13",
        "price": 949.0,
        "url": "https://qa.globalplace.local/laptops/dell-xps-13",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "Lenovo ThinkPad X1 Carbon",
        "price": 1099.0,
        "url": "https://qa.globalplace.local/laptops/lenovo-thinkpad-x1-carbon",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "HP Pavilion 15",
        "price": 599.0,
        "url": "https://qa.globalplace.local/laptops/hp-pavilion-15",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "PlayStation 5 Console",
        "price": 499.0,
        "url": "https://qa.globalplace.local/gaming/playstation-5-console",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "Xbox Series X",
        "price": 469.0,
        "url": "https://qa.globalplace.local/gaming/xbox-series-x",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "Nintendo Switch OLED",
        "price": 299.0,
        "url": "https://qa.globalplace.local/gaming/nintendo-switch-oled",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "PS5 DualSense Controller",
        "price": 69.0,
        "url": "https://qa.globalplace.local/gaming/ps5-dualsense-controller",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "Dyson V11 Vacuum Cleaner",
        "price": 449.0,
        "url": "https://qa.globalplace.local/home/dyson-v11-vacuum-cleaner",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "Philips Coffee Machine 3200",
        "price": 329.0,
        "url": "https://qa.globalplace.local/home/philips-coffee-machine-3200",
        "source": "willhaben",
        "image": "",
    },
    {
        "name": "iRobot Roomba i7",
        "price": 389.0,
        "url": "https://qa.globalplace.local/home/irobot-roomba-i7",
        "source": "ebay",
        "image": "",
    },
    {
        "name": "Air Fryer Philips Essential",
        "price": 129.0,
        "url": "https://qa.globalplace.local/home/air-fryer-philips-essential",
        "source": "willhaben",
        "image": "",
    },
]


def main():
    init_db()
    inserted_count = insert_products_if_missing(QA_PRODUCTS)
    print(f"Inserted QA products: {inserted_count}")
    print(f"Total QA products in seed list: {len(QA_PRODUCTS)}")


if __name__ == "__main__":
    main()
