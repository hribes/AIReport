import os
import itertools
import time
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from utils.logger import configurar_logger
from prompts.templates import (
    TEMPLATE_CLASSIFICADOR_GRAFICO,
    PROMPT_ANALISE_DINAMICA,
    PROMPT_RESUMO_EXECUTIVO
)
from config import GOOGLE_API_KEY_1, GOOGLE_API_KEY_2


logger = configurar_logger("gemini_service")

#para o balanceamento das APIs
CHAVES_API = [
    GOOGLE_API_KEY_1,
    GOOGLE_API_KEY_2
]

CHAVES_API = [chave for chave in CHAVES_API if chave]

if not CHAVES_API:
    raise ValueError("Nenhuma chave de API do Google foi encontrada no ambiente!")

# Cria um iterador infinito (Chave 1 -> Chave 2 -> Chave 1 -> Chave 2...)
ciclo_chaves = itertools.cycle(CHAVES_API)

def obter_proxima_chave():
    return next(ciclo_chaves)

MODELO_TEXTO = "gemini-2.5-flash" 

def chamar_gemini_com_fallback(prompt, variaveis: dict, parser, temperatura: float, max_tentativas: int = 3):
    """
    Tenta executar a chamada na IA. Se falhar (ex: limite de cota),
    pega a próxima chave da fila e tenta de novo automaticamente.
    """
    ultimo_erro = None
    
    for tentativa in range(1, max_tentativas + 1):
        chave_atual = obter_proxima_chave()
        try:
            llm = ChatGoogleGenerativeAI(model=MODELO_TEXTO, temperature=temperatura, api_key=chave_atual)
            chain = prompt | llm | parser
            
            return chain.invoke(variaveis)
            
        except Exception as e:
            ultimo_erro = e
            logger.warning(f"Falha na API (Tentativa {tentativa}/{max_tentativas}). Trocando chave e tentando de novo... Erro: {e}")
            time.sleep(2) 
            
    logger.error("Todas as tentativas de fallback falharam.")
    raise ultimo_erro






def decidir_tipo_grafico_ia(nome_campo: str, dados: dict) -> dict:
    logger.info(f"Consultando Oráculo para: {nome_campo}")
    try:
        prompt = PromptTemplate(template=TEMPLATE_CLASSIFICADOR_GRAFICO, input_variables=["nome_campo", "dados"])
        
        return chamar_gemini_com_fallback(
            prompt=prompt,
            variaveis={"nome_campo": nome_campo, "dados": dados},
            parser=JsonOutputParser(),
            temperatura=0.0
        )
    except Exception as e:
        logger.error(f"Erro no Oráculo para {nome_campo}: {e}")
        return {"tipo_grafico": "pular", "titulo_sugerido": nome_campo, "eixo_x": "", "eixo_y": "", "dados_processados": {}}


def gerar_analise_ia(campo: str, dados: dict) -> str:
    logger.info(f"Gerando análise executiva para: {campo}")
    try:
        return chamar_gemini_com_fallback(
            prompt=PROMPT_ANALISE_DINAMICA,
            variaveis={"campo": campo, "dados": dados},
            parser=StrOutputParser(),
            temperatura=0.2
        )
    except Exception as e:
        logger.error(f"Erro ao gerar análise para {campo}: {e}")
        return f"**Erro na análise:** Não foi possível gerar insights. Detalhe: {str(e)}"


def gerar_resumo_geral(textos_detalhados_agrupados: str) -> str:
    logger.info("Gerando Sumário Executivo Transversal...")
    try:
        return chamar_gemini_com_fallback(
            prompt=PROMPT_RESUMO_EXECUTIVO,
            variaveis={"textos_detalhados_agrupados": textos_detalhados_agrupados},
            parser=StrOutputParser(),
            temperatura=0.2
        )
    except Exception as e:
        logger.error(f"Erro ao gerar resumo executivo: {e}")
        return "**Erro crítico ao gerar Sumário Executivo.**"