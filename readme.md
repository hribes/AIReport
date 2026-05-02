# RelatAI: Motor de Inteligência Executiva

## Sobre o Projeto
O **RelatorioAI** é um pipeline analítico autônomo focado em Decision Science e automação de relatórios. Este projeto pessoal nasceu da necessidade de transformar dados brutos (JSON) em inteligência acionável sem intervenção manual. 

Ao invés de painéis estáticos, o motor utiliza **LLMs (Large Language Models)** e **Roteamento Semântico** para analisar o contexto das métricas, decidir dinamicamente o melhor formato visual (gráfico de barras, linhas, pizza ou apenas texto), gerar insights executivos e compilar tudo em um documento PDF responsivo. Por fim, o arquivo é codificado em Base64, tornando-o perfeito para ser consumido por APIs, webhooks ou plataformas de automação (como n8n).

## Arquitetura de Pastas

A organização do código foi desenhada com foco em modularidade e responsabilidade única:
```text
RelatorioAI/
│
├── main.py                  # Orquestrador principal (Microserviço)
├── .env                     # Variáveis de ambiente (Chaves de API)
│
├── prompts/                 # Camada de Engenharia de Prompts
│   └── templates.py         # Instruções de sistema, roteamento e templates da IA
│
├── services/                # Camada de Regras de Negócio e Integrações
│   ├── chart_service.py     # Roteador dinâmico e geração de gráficos (Seaborn)
│   ├── gemini_service.py    # Comunicação com a IA (Roteamento semântico e análises)
│   └── pdf_service.py       # Renderização dinâmica do documento e layout responsivo
│
└── utils/                   # Ferramentas de Suporte
    ├── base64_encoder.py    # Conversor de arquivos físicos para string segura
    └── logger.py            # Sistema de telemetria e rastreamento de logs

```

## Arquitetura de Execução
O fluxo de processamento funciona no formato de "Esteira de Inteligência":
- Ingestão de Dados: O sistema recebe um payload dinâmico (JSON) contendo KPIs e métricas agrupadas.

- Roteamento Semântico (Decisão): Antes de desenhar, a IA lê os metadados e decide qual é a melhor representação visual para aquela métrica (Roteamento).

- Análise Generativa: A IA escreve um parecer analítico focado em growth e product para justificar os números.

- Renderização Visual: O Seaborn desenha os gráficos baseados na decisão da etapa 2.

- Síntese Executiva: A IA lê todas as análises geradas e cria um Resumo Geral consolidado.

- Compilação Responsiva: O PDF é gerado ajustando dinamicamente o tamanho das imagens para que acompanhem o texto sem quebrar o layout da página.

- Empacotamento & Limpeza: O PDF é convertido para Base64 (retornado como JSON), e todas as pastas e arquivos temporários são apagados do servidor. (Menos o relatório - Por enquanto)

## Como Executar Localmente
Siga o checklist abaixo para rodar o motor na sua máquina:

### 1. Clone o repositório e acesse a pasta:
``` Bash
git clone [https://github.com/hribes/AIReport.git](https://github.com/hribes/AIReport.git)
cd RelatorioAI
```

### 2. Crie e ative o ambiente virtual:
```Bash
python -m venv .venv

# No Windows:
.venv\Scripts\activate
# No Linux/Mac:
source .venv/bin/activate
```

### 3. Instale as dependências:
```Bash
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente:
Crie um arquivo chamado .env na raiz do projeto e insira a sua chave do Google Gemini:
``` Bash
GOOGLE_API_KEY=sua_chave_aqui
```

### 5. Execute o Orquestrador:
``` Bash
python main.py
```

O terminal exibirá os logs de processamento e retornará um JSON contendo o status de sucesso e o documento codificado.