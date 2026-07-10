import os
import boto3
import logging
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
from pathlib import Path



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
# Caminho absoluto da pasta onde este script está localizado
BASE_DIR = Path(__file__).resolve().parent.parent  # sobe de /scripts para a raiz do projeto
PASTA_ORIGEM = BASE_DIR / "camada_bronze"

def upload_bronze_s3():
    try:
        # Verifica se o diretório existe antes de tentar listar
        if not os.path.exists(PASTA_ORIGEM):
            logger.error(f"Diretório não encontrado: {PASTA_ORIGEM}")
            return

        for arquivo in os.listdir(PASTA_ORIGEM):
            if arquivo.endswith('.csv'):
                caminho_local = os.path.join(PASTA_ORIGEM, arquivo)
                caminho_s3 = f"bronze/{arquivo}"
                
                try:
                    logger.info(f"Copiando {arquivo} para o S3...")
                    s3_client.upload_file(caminho_local, BUCKET_NAME, caminho_s3)
                    logger.info(f"Upload de {arquivo} concluído com sucesso!")
                
                except ClientError as e:
                    logger.error(f"Erro ao enviar {arquivo} para o S3: {e}")
                except NoCredentialsError:
                    logger.error("Credenciais AWS não encontradas.")
                except Exception as e:
                    logger.error(f"Erro inesperado ao processar {arquivo}: {e}")
                    
    except Exception as e:
        logger.error(f"Erro crítico na execução do script: {e}")

if __name__ == "__main__":
    upload_bronze_s3()
