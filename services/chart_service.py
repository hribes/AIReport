import os
import uuid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from utils.logger import configurar_logger

logger = configurar_logger(__name__)

sns.set_theme(style="whitegrid")
COR_PRIMARIA = "#0047AB" 


def _garantir_pasta_temp():
    """Cria a pasta temporária para armazenar os gráficos, se não existir."""
    pasta = "temp_images"
    if not os.path.exists(pasta):
        os.makedirs(pasta)
    return pasta

def gerar_grafico_barras(dados: dict, titulo: str, eixo_x: str, eixo_y: str) -> str:
    """
    Gera um gráfico de barras executivo e salva em um arquivo temporário.
    """
    logger.info(f"Gerando grafico de barras: {titulo}")
    pasta_temp = _garantir_pasta_temp()
    
    nome_arquivo = f"{uuid.uuid4().hex}.png"
    caminho_completo = os.path.join(pasta_temp, nome_arquivo)
    
    try:
        categorias = list(dados.keys())
        valores = list(dados.values())
        
        plt.figure(figsize=(8, 5))
        
        ax = sns.barplot(x=valores, y=categorias, color=COR_PRIMARIA)
        
        plt.title(titulo, fontsize=14, pad=15, fontweight='bold')
        plt.xlabel(eixo_y, fontsize=11) # Esta trocado pq é a IA quem envia, pensando que é barras verticais, mas como quero horizontais eu precisei trocar os eixos
        plt.ylabel(eixo_x, fontsize=11)
        
        ax.bar_label(ax.containers[0], padding=4, fmt='%.1f')
        
        sns.despine()
        
        plt.tight_layout()
        plt.savefig(caminho_completo, dpi=300)
        
        # IMPORTANTE: Limpa a memória para a próxima requisição
        plt.close()
        
        logger.debug(f"Grafico salvo com sucesso em: {caminho_completo}")
        return caminho_completo
        
    except Exception as e:
        logger.error(f"Erro ao gerar grafico de barras '{titulo}': {str(e)}")
        plt.close()
        return "" # Retorna string vazia se falhar, para o PDF não quebrar
    
def gerar_grafico_linha(dados: dict, titulo: str, eixo_x: str, eixo_y: str) -> str:
    """Gera um gráfico de linha temporal executivo."""
    logger.info(f"Gerando grafico de linha: {titulo}")
    pasta_temp = _garantir_pasta_temp()
    caminho_completo = os.path.join(pasta_temp, f"{uuid.uuid4().hex}.png")
    
    try:
        categorias, valores = list(dados.keys()), list(dados.values())
        plt.figure(figsize=(8, 4))
        
        sns.lineplot(x=categorias, y=valores, color=COR_PRIMARIA, marker="o", linewidth=2.5)
        
        plt.title(titulo, fontsize=14, pad=15, fontweight='bold')
        plt.xlabel(eixo_x, fontsize=11)
        plt.ylabel(eixo_y, fontsize=11)
        sns.despine()
        
        plt.tight_layout()
        plt.savefig(caminho_completo, dpi=300)
        plt.close()
        return caminho_completo
    except Exception as e:
        logger.error(f"Erro no grafico de linha: {e}")
        plt.close()
        return ""

def gerar_grafico_pizza(dados: dict, titulo: str, **kwargs) -> str:
    """Gera um gráfico de pizza (estilo Donut) executivo com legenda lateral."""
    logger.info(f"Gerando grafico de pizza/donut: {titulo}")
    pasta_temp = _garantir_pasta_temp()
    caminho_completo = os.path.join(pasta_temp, f"{uuid.uuid4().hex}.png")
    
    try:
        labels = list(dados.keys())
        sizes = list(dados.values())
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        cores = [COR_PRIMARIA, "#F7931A", "#2A9D8F", "#E9C46A", "#E76F51"]
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=None,
            autopct=lambda p: f'{p:.1f}%' if p > 4 else '', # Oculta % menores que 4%
            startangle=90, 
            colors=cores, 
            pctdistance=0.80, 
            wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
        )
        
        for autotext in autotexts:
            autotext.set_fontsize(11)
            autotext.set_fontweight('bold')
            autotext.set_color('#333333') 
        
        ax.legend(wedges, labels,
                  title="Ativos",
                  title_fontproperties={'weight': 'bold'},
                  loc="center left",
                  bbox_to_anchor=(1, 0, 0.5, 1),
                  frameon=False)
        
        plt.title(titulo, fontsize=14, pad=15, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(caminho_completo, dpi=300)
        plt.close()
        return caminho_completo
    except Exception as e:
        logger.error(f"Erro no grafico de pizza: {e}")
        plt.close()
        return ""

def pular_grafico(dados: dict, titulo: str, **kwargs) -> str:
    """Retorna uma string vazia para campos que são apenas texto/KPIs."""
    logger.info(f"Pulando geracao de grafico para: {titulo} (Campo apenas de texto)")
    return ""


# mapeamento do tipo de grafico retornado pela AI
MAPA_FUNCOES_GRAFICOS = {
    "linha": gerar_grafico_linha,
    "pizza": gerar_grafico_pizza,
    "barras": gerar_grafico_barras,
    "pular": pular_grafico
}

def processar_grafico_dinamico(dados_brutos: dict, decisao_ia: dict) -> str:
    """
    Recebe os dados brutos e a decisão da IA, extraindo a matriz processada 
    para não quebrar as bibliotecas de plotagem com JSONs aninhados.
    """
    tipo = decisao_ia.get("tipo_grafico", "pular").lower()
    titulo = decisao_ia.get("titulo_sugerido", "Análise de Dados")
    eixo_x = decisao_ia.get("eixo_x", "")
    eixo_y = decisao_ia.get("eixo_y", "")
    
    # Pega os dados planos que a IA extraiu
    # Se a IA não extraiu, cai nos dados brutos
    dados_limpos_para_plot = decisao_ia.get("dados_processados", dados_brutos)
    
    # Trava de segurança Se a IA escolheu gráfico mas não mandou os dados achatados, pulamos
    if tipo != "pular" and not isinstance(dados_limpos_para_plot, dict):
        logger.warning(f"IA escolheu '{tipo}' mas falhou em achatar os dados. Forçando 'pular'.")
        tipo = "pular"
    
    funcao_plot = MAPA_FUNCOES_GRAFICOS.get(tipo, pular_grafico)
    
    if funcao_plot == pular_grafico:
        return funcao_plot(dados=dados_limpos_para_plot, titulo=titulo)
    elif funcao_plot == gerar_grafico_pizza:
        return funcao_plot(dados=dados_limpos_para_plot, titulo=titulo)
    else:
        return funcao_plot(dados=dados_limpos_para_plot, titulo=titulo, eixo_x=eixo_x, eixo_y=eixo_y)