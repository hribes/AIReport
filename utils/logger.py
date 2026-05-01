import logging
import os
from logging.handlers import RotatingFileHandler

def configurar_logger(nome_modulo: str):
    """
    Cria e configura um logger padrão para ser usado em toda a aplicação.
    """
    pasta_logs = "logs"
    if not os.path.exists(pasta_logs):
        os.makedirs(pasta_logs)


    formato_log = logging.Formatter(
        '%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger(nome_modulo)
    logger.setLevel(logging.INFO) # Captura de INFO para cima (INFO, WARNING, ERROR, CRITICAL)

    if not logger.handlers:
        file_handler = RotatingFileHandler(
            f"{pasta_logs}/app.log", maxBytes=5000000, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formato_log)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formato_log)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger