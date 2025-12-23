from datetime import datetime, timedelta
from airflow.decorators import dag, task

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@dag(
    dag_id='simple_etl_sample',
    default_args=default_args,
    description='A small sample ETL DAG',
    schedule_interval=None,  # Set to '@daily' for automatic runs
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['example'],
)
def simple_etl():

    @task()
    def extract():
        """Simulate extracting data."""
        return {"data": [10, 20, 30]}

    @task()
    def transform(raw_data: dict):
        """Simulate transforming data (doubling values)."""
        transformed_data = [x * 2 for x in raw_data["data"]]
        return transformed_data

    @task()
    def load(processed_data: list):
        """Simulate loading data into a destination."""
        print(f"Loading data to destination: {processed_data}")

    # Set dependencies by calling the tasks
    data = extract()
    transformed = transform(data)
    load(transformed)

# Instantiate the DAG
sample_dag = simple_etl()
