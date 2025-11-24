from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    "owner": "skander",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="crypto_reddit_pipeline",
    default_args=default_args,
    schedule_interval="* * * * *",  # toutes les 1 minute
    start_date=days_ago(0),
    catchup=False,
) as dag:

    # Lancer le collector CoinGecko
    run_coingecko = BashOperator(
        task_id="run_coingecko",
        bash_command="docker-compose run --rm coingecko_collector"
    )

    # Lancer le collector Reddit
    run_reddit = BashOperator(
        task_id="run_reddit",
        bash_command="docker-compose run --rm reddit_collector"
    )

    # Définir les dépendances (ex: Reddit attend CoinGecko)
    run_coingecko >> run_reddit
