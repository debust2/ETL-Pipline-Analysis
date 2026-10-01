import pandas as pd
import s3fs

s3_config = {
    "key":"my_user_name",
    "secret":"my_password",
    "client_kwargs":{"endpoint_url": "http://localhost:9000"}
}

s3_url = "s3://data/users.json"


df = pd.read_json(s3_url, storage_options=s3_config)

print(df.head(5))








