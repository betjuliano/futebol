import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def pagina_dashboard(df):
    st.header("Dashboard de Jogos por Modelo")

    # Verifica se a coluna 'Modelo' existe
    if 'Modelo' not in df.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Padroniza a coluna 'Modelo'
    df['Modelo'] = df['Modelo'].astype(str).str.strip()

    # Filtro por modelo
    modelos = ["Todos"] + sorted(df['Modelo'].dropna().unique())
    modelo = st.selectbox("Filtrar por Modelo:", modelos)

    # Filtro por TIP
    exibir_so_com_tip = st.checkbox("Exibir apenas jogos com TIP", value=False)

    # Cria uma cópia do DataFrame para aplicar os filtros
    df_filtrado = df.copy()

    # Aplica o filtro por modelo
    if modelo != "Todos":
        df_filtrado = df_filtrado.loc[df_filtrado['Modelo'] == modelo]

    # Verifica se há dados após o filtro por modelo
    if df_filtrado.empty:
        st.warning("Nenhum jogo encontrado para esse modelo.")
        return

    # Adiciona a coluna 'TIP' se possível
    if all(col in df_filtrado.columns for col in ['0x0', '1x0', '0x1']):
        df_filtrado['TIP'] = df_filtrado.apply(lambda row: ', '.join([
            tip for prob, tip in [
                (row.get('0x0', 1.0), '0-0'),
                (row.get('1x0', 1.0), '1-0'),
                (row.get('0x1', 1.0), '0-1'),
            ] if prob < .04
        ]), axis=1)
    else:
        st.warning("Colunas necessárias para calcular 'TIP' estão ausentes.")

    # Aplica o filtro TIP se selecionado
    if exibir_so_com_tip:
        df_filtrado = df_filtrado.loc[df_filtrado['TIP'].str.strip() != '']

    # Verifica se há dados após o filtro TIP
    if df_filtrado.empty:
        st.warning("Nenhum jogo encontrado com os filtros aplicados.")
        return

    # Filtro por campeonato
    if 'Campeonato' in df_filtrado.columns:
        campeonatos = ["Todos"] + sorted(df_filtrado['Campeonato'].dropna().unique())
        campeonato = st.selectbox("Filtrar por Campeonato:", campeonatos)
        if campeonato != "Todos":
            df_filtrado = df_filtrado.loc[df_filtrado['Campeonato'] == campeonato]

    # Verifica se há dados após o filtro por campeonato
    if df_filtrado.empty:
        st.warning("Nenhum jogo encontrado com os filtros aplicados.")
        return

    # Define as colunas a exibir
    colunas_exibir = [
        'Horario', 'Campeonato', 'Casa', 'Visitante',
        'PROJEÇÃO PTS CASA', 'PROJEÇÃO PTS VISITANTE', 'ODD1', 'ODD2', 'ODD3',
        'TIP', 'N DE PARTIDAS',
        '%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT',
        'XG CASA', 'CV CASA', 'XG VISITANTE', 'CV VISITANTE',
        'XG TOTAL', 'CV TOTAL',
        '0x0', '0x1', '1x0',
        'PROJEÇÃO VIT CASA', 'PROJEÇÃO VIT VISITANTE',
        'PROJEÇÃO GOL CASA FEITO', 'PROJEÇÃO GOL VISITANTE FEITO',
        'Índice de Confiança', 'Modelo'
    ]

    colunas_existentes = [col for col in colunas_exibir if col in df_filtrado.columns]

    # Converte colunas percentuais para string com símbolo %
    colunas_percentuais = [
        'PROJEÇÃO PTS CASA', 'PROJEÇÃO PTS VISITANTE',
        'PROJEÇÃO VIT CASA', 'PROJEÇÃO VIT VISITANTE',
        'PROJEÇÃO GOL CASA FEITO', 'PROJEÇÃO GOL VISITANTE FEITO',
        '%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT',
        '0x0', '0x1', '1x0'
    ]
    for col in colunas_percentuais:
        if col in df_filtrado.columns:
            try:
                df_filtrado.loc[:, col] = (df_filtrado[col].astype(float) * 100).round(1).astype(str) + '%'
            except Exception as e:
                st.warning(f"Erro ao formatar a coluna {col}: {e}")

    # Exibe os dados finais no dashboard
    df_final = df_filtrado[colunas_existentes].copy()
    st.dataframe(df_final, use_container_width=True)


def pagina_graficos(df):
    st.header("Gráficos de Análise de Jogos")

    # Verifica se a coluna 'Modelo' existe
    if 'Modelo' not in df.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Frequência de Modelos
    st.subheader("Frequência de Modelos")
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

    # Linha do Tempo dos Jogos
    st.subheader("Linha do Tempo dos Jogos")
    if 'Horario' in df.columns:
        try:
            df['Horario_dt'] = pd.to_datetime(df['Horario'], errors='coerce')
            df = df.dropna(subset=['Horario_dt'])
            df = df.sort_values('Horario_dt')
            df['Jogo'] = df['Casa'] + ' x ' + df['Visitante']
            df['Horário Formatado'] = df['Horario_dt'].dt.strftime('%d/%m %H:%M')
            st.dataframe(df[['Horário Formatado', 'Jogo', 'Modelo', 'Índice de Confiança']], use_container_width=True)
        except Exception as e:
            st.warning(f"Erro ao processar a coluna Horario: {e}")
