from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# Contexto geral - ele dita a persona, cenário da empresa e as regras de formatação
_contexto_base = """
Você é um Analista de Dados Sênior especializado em Growth e Analytics, reportando diretamente para a Diretoria Executiva.

Contexto do Negócio:
- O foco atual da empresa é otimização de receita, análise de comportamento de clientes e identificação de padrões de alto valor.
- Suas análises devem sempre tentar correlacionar o dado apresentado com impacto financeiro ou retenção.

Diretrizes de Formatação e Segurança (OBRIGATÓRIAS):
1. Use a metodologia Top-Down: A conclusão principal e o impacto devem estar no primeiro parágrafo.
2. Use bullet points para destrinchar os números e facilitar a leitura dinâmica.
3. Não explique o que a métrica é (a diretoria já sabe). Foque no que os dados significam.
4. Responda ESTRITAMENTE em formato Markdown limpo.
5. TRAVA DE ANTI-ALUCINAÇÃO: Baseie-se ÚNICA E EXCLUSIVAMENTE nos números fornecidos. Se o bloco de dados enviado estiver vazio, nulo (null) ou não contiver métricas válidas, NÃO INVENTE cenários. Sua resposta deve ser estritamente: "Os dados para este indicador não foram fornecidos ou estão indisponíveis para análise no período selecionado."
"""

prompt_sistema = SystemMessagePromptTemplate.from_template(_contexto_base)




# Templates especificos por campo
# Os templates abaixo não estão corretos ainda (AJUSTAR)
_template_receita = """
Analise os dados abaixo referentes a {campo}.
Concentre sua análise em identificar anomalias, oportunidades de upsell e concentração de receita.

Dados da coluna:
{dados}

Escreva sua análise executiva:
"""
prompt_receita = HumanMessagePromptTemplate.from_template(_template_receita)

# Template para análises de Engajamento ou Churn
_template_engajamento = """
Analise os dados abaixo referentes a {campo}.
Foque sua avaliação em identificar gargalos de retenção e sugerir uma ação rápida baseada na volumetria de queda.

Dados da coluna:
{dados}

Escreva sua análise executiva:
"""
prompt_engajamento = HumanMessagePromptTemplate.from_template(_template_engajamento)

# Template Genérico (Para colunas que não têm um template específico ainda)
_template_generico = """
Analise os dados abaixo referentes a {campo} e extraia os principais insights operacionais.

Dados da coluna:
{dados}

Escreva sua análise executiva:
"""
prompt_generico = HumanMessagePromptTemplate.from_template(_template_generico)




# Junção da base (contexto) com os por campos
# O ChatPromptTemplate.from_messages junta o Sistema com o Humano de forma estruturada.

MAPA_TEMPLATES = {
    # Mapeie o nome que vem do front-end com a combinação correta de prompts
    "receita_mensal": ChatPromptTemplate.from_messages([prompt_sistema, prompt_receita]),
    "ticket_medio_l6m": ChatPromptTemplate.from_messages([prompt_sistema, prompt_receita]),
    
    "taxa_evasao": ChatPromptTemplate.from_messages([prompt_sistema, prompt_engajamento]),
    "usuarios_ativos": ChatPromptTemplate.from_messages([prompt_sistema, prompt_engajamento]),
    
    "default": ChatPromptTemplate.from_messages([prompt_sistema, prompt_generico])
}