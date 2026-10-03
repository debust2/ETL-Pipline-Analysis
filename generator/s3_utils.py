import json, os
import boto3
import pandas as pd
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from io import BytesIO

load_dotenv()

#enviroments
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD")
MINIO_ENDPOINT_URL = os.getenv("MINIO_ENDPOINT_URL")


def get_s3_client():
    s3_client = boto3.client("s3",
                             aws_access_key_id = MINIO_ROOT_USER,
                             aws_secret_access_key = MINIO_ROOT_PASSWORD,
                             endpoint_url = MINIO_ENDPOINT_URL)
    return s3_client


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


def write_data_s3_json(s3_client, bucket_name: str, data: list[dict], file_key: str):
        json_string = json.dumps(data, indent = 4, ensure_ascii = False, default=str)
        s3_client.put_object(Bucket = bucket_name,
                             Key = file_key,
                             Body = json_string.encode("utf-8"), #преобразовываем данные в формат utf-8, так как метод не принимает текст
                             ContentType = "application/json")

def write_s3_parquet(s3_client, bucket_name: str, data: list[dict], key_name: str):
    stream = BytesIO()

    df = pd.DataFrame(data)
    df.to_parquet(stream, index=False, engine="pyarrow")

    stream.seek(0)
    s3_client.upload_fileobj(
        Fileobj = stream, #file in our stream
        Bucket = bucket_name,
        Key = key_name
    )

def write_s3_csv(s3_client, bucket_name:str, data: list[dict], key_name: str):
     df = pd.DataFrame(data).to_csv(index=False)
     s3_client.put_object(Bucket = bucket_name,
                          Key = key_name,
                          Body = df.encode("utf-8"),
                          ContentType = "text/csv")