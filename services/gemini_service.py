import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import PromptTemplate
from prompts.templates import MAPA_TEMPLATES
from utils.logger import configurar_logger
from config import GOOGLE_API_KEY 
from prompts.templates import MAPA_TEMPLATES, _contexto_base, TEMPLATE_RESUMO_GERAL, TEMPLATE_CLASSIFICADOR_GRAFICO


logger = configurar_logger(__name__)

def gerar_resumo_geral(textos_detalhados_agrupados: str) -> str:
    """Usa a IA para ler todas as análises geradas e criar um sumário executivo."""
    logger.info("Solicitando Resumo Executivo Transversal para a IA...")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", 
            temperature=0.4, # Temperatura um pouco maior para criatividade na síntese
            api_key=GOOGLE_API_KEY
        )
        
        # Junta o System Prompt com o Template de Resumo
        prompt_completo = _contexto_base + "\n\n" + TEMPLATE_RESUMO_GERAL
        prompt = PromptTemplate(template=prompt_completo, input_variables=["textos_detalhados_agrupados"])
        
        chain = prompt | llm | StrOutputParser()
        
        resposta = chain.invoke({"textos_detalhados_agrupados": textos_detalhados_agrupados})
        return resposta
    except Exception as e:
        logger.error(f"Erro ao gerar resumo geral via IA: {str(e)}")
        return "**Erro:** Não foi possível gerar o resumo executivo neste momento."

def gerar_analise_ia(nome_campo: str, dados_campo: dict) -> str:
    """
    Recebe os dados de um campo específico, seleciona o template adequado,
    chama o Gemini via LangChain e retorna a análise em Markdown.
    """
    logger.info(f"Iniciando geracao de analise via IA para o campo: {nome_campo}")
    
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # Mudamos aqui para a versão mais estável
            temperature=0.2,
            api_key=GOOGLE_API_KEY
        )
        
        prompt = MAPA_TEMPLATES.get(nome_campo, MAPA_TEMPLATES["default"]) # Se o campo passado não está no mapa ele passar o default
        
        chain = prompt | llm | StrOutputParser()
        
        dados_formatados = json.dumps(dados_campo, indent=2, ensure_ascii=False)
        nome_formatado = nome_campo.replace("_", " ").title()
        
        logger.debug(f"Enviando payload para o Gemini (Campo: {nome_formatado})...")
        resposta = chain.invoke({
            "campo": nome_formatado,
            "dados": dados_formatados
        })
        
        logger.info(f"Analise gerada com sucesso para o campo: {nome_campo}")
        return resposta
        
    except Exception as e:
        logger.error(f"Erro ao gerar analise para {nome_campo}: {str(e)}")
        return f"**Erro na análise de {nome_campo}:** Não foi possível processar os dados neste momento."

def decidir_tipo_grafico_ia(nome_campo: str, dados: dict) -> dict:
    """Usa a IA para analisar os dados e decidir dinamicamente o tipo de gráfico e eixos."""
    logger.info(f"Consultando IA para decidir tipo de grafico para: {nome_campo}")
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash", # USE O NOME QUE FUNCIONOU NA SUA CHAVE!
            temperature=0.0, # Temperatura ZERO para evitar que a IA invente formatos de JSON
            api_key=GOOGLE_API_KEY
        )
        
        prompt = PromptTemplate(
            template=TEMPLATE_CLASSIFICADOR_GRAFICO, 
            input_variables=["nome_campo", "dados"]
        )
        
        # O JsonOutputParser converte o texto da IA direto para um dicionário Python
        chain = prompt | llm | JsonOutputParser()
        
        resposta_json = chain.invoke({"nome_campo": nome_campo, "dados": dados})
        return resposta_json
        
    except Exception as e:
        logger.error(f"Erro na IA ao classificar grafico para {nome_campo}: {e}")
        # Fallback de segurança: se a IA falhar, mandamos pular para não quebrar o PDF
        return {"tipo_grafico": "pular", "titulo_sugerido": "Erro", "eixo_x": "", "eixo_y": ""}
# ==========================================
# CRITÉRIO DE SUCESSO: TESTE LOCAL
# ==========================================
if __name__ == "__main__":
    # Importante: O seu .env precisa ter a chave real do Gemini agora!
    
    # Simulando um dado extraído do front-end pelo json_parser
    nome_teste = "analise_icp_l6m"
    dados_teste = {
        "usuarios_ativos_l6m": 15420,
        "ticket_medio": "R$ 450,00",
        "taxa_conversao_upsell": "12%",
        "principal_ofensor_churn": "Falta de engajamento no primeiro mes"
    }
    
    print("\n--- INICIANDO CHAMADA AO GEMINI ---")
    resultado_markdown = gerar_analise_ia(nome_teste, dados_teste)
    
    print("\n--- RETORNO DA IA (FORMATO MARKDOWN) ---")
    print(resultado_markdown)