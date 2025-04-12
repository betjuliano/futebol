# modules/pages.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def pagina_dashboard(df):
    st.header("Dashboard de Jogos por Modelo")

    # Verifica se a coluna 'Modelo' existe
    if 'Modelo' not in df.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Filtro por modelo
    modelos = ["Todos"] + sorted(df['Modelo'].unique())
    modelo = st.selectbox("Filtrar por Modelo:", modelos)
    if modelo != "Todos":
        df = df[df['Modelo'] == modelo]

    # Adiciona a coluna 'TIP' com correção no lambda
    if all(col in df.columns for col in ['0x0', '1x0', '0x1']):
        df['TIP'] = df.apply(lambda row: ', '.join([
            tip for prob, tip in [
                (row.get('0x0', 1.0), '0-0'),
                (row.get('1x0', 1.0), '1-0'),
                (row.get('0x1', 1.0), '0-1'),
            ] if prob < 4  # Corrigido para ponto decimal
        ]), axis=1)
    else:
        st.warning("Colunas necessárias para calcular 'TIP' estão ausentes.")

    # Define as colunas a exibir
    colunas_exibir = [
        'Horario', 'Casa', 'Visitante', 'ODD1', 'ODD2', 'ODD3', 'TIP', 'N DE PARTIDAS',
        '%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT',
        'XG CASA', 'XG VISITANTE', 'XGSCORE CASA', 'XGSCORE VISITANTE',
        '0x0', '0x1', '1x0', 'Índice de Confiança', 'Modelo'
    ]
    colunas_existentes = [col for col in colunas_exibir if col in df.columns]

    # Converte colunas de percentuais
    percentuais = ['%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT', '0x0', '0x1', '1x0']
    for col in percentuais:
        if col in df.columns:
            df[col] = (df[col] * 100).round(1).astype(str) + '%'

    # Exibe o DataFrame final
    df_final = df[colunas_existentes].copy()
    st.dataframe(df_final, use_container_width=True)
    pass

def pagina_graficos(df):
    st.header("Gráficos de Análise de Jogos")

    # Verifica se a coluna 'Modelo' existet.subheader("Distribuição de Modelos")
    if 'Modelo' not in df.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    st.subheader("Frequência de Modelos") "#ef5350",
    modelo_counts = df['Modelo'].value_counts()        "0-1 ou 1-0": "#42a5f5",
    fig1, ax1 = plt.subplots()
    cores = { 0x1": "#ab47bc",
        "Lay 1x0 com Pressão do Visitante (Alta Gols)": "#ff7043",car Menos Provável: 1x0": "#8d6e63",
        "Outro": "#b0bec5"
    }ols)": "#ff7043",
    colors = [cores.get(modelo, "#90a4ae") for modelo in modelo_counts.index]
    ax1.barh(modelo_counts.index, modelo_counts.values, color=colors)
    ax1.set_xlabel("Número de Jogos")
    ax1.set_title("Frequência de Modelos")
    st.pyplot(fig1)bel("Número de Jogos")

    st.subheader("Linha do Tempo dos Jogos")yplot(fig1)
    if 'Horario' in df.columns:











    pass            st.warning("Erro ao processar a coluna Horario.")        except:            st.dataframe(df[['Horário Formatado', 'Jogo', 'Modelo', 'Índice de Confiança']], use_container_width=True)            df['Horário Formatado'] = df['Horario_dt'].dt.strftime('%d/%m %H:%M')            df['Jogo'] = df['Casa'] + ' x ' + df['Visitante']            df = df.sort_values('Horario_dt')            df = df.dropna(subset=['Horario_dt'])            df['Horario_dt'] = pd.to_datetime(df['Horario'], errors='coerce')        try:    st.subheader("Linha do Tempo dos Jogos")
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
    pass
