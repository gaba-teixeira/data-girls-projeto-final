import os
import boto3
import logging
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configuração de logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Inicializa o cliente do S3
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('AWS_REGION')
)

BUCKET_NAME = os.getenv('BUCKET_NAME')
PASTA_ORIGEM = '../camada_bronze'

def upload_bronze_s3():
    for arquivo in os.listdir(PASTA_ORIGEM):
        if arquivo.endswith('.csv'):
            # Define o arquivo a ser enviado
            caminho_local = os.path.join(PASTA_ORIGEM, arquivo)
            # Define o caminho no S3
            caminho_s3 = f"bronze/{arquivo}"
            
            logger.info(f"Copiando {arquivo} para o S3...")

            s3_client.upload_file(caminho_local, BUCKET_NAME, caminho_s3)
            logger.info("Upload concluído!")

if __name__ == "__main__":
    upload_bronze_s3()

