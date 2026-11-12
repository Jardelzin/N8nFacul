---
name: data-enrichment
description: >
  Skill de Enriquecimento de Dados — complementa o dataset EdStats com
  metadados adicionais (região, faixa de renda, continente) para
  possibilitar análises mais ricas e segmentadas.
version: "1.0.0"
author: Agente Inteligente de Monitoramento Educacional
tags:
  - enriquecimento
  - metadados
  - world-bank
---

# 🌍 Skill: Data Enrichment

## Objetivo

Enriquecer os dados educacionais do World Bank com metadados contextuais
que permitem análises segmentadas por região geográfica e faixa de renda.

## Capacidades

1. **Classificação por Região** — agrupa países por continente / região
   geográfica (América Latina, Europa, Ásia, África, etc.).
2. **Classificação por Renda** — categoriza países pela faixa de renda
   do World Bank (Low Income, Lower Middle, Upper Middle, High Income).
3. **Agregações regionais** — calcula médias e medianas por região para
   cada indicador educacional.
4. **Exportação enriquecida** — gera CSV com colunas adicionais de
   contexto.

## Como usar

```python
from skills.data_enrichment.scripts.enrich_data import enriquecer_dataset

df_enriquecido = enriquecer_dataset(df_original)
```

Ou via CLI:

```bash
python skills/data_enrichment/scripts/enrich_data.py
```

## Metadados adicionados

| Coluna         | Tipo   | Descrição                                   |
|----------------|--------|---------------------------------------------|
| `regiao`       | str    | Região geográfica (ex: América do Sul)      |
| `continente`   | str    | Continente (ex: Américas, Europa, Ásia)     |
| `faixa_renda`  | str    | Classificação do World Bank                 |
| `is_oecd`      | bool   | Se o país é membro da OCDE                  |
