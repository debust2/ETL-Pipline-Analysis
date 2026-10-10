from generation_data import(create_customers_data, create_orders_data, 
                            create_events_data, create_products_data, create_returns_data)
from s3_utils import(get_s3_client, write_data_s3_json, write_s3_parquet, write_s3_csv, bucket_creation_check, download_file)

bucket_name = "data"
customers_key = "customers.json"
orders_key = "orders.json"
products_key = "products.parquet"
events_key = "events.parquet"
returns_key = "returns.csv"
filename = "../files/customers.json"

if __name__ == "__main__":
    s3_connection = get_s3_client()
    bucket_creation_check(s3_connection, bucket_name)

    #---------- create_data
    customers = create_customers_data(150)
    products = create_products_data(150)
    orders = create_orders_data(customers, products, 150)
    events = create_events_data(customers, products, 150)
    returns = create_returns_data(orders)

    #-------------- wtire data to files (json, parquet, csv)
    write_data_s3_json(s3_connection, bucket_name, customers, customers_key)
    write_data_s3_json(s3_connection, bucket_name, orders, orders_key)
    write_s3_parquet(s3_connection, bucket_name, products, products_key)
    write_s3_parquet(s3_connection, bucket_name, events, events_key)
    write_s3_csv(s3_connection, bucket_name, returns, returns_key)

    #-----download data to directory
    download_file(s3_connection, bucket_name, customers_key, filename)