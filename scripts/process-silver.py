import pandas as pd
import awswrangler as wr
import os
import logging
from dotenv import load_dotenv
import numpy as np
from botocore.exceptions import ClientError

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Configurações
BUCKET_NAME = os.getenv('BUCKET_NAME')
pd.set_option('display.max_columns', None)




def processar_camada_prata():
    try:
        # 1. Leitura da Camada Bronze (usando awswrangler direto do S3)
        logger.info("Lendo arquivos da camada bronze...")
        
        
        df_test = wr.s3.read_csv(f"s3://{BUCKET_NAME}/bronze/test.csv")
        df_train = wr.s3.read_csv(f"s3://{BUCKET_NAME}/bronze/train.csv")

        # Adicionando a coluna que falta no dataset "test.csv"
        df_test['Credit_Score'] = np.nan

        # Unindo os dois dataset
        df = pd.concat([df_test, df_train], axis=0, ignore_index=True)

        # Limpeza global de vazios no DataFrame
        df = df.replace(r'^\s*$', np.nan, regex=True)

        #Tratando nomes vazios
        df['Name'] = df['Name'].fillna(
            df.groupby('Customer_ID')['Name'].transform('first')
        )

        #Tratando Annual Income vazios
        df['Annual_Income'] = df['Annual_Income'].fillna(
            df.groupby('Customer_ID')['Annual_Income'].transform('first')
        )
        #Tratando Occupation vazios
        df['Occupation'] = df['Occupation'].replace('_______', np.nan)
        df['Occupation'] = df['Occupation'].fillna(
            df.groupby('Customer_ID')['Occupation'].transform('first')
        )

        # Retirando registros duplicados
        df = df.drop_duplicates(subset=['Customer_ID', 'Month'])


        # Garantindo tipos numéricos (limpando caracteres estranhos se necessário)
        cols_numericas = ['Age', 'Annual_Income', 'Monthly_Inhand_Salary', 'Outstanding_Debt', 'Total_EMI_per_month','Amount_invested_monthly','Num_of_Delayed_Payment','Changed_Credit_Limit', 'Num_Bank_Accounts','Num_Credit_Card','Interest_Rate','Num_of_Loan']
        for col in cols_numericas:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Removendo registros inconsistentes de idade
        df['Age'] = df['Age'].fillna(
        df.groupby('Customer_ID')['Age'].transform('first'))
        df = df[(df['Age'] >= 18) & (df['Age'] <= 100)]

        # Tratando registros nulos vindo da outra tabela
        df['Credit_Score'] = df['Credit_Score'].fillna('Not Analyzed')

        # Tratando valores faltantes em Monthly_Inhand_Salary
        df['Monthly_Inhand_Salary'] = df['Monthly_Inhand_Salary'].fillna(df['Annual_Income'] / 12)

        #Removendo dados sensiveis
        df = df.drop(columns=['SSN'])

        # Converte todas as colunas do tipo object (string) para string explícita
        # Isso resolve o erro 'Expected bytes, got a float object'
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)
        
        logger.info("Salvando na camada prata...")
        path_prata = f"s3://{BUCKET_NAME}/prata/"
        
        wr.s3.to_parquet(df=df, path=path_prata, dataset=True, mode="overwrite")
        logger.info(f"Sucesso! Dados tratados salvos em: {path_prata}")
        
    except ClientError as e:
        logger.error(f"Erro de comunicação com a AWS: {e}")
    except KeyError as e:
        logger.error(f"Erro de processamento: Coluna não encontrada {e}")
    except ValueError as e:
        logger.error(f"Erro de valor durante a transformação: {e}")
    except Exception as e:
        logger.error(f"Erro inesperado durante o processamento da camada prata: {e}")
        raise

if __name__ == "__main__":
    processar_camada_prata()

