import os
import markdown
from fpdf import FPDF, XPos, YPos # Importamos os posicionadores modernos
from utils.logger import configurar_logger

logger = configurar_logger(__name__)

# Configuração de Cores Corporativas (RGB)
COR_AZUL = (0, 71, 171)
COR_TEXTO_ESCURO = (40, 40, 40)
COR_TEXTO_CLARO = (80, 80, 80)
COR_LINHA = (200, 200, 200)

class RelatorioEnterprisePDF(FPDF):
    def header(self):
        # Só desenha o cabeçalho azul se NÃO for a primeira página (Resumo Geral)
        if self.page_no() > 1:
            self.set_fill_color(*COR_AZUL)
            self.rect(0, 0, 210, 20, 'F')
            self.set_font("helvetica", "B", 12)
            self.set_text_color(255, 255, 255)
            self.set_y(5)
            # Modernizado ln=True -> new_x/new_y
            self.cell(0, 10, "Relatório de Inteligência Executiva - Detalhamento", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(*COR_TEXTO_CLARO)
        self.cell(0, 10, f"Página {self.page_no()}/{{nb}}", align="C")

    # NOTA: Removemos a estilização ToC Entry customizada e a global de estilos 
    # que causavam erros de versão. Vamos usar o padrão estável.

def gerar_pdf_relatorio(resumo_geral_md: str, conteudo_secoes: list, nome_arquivo_saida: str = "relatorio_final.pdf") -> str:
    """
    Gera o PDF Enterprise com Resumo Geral, Sumário e Detalhamento. Compatível com fpdf2 v2.7+.
    """
    logger.info("Iniciando a geracao do PDF Enterprise (Motor Corrigido)...")

    pasta_saida = "relatorios_gerados"
    if not os.path.exists(pasta_saida): os.makedirs(pasta_saida)
    caminho_pdf = os.path.join(pasta_saida, nome_arquivo_saida)

    # Inicializa o PDF
    pdf = RelatorioEnterprisePDF()
    pdf.alias_nb_pages()
    
    # ---------------------------------------------------------
    # PÁGINA 1: SUMÁRIO EXECUTIVO (Capa de Impacto)
    # ---------------------------------------------------------
    pdf.add_page()
    
    # Título Principal Gigante
    pdf.set_font("helvetica", "B", 26)
    pdf.set_text_color(*COR_AZUL)
    # Modernizado ln=True -> new_x/new_y
    pdf.cell(0, 20, "SUMÁRIO EXECUTIVO", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # Subtítulo com Data
    pdf.set_font("helvetica", "I", 12)
    pdf.set_text_color(*COR_TEXTO_CLARO)
    pdf.cell(0, 10, "Análise Transversal de Performance - Maio/2026", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_draw_color(*COR_LINHA)
    pdf.line(10, 50, 200, 50)
    pdf.ln(15)

    # Injeta o texto do Resumo Geral
    html_resumo = markdown.markdown(resumo_geral_md)
    pdf.set_font("helvetica", size=12)
    pdf.set_text_color(*COR_TEXTO_ESCURO)
    pdf.write_html(html_resumo) 

    # ---------------------------------------------------------
    # CONTEÚDO DETALHADO (Alimentando o orquestrador do Sumário)
    # ---------------------------------------------------------
    
    # NOTA: O bloco pdf.set_section_title_styles que causava o TypeError foi removido daqui.

    for secao in conteudo_secoes:
        titulo = secao.get("titulo", "Análise")
        texto_md = secao.get("texto_md", "")
        caminho_imagem = secao.get("imagem", "")

        # CRÍTICO: Adiciona uma nova página
        pdf.add_page()
        
        # 1. Estilizamos o Título na página de detalhe (O sumário lerá essa formatação)
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(*COR_AZUL)
        
        # 2. Imprimimos o título no corpo do PDF (Modernizado ln=True)
        pdf.cell(0, 10, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        # 3. Registramos no Sumário (ToC)
        pdf.start_section(titulo) 
        
        pdf.ln(5)

        # Injeção do texto HTML detalhado
        html_text = markdown.markdown(texto_md)
        pdf.set_font("helvetica", size=11)
        pdf.set_text_color(*COR_TEXTO_ESCURO)
        
        try:
            pdf.write_html(html_text)
        except Exception as e:
            logger.warning(f"Fallback no PDF: {e}")
            pdf.multi_cell(0, 6, texto_md)
            
        pdf.ln(8)

        # Imagem (Gráfico)
        # Imagem (Gráfico Dinâmico e Responsivo)
        if caminho_imagem and os.path.exists(caminho_imagem):
            # 1. Calcula o espaço restante na página atual (Altura total - Margem Inferior - Posição Y Atual)
            espaco_restante_y = (pdf.h - pdf.b_margin) - pdf.get_y()
            
            # Define o tamanho ideal que gostaríamos que o gráfico tivesse (80% da largura da folha)
            largura_ideal = pdf.epw * 0.8
            x_centro = (210 - largura_ideal) / 2
            
            # 2. A Regra Dinâmica:
            # Se sobrou menos de 60mm (6cm), a imagem vai ficar muito esmagada.
            # É melhor quebrar a página e desenhar ela bonita e grande do outro lado.
            if espaco_restante_y < 60:
                logger.debug("Pouco espaço na página. Movendo gráfico para a próxima.")
                pdf.add_page()
                # Na nova página, limitamos a imagem a ocupar no máximo metade da altura
                pdf.image(caminho_imagem, x=x_centro, w=largura_ideal, h=pdf.eph * 0.5, keep_aspect_ratio=True)
            else:
                # 3. Se sobrou espaço suficiente, forçamos a imagem a caber no buraco exato que sobrou, 
                # deixando 10mm de respiro em baixo.
                logger.debug("Espaço suficiente. Ajustando imagem na mesma página.")
                altura_permitida = espaco_restante_y - 10
                # O keep_aspect_ratio=True impede que o gráfico fique "esticado" ou deformado
                pdf.image(caminho_imagem, x=x_centro, w=largura_ideal, h=altura_permitida, keep_aspect_ratio=True)
            
            pdf.ln(10)

    # ---------------------------------------------------------
    # INSERÇÃO DO SUMÁRIO (Tabela de Conteúdos)
    # ---------------------------------------------------------
    logger.debug("Gerando e inserindo página de Sumário...")
    
    # Criamos uma função temporária para estilizar o título da página do Sumário
    def estilizar_titulo_sumario(pdf_instance):
        pdf_instance.set_font("helvetica", "B", 20)
        pdf_instance.set_text_color(*COR_TEXTO_ESCURO)
        # Modernizado ln=True
        pdf_instance.cell(0, 15, "Conteúdo Detalhado", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf_instance.ln(10)

    # Insere o ToC na página 2 (após a capa do resumo geral)
    try:
        pdf.insert_toc_page(
            page_number=2,
            title_render_function=estilizar_titulo_sumario,
        )
    except Exception as e:
        logger.warning(f"Não foi possível gerar a página de Sumário (ToC): {e}. Pulando etapa.")

    try:
        pdf.output(caminho_pdf)
        logger.info(f"PDF Enterprise gerado com sucesso em: {caminho_pdf}")
        return caminho_pdf
    except Exception as e:
        logger.error(f"Erro ao salvar PDF final: {str(e)}")
        return ""

# ==========================================
# TESTE LOCAL MANTIDO
# ==========================================
if __name__ == "__main__":
    from services.chart_service import processar_grafico_para_campo
    print("\n--- INICIANDO TESTE PDF ENTERPRISE (MOTOR CORRIGIDO) ---")
    
    resumo_geral_simulado = """
**Manchete:** O Churn no primeiro mês está em 15%, anulando o recorde de LTV obtido.

**Destaques Operacionais**
* **LTV atingiu R$ 450,00**, aumento de 12% vs. mês anterior.
* **Volume BTC:** Domina 55% das operações, sugerindo foco em campanhas para este par.
    """

    img_pizza = processar_grafico_para_campo("volume_por_ativo", {"BTC": 55, "ETH": 45})
    img_barras = processar_grafico_para_campo("usuarios_ativos_l6m", {"Jan": 100, "Fev": 120})

    payload_detalhado = [
        {"titulo": "Análise da Base de Usuários", "texto_md": "O Churn de 15%...", "imagem": img_barras},
        {"titulo": "Distribuição de Volume", "texto_md": "Volume BTC/ETH...", "imagem": img_pizza}
    ]

    caminho = gerar_pdf_relatorio(resumo_geral_simulado, payload_detalhado, "relatorio_enterprise.pdf")

    if caminho:
        print(f"✅ Sucesso! Abra o arquivo: '{caminho}'")
    else:
        print("❌ Falha na geração do PDF.")