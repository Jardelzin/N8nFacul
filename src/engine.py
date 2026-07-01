import json
import os
import pandas as pd
from cleaner import limpar_dados
from analyzer import calcular_variacao_alfabetizacao

def main():
    # Caminho do dataset
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_csv = os.path.join(base_dir, 'data', 'EdStatsData.csv')
    
    # Países e indicadores para análise (aqui é onde o n8n pode passar argumentos no futuro)
    paises_alvo = ['BRA', 'USA', 'FIN']
    
    # 1. Processo de Limpeza
    df_limpo, anos = limpar_dados(caminho_csv, paises_alvo)
    
    # 2. Processo de Análise (Engenharia de Features)
    # Vamos criar um dicionário para enviar para a OpenAI
    insights = {}
    for pais in paises_alvo:
        df_pais = df_limpo[df_limpo['Country Code'] == pais]
        variacao = calcular_variacao_alfabetizacao(df_pais)
        
        insights[pais] = {
            "variacao_alfabetizacao_10_anos": round(variacao, 2),
            "status": "estagnado" if abs(variacao) < 1 else "em_evolucao"
        }
    
    # 3. Salvar o JSON para o n8n consumir
    caminho_saida = os.path.join(base_dir, 'data', 'insights_input.json')
    with open(caminho_saida, 'w') as f:
        json.dump(insights, f, indent=4)
        
    print(f"Sucesso! Relatório gerado em: {caminho_saida}")

if __name__ == "__main__":
    main()