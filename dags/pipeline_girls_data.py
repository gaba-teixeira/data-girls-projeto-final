from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# 1. Definição dos argumentos padrão para todas as tasks
default_args = {
    'owner': 'data_engineering_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1), 
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,                        
    'retry_delay': timedelta(minutes=2), 
}

# 2. Instanciação da DAG
with DAG(
    dag_id='pipeline_projeto_final',
    default_args=default_args,
    description='Pipeline de ETL que extrai dados do Kaggle e processa nas camadas Bronze, Silver e Gold no S3.',
    schedule_interval='@hourly',             
    catchup=False,                      
    tags=['kaggle', 's3', 'gold'],      
) as dag:

    # 3. Definição das Tasks (Tarefas)
    
    task_extract_kaggle = BashOperator(
        task_id='extract_kaggle',
        bash_command='python /opt/airflow/scripts/extract-kaggle.py',
    )

    task_upload_bronze = BashOperator(
        task_id='upload_bronze',
        bash_command='python /opt/airflow/scripts/upload-bronze.py',
    )

    task_process_silver = BashOperator(
        task_id='process_silver',
        bash_command='python /opt/airflow/scripts/process-silver.py',
    )

    task_process_gold = BashOperator(
        task_id='process_gold',
        bash_command='python /opt/airflow/scripts/process-gold.py',
    )

    # 4. Definição do fluxo de dependências (Pipeline)
    task_extract_kaggle >> task_upload_bronze >> task_process_silver >> task_process_gold