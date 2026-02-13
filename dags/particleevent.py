from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator

# 1. Define the logic for your tasks
def transform_data():
    print("Transforming data from source to destination...")
    return "Data transformation complete!"

# 2. Define the DAG
with DAG(
    dag_id='sample_etl_workflow',
    description='A simple starter DAG for ETL',
    schedule_interval=timedelta(days=1),  # Runs daily
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['example', 'basic'],
) as dag:

    # 3. Define Tasks
    start_node = EmptyOperator(task_id='start')

    extract_task = EmptyOperator(task_id='extract_data')

    transform_task = PythonOperator(
        task_id='transform_data',
        python_callable=transform_data
    )

    load_task = EmptyOperator(task_id='load_data')

    end_node = EmptyOperator(task_id='end')

    # 4. Define Dependencies (The Flow)
    start_node >> extract_task >> transform_task >> load_task >> end_node
