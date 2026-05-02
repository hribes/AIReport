import os
import time  
from utils.logger import configurar_logger
from services.gemini_service import gerar_analise_ia, gerar_resumo_geral, decidir_tipo_grafico_ia
from services.chart_service import processar_grafico_dinamico
from services.pdf_service import gerar_pdf_relatorio

logger = configurar_logger("main")

def executar_motor_inteligencia():
    tempo_inicio = time.time()
    print("\n" + "="*50)
    print("INICIANDO MOTOR DE INTELIGÊNCIA EXECUTIVA")
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
        print(f"\nPROCESSANDO O CAMPO BRUTO: {campo}...")
        
        # A. Consulta o Oráculo: Qual gráfico usar? Qual o título?
        decisao_visual_ia = decidir_tipo_grafico_ia(campo, dados)
        titulo_inteligente = decisao_visual_ia.get("titulo_sugerido", campo)
        
        print(f"   ↳ A IA decidiu: Gráfico de '{decisao_visual_ia.get('tipo_grafico')}' com título '{titulo_inteligente}'")

        # B. Pede a análise detalhada para a IA
        texto_md = gerar_analise_ia(campo, dados)
        
        # C. Gera o gráfico passando a decisão da IA para o roteador dinâmico
        caminho_img = processar_grafico_dinamico(dados, decisao_visual_ia)
        
        # D. Guarda na lista do PDF e no blocão de texto para o resumo
        conteudo_secoes.append({
            "titulo": titulo_inteligente,
            "texto_md": texto_md,
            "imagem": caminho_img
        })
        
        if not texto_md.startswith("**Erro"):
            textos_para_resumo += f"\n\n--- Seção: {titulo_inteligente} ---\n{texto_md}"

        print("⏳ Aguardando 10 segundos para não sobrecarregar a API gratuita...")
        time.sleep(10)

    # 3. Geração do Resumo Executivo (A Síntese Transversal)
    print("\n🧠 Analisando todos os textos para criar o Sumário Executivo...")
    resumo_geral_md = gerar_resumo_geral(textos_para_resumo)

    # 4. Compilação do Documento
    print("\n📄 Compilando PDF Enterprise...")
    nome_arquivo = "Relatorio_Diretoria_Automatizado.pdf"
    caminho_final = gerar_pdf_relatorio(resumo_geral_md, conteudo_secoes, nome_arquivo)

    if caminho_final:
        tempo_fim = time.time() 
        duracao_total = tempo_fim - tempo_inicio
        
        # Transformando os segundos em algo legível (ex: 1m 12s)
        minutos = int(duracao_total // 60)
        segundos = int(duracao_total % 60)
        if minutos > 0:
            tempo_formatado = f"{minutos}m {segundos}s"
        else:
            tempo_formatado = f"{duracao_total:.1f}s"

        logger.info(f"Processo de Inteligencia finalizado. Tempo de execucao: {tempo_formatado}")

        print("\n")
        print(f"SUCESSO! Relatório gerado em: {caminho_final}")
        print(f"Tempo total de processamento: {tempo_formatado}")
    else:
        print("\n❌ Falha na montagem final do PDF.")

if __name__ == "__main__":
    executar_motor_inteligencia()