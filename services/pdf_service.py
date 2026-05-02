import os
import markdown
from fpdf import FPDF, XPos, YPos # Importamos os posicionadores modernos
from utils.logger import configurar_logger

logger = configurar_logger(__name__)

COR_AZUL = (0, 71, 171)
COR_TEXTO_ESCURO = (40, 40, 40)
COR_TEXTO_CLARO = (80, 80, 80)
COR_LINHA = (200, 200, 200)

class RelatorioEnterprisePDF(FPDF):
    def header(self):
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
    
    pdf.set_font("helvetica", "B", 26)
    pdf.set_text_color(*COR_AZUL)
    pdf.cell(0, 20, "SUMÁRIO EXECUTIVO", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_font("helvetica", "I", 12)
    pdf.set_text_color(*COR_TEXTO_CLARO)
    pdf.cell(0, 10, "Análise Transversal de Performance - Maio/2026", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.set_draw_color(*COR_LINHA)
    pdf.line(10, 50, 200, 50)
    pdf.ln(15)

    html_resumo = markdown.markdown(resumo_geral_md)
    pdf.set_font("helvetica", size=12)
    pdf.set_text_color(*COR_TEXTO_ESCURO)
    pdf.write_html(html_resumo) 

    # ---------------------------------------------------------
    # CONTEÚDO DETALHADO (Alimentando o orquestrador do Sumário)
    # ---------------------------------------------------------

    for secao in conteudo_secoes:
        titulo = secao.get("titulo", "Análise")
        texto_md = secao.get("texto_md", "")
        caminho_imagem = secao.get("imagem", "")

        pdf.add_page()
        
        pdf.set_font("helvetica", "B", 14)
        pdf.set_text_color(*COR_AZUL)
        
        pdf.cell(0, 10, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        
        pdf.start_section(titulo) 
        
        pdf.ln(5)

        html_text = markdown.markdown(texto_md)
        pdf.set_font("helvetica", size=11)
        pdf.set_text_color(*COR_TEXTO_ESCURO)
        
        try:
            pdf.write_html(html_text)
        except Exception as e:
            logger.warning(f"Fallback no PDF: {e}")
            pdf.multi_cell(0, 6, texto_md)
            
        pdf.ln(8)


        if caminho_imagem and os.path.exists(caminho_imagem):
            espaco_restante_y = (pdf.h - pdf.b_margin) - pdf.get_y()
            
            largura_ideal = pdf.epw * 0.8
            x_centro = (210 - largura_ideal) / 2
            
            if espaco_restante_y < 60:
                logger.debug("Pouco espaço na página. Movendo gráfico para a próxima.")
                pdf.add_page()
                pdf.image(caminho_imagem, x=x_centro, w=largura_ideal, h=pdf.eph * 0.5, keep_aspect_ratio=True)
            else:
                logger.debug("Espaço suficiente. Ajustando imagem na mesma página.")
                altura_permitida = espaco_restante_y - 10
                pdf.image(caminho_imagem, x=x_centro, w=largura_ideal, h=altura_permitida, keep_aspect_ratio=True)
            
            pdf.ln(10)



    logger.debug("Gerando e inserindo página de Sumário...")
    
    def estilizar_titulo_sumario(pdf_instance):
        pdf_instance.set_font("helvetica", "B", 20)
        pdf_instance.set_text_color(*COR_TEXTO_ESCURO)
        pdf_instance.cell(0, 15, "Conteúdo Detalhado", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf_instance.ln(10)

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
