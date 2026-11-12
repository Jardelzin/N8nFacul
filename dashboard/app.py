"""
app.py — Dashboard de Monitoramento Educacional (Streamlit)

Visualiza os dados processados pelo Agente Inteligente:
  • Seleção interativa de países e indicadores
  • Gráficos de evolução temporal
  • Rankings comparativos
  • Tabela de alertas
  • Exportação de relatórios

Uso:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
import sys

# ── Caminhos ────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

from cleaner import (
    processar_pipeline,
    identificar_colunas_anos,
    INDICADORES_PADRAO,
    PAISES_PADRAO,
)
from analyzer import (
    calcular_crescimento,
    gerar_ranking,
    comparar_paises,
    gerar_insights_completos,
)

# ── Configuração da página ──────────────────────────────────
st.set_page_config(
    page_title="🎓 Monitor Educacional Global",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 Agente Inteligente de Monitoramento Educacional")
st.caption("Dados: World Bank Education Statistics (EdStats)")


# ── Sidebar: configuração ──────────────────────────────────
st.sidebar.header("⚙️ Configurações")

CAMINHO_CSV = os.path.join(ROOT, 'data', 'EdStatsData.csv')
CAMINHO_RANKING = os.path.join(ROOT, 'data', 'educacao_ranking_final.csv')
CAMINHO_INSIGHTS = os.path.join(ROOT, 'data', 'insights_input.json')
CAMINHO_RELATORIO = os.path.join(ROOT, 'data', 'relatorio_ia.md')


@st.cache_data(show_spinner="Carregando e processando dados...")
def carregar_dados(paises, indicadores):
    """Carrega e processa o dataset (com cache do Streamlit)."""
    df, anos = processar_pipeline(CAMINHO_CSV, list(paises), list(indicadores))
    return df, anos


# ── Verificar se o dataset existe ───────────────────────────
if not os.path.exists(CAMINHO_CSV):
    st.error(
        "❌ Dataset não encontrado!\n\n"
        f"Coloque o arquivo `EdStatsData.csv` em:\n`{CAMINHO_CSV}`\n\n"
        "Baixe de: https://www.kaggle.com/datasets/theworldbank/world-bank-edstats"
    )
    st.stop()


# ── Seleção de países e indicadores ─────────────────────────
paises_sel = st.sidebar.multiselect(
    "🌎 Países",
    options=PAISES_PADRAO,
    default=['BRA', 'USA', 'FIN', 'CHN', 'KOR'],
    help="Selecione os países para análise",
)

indicadores_sel = st.sidebar.multiselect(
    "📊 Indicadores",
    options=list(INDICADORES_PADRAO.keys()),
    default=list(INDICADORES_PADRAO.keys())[:4],
    format_func=lambda x: INDICADORES_PADRAO.get(x, x),
    help="Selecione os indicadores educacionais",
)

if not paises_sel or not indicadores_sel:
    st.warning("Selecione ao menos um país e um indicador na barra lateral.")
    st.stop()


# ── Carregar dados ──────────────────────────────────────────
try:
    df, colunas_anos = carregar_dados(tuple(paises_sel), tuple(indicadores_sel))
except Exception as e:
    st.error(f"Erro ao processar dados: {e}")
    st.stop()


# ── Métricas principais ────────────────────────────────────
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌎 Países", len(paises_sel))
col2.metric("📊 Indicadores", len(indicadores_sel))
col3.metric("📅 Período", f"{colunas_anos[0]}–{colunas_anos[-1]}" if colunas_anos else "N/A")
col4.metric("📋 Registros", len(df))


# ── Abas ────────────────────────────────────────────────────
tab_evolucao, tab_ranking, tab_alertas, tab_relatorio, tab_dados = st.tabs([
    "📈 Evolução Temporal",
    "🏆 Rankings",
    "⚠️ Alertas",
    "🤖 Relatório IA",
    "📋 Dados Brutos",
])


# ── Tab 1: Evolução Temporal ───────────────────────────────
with tab_evolucao:
    st.subheader("📈 Evolução dos Indicadores ao Longo do Tempo")

    ind_chart = st.selectbox(
        "Selecione o indicador:",
        indicadores_sel,
        format_func=lambda x: INDICADORES_PADRAO.get(x, x),
        key="ind_evolucao",
    )

    try:
        df_comp = comparar_paises(df, paises_sel, ind_chart, colunas_anos)

        if not df_comp.empty:
            # Converter índice para inteiro para exibição correta no eixo X
            df_comp.index = df_comp.index.astype(int)

            st.line_chart(df_comp, use_container_width=True)

            with st.expander("📋 Ver dados da comparação"):
                st.dataframe(df_comp, use_container_width=True)
        else:
            st.info("Sem dados disponíveis para este indicador/países.")
    except Exception as e:
        st.warning(f"Não foi possível gerar o gráfico: {e}")


# ── Tab 2: Rankings ────────────────────────────────────────
with tab_ranking:
    st.subheader("🏆 Rankings por Indicador")

    df_cresc = calcular_crescimento(df, colunas_anos)

    col_rank1, col_rank2 = st.columns(2)

    with col_rank1:
        st.markdown("#### 📊 Ranking por Valor Atual")
        ind_rank = st.selectbox(
            "Indicador:",
            indicadores_sel,
            format_func=lambda x: INDICADORES_PADRAO.get(x, x),
            key="ind_rank_valor",
        )
        rank_val = gerar_ranking(df_cresc, ind_rank, 'valor_final', top_n=len(paises_sel))
        if not rank_val.empty:
            chart_data = rank_val.set_index('Country Code')['valor_final']
            st.bar_chart(chart_data, use_container_width=True)
            st.dataframe(
                rank_val[['ranking', 'Country Code', 'Country Name', 'valor_final', 'periodo']],
                use_container_width=True,
                hide_index=True,
            )

    with col_rank2:
        st.markdown("#### 📈 Ranking por Evolução (%)")
        rank_evo = gerar_ranking(df_cresc, ind_rank, 'variacao_pct', top_n=len(paises_sel))
        if not rank_evo.empty:
            chart_data = rank_evo.set_index('Country Code')['variacao_pct']
            st.bar_chart(chart_data, use_container_width=True)
            st.dataframe(
                rank_evo[['ranking', 'Country Code', 'Country Name', 'variacao_pct', 'periodo']],
                use_container_width=True,
                hide_index=True,
            )


# ── Tab 3: Alertas ──────────────────────────────────────────
with tab_alertas:
    st.subheader("⚠️ Alertas Automáticos")

    insights, _ = gerar_insights_completos(df, colunas_anos, paises_sel)
    alertas = insights.get('alertas', [])

    if alertas:
        df_alertas = pd.DataFrame(alertas)

        # Filtro por tipo
        tipos = df_alertas['tipo'].unique().tolist()
        tipo_sel = st.multiselect("Filtrar por tipo:", tipos, default=tipos)
        df_alertas_f = df_alertas[df_alertas['tipo'].isin(tipo_sel)]

        # Colorir por tipo
        st.dataframe(
            df_alertas_f[['tipo', 'pais', 'indicador', 'variacao_pct', 'mensagem']],
            use_container_width=True,
            hide_index=True,
        )

        st.metric("Total de alertas", len(df_alertas_f))
    else:
        st.success("✅ Nenhum alerta identificado — todos os indicadores estão saudáveis!")


# ── Tab 4: Relatório IA ────────────────────────────────────
with tab_relatorio:
    st.subheader("🤖 Relatório Gerado pela IA")

    if os.path.exists(CAMINHO_RELATORIO):
        with open(CAMINHO_RELATORIO, 'r', encoding='utf-8') as f:
            relatorio = f.read()
        st.markdown(relatorio)
    else:
        st.info(
            "O relatório da IA ainda não foi gerado.\n\n"
            "Execute o workflow do n8n ou rode manualmente:\n"
            "```\npython src/engine.py\n```\n"
            "Depois envie o `prompt_openai.txt` para a API da OpenAI."
        )

    # Exibir insights JSON se disponível
    if os.path.exists(CAMINHO_INSIGHTS):
        with st.expander("📄 Ver insights brutos (JSON)"):
            with open(CAMINHO_INSIGHTS, 'r', encoding='utf-8') as f:
                st.json(json.load(f))


# ── Tab 5: Dados Brutos ────────────────────────────────────
with tab_dados:
    st.subheader("📋 Dados Processados")

    st.dataframe(df, use_container_width=True, height=400)

    # Exportar CSV
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="⬇️ Baixar dados processados (CSV)",
        data=csv_data,
        file_name="dados_educacionais_processados.csv",
        mime="text/csv",
    )

    # Estatísticas descritivas
    with st.expander("📊 Estatísticas descritivas"):
        st.dataframe(
            df[colunas_anos].describe().round(2),
            use_container_width=True,
        )


# ── Footer ──────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🎓 Agente Inteligente de Monitoramento Educacional | "
    "World Bank EdStats | "
    "Desenvolvido com Python, n8n, OpenAI e Streamlit"
)
