import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Build the connection safely (handles special characters like @ in passwords)
connection_url = URL.create(
    drivername="mssql+pymssql",
    username="sa",
    password=os.environ["SQL_PASSWORD"],
    host="sqlserver",
    port=1433,
    database="olist_source",
)
engine = create_engine(connection_url)

SOURCE_DIR = "/home/jovyan/data/source"

# csv file -> (table name, datetime columns)
TABLES = {
    "olist_customers_dataset.csv": ("customers", []),
    "olist_sellers_dataset.csv": ("sellers", []),
    "olist_products_dataset.csv": ("products", []),
    "olist_orders_dataset.csv": ("orders", [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date"]),
    "olist_order_items_dataset.csv": ("order_items", ["shipping_limit_date"]),
    "olist_order_payments_dataset.csv": ("order_payments", []),
}

for file_name, (table, date_cols) in TABLES.items():
    df = pd.read_csv(
        os.path.join(SOURCE_DIR, file_name),
        dtype={"customer_zip_code_prefix": str, "seller_zip_code_prefix": str},
        parse_dates=date_cols,
    )
    with engine.begin() as conn:
        conn.execute(text(f"TRUNCATE TABLE dbo.{table}"))   # makes the script re-runnable
    df.to_sql(table, engine, schema="dbo", if_exists="append",
              index=False, chunksize=1000)
    print(f"Loaded {len(df):>7,} rows -> dbo.{table}")

print("Source database ready.")