import os
import uuid
import matplotlib.pyplot as plt
import seaborn as sns
from utils.logger import configurar_logger

logger = configurar_logger(__name__)

sns.set_theme(style="whitegrid")
COR_PRIMARIA = "#0047AB" 


#MELHORAR O VISUAL DOS GRÁFICOS
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
        
        ax = sns.barplot(x=categorias, y=valores, color=COR_PRIMARIA)
        
        plt.title(titulo, fontsize=14, pad=15, fontweight='bold')
        plt.xlabel(eixo_x, fontsize=11)
        plt.ylabel(eixo_y, fontsize=11)
        
        ax.bar_label(ax.containers[0], padding=3)
        
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
            autotext.set_color('#333333') # Um cinza escuro para dar contraste
        
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



MAPA_GRAFICOS = { #PRECISO FAZER O MAPEAMENTO CORRETO AQUI AINDA
    "historico_ltv_mensal": (gerar_grafico_linha, "Evolução do LTV (L6M)", "Mês", "LTV (R$)"),
    "volume_por_ativo": (gerar_grafico_pizza, "Distribuição de Volume por Ativo", "", ""),
    "usuarios_ativos_l6m": (gerar_grafico_barras, "Usuários Ativos (L6M)", "Mês", "Usuários"),
    # Fallback genérico
    "default": (gerar_grafico_barras, "Análise de Dados", "Categorias", "Valores")
}

def processar_grafico_para_campo(nome_campo: str, dados: dict) -> str:
    """
    Identifica qual gráfico desenhar com base no nome do campo
    e executa a função correspondente.
    """
    configuracao = MAPA_GRAFICOS.get(nome_campo, MAPA_GRAFICOS["default"])
    funcao_plot, titulo, eixo_x, eixo_y = configuracao
    
    if funcao_plot == gerar_grafico_pizza:
        return funcao_plot(dados=dados, titulo=titulo)
    else:
        return funcao_plot(dados=dados, titulo=titulo, eixo_x=eixo_x, eixo_y=eixo_y)

# ==========================================
# CRITÉRIO DE SUCESSO: TESTE LOCAL COM ROTEADOR
# ==========================================
if __name__ == "__main__":
    print("\n--- INICIANDO TESTE DO ROTEADOR DE GRÁFICOS ---")

    # Simulando o dicionário de campos ativos que viria do json_parser
    payload_simulado = {
        "usuarios_ativos_l6m": {
            "Jan": 1200, "Fev": 1350, "Mar": 1500, "Abr": 1450, "Mai": 1600, "Jun": 1750
        },
        "historico_ltv_mensal": {
            "Jan": 450, "Fev": 465, "Mar": 480, "Abr": 475, "Mai": 490, "Jun": 510
        },
        "volume_por_ativo": {
            "BTC": 55, "ETH": 25, "SOL": 10, "USDC": 7, "Outros": 3
        }
    }

    # O loop que simula o fluxo do seu orquestrador principal
    for campo, dados in payload_simulado.items():
        print(f"\nProcessando requisição para: {campo}")
        
        # Chama APENAS o roteador, ele decide o resto
        caminho_imagem = processar_grafico_para_campo(nome_campo=campo, dados=dados)
        
        if caminho_imagem:
            print(f"✅ Sucesso! Gráfico salvo em: {caminho_imagem}")
        else:
            print(f"❌ Falha ao gerar o gráfico para {campo}.")

    print("\nTeste concluído! Abra a pasta 'temp_images' para ver os 3 gráficos gerados (Barras, Linha e Donut).")