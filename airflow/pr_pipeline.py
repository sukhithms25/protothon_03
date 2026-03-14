from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

dag = DAG(
    "ai_pr_pipeline",
    start_date=datetime(2024,1,1),
    schedule_interval=None
)

task1 = PythonOperator(
    task_id="issue_reader",
    python_callable=process_issue,
    dag=dag
)