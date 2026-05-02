from utils.logger import configurar_logger

logger = configurar_logger(__name__)

def extrair_campos_selecionados(payload_front: dict) -> dict:
    """
    Recebe o JSON bruto do front-end e retorna apenas os campos selecionados
    com seus respectivos dados.
    """
    logger.info(f"Iniciando extracao de campos. Total recebido: {len(payload_front)}")
    campos_ativos = {}
    
    try:
        for nome_campo, informacoes in payload_front.items():
            
            if isinstance(informacoes, dict) and informacoes.get("selected") == 1: #Verifica se o 'Selected' é igual a 1
                dados_do_campo = informacoes.get("data", {})
                campos_ativos[nome_campo] = dados_do_campo    

                logger.debug(f"Campo processado: {nome_campo}")

        logger.info(f"Extracao concluida. {len(campos_ativos)} campos ativos encontrados.")
        return campos_ativos
    except Exception as e:
        logger.error(f"Erro ao extrair campos do JSON: {str(e)}")
        raise
        
