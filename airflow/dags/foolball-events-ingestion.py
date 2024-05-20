from airflow import DAG
from airflow.operators.python import PythonOperator
from include.event_ingestion import ingest_events
from datetime import datetime, timedelta
from dateutil import tz

local_tz = tz.gettz("Asia/Jakarta")

EPL_ID = 152

default_args = {
    'owner': 'Kelompok 5',
    'depends_on_past': True,
    'email': ['kelompok5@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=1)
}

# Define the Python function
def ingest_periodically(league_id, **kwargs):
    start = kwargs["data_interval_start"].strftime("%Y-%m-%d")
    end = kwargs["data_interval_end"].strftime("%Y-%m-%d")

    ingest_events(league_id, start, end)

dag = DAG('epl-events-ingestion',
          catchup=True,
          schedule_interval='0 10 * * 1',
        #   schedule_interval=None,
          start_date=datetime(2023, 8, 7, tzinfo=local_tz),
          default_args=default_args)

ingestion_task = PythonOperator(
    task_id="ingestion_task",
    python_callable=ingest_periodically,
    op_args=[EPL_ID],
    provide_context=True,
    dag=dag
)