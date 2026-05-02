import os
from utils.logger import configurar_logger
from services.gemini_service import gerar_analise_ia, gerar_resumo_geral
from services.chart_service import processar_grafico_para_campo
from services.pdf_service import gerar_pdf_relatorio

logger = configurar_logger("main")

def executar_motor_inteligencia():
    print("\n" + "="*50)
    print("🚀 INICIANDO MOTOR DE INTELIGÊNCIA EXECUTIVA")
    print("="*50 + "\n")

    # 1. Simulando os dados que viriam do seu banco/JSON filtrado
    dados_filtrados = {
        "analise_icp_l6m": {
            "usuarios_ativos": 15420, "ticket_medio": 450, "taxa_upsell": "12%", "churn_1m": "15%"
        },
        "volume_por_ativo": {
            "BTC": 55, "ETH": 25, "SOL": 10, "USDC": 7, "Outros": 3
        },
        "historico_ltv_mensal": {
            "Jan": 420, "Fev": 435, "Mar": 450, "Abr": 445, "Mai": 460
        }
    }

    # Nomes bonitos para as seções do PDF baseados nas chaves
    titulos_map = {
        "analise_icp_l6m": "Análise de ICP e Retenção",
        "volume_por_ativo": "Distribuição de Volume por Ativo",
        "historico_ltv_mensal": "Evolução do Lifetime Value (LTV)"
    }

    conteudo_secoes = []
    textos_para_resumo = ""

    # 2. Loop Principal (Processando cada indicador)
    for campo, dados in dados_filtrados.items():
        titulo = titulos_map.get(campo, campo)
        print(f"\n⚙️ Processando: {titulo}...")
        
        # A. Pede a análise detalhada para a IA
        texto_md = gerar_analise_ia(campo, dados)
        
        # B. Gera o gráfico lindo no Seaborn
        caminho_img = processar_grafico_para_campo(campo, dados)
        
        # C. Guarda na lista do PDF e no blocão de texto para o resumo
        conteudo_secoes.append({
            "titulo": titulo,
            "texto_md": texto_md,
            "imagem": caminho_img
        })
        
        # Acumula o texto para o resumo final (ignorando erros de sistema)
        if not texto_md.startswith("**Erro"):
            textos_para_resumo += f"\n\n--- Seção: {titulo} ---\n{texto_md}"

    # 3. Geração do Resumo Executivo (A Síntese Transversal)
    print("\n🧠 Analisando todos os textos para criar o Sumário Executivo...")
    resumo_geral_md = gerar_resumo_geral(textos_para_resumo)

    # 4. Compilação do Documento
    print("\n📄 Compilando PDF Enterprise...")
    nome_arquivo = "Relatorio_Diretoria_Automatizado.pdf"
    caminho_final = gerar_pdf_relatorio(resumo_geral_md, conteudo_secoes, nome_arquivo)

    if caminho_final:
        print("\n" + "="*50)
        print(f"✅ SUCESSO! Relatório gerado em: {caminho_final}")
        print("="*50 + "\n")
    else:
        print("\n❌ Falha na montagem final do PDF.")

if __name__ == "__main__":
    executar_motor_inteligencia()