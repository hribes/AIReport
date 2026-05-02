import os
import time
import json
import shutil
from utils.logger import configurar_logger
from services.gemini_service import gerar_analise_ia, gerar_resumo_geral, decidir_tipo_grafico_ia
from services.chart_service import processar_grafico_dinamico
from services.pdf_service import gerar_pdf_relatorio
from utils.base64_encoder import codificar_pdf_para_base64

logger = configurar_logger("main")

def limpar_arquivos_temporarios():
    """Deleta as pastas temporárias onde imagens e PDFs foram salvos."""
    pastas_para_limpar = ["temp_images"] #por enquanto irei manter a pasta temporária do relatorio
    
    for pasta in pastas_para_limpar:
        if os.path.exists(pasta):
            try:
                shutil.rmtree(pasta) 
                logger.debug(f"Limpeza concluída: '{pasta}' apagada.")
            except Exception as e:
                logger.warning(f"Não foi possível limpar a pasta '{pasta}': {e}")

def executar_motor_inteligencia(payload_entrada: dict) -> str:
    """
    Recebe os dados brutos, orquestra a IA, gera o PDF, converte para Base64 
    e retorna um JSON de resposta estrito para o sistema chamador.
    """
    tempo_inicio = time.time()
    logger.info("Iniciando Motor de Inteligência Executiva...")

    resposta_final = {
        "status": "erro",
        "mensagem": "",
        "tempo_execucao_segundos": 0,
        "pdf_base64": ""
    }

    try:
        conteudo_secoes = []
        textos_para_resumo = ""

        for campo, dados in payload_entrada.items():
            logger.info(f"Processando campo bruto: {campo}...")
            
            decisao_visual_ia = decidir_tipo_grafico_ia(campo, dados)
            titulo_inteligente = decisao_visual_ia.get("titulo_sugerido", campo)
            logger.info(f"A IA decidiu: Gráfico de '{decisao_visual_ia.get('tipo_grafico')}' com título '{titulo_inteligente}'")

            texto_md = gerar_analise_ia(campo, dados)
            caminho_img = processar_grafico_dinamico(dados, decisao_visual_ia)
            
            conteudo_secoes.append({
                "titulo": titulo_inteligente,
                "texto_md": texto_md,
                "imagem": caminho_img
            })
            
            if not texto_md.startswith("**Erro"):
                textos_para_resumo += f"\n\n--- Seção: {titulo_inteligente} ---\n{texto_md}"

            logger.info("Aguardando 10 segundos de segurança para a API...") #Como a API é gratuita tem uma quantidade limite de requisições por minuto
            time.sleep(10)

        logger.info("Analisando textos para criar o Sumário Executivo...")
        resumo_geral_md = gerar_resumo_geral(textos_para_resumo)

        nome_arquivo = "Relatorio_Temporario.pdf"
        caminho_final = gerar_pdf_relatorio(resumo_geral_md, conteudo_secoes, nome_arquivo)

        if not caminho_final:
            raise Exception("A geração física do PDF falhou internamente.")

        logger.info("Codificando documento para Base64...")
        pdf_base64_string = codificar_pdf_para_base64(caminho_final)
        
        if not pdf_base64_string:
            raise Exception("Falha na conversão para Base64.")

        resposta_final["status"] = "sucesso"
        resposta_final["mensagem"] = "Relatório executivo gerado e convertido com sucesso."
        resposta_final["pdf_base64"] = pdf_base64_string

    except Exception as e:
        logger.error(f"FALHA CRÍTICA NO PIPELINE: {str(e)}")
        resposta_final["mensagem"] = str(e)
    
    finally:
        logger.info("Limpando arquivos temporários do disco...")
        limpar_arquivos_temporarios()
        
        duracao_total = time.time() - tempo_inicio
        resposta_final["tempo_execucao_segundos"] = round(duracao_total, 2)
        logger.info(f"Processo finalizado em {resposta_final['tempo_execucao_segundos']}s")

        return json.dumps(resposta_final, ensure_ascii=False, indent=2)

# ==========================================
# ÁREA DE TESTE DO MICROSERVIÇO
# ==========================================
if __name__ == "__main__":
    # O JSON inicial (Payload) que viria do seu banco ou webhook
    json_inicial_simulado = {
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

    print("\n" + "="*50)
    print("INICIANDO MOTOR DE INTELIGÊNCIA EXECUTIVA")
    print("="*50 + "\n")

    # A variável 'saida_json_string' agora guarda a resposta da nossa API
    saida_json_string = executar_motor_inteligencia(json_inicial_simulado)
    
    # Vamos tratar o print apenas para não poluir o terminal com os milhares de caracteres do Base64
    saida_dict = json.loads(saida_json_string)
    if saida_dict["status"] == "sucesso":
        # Trunca o base64 só para exibição na tela
        preview_base64 = saida_dict["pdf_base64"][:150] + "... [TRUNCADO PARA LEITURA] ..."
        saida_dict["pdf_base64"] = preview_base64
        
    print("\n" + "="*50)
    print("SAÍDA DO SISTEMA (JSON DE RESPOSTA):")
    print("="*50)
    print(json.dumps(saida_dict, ensure_ascii=False, indent=4))