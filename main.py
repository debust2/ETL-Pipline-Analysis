from faker import Faker
import pandas as pd
import random
import s3fs
from dotenv import load_dotenv
import os

load_dotenv()

log = os.getenv("MINIO_ROOT_USER")
password = os.getenv("MINIO_ROOT_PASSWORD")
host = os.getenv("MINIO_ENDPOINT_URL")

fake = Faker()
s3_config ={
    "key": log,
    "secret":password,
    "client_kwargs":{"endpoint_url":host}
}
users_url = 's3://data/users.json'
orders_url = 's3://data/orders.json'

#creating data
def create_users_data(count: int) -> pd.DataFrame:
    user = [{"user_id": i, "user_name":fake.name(), "user_email": fake.email(), "user_address": fake.address(),
             "user_date_of_birthday": fake.date_of_birth(minimum_age = 18, maximum_age = 65)} for i in range(1, count + 1)]
    return pd.DataFrame(user)

def create_order_data(count: int) -> pd.DataFrame:
    orders = [{
            "order_id": i,
            "customer_name": fake.name(),
            "customer_email": fake.email(),
            "product_name": fake.word().capitalize() + " " + fake.word(),
            "quantity": random.randint(1, 5),
            "price": round(random.uniform(10.0, 500.0), 2),
            "order_date": fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S"),
            "status": random.choice(["Completed", "Pending", "Cancelled"])} for i in range(1, count + 1)]
    return pd.DataFrame(orders)


#write data to json file
def write_data_s3_json(name: str, data: pd.DataFrame, options: dict) -> bool:
    try:
        data.to_json(name, orient="records", indent = 4, date_format="iso", force_ascii = False, 
                     storage_options = options)
        print(f"Данные успешно загружены в файл {name}")
        return True
    except Exception as e:
        print(f"Произошла ошибка {e} при записи данных в файл: {name}")
        return False



if __name__ == "__main__":
    user_df = create_users_data(150)
    orders_df = create_order_data(150)
    write_data_s3_json(users_url, user_df, s3_config)
    write_data_s3_json(orders_url, orders_df, s3_config)