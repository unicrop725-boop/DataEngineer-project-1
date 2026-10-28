import os
from datetime import datetime, timedelta

import pandas as pd
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

SOURCE_TABLES = [
    "customers", "sellers", "products",
    "orders", "order_items", "order_payments",
]
BRONZE_PATH = "/opt/airflow/lake/bronze/olist_source"


def get_source_engine():
    """Build a DB engine from the Airflow connection (our 'Linked Service')."""
    conn = BaseHook.get_connection("olist_source")
    url = URL.create(
        drivername="mssql+pymssql",
        username=conn.login,
        password=conn.password,
        host=conn.host,
        port=conn.port,
        database=conn.schema,
    )
    return create_engine(url)


@dag(
    dag_id="ingest_source_to_bronze",
    description="Copy source SQL tables to the bronze layer as Parquet",
    start_date=datetime(2026, 10, 1),
    schedule=None,              # manual for now; we add a schedule on Day 4
    catchup=False,
    tags=["ingestion", "bronze"],
    default_args={"retries": 2, "retry_delay": timedelta(minutes=1)},
)
def ingest_source_to_bronze():

    @task
    def copy_table_to_bronze(table_name: str, ds=None) -> dict:
        """Parameterized copy activity: works for ANY table name."""
        engine = get_source_engine()
        df = pd.read_sql(f"SELECT * FROM dbo.{table_name}", engine)

        # Ingestion metadata columns (standard practice in bronze)
        df["_ingested_at"] = pd.Timestamp.now(tz="UTC")
        df["_source_system"] = "olist_source"

        # Partition folder by load date, like ADLS: table/load_date=YYYY-MM-DD/
        out_dir = os.path.join(BRONZE_PATH, table_name, f"load_date={ds}")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"{table_name}.parquet")
        df.to_parquet(out_file, index=False)

        print(f"{table_name}: {len(df):,} rows -> {out_file}")
        return {"table": table_name, "rows": len(df)}

    @task
    def log_summary(results: list):
        total = 0
        for r in results:
            print(f"{r['table']:<16} {r['rows']:>8,} rows")
            total += r["rows"]
        print(f"TOTAL            {total:>8,} rows copied to bronze")

    # ForEach: one copy task per table, created dynamically
    results = copy_table_to_bronze.expand(table_name=SOURCE_TABLES)
    log_summary(results)


ingest_source_to_bronze()