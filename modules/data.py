# modules/data.py
import streamlit as st
import pandas as pd

placares_btts = ['1x1', '2x1', '1x2', '2x2', '3x1', '1x3', '3x2', '2x3', '3x3']
placares_comparacao = ['1x1', '2x1', '1x2', '2x2', '3x1', '1x3', '0x0', '1x0', '0x1', '2x0', '0x2']

@st.cache_data
def carregar_dados(filename="jogos1104.xlsx"):
    df = pd.read_excel(filename, sheet_name="Planilha1")
    df.fillna(0, inplace=True)
    return df

def aplicar_modelos(df):
    def classificar_modelo(row):
        try:
            if row.get('%PARTIDAS GOLS CASA HT', 0) > 0.7 and row.get('%PARTIDAS GOLS VISIT HT', 0) < 0.7 and row.get('% JOGOS TIME CASA GANHOU', 0) > 0.5 and row.get('% JOGOS TIME VISITANTE PERDEU', 0) > 0.5:
                return "Lay Visitante"
            if row.get('%PARTIDAS GOLS CASA HT', 0) < 0.7 and row.get('%PARTIDAS GOLS VISIT HT', 0) > 0.7 and row.get('% JOGOS TIME VISITANTE GANHOU', 0) > 0.5 and row.get('% JOGOS TIME CASA PERDEU', 0) > 0.5:
                return "Lay Casa"
            if row.get('XG CASA', 0) > 1.0 and row.get('XG VISITANTE', 0) > 1.0 and row.get('CV CASA', 1.1) < 1.0 and row.get('CV VISITANTE', 1.1) < 1.0:
                soma_btts = sum([row.get(p, 0) for p in placares_btts])
                if soma_btts > 0.3:
                    return "Lay 0-1 ou 1-0"
            if row.get('0x0', 1) < 0.05 and row.get('0x1', 1) < 0.05 and row.get('1x0', 1) < 0.05 and row.get('XG TOTAL', 0) > 1.5:
                return "Alta Confiança de Gols"
            prob_01 = row.get('0x1', 1.0)
            outros = [row.get(p, 1.0) for p in placares_comparacao if p != '0x1']
            if prob_01 < min(outros) and prob_01 < 0.1:
                return "Lay 0x1"
            prob_10 = row.get('1x0', 1.0)
            outros = [row.get(p, 1.0) for p in placares_comparacao if p != '1x0']
            if prob_10 < min(outros) and prob_10 < 0.1:
                return "Lay 1x0"

            # Novo modelo 0x1 com Pressão da Casa (Alta Gols)
            maiores_placares = sorted([(row.get(p, 0), p) for p in placares_comparacao], reverse=True)[:4]
            placares_top4 = [p for _, p in maiores_placares]
            if (
                row.get('XG CASA', 0) > row.get('XG VISITANTE', 0)
                and row.get('XG TOTAL', 0) > 1.5
                and (row.get('%PARTIDAS GOLS CASA HT', 0) > 0.6 and row.get('%PARTIDAS GOLS VISIT HT', 0) > 0.6)
                and '0x0' not in placares_top4
                and '1x1' not in placares_top4
                and '0x1' not in placares_top4
            ):
                return "Lay 0x1 com Pressão da Casa (Alta Gols)"

            # Novo modelo 1x0 com Pressão do Visitante (Alta Gols)
            if (
                row.get('XG VISITANTE', 0) > row.get('XG CASA', 0)
                and row.get('XG TOTAL', 0) > 1.5
                and (row.get('%PARTIDAS GOLS CASA HT', 0) > 0.6 and row.get('%PARTIDAS GOLS VISIT HT', 0) > 0.6)
                and '0x0' not in placares_top4
                and '1x0' not in placares_top4
            ):
                return "Lay 1x0 com Pressão do Visitante (Alta Gols)"

        except:
            return "Erro na Classificação"
        return "Análise Individual"

    df['Modelo'] = df.apply(classificar_modelo, axis=1)
    return df

def calcular_indice_confiança(df):
    def calcular_indice(row):
        score = 0
        score += (1 - row.get('0x0', 0)) * 30
        score += (1 - row.get('0x1', 0)) * 20
        score += (1 - row.get('1x0', 0)) * 20
        score += (row.get('XG CASA', 0) + row.get('XG VISITANTE', 0)) * 10
        score += (row.get('XGSCORE CASA', 0) + row.get('XGSCORE VISITANTE', 0)) * 5
        score += (row.get('%PARTIDAS GOLS CASA HT', 0) + row.get('%PARTIDAS GOLS VISIT HT', 0)) * 10
        if row.get('CV TOTAL', 1.1) < 1.0:
            score += 10
        return round(score, 2)

    df['Índice de Confiança'] = df.apply(calcular_indice, axis=1)
    return df
