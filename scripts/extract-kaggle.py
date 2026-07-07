import os
import logging
import kagglehub

# ==========================================
# 1. Configuração Profissional de Logs
# ==========================================
logging.basicConfig(
    level=logging.INFO
)
logger = logging.getLogger(__name__)


DATASET_NAME = 'parisrohan/credit-score-classification'

# Pasta onde os dados serão salvos localmente
PASTA_DESTINO = '../dados_brutos'

# ==========================================
# 3. Função de Extração
# ==========================================
def extrair_dados():
    logger.info(f"Iniciando a extração do dataset: '{DATASET_NAME}'...")
    
    try:
        caminho_cache = kagglehub.dataset_download(DATASET_NAME)
        logger.info(f"Download concluído no cache: {caminho_cache}")
        
        # Cria a pasta destino
        os.makedirs(PASTA_DESTINO, exist_ok=True)
        
        arquivos_movidos = 0
        for nome_arquivo in os.listdir(caminho_cache):
            caminho_origem = os.path.join(caminho_cache, nome_arquivo)
            caminho_destino = os.path.join(PASTA_DESTINO, nome_arquivo)
            
            if os.path.isfile(caminho_origem):
                # Usando o os.replace para mover o arquivo limpo
                os.replace(caminho_origem, caminho_destino)
                logger.info(f"Arquivo movido com sucesso: {nome_arquivo}")
                arquivos_movidos += 1
                
        logger.info(f"Sucesso! {arquivos_movidos} arquivo(s) disponíveis na pasta: {PASTA_DESTINO}")
        
    except Exception as e:
        logger.error(f"Falha na extração dos dados: {e}")
        raise

if __name__ == "__main__":
    extrair_dados()