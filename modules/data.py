# modules/data.py
import streamlit as st
import pandas as pd
import io
import requests

placares_btts = ['1x1', '2x1', '1x2', '2x2', '3x1', '1x3', '3x2', '2x3', '3x3']
placares_comparacao = ['0x0', '1x0', '0x1', '2x0', '0x2', '1X1', '2x1', '1x2', '3x0', '0x3', '2x2', '3x1', '1x3', '3x2', '2x3', '4x0', '0x4', '4x1', '1x4', '4x2', '2x4', '4x3', '3x4']

def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1bnyG54WZ_ggkvekqwIicZGFdR-KXCffWEcXcQ4v0KcI/export?format=xlsx"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Garante que não houve erro de conexão
        arquivo_excel = io.BytesIO(response.content)
        df = pd.read_excel(arquivo_excel, sheet_name="Jogos")  # Ajuste o nome da aba se necessário
        df.fillna(0, inplace=True)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()  # Retorna DataFrame vazio em caso de erro

def aplicar_modelos(df):
    def classificar_modelo(row):
        try:
            # Lay 0x1 com Pressão da Casa (Alta Gols)
            if (row.get('XG CASA', 0) > row.get('XG VISITANTE', 0) and
                row.get('XG TOTAL', 0) > 1.5 and
                row.get('%PARTIDAS GOLS CASA HT', 0) > 0.6 and
                row.get('%PARTIDAS GOLS VISIT HT', 0) > 0.6 and
                '0x0' not in [row.get(p, 0) for p in placares_comparacao[:3]] and
                row.get('Odd2', 0) > 4 and
                row.get('Projeção GOL CASA', 0) > 0.5 and
                row.get('Projeção GOL VISITANTE', 0) < 0.5):
                return "Lay 0x1 com Pressão da Casa (Alta Gols)"

            # Lay 1x0 com Pressão do Visitante (Alta Gols)
            if (row.get('XG VISITANTE', 0) > row.get('XG CASA', 0) and
                row.get('XG TOTAL', 0) > 1.5 and
                row.get('%PARTIDAS GOLS CASA HT', 0) > 0.6 and
                row.get('%PARTIDAS GOLS VISIT HT', 0) > 0.6 and
                '0x0' not in [row.get(p, 0) for p in placares_comparacao[:4]] and
                row.get('Odd2', 0) > 4 and
                row.get('Projeção GOL VISITANTE', 0) > 0.5 and
                row.get('Projeção GOL CASA', 0) < 0.5):
                return "Lay 1x0 com Pressão do Visitante (Alta Gols)"

            # Lay Casa
            if (row.get('%PARTIDAS GOLS CASA HT', 0) < 0.7 and
                row.get('% GOLS VISITANTE', 0) > 0.7 and
                row.get('% JOGOS TIME VISITANTE GANHOU', 0) > 0.5 and
                row.get('% JOGOS TIME CASA PERDEU', 0) > 0.5 and
                row.get('Projeção PTS CASA', 0) < 0.5 and
                row.get('Projeção PTS VISITANTE', 0) > 0.5):
                return "Lay Casa"

            # Lay Visitante
            if (row.get('%PARTIDAS GOLS CASA HT', 0) > 0.7 and
                row.get('% GOLS VISITANTE', 0) < 0.7 and
                row.get('% JOGOS TIME CASA GANHOU', 0) > 0.5 and
                row.get('% JOGOS TIME VISITANTE PERDEU', 0) > 0.5 and
                row.get('Projeção PTS CASA', 0) > 0.5 and
                row.get('Projeção PTS VISITANTE', 0) < 0.5):
                return "Lay Visitante"

            # Lay Goleada Casa
            if (row.get('XG CASA', 0) > row.get('XG VISITANTE', 0) and
                row.get('XG TOTAL', 0) > 1.5 and
                row.get('%PARTIDAS GOLS CASA HT', 0) > 0.6 and
                row.get('%PARTIDAS GOLS VISIT HT', 0) > 0.6 and
                '0x0' not in [row.get(p, 0) for p in placares_comparacao[:3]] and
                row.get('GOLEADA CASA', 0) < 0.04):
                return "Lay Goleada Casa"

            # Alta probabilidade de gols
            if (row.get('0x0', 1) < 0.05 and
                row.get('0x1', 1) < 0.05 and
                row.get('1x0', 1) < 0.05 and
                row.get('XG TOTAL', 0) > 1.5):
                if row.get('GOLEADA CASA', 0) > 0.1 or row.get('GOLEADA VISITANTE', 0) > 0.1:
                    return "Alta Confiança de Gols (Potencial Goleada)"
                return "Alta Confiança de Gols"

            # Possível Goleada Casa ou Visitante
            if row.get('GOLEADA CASA', 0) > 0.2 and row.get('XG CASA', 0) > 1.8:
                return "Possível Goleada da Casa"
            if row.get('GOLEADA VISITANTE', 0) > 0.2 and row.get('XG VISITANTE', 0) > 1.8:
                return "Possível Goleada do Visitante"

        except Exception as e:
            return f"Erro na Classificação: {e}"
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

    df['Índice Bruto'] = df.apply(calcular_indice, axis=1)

    # Normaliza o índice para uma escala de 1 a 10
    minimo = df['Índice Bruto'].min()
    maximo = df['Índice Bruto'].max()
    if maximo != minimo:
        df['Índice de Confiança'] = df['Índice Bruto'].apply(lambda x: round(1 + 9 * (x - minimo) / (maximo - minimo), 2))
    else:
        df['Índice de Confiança'] = 5.0  # valor neutro se todos os scores forem iguais

    # Opcional: remove a coluna auxiliar
    df.drop(columns=['Índice Bruto'], inplace=True)

    return df