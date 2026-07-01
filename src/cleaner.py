import pandas as pd
import numpy as np
import os
def limpar_dados(caminho_csv, paises_alvo):
    """
    Carrega o dataset do Banco Mundial, filtra pelos países desejados,
    remove colunas completamente vazias e preenche dados de investimento.
    """
    print(f"Buscando dados em: {caminho_csv}...")
    
    # 1. Carregar o dataset (usamos low_memory=False porque o arquivo é grande)
    df = pd.read_csv(caminho_csv, low_memory=False)
    
    # 2. Filtrar apenas os países que o usuário/n8n pediu (ex: BRA, USA, FIN)
    # No Kaggle, a coluna de sigla se chama 'Country Code'
    df_filtrado = df[df['Country Code'].isin(paises_alvo)].copy()
    
    # 3. Microtarefa (Totalmente Automatizável): Remover colunas nulas
    # O dropna(axis=1, how='all') apaga colunas (anos) onde TODOS os dados estão vazios
    df_filtrado = df_filtrado.dropna(axis=1, how='all')
    
    # 4. Microtarefa: Preencher valores ausentes em investimentos públicos
    # O código do indicador de investimento em educação no World Bank geralmente é 'SE.XPD.TOTL.GD.ZS'
    mascara_investimento = df_filtrado['Indicator Code'] == 'SE.XPD.TOTL.GD.ZS'
    
    # Calculamos a média histórica (pegamos apenas as colunas numéricas de anos)
    colunas_anos = [col for col in df_filtrado.columns if col.isnumeric()]
    media_historica = df_filtrado.loc[mascara_investimento, colunas_anos].mean().mean()
    
    # Preenchemos (fillna) os buracos nos dados de investimento com essa média
    df_filtrado.loc[mascara_investimento, colunas_anos] = df_filtrado.loc[mascara_investimento, colunas_anos].fillna(media_historica)
    
    print("Limpeza concluída com sucesso! Valores nulos tratados.")
    
    return df_filtrado, colunas_anos

# Bloco de teste (só roda se você executar esse arquivo diretamente)
if __name__ == "__main__":
    # Pega o caminho da pasta onde o script está
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_arquivo = os.path.join(base_dir, 'data', 'EdStatsData.csv')
    
    paises_teste = ['BRA', 'USA', 'FIN']
    df_limpo, anos = limpar_dados(caminho_arquivo, paises_teste)
    print(df_limpo.head())