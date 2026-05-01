def extrair_campos_selecionados(payload_front: dict) -> dict:
    """
    Recebe o JSON bruto do front-end e retorna apenas os campos selecionados
    com seus respectivos dados.
    """
    campos_ativos = {}
    
    
    for nome_campo, informacoes in payload_front.items():
        
        if isinstance(informacoes, dict) and informacoes.get("selected") == 1: #Verifica se o 'Selected' é igual a 1
            dados_do_campo = informacoes.get("data", {})
            campos_ativos[nome_campo] = dados_do_campo    
    return campos_ativos




# Teste Local
# if __name__ == "__main__":
#     json_teste = {
#         "vendas_mensais": {
#             "selected": 1, 
#             "data": {"mes": "Janeiro", "valor": 50000}
#         },
#         "taxa_churn": {
#             "selected": 0, 
#             "data": None
#         },
#         "custo_aquisicao": {
#             "selected": 1, 
#             "data": {"campanha": "Google Ads", "custo": 1500}
#         },
#         "campo_sem_data_mas_selecionado": {
#             "selected": 1
#         }
#     }

#     resultado_limpo = extrair_campos_selecionados(json_teste)

#     import json
#     print("\n--- JSON ORIGINAL (FRONT-END) ---")
#     print(f"Total de campos recebidos: {len(json_teste)}")
    
#     print("\n--- JSON LIMPO (PRONTO PARA A IA) ---")
#     print(json.dumps(resultado_limpo, indent=4, ensure_ascii=False))