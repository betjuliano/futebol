# modules/pages.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def pagina_dashboard(df):
    st.header("Dashboard de Jogos por Modelo")
    modelos = ["Todos"] + sorted(df['Modelo'].unique())
    modelo = st.selectbox("Filtrar por Modelo:", modelos)
    if modelo != "Todos":
        df = df[df['Modelo'] == modelo]

    colunas_exibir = [
        'Horario', 'Casa', 'Visitante', 'ODD1', 'ODD2', 'ODD3', 'N DE PARTIDAS',
        '%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT',
        'XG CASA', 'XG VISITANTE', 'XGSCORE CASA', 'XGSCORE VISITANTE',
        '0x0', '0x1', '1x0', 'Índice de Confiança', 'Modelo'
    ]
    colunas_existentes = [col for col in colunas_exibir if col in df.columns]

    percentuais = ['%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT', '0x0', '0x1', '1x0']
    for col in percentuais:
        if col in df.columns:
            df[col] = (df[col] * 100).round(1).astype(str) + '%'

    df_final = df[colunas_existentes].copy()

    st.dataframe(df_final, use_container_width=True)


def pagina_graficos(df):
    st.header("Gráficos e Linha do Tempo")

    st.subheader("Distribuição de Modelos")
    modelo_counts = df['Modelo'].value_counts()
    fig1, ax1 = plt.subplots()
    cores = {
        "Lay Visitante": "#66bb6a",
        "Lay Casa": "#ef5350",
        "0-1 ou 1-0": "#42a5f5",
        "Alta Confiança de Gols": "#ffa726",
        "Placar Menos Provável: 0x1": "#ab47bc",
        "Placar Menos Provável: 1x0": "#8d6e63",
        "Lay 0x1 com Pressão da Casa (Alta Gols)": "#26a69a",
        "Lay 1x0 com Pressão do Visitante (Alta Gols)": "#ff7043",
        "Outro": "#b0bec5"
    }
    colors = [cores.get(modelo, "#90a4ae") for modelo in modelo_counts.index]
    ax1.barh(modelo_counts.index, modelo_counts.values, color=colors)
    ax1.set_xlabel("Número de Jogos")
    ax1.set_title("Frequência de Modelos")
    st.pyplot(fig1)

    st.subheader("Linha do Tempo dos Jogos")
    if 'Horario' in df.columns:
        try:
            df['Horario_dt'] = pd.to_datetime(df['Horario'], errors='coerce')
            df = df.dropna(subset=['Horario_dt'])
            df = df.sort_values('Horario_dt')
            df['Jogo'] = df['Casa'] + ' x ' + df['Visitante']
            df['Horário Formatado'] = df['Horario_dt'].dt.strftime('%d/%m %H:%M')
            st.dataframe(df[['Horário Formatado', 'Jogo', 'Modelo', 'Índice de Confiança']], use_container_width=True)
        except:
            st.warning("Erro ao processar a coluna Horario.")