import os
import shutil
import logging
import kagglehub
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)

DATASET_NAME = 'parisrohan/credit-score-classification'
BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_DESTINO = BASE_DIR / "camada_bronze"

def extrair_dados():
    logger.info(f"Iniciando a extração do dataset: '{DATASET_NAME}'...")
    
    try:
        caminho_cache = kagglehub.dataset_download(DATASET_NAME)
        
        # TRAVA DE SEGURANÇA: Se a pasta do cache existir mas estiver vazia, limpa e força o download
        if os.path.exists(caminho_cache) and not os.listdir(caminho_cache):
            logger.warning("Cache corrompido (pasta vazia encontrada). Forçando redownload...")
            shutil.rmtree(caminho_cache, ignore_errors=True)
            caminho_cache = kagglehub.dataset_download(DATASET_NAME) # Baixa de verdade agora
            
        logger.info(f"Download concluído no cache: {caminho_cache}")
        
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        
        arquivos_movidos = 0
        for root, dirs, files in os.walk(caminho_cache):
            for nome_arquivo in files:
                caminho_origem = os.path.join(root, nome_arquivo)
                caminho_destino = os.path.join(PASTA_DESTINO, nome_arquivo)
                shutil.copyfile(caminho_origem, caminho_destino)
                arquivos_movidos += 1

        logger.info(f"Sucesso! {arquivos_movidos} arquivo(s) disponíveis na pasta: {PASTA_DESTINO}")
        
    except Exception as e:
        logger.error(f"Falha na extração dos dados: {e}")
        raise

if __name__ == "__main__":
    extrair_dados()