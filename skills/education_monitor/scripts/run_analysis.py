#!/usr/bin/env python
"""
run_analysis.py — Script auxiliar da Skill education_monitor.

Permite executar a análise de forma programática (importável)
ou via CLI pelo n8n / agentes de código.
"""

import os
import sys

# Adicionar raiz do projeto ao path
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from cleaner import processar_pipeline, PAISES_PADRAO, INDICADORES_PADRAO
from analyzer import gerar_insights_completos
from engine import exportar_csv_final, exportar_json_insights, gerar_prompt_openai


def executar_skill(
    paises: list = None,
    indicadores: list = None,
    caminho_csv: str = None,
    caminho_saida: str = None,
) -> dict:
    """
    Ponto de entrada da skill: executa o pipeline completo e retorna
    os insights como dicionário Python.

    Args:
        paises: Lista de códigos ISO-3 de países.
        indicadores: Lista de códigos de indicadores.
        caminho_csv: Caminho para o dataset CSV.
        caminho_saida: Diretório de saída.

    Returns:
        Dicionário com insights, rankings e alertas.
    """
    paises = paises or PAISES_PADRAO
    indicadores = indicadores or list(INDICADORES_PADRAO.keys())
    caminho_csv = caminho_csv or os.path.join(ROOT, 'data', 'EdStatsData.csv')
    caminho_saida = caminho_saida or os.path.join(ROOT, 'data')

    os.makedirs(caminho_saida, exist_ok=True)

    # Pipeline
    df, anos = processar_pipeline(caminho_csv, paises, indicadores)
    insights, df_cresc = gerar_insights_completos(df, anos, paises)

    # Exportações
    exportar_csv_final(df_cresc, caminho_saida)
    exportar_json_insights(insights, caminho_saida)

    # Prompt
    prompt = gerar_prompt_openai(insights)
    with open(os.path.join(caminho_saida, 'prompt_openai.txt'), 'w', encoding='utf-8') as f:
        f.write(prompt)

    return insights


if __name__ == "__main__":
    resultado = executar_skill()
    print(f"\n✅ Skill executada — {resultado['resumo_geral']['total_alertas']} alertas gerados")
