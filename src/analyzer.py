import pandas as pd

def calcular_variacao_alfabetizacao(df):
    """
    Calcula a variação percentual do indicador de alfabetização
    (geralmente 'SE.ADT.1524.LT.ZS' ou similar).
    """
    # Exemplo: Filtra pelo indicador de alfabetização de jovens
    indicador = 'SE.ADT.1524.LT.ZS'
    df_alf = df[df['Indicator Code'] == indicador].copy()
    
    # Pega os últimos 10 anos disponíveis
    anos_disponiveis = [col for col in df_alf.columns if col.isnumeric()]
    ultimos_anos = anos_disponiveis[-10:]
    
    # Calcula a variação entre o primeiro e o último desses 10 anos
    valor_antigo = df_alf[ultimos_anos[0]].iloc[0]
    valor_novo = df_alf[ultimos_anos[-1]].iloc[0]
    
    variacao = ((valor_novo - valor_antigo) / valor_antigo) * 100
    
    return variacao

# Aqui você pode chamar essa função dentro do seu engine.py depois!