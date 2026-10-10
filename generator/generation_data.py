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
def create_customers_data(count: int) -> list[dict]:
    user = [{"customer_id": i, 
             "full_name":fake.name(), 
             "email": fake.email(), 
             "phone": fake.phone_number(),
             "city": fake.city(), 
             "birthdate": fake.date_of_birth(minimum_age = 18, maximum_age = 65),
             "created_at": fake.date_time_between("-2y", "now"),
    } for i in range(1, count + 1)]
    return user


def create_orders_data(customers: list[dict], products: list[dict], count: int) -> list[dict]:
    # заказы делают только 60% клиентов, остальные просто зарегистрированы
    buyers = random.sample(customers, k=int(len(customers) * 0.6))
    shipping_costs = {"courier": 4.9, "post": 3.9, "pickup": 0.0}

    orders = []
    for i in range(1, count + 1):
        customer = random.choice(buyers)
        order_date = fake.date_time_between(customer["created_at"], "now")   # не раньше регистрации
        status = random.choice(["completed", "completed", "completed", "pending", "cancelled"])
        shipping_method = random.choice(list(shipping_costs))

        # позиции заказа: от 1 до 4 разных товаров
        items = []
        for product in random.sample(products, k=random.randint(1, 4)):
            quantity = random.randint(1, 3)
            items.append({
                "product_id": product["product_id"],
                "quantity": quantity,
                "price": product["price"],
                "sales_amount": round(quantity * product["price"], 2),
            })

        orders.append({
            "order_id": i,
            "customer_id": customer["customer_id"],
            "order_date": order_date.isoformat(),
            "status": status,
            "shipping_date": (order_date + timedelta(days=random.randint(1, 3))).isoformat()
                             if status == "completed" else None,
            "due_date": (order_date + timedelta(days=random.randint(3, 7))).date().isoformat(),
            "payment_method": random.choice(["card", "paypal", "bank_transfer"]),
            "is_paid": status == "completed",
            "shipping_method": shipping_method,
            "shipping_cost": shipping_costs[shipping_method],
            "shipping_city": customer["city"],
            "items": items,
        })
    return orders



def create_products_data(count: int) -> list[dict]:
    products = []
    for i in range(1, count + 1):
        category = random.choice(list(PRODUCT_TYPES))
        product_type = random.choice(PRODUCT_TYPES[category])
        price = round(random.uniform(5.0, 300.0), 2)
        start_date = fake.date_between("-3y", "-1y")
        discontinued = random.random() < 0.1        # примерно 10% сняты с продажи

        products.append({
            "product_id": i,
            "product_name": f"{product_type} - {fake.color_name()}",
            "model_code": f"{product_type[:4].upper()}-{random.randint(1, 5)}",
            "category": category,
            "price": price,
            "cost": round(price * random.uniform(0.4, 0.8), 2),
            "start_date": start_date,
            "end_date": fake.date_between(start_date, "today") if discontinued else None,
        })
    return products


def create_events_data(customers: list[dict], products: list[dict], count: int) -> list[dict]:
    events = []
    for i in range(1, count + 1):
        event_type = random.choices(
            ["page_view", "product_view", "add_to_cart", "checkout_start", "purchase"],
            weights=[50, 25, 12, 8, 5],          # просмотров много, покупок мало
        )[0]
        is_guest = random.random() < 0.15        # 15% посетителей без аккаунта
        has_product = event_type in ("product_view", "add_to_cart")

        events.append({
            "event_id": f"e-{i:07d}",
            "customer_id": None if is_guest else random.choice(customers)["customer_id"],
            "product_id": random.choice(products)["product_id"] if has_product else None,
            "session_id": f"s-{random.randint(1, max(count // 5, 1)):06d}",
            "event_type": event_type,
            "event_time": fake.date_time_between("-1y", "now").isoformat(),
            "device": random.choice(["mobile", "desktop", "tablet"]),
            "utm_source": random.choice(["google", "facebook", "email", "direct"]),
        })
    return events


def create_returns_data(orders: list[dict]) -> list[dict]:
    completed = [o for o in orders if o["status"] == "completed"]
    sampled = random.sample(completed, k=int(len(completed) * 0.08))   # возвращают ~8% заказов

    returns = []
    for n, order in enumerate(sampled, start=1):
        item = random.choice(order["items"])                # возвращают одну позицию из заказа
        shipped = datetime.fromisoformat(order["shipping_date"])
        return_date = min(shipped + timedelta(days=random.randint(1, 30)), datetime.now())

        returns.append({
            "return_id": n,
            "order_id": order["order_id"],
            "product_id": item["product_id"],
            "return_date": return_date.date().isoformat(),
            "reason": random.choice(["damaged", "wrong_size", "not_as_described", "changed_mind"]),
            "refund_amount": item["sales_amount"],
        })
    return returns


