"""
cleaner.py — Módulo de Limpeza e Pré-processamento de Dados Educacionais

Operações implementadas:
  1. Limpeza de dados (remoção de duplicatas e colunas vazias)
  2. Tratamento de valores ausentes (interpolação + forward fill + média)
  3. Filtragem por países e indicadores selecionados

Autor: Agente Inteligente de Monitoramento Educacional
Dataset: World Bank Education Statistics (EdStats)
"""

import pandas as pd
import numpy as np
import os

# ─────────────────────────────────────────────────────────────
# Constantes globais usadas por todo o projeto
# ─────────────────────────────────────────────────────────────

INDICADORES_PADRAO = {
    'SE.XPD.TOTL.GD.ZS': 'Investimento em Educação (% PIB)',
    'SE.ADT.LITR.ZS': 'Taxa de Alfabetização Adulta (%)',
    'SE.ADT.1524.LT.ZS': 'Taxa de Alfabetização Jovem (%)',
    'SE.PRM.ENRR': 'Matrícula Ensino Primário (% bruto)',
    'SE.SEC.ENRR': 'Matrícula Ensino Secundário (% bruto)',
    'SE.TER.ENRR': 'Matrícula Ensino Superior (% bruto)',
    'SE.PRM.CMPT.ZS': 'Taxa de Conclusão Ensino Primário (%)',
    'SE.SEC.CMPT.LO.ZS': 'Taxa de Conclusão Ensino Secundário Inferior (%)',
}

PAISES_PADRAO = [
    'BRA', 'USA', 'FIN', 'CHN', 'DEU',
    'JPN', 'ZAF', 'IND', 'ARG', 'KOR',
]


# ─────────────────────────────────────────────────────────────
# Funções utilitárias
# ─────────────────────────────────────────────────────────────

def identificar_colunas_anos(df: pd.DataFrame) -> list:
    """Retorna, em ordem, as colunas cujos nomes são anos (ex: '1970', '2020')."""
    return sorted([col for col in df.columns if str(col).strip().isnumeric()])


def carregar_dataset(caminho_csv: str) -> pd.DataFrame:
    """
    Carrega o dataset EdStats a partir de um arquivo CSV.

    Args:
        caminho_csv: Caminho absoluto ou relativo para ``EdStatsData.csv``.

    Returns:
        DataFrame bruto do dataset.

    Raises:
        FileNotFoundError: Se o arquivo CSV não for encontrado.
    """
    if not os.path.exists(caminho_csv):
        raise FileNotFoundError(
            f"Dataset não encontrado em: {caminho_csv}\n"
            "Baixe de: https://www.kaggle.com/datasets/theworldbank/world-bank-edstats"
        )

    print(f"📂 Carregando dataset de: {caminho_csv}")
    df = pd.read_csv(caminho_csv, low_memory=False)
    print(f"   → {df.shape[0]:,} linhas × {df.shape[1]} colunas carregadas")
    return df


# ─────────────────────────────────────────────────────────────
# OPERAÇÃO 1 — Limpeza de dados
# ─────────────────────────────────────────────────────────────

def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove duplicatas, colunas 100 % nulas e padroniza tipos.

    Args:
        df: DataFrame bruto.

    Returns:
        DataFrame limpo.
    """
    print("\n🧹 Etapa 1: Limpeza de dados...")

    # Padronizar nomes de colunas
    df.columns = df.columns.str.strip()

    # Remover linhas duplicadas
    linhas_antes = len(df)
    df = df.drop_duplicates()
    print(f"   → {linhas_antes - len(df)} linhas duplicadas removidas")

    # Remover colunas totalmente vazias
    colunas_antes = len(df.columns)
    df = df.dropna(axis=1, how='all')
    print(f"   → {colunas_antes - len(df.columns)} colunas vazias removidas")

    # Converter colunas de anos para numérico
    colunas_anos = identificar_colunas_anos(df)
    for col in colunas_anos:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    print(f"   → {len(colunas_anos)} colunas de anos convertidas para numérico")

    print(f"   ✅ Limpeza concluída: {df.shape[0]:,} linhas × {df.shape[1]} colunas")
    return df


# ─────────────────────────────────────────────────────────────
# OPERAÇÃO 2 — Tratamento de valores ausentes
# ─────────────────────────────────────────────────────────────

def tratar_valores_ausentes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preenche valores ausentes em três camadas:

    1. Interpolação linear ao longo do tempo.
    2. Forward fill + backward fill nas extremidades.
    3. Média global do indicador como último recurso.

    Args:
        df: DataFrame filtrado.

    Returns:
        DataFrame com lacunas tratadas.
    """
    print("\n🔧 Etapa 2: Tratamento de valores ausentes...")

    colunas_anos = identificar_colunas_anos(df)
    if not colunas_anos:
        print("   ⚠️ Nenhuma coluna de ano encontrada")
        return df

    nulos_antes = df[colunas_anos].isna().sum().sum()

    # Camadas 1 e 2 — por linha (série temporal de cada registro)
    for idx in df.index:
        serie = df.loc[idx, colunas_anos].astype(float)
        serie = serie.interpolate(method='linear', limit_direction='both')
        serie = serie.ffill().bfill()
        df.loc[idx, colunas_anos] = serie

    # Camada 3 — média do indicador
    for indicador in df['Indicator Code'].unique():
        mask = df['Indicator Code'] == indicador
        media = df.loc[mask, colunas_anos].mean().mean()
        if not np.isnan(media):
            df.loc[mask, colunas_anos] = df.loc[mask, colunas_anos].fillna(media)

    nulos_depois = df[colunas_anos].isna().sum().sum()
    print(f"   → Valores nulos: {nulos_antes:,} → {nulos_depois:,} "
          f"({nulos_antes - nulos_depois:,} tratados)")
    print("   ✅ Tratamento concluído")
    return df


# ─────────────────────────────────────────────────────────────
# OPERAÇÃO 3 — Filtragem (países + indicadores)
# ─────────────────────────────────────────────────────────────

def filtrar_dados(
    df: pd.DataFrame,
    paises: list = None,
    indicadores: list = None,
) -> pd.DataFrame:
    """
    Filtra o dataset por países e indicadores de interesse.

    Args:
        df: DataFrame limpo.
        paises: Códigos ISO-3 (``['BRA', 'USA', ...]``).
        indicadores: Códigos de indicadores do World Bank.

    Returns:
        DataFrame filtrado.
    """
    print("\n🔍 Etapa 3: Filtragem de dados...")

    paises = paises or PAISES_PADRAO
    indicadores = indicadores or list(INDICADORES_PADRAO.keys())

    df_f = df[df['Country Code'].isin(paises)].copy()
    print(f"   → Filtrados {len(paises)} países: {', '.join(paises)}")

    df_f = df_f[df_f['Indicator Code'].isin(indicadores)].copy()
    print(f"   → Filtrados {len(indicadores)} indicadores")

    # Descartar colunas de anos que ficaram 100 % nulas após filtro
    df_f = df_f.dropna(axis=1, how='all')
    anos_restantes = identificar_colunas_anos(df_f)

    print(f"   ✅ Resultado: {df_f.shape[0]} registros, "
          f"anos {anos_restantes[0] if anos_restantes else '?'}"
          f"–{anos_restantes[-1] if anos_restantes else '?'}")
    return df_f


# ─────────────────────────────────────────────────────────────
# Pipeline completo
# ─────────────────────────────────────────────────────────────

def processar_pipeline(
    caminho_csv: str,
    paises: list = None,
    indicadores: list = None,
) -> tuple:
    """
    Pipeline ponta-a-ponta: Carregar → Limpar → Filtrar → Tratar nulos.

    Returns:
        ``(DataFrame processado, lista de colunas de anos)``
    """
    df = carregar_dataset(caminho_csv)
    df = limpar_dados(df)
    df = filtrar_dados(df, paises, indicadores)
    df = tratar_valores_ausentes(df)

    colunas_anos = identificar_colunas_anos(df)

    print(f"\n{'=' * 60}")
    print("✅ PIPELINE COMPLETO")
    print(f"   Registros: {len(df)}")
    print(f"   Países:    {df['Country Code'].nunique()}")
    print(f"   Indicadores: {df['Indicator Code'].nunique()}")
    if colunas_anos:
        print(f"   Período:   {colunas_anos[0]} – {colunas_anos[-1]}")
    print(f"{'=' * 60}")

    return df, colunas_anos


# ─────────────────────────────────────────────────────────────
# Execução direta (teste)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho = os.path.join(base_dir, 'data', 'EdStatsData.csv')

    df_result, anos = processar_pipeline(caminho)
    print("\nAmostra dos dados processados:")
    print(df_result.head())
