from faker import Faker
import random
from dotenv import load_dotenv
import os
import boto3 
import json
from botocore.exceptions import ClientError

load_dotenv()

#enviroments
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL")

fake = Faker()

users_key = "users.json"
orders_key = "orders.json"
bucket_name = "datatest"


def get_s3_client():
    s3_config = boto3.client("s3",
                             aws_access_key_id = MINIO_ROOT_USER,
                             aws_secret_access_key = MINIO_ROOT_PASSWORD,
                             endpoint_url = MINIO_ENDPOINT_URL)
    return s3_config


def bucket_creation_check(s3_client, bucket: str) -> None:
    try:
        s3_client.head_bucket(Bucket=bucket)
        print(f"The bucket '{bucket}' already exists.")
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code")
        if error_code in ("404", "NoSuchBucket"):
            s3_client.create_bucket(Bucket=bucket)
            print(f"The bucket '{bucket}' was successfully created.")
        else:
            raise e


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
def write_data_s3_json(s3_client, bucket_name: str, data: list[dict], file_key: str) -> bool:
    try:
        json_string = json.dumps(data, indent = 4, ensure_ascii = False, default=str)
        s3_client.put_object(Bucket = bucket_name,
                             Key = file_key,
                             Body = json_string.encode("utf-8"), #преобразовываем данные в формат utf-8, так как метод не принимает текст
                             ContentType = "application/json")
        print(f"Данные успешно загружены в файл {file_key}")
        return True
    except Exception as e:
        print(f"Произошла ошибка {e} при записи данных в файл: {file_key}")
        return False


if __name__ == "__main__":
    s3_connection = get_s3_client()
    #create and check bucket exist
    bucket_creation_check(s3_connection, bucket_name)
    users = create_users_data(150)
    orders = create_order_data(150)
    write_data_s3_json(s3_connection, bucket_name, users, users_key)
    write_data_s3_json(s3_connection, bucket_name, orders, orders_key)
