---
name: education-monitor
description: >
  Skill de Monitoramento Educacional — processa dados do World Bank EdStats,
  gera rankings, comparações entre países e insights estruturados para
  análise por IA (OpenAI).  Pode ser invocada por agentes de código (Codex,
  Claude Code) ou pelo workflow n8n.
version: "1.0.0"
author: Agente Inteligente de Monitoramento Educacional
tags:
  - educação
  - world-bank
  - data-engineering
  - analytics
---

# 🎓 Skill: Education Monitor

## Objetivo

Automatizar a análise de indicadores educacionais globais a partir do dataset
**World Bank Education Statistics (EdStats)**.

## Capacidades

| #  | Capacidade                          | Módulo            |
|----|-------------------------------------|-------------------|
| 1  | Limpeza de dados                    | `src/cleaner.py`  |
| 2  | Tratamento de valores ausentes      | `src/cleaner.py`  |
| 3  | Filtragem por países e indicadores  | `src/cleaner.py`  |
| 4  | Geração de rankings                 | `src/analyzer.py` |
| 5  | Cálculo de crescimento              | `src/analyzer.py` |
| 6  | Comparação entre países             | `src/analyzer.py` |
| 7  | Alertas automáticos                 | `src/analyzer.py` |
| 8  | Exportação CSV final                | `src/engine.py`   |
| 9  | Geração de prompt para OpenAI       | `src/engine.py`   |
| 10 | Dashboard visual (Streamlit)        | `dashboard/app.py`|

## Como usar

### Execução direta (CLI)

```bash
# Análise padrão (10 países, 8 indicadores)
python src/engine.py

# Personalizar países e indicadores
python src/engine.py --paises BRA,USA,FIN --output data/

# Todos os parâmetros
python src/engine.py \
  --dataset data/EdStatsData.csv \
  --paises BRA,USA,FIN,CHN \
  --indicadores SE.XPD.TOTL.GD.ZS,SE.ADT.LITR.ZS \
  --output data/
```

### Execução via n8n

Importe `n8n/workflow.json` no n8n. O workflow:

1. **Gatilho** (manual ou semanal)
2. **Execute Command** → roda `python src/engine.py`
3. **Read File** → lê `data/insights_input.json`
4. **HTTP Request** → envia para API OpenAI (GPT-4o)
5. **Write File** → salva relatório em `data/relatorio_ia.md`

### Dashboard

```bash
streamlit run dashboard/app.py
```

## Indicadores suportados

| Código                 | Descrição                                      |
|------------------------|-------------------------------------------------|
| `SE.XPD.TOTL.GD.ZS`   | Investimento em Educação (% PIB)               |
| `SE.ADT.LITR.ZS`      | Taxa de Alfabetização Adulta (%)               |
| `SE.ADT.1524.LT.ZS`   | Taxa de Alfabetização Jovem (%)                |
| `SE.PRM.ENRR`          | Matrícula Ensino Primário (% bruto)            |
| `SE.SEC.ENRR`          | Matrícula Ensino Secundário (% bruto)          |
| `SE.TER.ENRR`          | Matrícula Ensino Superior (% bruto)            |
| `SE.PRM.CMPT.ZS`       | Taxa de Conclusão Ensino Primário (%)          |
| `SE.SEC.CMPT.LO.ZS`    | Taxa de Conclusão Ensino Secundário Inferior (%)|

## Países padrão

`BRA`, `USA`, `FIN`, `CHN`, `DEU`, `JPN`, `ZAF`, `IND`, `ARG`, `KOR`

## Saídas

| Arquivo                          | Formato | Descrição                                 |
|----------------------------------|---------|-------------------------------------------|
| `data/educacao_ranking_final.csv`| CSV     | Rankings e métricas consolidadas          |
| `data/insights_input.json`       | JSON    | Insights estruturados para IA             |
| `data/prompt_openai.txt`         | TXT     | Prompt pronto para API OpenAI             |
| `data/relatorio_ia.md`           | MD      | Relatório gerado pela IA (via n8n)        |

## Pré-requisitos

- Python 3.10+
- Dataset: `data/EdStatsData.csv` (baixar do [Kaggle](https://www.kaggle.com/datasets/theworldbank/world-bank-edstats))
- Dependências: `pip install -r requirements.txt`
