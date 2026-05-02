import base64
import os
from utils.logger import configurar_logger

logger = configurar_logger(__name__)

def codificar_pdf_para_base64(caminho_pdf: str) -> str:
    """Lê um arquivo PDF físico e o converte para uma string Base64."""
    logger.info(f"Iniciando conversão para Base64 do arquivo: {caminho_pdf}")
    
    if not os.path.exists(caminho_pdf):
        logger.error("Arquivo PDF não encontrado para conversão.")
        return ""
    
    try:
        with open(caminho_pdf, "rb") as arquivo_pdf:
            pdf_bytes = arquivo_pdf.read()
            base64_codificado = base64.b64encode(pdf_bytes).decode('utf-8')
            
            logger.info("Conversão para Base64 concluída com sucesso.")
            return base64_codificado
            
    except Exception as e:
        logger.error(f"Erro ao converter PDF para Base64: {e}")
        return ""