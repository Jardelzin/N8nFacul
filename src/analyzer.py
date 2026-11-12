"""
analyzer.py — Módulo de Análise e Geração de Insights Educacionais

Operações implementadas:
  4. Geração de rankings por indicador
  5. Cálculo de crescimento / variação percentual
  6. Comparação entre países (evolução temporal)
  7. Geração de alertas e insights estruturados para a IA

Autor: Agente Inteligente de Monitoramento Educacional
"""

import pandas as pd
import numpy as np

# Importar constantes compartilhadas
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cleaner import INDICADORES_PADRAO, identificar_colunas_anos


# ─────────────────────────────────────────────────────────────
# OPERAÇÃO 4 — Cálculo de crescimento
# ─────────────────────────────────────────────────────────────

def calcular_crescimento(df: pd.DataFrame, colunas_anos: list) -> pd.DataFrame:
    """
    Calcula a variação percentual entre o primeiro e o último valor
    disponível para cada par (país, indicador).

    Returns:
        DataFrame com colunas: Country Code, Country Name, Indicator Code,
        Indicator Name, valor_inicial, valor_final, variacao_pct, periodo.
    """
    print("\n📈 Calculando crescimento por país/indicador...")

    resultados = []
    for _, row in df.iterrows():
        valores = row[colunas_anos].dropna()
        if len(valores) < 2:
            continue

        primeiro_ano = valores.index[0]
        ultimo_ano = valores.index[-1]
        v_ini = float(valores.iloc[0])
        v_fim = float(valores.iloc[-1])

        variacao = (
            ((v_fim - v_ini) / abs(v_ini)) * 100
            if v_ini != 0
            else np.nan
        )

        resultados.append({
            'Country Code': row['Country Code'],
            'Country Name': row.get('Country Name', row['Country Code']),
            'Indicator Code': row['Indicator Code'],
            'Indicator Name': row.get('Indicator Name', row['Indicator Code']),
            'valor_inicial': round(v_ini, 2),
            'valor_final': round(v_fim, 2),
            'variacao_pct': round(variacao, 2) if not np.isnan(variacao) else None,
            'ano_inicial': primeiro_ano,
            'ano_final': ultimo_ano,
            'periodo': f"{primeiro_ano}–{ultimo_ano}",
        })

    df_cresc = pd.DataFrame(resultados)
    print(f"   ✅ Crescimento calculado para {len(resultados)} combinações")
    return df_cresc


# ─────────────────────────────────────────────────────────────
# OPERAÇÃO 5 — Geração de rankings
# ─────────────────────────────────────────────────────────────

def gerar_ranking(
    df_crescimento: pd.DataFrame,
    indicador: str = None,
    metrica: str = 'valor_final',
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Gera ranking dos países para um indicador e métrica escolhidos.

    Args:
        df_crescimento: DataFrame de métricas (saída de ``calcular_crescimento``).
        indicador: Código do indicador (``None`` = todos).
        metrica: Coluna de ordenação (``'valor_final'`` ou ``'variacao_pct'``).
        top_n: Quantidade de posições.

    Returns:
        DataFrame com coluna ``ranking``.
    """
    df_rank = (
        df_crescimento[df_crescimento['Indicator Code'] == indicador].copy()
        if indicador
        else df_crescimento.copy()
    )

    df_rank = df_rank.dropna(subset=[metrica])
    df_rank = df_rank.sort_values(metrica, ascending=False).head(top_n)
    df_rank['ranking'] = range(1, len(df_rank) + 1)

    nome = INDICADORES_PADRAO.get(indicador, indicador or 'Todos')
    print(f"   🏆 Ranking '{metrica}' — {nome}: {len(df_rank)} países")
    return df_rank


# ─────────────────────────────────────────────────────────────
# OPERAÇÃO 6 — Comparação entre países
# ─────────────────────────────────────────────────────────────

def comparar_paises(
    df: pd.DataFrame,
    paises: list,
    indicador: str,
    colunas_anos: list,
) -> pd.DataFrame:
    """
    Retorna tabela pivotada (anos × países) para um indicador,
    facilitando gráficos de evolução temporal.

    Returns:
        DataFrame cujas linhas são anos e colunas são códigos de país.
    """
    nome = INDICADORES_PADRAO.get(indicador, indicador)
    print(f"\n📊 Comparando países para: {nome}")

    mask = (df['Country Code'].isin(paises)) & (df['Indicator Code'] == indicador)
    df_comp = df.loc[mask, ['Country Code'] + colunas_anos].copy()

    df_pivot = df_comp.set_index('Country Code')[colunas_anos].T
    df_pivot.index.name = 'Ano'
    df_pivot = df_pivot.dropna(how='all')

    print(f"   ✅ {len(df_pivot)} anos × {len(df_pivot.columns)} países")
    return df_pivot


# ─────────────────────────────────────────────────────────────
# OPERAÇÃO 7 — Alertas automáticos
# ─────────────────────────────────────────────────────────────

def _gerar_alertas(df_crescimento: pd.DataFrame) -> list:
    """Identifica situações que merecem atenção especial."""
    alertas = []
    for _, row in df_crescimento.iterrows():
        nome_ind = INDICADORES_PADRAO.get(row['Indicator Code'], row['Indicator Code'])
        v = row['variacao_pct']
        if v is None:
            continue

        if abs(v) < 1:
            alertas.append({
                'tipo': 'ESTAGNAÇÃO',
                'pais': row['Country Code'],
                'indicador': nome_ind,
                'variacao_pct': v,
                'mensagem': (
                    f"{row['Country Name']} apresenta estagnação em {nome_ind}"
                ),
            })
        elif v < -5:
            alertas.append({
                'tipo': 'QUEDA',
                'pais': row['Country Code'],
                'indicador': nome_ind,
                'variacao_pct': v,
                'mensagem': (
                    f"{row['Country Name']} teve queda de {v:.1f}% em {nome_ind}"
                ),
            })
        elif v > 50:
            alertas.append({
                'tipo': 'DESTAQUE_POSITIVO',
                'pais': row['Country Code'],
                'indicador': nome_ind,
                'variacao_pct': v,
                'mensagem': (
                    f"{row['Country Name']} cresceu {v:.1f}% em {nome_ind}"
                ),
            })

    return alertas


# ─────────────────────────────────────────────────────────────
# Insights completos (entrada para OpenAI)
# ─────────────────────────────────────────────────────────────

def gerar_insights_completos(
    df: pd.DataFrame,
    colunas_anos: list,
    paises: list = None,
) -> tuple:
    """
    Monta um dicionário rico de insights pronto para envio à API da OpenAI.

    Returns:
        ``(dict insights, DataFrame df_crescimento)``
    """
    print("\n🧠 Gerando insights completos para análise por IA...")

    if paises is None:
        paises = df['Country Code'].unique().tolist()

    # Crescimento
    df_cresc = calcular_crescimento(df, colunas_anos)

    # Rankings por indicador (valor atual + evolução)
    rankings = {}
    for ind in df['Indicator Code'].unique():
        nome = INDICADORES_PADRAO.get(ind, ind)
        rank_val = gerar_ranking(df_cresc, ind, 'valor_final', top_n=len(paises))
        rank_evo = gerar_ranking(df_cresc, ind, 'variacao_pct', top_n=len(paises))
        rankings[nome] = {
            'ranking_valor_atual': rank_val[
                ['ranking', 'Country Code', 'Country Name', 'valor_final', 'periodo']
            ].to_dict('records'),
            'ranking_evolucao': rank_evo[
                ['ranking', 'Country Code', 'Country Name', 'variacao_pct', 'periodo']
            ].to_dict('records'),
        }

    # Crescimento por país
    cresc_pais = {}
    for pais in paises:
        dados = df_cresc[df_cresc['Country Code'] == pais]
        cresc_pais[pais] = {}
        for _, r in dados.iterrows():
            nome = INDICADORES_PADRAO.get(r['Indicator Code'], r['Indicator Code'])
            cresc_pais[pais][nome] = {
                'valor_inicial': r['valor_inicial'],
                'valor_final': r['valor_final'],
                'variacao_pct': r['variacao_pct'],
                'periodo': r['periodo'],
            }

    # Alertas
    alertas = _gerar_alertas(df_cresc)

    # Resumo
    resumo = {
        'total_paises': len(paises),
        'total_indicadores': df['Indicator Code'].nunique(),
        'periodo_analise': (
            f"{colunas_anos[0]}–{colunas_anos[-1]}" if colunas_anos else "N/A"
        ),
        'total_alertas': len(alertas),
        'paises_analisados': paises,
        'indicadores_analisados': [
            INDICADORES_PADRAO.get(i, i) for i in df['Indicator Code'].unique()
        ],
    }

    insights = {
        'resumo_geral': resumo,
        'rankings': rankings,
        'crescimento_por_pais': cresc_pais,
        'alertas': alertas,
    }

    print(f"   ✅ {len(rankings)} rankings, {len(alertas)} alertas, "
          f"{len(paises)} países analisados")

    return insights, df_cresc
