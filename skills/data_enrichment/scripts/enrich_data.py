#!/usr/bin/env python
"""
enrich_data.py — Enriquece o dataset educacional com metadados regionais.

Adiciona informações de região, continente, faixa de renda e pertencimento
à OCDE para possibilitar análises segmentadas.
"""

import pandas as pd
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ─────────────────────────────────────────────────────────────
# Mapeamentos estáticos (subconjunto dos países-alvo)
# ─────────────────────────────────────────────────────────────

METADADOS_PAISES = {
    'BRA': {'regiao': 'América do Sul',   'continente': 'Américas', 'faixa_renda': 'Upper Middle Income', 'is_oecd': False},
    'USA': {'regiao': 'América do Norte', 'continente': 'Américas', 'faixa_renda': 'High Income',         'is_oecd': True},
    'FIN': {'regiao': 'Europa do Norte',  'continente': 'Europa',   'faixa_renda': 'High Income',         'is_oecd': True},
    'CHN': {'regiao': 'Ásia Oriental',    'continente': 'Ásia',     'faixa_renda': 'Upper Middle Income', 'is_oecd': False},
    'DEU': {'regiao': 'Europa Ocidental', 'continente': 'Europa',   'faixa_renda': 'High Income',         'is_oecd': True},
    'JPN': {'regiao': 'Ásia Oriental',    'continente': 'Ásia',     'faixa_renda': 'High Income',         'is_oecd': True},
    'ZAF': {'regiao': 'África Austral',   'continente': 'África',   'faixa_renda': 'Upper Middle Income', 'is_oecd': False},
    'IND': {'regiao': 'Ásia Meridional',  'continente': 'Ásia',     'faixa_renda': 'Lower Middle Income', 'is_oecd': False},
    'ARG': {'regiao': 'América do Sul',   'continente': 'Américas', 'faixa_renda': 'Upper Middle Income', 'is_oecd': False},
    'KOR': {'regiao': 'Ásia Oriental',    'continente': 'Ásia',     'faixa_renda': 'High Income',         'is_oecd': True},
}


def enriquecer_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adiciona colunas de metadados ao DataFrame com base no ``Country Code``.

    Args:
        df: DataFrame contendo a coluna ``Country Code``.

    Returns:
        DataFrame com colunas extras: ``regiao``, ``continente``,
        ``faixa_renda``, ``is_oecd``.
    """
    print("🌍 Enriquecendo dataset com metadados regionais...")

    meta_df = pd.DataFrame.from_dict(METADADOS_PAISES, orient='index')
    meta_df.index.name = 'Country Code'
    meta_df = meta_df.reset_index()

    df_enr = df.merge(meta_df, on='Country Code', how='left')

    preenchidos = df_enr['regiao'].notna().sum()
    print(f"   → {preenchidos}/{len(df_enr)} registros enriquecidos")
    print("   ✅ Enriquecimento concluído")

    return df_enr


def gerar_agregacoes_regionais(df: pd.DataFrame, colunas_anos: list) -> pd.DataFrame:
    """
    Calcula médias por continente e indicador para cada ano.

    Returns:
        DataFrame com agregações regionais.
    """
    if 'continente' not in df.columns:
        df = enriquecer_dataset(df)

    print("📊 Gerando agregações regionais...")

    agg = df.groupby(['continente', 'Indicator Code'])[colunas_anos].mean()
    agg = agg.reset_index()

    print(f"   ✅ {len(agg)} agregações geradas")
    return agg


if __name__ == "__main__":
    sys.path.insert(0, os.path.join(ROOT, 'src'))
    from cleaner import processar_pipeline, identificar_colunas_anos

    caminho_csv = os.path.join(ROOT, 'data', 'EdStatsData.csv')

    if os.path.exists(caminho_csv):
        df, anos = processar_pipeline(caminho_csv)
        df_enr = enriquecer_dataset(df)
        agg = gerar_agregacoes_regionais(df_enr, anos)
        print(agg.head(10))
    else:
        print(f"⚠️ Dataset não encontrado: {caminho_csv}")
        print("   Baixe de: https://www.kaggle.com/datasets/theworldbank/world-bank-edstats")
