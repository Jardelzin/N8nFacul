"""
engine.py — Motor de Orquestração do Agente Educacional

Coordena o pipeline completo:
  1. Carrega e processa os dados  (cleaner.py)
  2. Gera análises e rankings     (analyzer.py)
  3. Exporta CSV final consolidado
  4. Exporta JSON com insights para a OpenAI / n8n
  5. Gera o prompt estruturado para a API da OpenAI

Uso via CLI (compatível com n8n Execute Command):
    python src/engine.py
    python src/engine.py --paises BRA,USA,FIN --output data/

Autor: Agente Inteligente de Monitoramento Educacional
"""

import json
import os
import sys
import argparse
from datetime import datetime

import pandas as pd

# Garantir que o diretório src esteja no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cleaner import processar_pipeline, PAISES_PADRAO, INDICADORES_PADRAO
from analyzer import gerar_insights_completos, calcular_crescimento


# ─────────────────────────────────────────────────────────────
# Exportação de resultados
# ─────────────────────────────────────────────────────────────

def exportar_csv_final(df_crescimento: pd.DataFrame, caminho_saida: str) -> str:
    """
    Exporta CSV consolidado com rankings e métricas de crescimento.

    Args:
        df_crescimento: DataFrame gerado por ``calcular_crescimento``.
        caminho_saida: Diretório de destino.

    Returns:
        Caminho absoluto do CSV gerado.
    """
    arquivo = os.path.join(caminho_saida, 'educacao_ranking_final.csv')

    df_exp = df_crescimento.copy()
    df_exp['indicador_nome'] = df_exp['Indicator Code'].map(
        lambda x: INDICADORES_PADRAO.get(x, x)
    )

    colunas = [
        'Country Code', 'Country Name', 'Indicator Code', 'indicador_nome',
        'valor_inicial', 'valor_final', 'variacao_pct',
        'ano_inicial', 'ano_final', 'periodo',
    ]
    df_exp = df_exp[[c for c in colunas if c in df_exp.columns]]
    df_exp = df_exp.sort_values(
        ['Indicator Code', 'variacao_pct'], ascending=[True, False]
    )

    df_exp.to_csv(arquivo, index=False, encoding='utf-8-sig')
    print(f"\n💾 CSV final exportado: {arquivo}")
    print(f"   → {len(df_exp)} registros salvos")
    return arquivo


def exportar_json_insights(insights: dict, caminho_saida: str) -> str:
    """Exporta os insights em JSON para o n8n / OpenAI."""
    arquivo = os.path.join(caminho_saida, 'insights_input.json')
    with open(arquivo, 'w', encoding='utf-8') as f:
        json.dump(insights, f, indent=2, ensure_ascii=False, default=str)
    print(f"📄 JSON de insights exportado: {arquivo}")
    return arquivo


# ─────────────────────────────────────────────────────────────
# Prompt para OpenAI
# ─────────────────────────────────────────────────────────────

def gerar_prompt_openai(insights: dict) -> str:
    """
    Cria o prompt que instrui a OpenAI a **analisar** os dados
    (não apenas resumir números).
    """
    return f"""Você é um analista sênior de políticas educacionais internacionais.

Com base nos dados do World Bank Education Statistics (EdStats), analise as
informações abaixo e produza um **relatório executivo em português brasileiro**.

## DADOS PARA ANÁLISE

### Resumo Geral
{json.dumps(insights['resumo_geral'], indent=2, ensure_ascii=False)}

### Rankings por Indicador
{json.dumps(insights['rankings'], indent=2, ensure_ascii=False)}

### Crescimento por País
{json.dumps(insights['crescimento_por_pais'], indent=2, ensure_ascii=False)}

### Alertas Identificados
{json.dumps(insights['alertas'], indent=2, ensure_ascii=False)}

## INSTRUÇÕES PARA A ANÁLISE

Produza um relatório com as seguintes seções:

1. **Panorama Geral** — visão macro dos dados analisados.
2. **Países que Mais Evoluíram** — identifique os 3 melhores e explique possíveis
   fatores (investimento, reformas, contexto socioeconômico).
3. **Países Estagnados ou em Declínio** — desempenho preocupante e possíveis causas.
4. **Relação Investimento × Resultados** — maior investimento correlaciona com
   melhores indicadores?
5. **Destaques por Indicador** — insights específicos para cada indicador.
6. **Recomendações de Políticas Públicas** — ações concretas para países com
   indicadores baixos.
7. **Tendências Futuras** — projeções baseadas nos dados históricos.

IMPORTANTE:
- NÃO apenas repita números. Produza ANÁLISE e INTELIGÊNCIA.
- Compare países entre si e identifique padrões.
- Sugira explicações com contexto geopolítico e histórico.
- Linguagem executiva, adequada para tomadores de decisão.
"""


# ─────────────────────────────────────────────────────────────
# Função principal
# ─────────────────────────────────────────────────────────────

def main():
    """Executa o pipeline completo via linha de comando."""

    parser = argparse.ArgumentParser(
        description='Agente Inteligente de Monitoramento Educacional',
    )
    parser.add_argument(
        '--paises', type=str, default=None,
        help='Códigos ISO separados por vírgula (ex: BRA,USA,FIN)',
    )
    parser.add_argument(
        '--indicadores', type=str, default=None,
        help='Códigos de indicadores separados por vírgula',
    )
    parser.add_argument(
        '--dataset', type=str, default=None,
        help='Caminho para EdStatsData.csv',
    )
    parser.add_argument(
        '--output', type=str, default=None,
        help='Diretório de saída',
    )
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_csv = args.dataset or os.path.join(base_dir, 'data', 'EdStatsData.csv')
    caminho_saida = args.output or os.path.join(base_dir, 'data')
    os.makedirs(caminho_saida, exist_ok=True)

    paises = args.paises.split(',') if args.paises else PAISES_PADRAO
    indicadores = (
        args.indicadores.split(',') if args.indicadores
        else list(INDICADORES_PADRAO.keys())
    )

    print("=" * 60)
    print("🎓 AGENTE INTELIGENTE DE MONITORAMENTO EDUCACIONAL")
    print(f"   Data/hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 1. Pipeline de processamento
    df_proc, colunas_anos = processar_pipeline(caminho_csv, paises, indicadores)

    # 2. Insights e rankings
    insights, df_cresc = gerar_insights_completos(df_proc, colunas_anos, paises)

    # 3. CSV final
    arq_csv = exportar_csv_final(df_cresc, caminho_saida)

    # 4. JSON para n8n / OpenAI
    arq_json = exportar_json_insights(insights, caminho_saida)

    # 5. Prompt OpenAI
    prompt = gerar_prompt_openai(insights)
    arq_prompt = os.path.join(caminho_saida, 'prompt_openai.txt')
    with open(arq_prompt, 'w', encoding='utf-8') as f:
        f.write(prompt)
    print(f"📝 Prompt OpenAI salvo: {arq_prompt}")

    # Resumo final
    print(f"\n{'=' * 60}")
    print("🏁 EXECUÇÃO FINALIZADA COM SUCESSO!")
    print(f"   📊 CSV Final      : {arq_csv}")
    print(f"   📄 JSON Insights  : {arq_json}")
    print(f"   📝 Prompt OpenAI  : {arq_prompt}")
    print(f"{'=' * 60}")

    return insights, df_cresc


if __name__ == "__main__":
    main()
