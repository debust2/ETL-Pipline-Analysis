from faker import Faker
import random
from dotenv import load_dotenv
import os
import boto3 
import json

load_dotenv()

log = os.getenv("MINIO_ROOT_USER")
password = os.getenv("MINIO_ROOT_PASSWORD")
host = os.getenv("MINIO_ENDPOINT_URL")

fake = Faker()

users_key = "users.json"
orders_key = "orders.json"




#creating data
def create_users_data(count: int) -> list[dict]:
    user = [{"user_id": i, "user_name":fake.name(), "user_email": fake.email(), "user_address": fake.address(),
             "user_date_of_birthday": fake.date_of_birth(minimum_age = 18, maximum_age = 65)} for i in range(1, count + 1)]
    return user

def create_order_data(count: int) -> list[dict]:
    orders = [{
            "order_id": i,
            "customer_name": fake.name(),
            "customer_email": fake.email(),
            "product_name": fake.word().capitalize() + " " + fake.word(),
            "quantity": random.randint(1, 5),
            "price": round(random.uniform(10.0, 500.0), 2),
            "order_date": fake.date_time_this_year().strftime("%Y-%m-%d %H:%M:%S"),
            "status": random.choice(["Completed", "Pending", "Cancelled"])} for i in range(1, count + 1)]
    return orders


#write data to json file
def write_data_s3_json(bucket_name: str, data: list[dict], file_key: str) -> bool:
    try:
        #конфиг для подключения к Minio
        s3_config = boto3.client("s3",
                         aws_access_key_id = log,
                         aws_secret_access_key = password,
                         endpoint_url = host)

        #Check exsits bucket
        try:
            s3_config.head_bucket(Bucket=bucket_name)
            print(f"Бакет {bucket_name} уже существует")
        except Exception as e:
            s3_config.create_bucket(Bucket=bucket_name)
            print(f"Бакет {bucket_name} был создан")

        json_string = json.dumps(data, indent = 4, ensure_ascii = False, default=str)
        s3_config.put_object(Bucket = bucket_name,
                             Key = file_key,
                             Body = json_string.encode("utf-8"), #преобразовываем данные в формат utf-8, так как метод не принимает текст
                             ContentType = "application/json")
        print(f"Данные успешно загружены в файл {file_key}")
        return True
    except Exception as e:
        print(f"Произошла ошибка {e} при записи данных в файл: {file_key}")
        return False


if __name__ == "__main__":
    users = create_users_data(150)
    orders = create_order_data(150)
    write_data_s3_json("data", users, users_key)
    write_data_s3_json("data", orders, orders_key)
