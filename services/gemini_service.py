import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from utils.logger import configurar_logger
from prompts.templates import (
    TEMPLATE_CLASSIFICADOR_GRAFICO,
    PROMPT_ANALISE_DINAMICA,
    PROMPT_RESUMO_EXECUTIVO
)
from config import GOOGLE_API_KEY


logger = configurar_logger("gemini_service")
# GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

MODELO_TEXTO = "gemini-3-flash-preview" 

def decidir_tipo_grafico_ia(nome_campo: str, dados: dict) -> dict:
    """Oráculo Semântico: Lê o JSON sujo e devolve a configuração do gráfico + dados limpos."""
    logger.info(f"Consultando Oráculo (IA) para a seção: {nome_campo}")
    try:
        # Temperatura ZERO para ele não inventar chaves no JSON
        llm = ChatGoogleGenerativeAI(model=MODELO_TEXTO, temperature=0.0, api_key=GOOGLE_API_KEY)
        prompt = PromptTemplate(template=TEMPLATE_CLASSIFICADOR_GRAFICO, input_variables=["nome_campo", "dados"])
        
        chain = prompt | llm | JsonOutputParser()
        resposta_json = chain.invoke({"nome_campo": nome_campo, "dados": dados})
        
        return resposta_json
        
    except Exception as e:
        logger.error(f"Erro no Oráculo de gráficos para {nome_campo}: {e}")
        # Fallback de segurança atualizado com a chave 'dados_processados'
        return {"tipo_grafico": "pular", "titulo_sugerido": nome_campo, "eixo_x": "", "eixo_y": "", "dados_processados": {}}


def gerar_analise_ia(campo: str, dados: dict) -> str:
    """Tradutor Micro -> Macro: Gera o texto analítico focado em negócios."""
    logger.info(f"Gerando análise executiva para: {campo}")
    try:
        # Temperatura leve para permitir que ele atue como um consultor e conecte pontos
        llm = ChatGoogleGenerativeAI(model=MODELO_TEXTO, temperature=0.2, api_key=GOOGLE_API_KEY)
        
        # Usamos o prompt dinâmico que serve para QUALQUER seção do Jira/OKR
        chain = PROMPT_ANALISE_DINAMICA | llm | StrOutputParser()
        
        resposta_md = chain.invoke({"campo": campo, "dados": dados})
        return resposta_md
        
    except Exception as e:
        logger.error(f"Erro ao gerar análise para {campo}: {e}")
        return f"**Erro na análise:** Não foi possível gerar insights para {campo}. Detalhe: {str(e)}"


def gerar_resumo_geral(textos_detalhados_agrupados: str) -> str:
    """Sumário Executivo: Lê todas as seções e cria o diagnóstico transversal."""
    logger.info("Gerando Sumário Executivo Transversal...")
    try:
        llm = ChatGoogleGenerativeAI(model=MODELO_TEXTO, temperature=0.2, api_key=GOOGLE_API_KEY)
        
        # Usamos o prompt específico do Resumo Executivo
        chain = PROMPT_RESUMO_EXECUTIVO | llm | StrOutputParser()
        
        resposta_md = chain.invoke({"textos_detalhados_agrupados": textos_detalhados_agrupados})
        return resposta_md
        
    except Exception as e:
        logger.error(f"Erro ao gerar resumo executivo: {e}")
        return "**Erro crítico ao gerar Sumário Executivo.**"