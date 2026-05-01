# Relatório usando AI

Criação de um relatório usando LangChain e Gemini para uma linguagem pensada aos C-Levels, contendo todas as informações passadas.

## Estruturação das Pastas

```
meu_projeto/
│
├── main.py                   # Recebe o JSON e chama os services
├── config.py                 # os.environ["GOOGLE_API_KEY"] = ...
│
├── prompts/
│   └── templates.py          # Objetos PromptTemplate do LangChain
│
├── services/
│   ├── gemini_service.py     # Inicializa ChatGoogleGenerativeAI e roda a Chain
│   ├── chart_service.py      # Matplotlib/Seaborn (criação dos gráficos)
│   └── pdf_service.py        # Geração do PDF (HTML -> PDF)
│
└── utils/
    ├── json_parser.py        # Limpeza do JSON
    └── base64_encoder.py     # Conversão final para envio
```