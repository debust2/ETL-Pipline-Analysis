import random
from datetime import *
from faker import Faker

fake = Faker()

PRODUCT_TYPES = {
    "Electronics": ["Headphones", "Charger", "Smartwatch", "Speaker", "Webcam"],
    "Home": ["Lamp", "Blanket", "Coffee Maker", "Vase", "Cutting Board"],
    "Sport": ["Yoga Mat", "Dumbbells", "Water Bottle", "Running Belt", "Jump Rope"],
    "Books": ["Notebook", "Planner", "Cookbook", "Sketchbook"],
    "Beauty": ["Face Cream", "Shampoo", "Perfume", "Lip Balm"],
    "Toys": ["Puzzle", "Board Game", "Building Set", "Plush Toy"],
}

EVENT_TYPES = ["page_view", "product_view", "add_to_cart", "checkout_start", "purchase"]

#creating data
def create_users_data(count: int) -> list[dict]:
    user = [{"user_id": i, 
             "full_name":fake.name(), 
             "email": fake.email(), 
             "country": fake.country(),
             "city": fake.city(), 
             "birth_date": fake.date_of_birth(minimum_age = 18, maximum_age = 65),
             "registration_date": fake.date_time_between("-2y", "now"),
             "marketing_consent": random.random() < 0.6,
    } for i in range(1, count + 1)]
    return user

def create_orders_data(users: list[dict], products: list[dict], count: int) -> list[dict]:
    orders = []
    for i in range(1, count + 1):
        status = random.choice(["completed", "completed", "completed", "pending", "cancelled"])
        items = [{
            "product_id": p["product_id"],
            "qty": random.randint(1, 3),
            "unit_price": p["price"],
            "discount": random.choice([0.0, 0.0, 0.05, 0.1, 0.2]),
        } for p in random.sample(products, k=random.randint(1, 4))]
        orders.append({
            "order_id": i,
            "user_id": random.choice(users)["user_id"],
            "order_ts": fake.date_time_between("-1y", "now").isoformat(),
            "status": status,
            "payment": {
                "method": random.choice(["card", "paypal", "bank_transfer"]),
                "currency": "EUR",
                "paid": status == "completed",
            },
            "shipping": {
                "method": random.choice(["courier", "pickup", "post"]),
                "cost": random.choice([0.0, 3.9, 4.9, 9.9]),
                "address": {
                    "country": fake.country(),
                    "city": fake.city(),
                    "postal_code": fake.postcode(),
                },
            },
            "items": items,
        })
    return orders

def create_products_data(count: int) -> list[dict]:
    products = []
    for i in range(1, count + 1):
        category = random.choice(list(PRODUCT_TYPES))
        price = round(random.uniform(5.0, 300.0), 2)
        products.append({
            "product_id": i,
            "product_name": f"{fake.color_name()} {random.choice(PRODUCT_TYPES[category])}",
            "category": category,
            "brand": fake.company(),
            "price": price,
            "cost": round(price * random.uniform(0.4, 0.8), 2),   
            "is_active": random.random() < 0.9,                    
            "created_at": fake.date_time_between("-3y", "-1y"),
        })
    return products

def create_events_data(users: list[dict], products: list[dict], count: int) -> list[dict]:
    events = []
    for i in range(1, count + 1):
        event_type = random.choices(EVENT_TYPES, weights=[50, 25, 12, 8, 5])[0]
        is_guest = random.random() < 0.15
        events.append({
            "event_id": f"e-{i:06d}",
            "user_id": None if is_guest else random.choice(users)["user_id"],
            "product_id": None if event_type == "page_view" else random.choice(products)["product_id"],
            "session_id": f"s-{random.randint(1, max(count // 5, 1)):05d}",
            "event_type": event_type,
            "event_ts": fake.date_time_between("-1y", "now").isoformat(),
            "properties": {
                "device": random.choice(["mobile", "desktop", "tablet"]),
                "utm_source": random.choice(["google", "facebook", "email", "direct"]),
            },
        })
    return events

def create_returns_data(orders: list[dict]) -> list[dict]:
    returns = []
    sampled = random.sample(orders, k=int(len(orders) * 0.08))
    for n, order in enumerate(sampled, start=1):
        item = random.choice(order["items"])
        order_ts = datetime.fromisoformat(order["order_ts"])
        returns.append({
            "return_id": n,
            "order_id": order["order_id"],
            "product_id": item["product_id"],
            "reason": random.choice(["damaged", "wrong_size", "not_as_described", "changed_mind"]),
            "refund_amount": round(item["unit_price"] * item["qty"] * (1 - item["discount"]), 2),
            "return_date": (order_ts + timedelta(days=random.randint(1, 30))).date().isoformat(),
        })
    return returns



