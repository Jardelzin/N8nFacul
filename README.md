# 🎓 Agente Inteligente de Monitoramento Educacional

> Pipeline completo de coleta, tratamento, análise e geração de relatórios educacionais com IA, utilizando dados do **World Bank Education Statistics (EdStats)**.

---

## 📋 Visão Geral

Uma organização internacional deseja acompanhar continuamente a evolução dos indicadores educacionais de diversos países. Este projeto automatiza todo o fluxo:

1. **Coleta** — utiliza o dataset público [EdStats do Kaggle](https://www.kaggle.com/datasets/theworldbank/world-bank-edstats)
2. **Processamento** — limpeza, tratamento de nulos, filtragem e rankings com Python (pandas/numpy)
3. **Análise com IA** — prompt estruturado para OpenAI (GPT-4o) que produz **inteligência analítica**, não apenas resumo de números
4. **Orquestração** — workflow n8n que automatiza gatilho → script → IA → armazenamento
5. **Visualização** — dashboard interativo com Streamlit

---

## 🗂️ Estrutura do Projeto

```
N8nFacul/
├── data/                          # Dados (CSV do Kaggle + saídas geradas)
│   ├── .gitkeep
│   ├── EdStatsData.csv            # ← Baixar do Kaggle (não versionado)
│   ├── educacao_ranking_final.csv # Saída: CSV consolidado
│   ├── insights_input.json        # Saída: insights para IA
│   └── prompt_openai.txt          # Saída: prompt para OpenAI
│
├── src/                           # Código Python principal
│   ├── __init__.py
│   ├── cleaner.py                 # Limpeza, filtragem, tratamento de nulos
│   ├── analyzer.py                # Rankings, crescimento, comparações, alertas
│   └── engine.py                  # Orquestrador do pipeline completo
│
├── n8n/                           # Workflow de orquestração
│   └── workflow.json              # Importar no n8n
│
├── skills/                        # Skills versionadas
│   ├── education_monitor/         # Skill principal de monitoramento
│   │   ├── SKILL.md
│   │   └── scripts/
│   │       └── run_analysis.py
│   └── data_enrichment/           # Skill de enriquecimento de dados
│       ├── SKILL.md
│       └── scripts/
│           └── enrich_data.py
│
├── dashboard/                     # Dashboard visual
│   └── app.py                     # Streamlit
│
├── .env.example                   # Variáveis de ambiente (modelo)
├── .gitignore
├── requirements.txt
└── README.md                      # ← Você está aqui
```

---

## 🚀 Como Executar

### 1. Pré-requisitos

- Python 3.10+
- n8n (para orquestração)
- Chave de API da OpenAI

### 2. Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/N8nFacul.git
cd N8nFacul

# Criar ambiente virtual
python -m venv env
env\Scripts\activate    # Windows
# source env/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 3. Baixar o Dataset

Baixe o dataset do Kaggle e coloque em `data/EdStatsData.csv`:

```bash
# Via Kaggle CLI (se configurado)
kaggle datasets download -d theworldbank/world-bank-edstats -p data/ --unzip
```

Ou baixe manualmente de: https://www.kaggle.com/datasets/theworldbank/world-bank-edstats

### 4. Executar o Pipeline Python

```bash
# Análise padrão (10 países, 8 indicadores)
python src/engine.py

# Personalizar países
python src/engine.py --paises BRA,USA,FIN,CHN

# Ver todas as opções
python src/engine.py --help
```

### 5. Executar o Dashboard

```bash
streamlit run dashboard/app.py
```

### 6. Executar o Workflow n8n

1. Abra o n8n no navegador
2. Importe o arquivo `n8n/workflow.json`
3. Configure a credencial da OpenAI (HTTP Header Auth com `Authorization: Bearer sk-...`)
4. Configure a variável de ambiente `PROJECT_DIR` com o caminho do projeto
5. Execute manualmente ou aguarde o gatilho semanal

---

## 🐍 Operações Python Implementadas

| # | Operação | Módulo | Descrição |
|---|----------|--------|-----------|
| 1 | Limpeza de dados | `cleaner.py` | Remove duplicatas, colunas vazias, padroniza tipos |
| 2 | Tratamento de valores ausentes | `cleaner.py` | Interpolação linear + forward fill + média histórica |
| 3 | Filtragem | `cleaner.py` | Seleção por países (ISO-3) e indicadores |
| 4 | Cálculo de crescimento | `analyzer.py` | Variação percentual entre primeiro e último valor |
| 5 | Geração de rankings | `analyzer.py` | Ranking por valor atual e por evolução |
| 6 | Comparação entre países | `analyzer.py` | Tabela pivotada (anos × países) para gráficos |
| 7 | Alertas automáticos | `analyzer.py` | Detecta estagnação, queda e destaques positivos |
| 8 | Exportação CSV final | `engine.py` | CSV consolidado com todas as métricas |

---

## 🤖 Análise com IA (OpenAI)

A IA **não apenas resume números** — ela produz **inteligência analítica**:

- 🏆 **Quais países evoluíram mais** e por quê
- ⚠️ **Quais estão estagnados** e possíveis causas
- 💰 **Relação investimento × resultados**
- 📊 **Destaques por indicador** com contexto histórico
- 💡 **Recomendações de políticas públicas**
- 🔮 **Tendências futuras** baseadas nos dados

O prompt é gerado automaticamente pelo `engine.py` e salvo em `data/prompt_openai.txt`.

---

## ⚡ Workflow n8n

O workflow (`n8n/workflow.json`) implementa o fluxo completo:

```
┌──────────────┐    ┌───────────────────┐    ┌──────────────┐
│ Gatilho       │───▶│ Executar Python    │───▶│ Ler JSON     │
│ (Manual/Cron) │    │ (src/engine.py)    │    │ (insights)   │
└──────────────┘    └───────────────────┘    └──────┬───────┘
                                                     │
                    ┌───────────────────┐    ┌───────▼───────┐
                    │ Salvar Relatório   │◀──│ OpenAI GPT-4o │
                    │ (relatorio_ia.md)  │   │ (análise)     │
                    └───────────────────┘    └───────────────┘
```

**Nós do workflow:**
1. **Gatilho Manual** — para execuções sob demanda
2. **Gatilho Semanal** — automação periódica
3. **Execute Command** — roda o script Python
4. **Read File** — lê o JSON de insights
5. **HTTP Request** — chama a API da OpenAI
6. **Code** — formata o relatório
7. **Write File** — salva o relatório em Markdown

---

## 🧩 Skills

### education_monitor
Skill principal que encapsula todo o pipeline de análise educacional.
Pode ser invocada por agentes de código ou pelo n8n.

→ Ver: [`skills/education_monitor/SKILL.md`](skills/education_monitor/SKILL.md)

### data_enrichment
Skill de enriquecimento que adiciona metadados regionais (continente, 
faixa de renda, OCDE) para análises segmentadas.

→ Ver: [`skills/data_enrichment/SKILL.md`](skills/data_enrichment/SKILL.md)

---

## 📊 Dashboard (Bônus)

Dashboard interativo com Streamlit que inclui:

- 📈 **Evolução temporal** — gráficos de linha por indicador
- 🏆 **Rankings** — barras comparativas por valor atual e evolução
- ⚠️ **Alertas** — tabela filtrada de situações de atenção
- 🤖 **Relatório IA** — visualização do relatório gerado pela OpenAI
- 📋 **Dados brutos** — tabela interativa com download CSV

```bash
streamlit run dashboard/app.py
```

---

## 🤖 Como o Codex (ou Claude Code) foi utilizado

Durante o desenvolvimento deste projeto, um **agente de IA no VS Code** (atuando como Engenheiro de Dados e IA) foi utilizado extensivamente para acelerar e melhorar a qualidade do código. As principais tarefas realizadas com auxílio do agente foram:

### 1. Criação de Funções Python
O agente gerou funções completas para o pipeline de dados, incluindo:
- `limpar_dados()` — limpeza com remoção de duplicatas e colunas vazias
- `tratar_valores_ausentes()` — estratégia em 3 camadas (interpolação, forward fill, média)
- `filtrar_dados()` — filtragem flexível por países e indicadores
- `calcular_crescimento()` — cálculo de variação percentual entre períodos
- `gerar_ranking()` — geração de rankings ordenados por múltiplas métricas
- `comparar_paises()` — tabela pivotada para comparação temporal
- `gerar_insights_completos()` — montagem do dicionário de insights para IA
- `exportar_csv_final()` — exportação CSV consolidado
- `gerar_prompt_openai()` — geração do prompt analítico

### 2. Geração de Documentação
- Criou docstrings detalhadas para todas as funções (Google-style)
- Gerou este README completo com instruções de uso
- Documentou as Skills (`SKILL.md`) com tabelas de capacidades
- Criou o arquivo `.env.example` com comentários explicativos

### 3. Refatoração de Código
- Reorganizou o código original (que tinha apenas 3 operações) em um pipeline modular com 8 operações
- Separou responsabilidades em módulos claros (`cleaner`, `analyzer`, `engine`)
- Adicionou argumentos CLI (`argparse`) para flexibilidade
- Implementou constantes globais (`INDICADORES_PADRAO`, `PAISES_PADRAO`) para evitar hardcoding
- Adicionou tratamento de erros e mensagens de progresso com emojis

### 4. Criação de Scripts Auxiliares
- `skills/education_monitor/scripts/run_analysis.py` — ponto de entrada da skill
- `skills/data_enrichment/scripts/enrich_data.py` — enriquecimento com metadados regionais
- Dashboard completo com Streamlit (`dashboard/app.py`)

### 5. Geração do Workflow n8n
- Criou o `workflow.json` completo com todos os nós necessários
- Configurou o prompt para a OpenAI que solicita **análise inteligente** (não apenas resumo)
- Implementou nó de formatação (Code) para adicionar metadados ao relatório

### 6. Identificação de Melhorias
- Identificou que o código original não tinha ranking nem exportação CSV
- Sugeriu a adição de alertas automáticos (estagnação, queda, destaque)
- Propôs o sistema de Skills para organizar capacidades reutilizáveis
- Recomendou a separação de metadados regionais em uma skill dedicada

---

## 📦 Indicadores Analisados

| Código | Descrição |
|--------|-----------|
| `SE.XPD.TOTL.GD.ZS` | Investimento em Educação (% PIB) |
| `SE.ADT.LITR.ZS` | Taxa de Alfabetização Adulta (%) |
| `SE.ADT.1524.LT.ZS` | Taxa de Alfabetização Jovem (%) |
| `SE.PRM.ENRR` | Matrícula Ensino Primário (% bruto) |
| `SE.SEC.ENRR` | Matrícula Ensino Secundário (% bruto) |
| `SE.TER.ENRR` | Matrícula Ensino Superior (% bruto) |
| `SE.PRM.CMPT.ZS` | Taxa de Conclusão Ensino Primário (%) |
| `SE.SEC.CMPT.LO.ZS` | Taxa de Conclusão Ensino Secundário Inferior (%) |

## 🌎 Países Padrão

| Código | País |
|--------|------|
| BRA | Brasil |
| USA | Estados Unidos |
| FIN | Finlândia |
| CHN | China |
| DEU | Alemanha |
| JPN | Japão |
| ZAF | África do Sul |
| IND | Índia |
| ARG | Argentina |
| KOR | Coreia do Sul |

---

## 📄 Licença

Projeto acadêmico — Desafio Acelera AI.

## 👤 Autor

Desenvolvido como projeto do programa Acelera AI — 2º Desafio.
