import duckdb
import os
import logging
from dotenv import load_dotenv

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def modelagem_camada_ouro():

    con = None
    
    try:
        logging.info("Iniciando a pipeline da camada Ouro...")
        
        # 1. Carrega variáveis (No Airflow em produção, você costuma usar Variables ou Connections do próprio Airflow)
        load_dotenv()
        bucket_name = os.getenv('BUCKET_NAME')
        aws_region = os.getenv('AWS_REGION')
        aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')

        # 2. Inicializa a conexão
        con = duckdb.connect()

        # 3. Configurações do S3
        logging.info("Carregando extensões e configurando credenciais AWS...")
        con.execute("INSTALL httpfs; LOAD httpfs;")
        con.execute("INSTALL aws; LOAD aws;")
        
        con.execute(f"SET s3_region='{aws_region}';")
        con.execute(f"SET s3_access_key_id='{aws_access_key}';")
        con.execute(f"SET s3_secret_access_key='{aws_secret_key}';")

        # Pegando dados do S3
        caminho_origem = f"s3://{bucket_name}/prata/*.parquet"
        con.execute(f"""
            CREATE OR REPLACE VIEW dados_origem AS 
            SELECT * FROM read_parquet('{caminho_origem}');
        """)

        # 5. Processamento das Dimensões
        logging.info("Processando dim_cliente...")
        con.execute(f"""
            CREATE OR REPLACE TABLE dim_cliente AS
            SELECT 
                Customer_ID, FIRST(Name) AS Name, FIRST(Age) AS Age, FIRST(Occupation) AS Occupation
            FROM dados_origem GROUP BY Customer_ID;
            COPY dim_cliente TO 's3://{bucket_name}/ouro/dim_cliente/dim_cliente.parquet' (FORMAT PARQUET);
        """)

        logging.info("Processando dim_perfil_credito...")
        con.execute(f"""
            CREATE OR REPLACE TABLE dim_perfil_credito AS
            SELECT DISTINCT
                md5(concat_ws('||', COALESCE(Credit_Score, ''), COALESCE(Credit_Mix, ''), 
                COALESCE(Payment_Behaviour, ''), COALESCE(Payment_of_Min_Amount, ''), 
                COALESCE(Credit_History_Age, ''), COALESCE(CAST(Changed_Credit_Limit AS VARCHAR), ''))) AS ID_Perfil_Credito,
                Credit_Score, Credit_Mix, Payment_Behaviour, Payment_of_Min_Amount, 
                Credit_History_Age, Changed_Credit_Limit
            FROM dados_origem;
            COPY dim_perfil_credito TO 's3://{bucket_name}/ouro/dim_perfil_credito/dim_perfil_credito.parquet' (FORMAT PARQUET);
        """)

        logging.info("Processando dim_bancarizacao...")
        con.execute(f"""
            CREATE OR REPLACE TABLE dim_bancarizacao AS
            SELECT DISTINCT
                md5(concat_ws('||', COALESCE(Type_of_Loan, ''), COALESCE(CAST(Num_of_Loan AS VARCHAR), ''), 
                COALESCE(CAST(Num_Bank_Accounts AS VARCHAR), ''), COALESCE(CAST(Num_Credit_Card AS VARCHAR), ''))) AS ID_Emprestimo,
                Type_of_Loan, Num_of_Loan, Num_Bank_Accounts, Num_Credit_Card
            FROM dados_origem;
            COPY dim_bancarizacao TO 's3://{bucket_name}/ouro/dim_bancarizacao/dim_bancarizacao.parquet' (FORMAT PARQUET);
        """)


        # 6. Processamento da Fato
        logging.info("Processando fato_historico_credito...")
        con.execute(f"""
            CREATE OR REPLACE TABLE fato_historico_credito AS
            SELECT 
                ID, Customer_ID, Month,
                md5(concat_ws('||', COALESCE(Credit_Score, ''), COALESCE(Credit_Mix, ''), 
                COALESCE(Payment_Behaviour, ''), COALESCE(Payment_of_Min_Amount, ''), 
                COALESCE(Credit_History_Age, ''), COALESCE(CAST(Changed_Credit_Limit AS VARCHAR), ''))) AS ID_Perfil_Credito,
                md5(concat_ws('||', COALESCE(Type_of_Loan, ''), COALESCE(CAST(Num_of_Loan AS VARCHAR), ''), 
                COALESCE(CAST(Num_Bank_Accounts AS VARCHAR), ''), COALESCE(CAST(Num_Credit_Card AS VARCHAR), ''))) AS ID_Emprestimo,
                Annual_Income, Monthly_Inhand_Salary, Outstanding_Debt, Monthly_Balance, 
                Credit_Utilization_Ratio, Total_EMI_per_month, Amount_invested_monthly, 
                Interest_Rate, Delay_from_due_date, Num_of_Delayed_Payment, Num_Credit_Inquiries
            FROM dados_origem;
            COPY fato_historico_credito TO 's3://{bucket_name}/ouro/fato_historico_credito/fato_historico_credito.parquet' (FORMAT PARQUET);
        """)

        logging.info("Upload na camada ouro concluído com sucesso!")

    except Exception as e:
        logging.error(f" Erro durante a execução da pipeline: {str(e)}")
        raise e 

    finally:
        # Fechar conexão 
        if con is not None:
            con.close()
            logging.info("Conexão com DuckDB encerrada.")

if __name__ == "__main__":
    modelagem_camada_ouro()