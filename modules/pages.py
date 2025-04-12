import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def pagina_dashboard(df_original):
    st.header("Dashboard de Jogos por Modelo")

    # Verifica se a coluna 'Modelo' existe
    if 'Modelo' not in df_original.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Padroniza a coluna 'Modelo' sem criar cópia
    df_original['Modelo'] = df_original['Modelo'].astype(str).str.strip()

    # Filtro por modelo
    modelos = ["Todos"] + sorted(df_original['Modelo'].dropna().unique())
    modelo = st.selectbox("Filtrar por Modelo:", modelos)

    # Filtro por TIP
    exibir_so_com_tip = st.checkbox("Exibir apenas jogos com TIP", value=False)

    # Aplicar filtros diretamente usando query ou boolean indexing
    mask = pd.Series(True, index=df_original.index)

    if modelo != "Todos":
        mask &= df_original['Modelo'] == modelo

    # Adiciona a coluna 'TIP' diretamente no DataFrame original
    if all(col in df_original.columns for col in ['0x0', '1x0', '0x1']):
        if 'TIP' not in df_original.columns:
            df_original['TIP'] = df_original.apply(lambda row: ', '.join([
                tip for prob, tip in [
                    (row.get('0x0', 1.0), '0-0'),
                    (row.get('1x0', 1.0), '1-0'),
                    (row.get('0x1', 1.0), '0-1'),
                ] if prob < .04
            ]), axis=1)
    else:
        st.warning("Colunas necessárias para calcular 'TIP' estão ausentes.")

    # Aplica o filtro TIP se selecionado
    if exibir_so_com_tip and 'TIP' in df_original.columns:
        mask &= df_original['TIP'].str.strip() != ''

    # Filtro por campeonato
    if 'Campeonato' in df_original.columns:
        campeonatos = ["Todos"] + sorted(df_original.loc[mask, 'Campeonato'].dropna().unique())
        campeonato = st.selectbox("Filtrar por Campeonato:", campeonatos)
        if campeonato != "Todos":
            mask &= df_original['Campeonato'] == campeonato

    # Aplicar todos os filtros de uma vez
    df_filtrado = df_original[mask]

    # Verifica se há dados após os filtros
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

    # Criar um novo DataFrame apenas para exibição com as colunas formatadas
    df_exibicao = pd.DataFrame()

    # Copiar as colunas não percentuais diretamente
    colunas_percentuais = [
        'PROJEÇÃO PTS CASA', 'PROJEÇÃO PTS VISITANTE',
        'PROJEÇÃO VIT CASA', 'PROJEÇÃO VIT VISITANTE',
        'PROJEÇÃO GOL CASA FEITO', 'PROJEÇÃO GOL VISITANTE FEITO',
        '%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT',
        '0x0', '0x1', '1x0'
    ]

    colunas_normais = [col for col in colunas_existentes if col not in colunas_percentuais]
    for col in colunas_normais:
        df_exibicao[col] = df_filtrado[col]

    # Formatar apenas as colunas percentuais
    for col in colunas_percentuais:
        if col in df_filtrado.columns:
            try:
                df_exibicao[col] = (df_filtrado[col].astype(float) * 100).round(1).astype(str) + '%'
            except Exception as e:
                st.warning(f"Erro ao formatar a coluna {col}: {e}")
                df_exibicao[col] = df_filtrado[col]  # Usar valor original em caso de erro

    # Exibe os dados finais no dashboard
    st.dataframe(df_exibicao, use_container_width=True)


def pagina_graficos(df_original):
    st.header("Gráficos de Análise de Jogos")

    # Verifica se a coluna 'Modelo' existe
    if 'Modelo' not in df_original.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Frequência de Modelos
    st.subheader("Frequência de Modelos")
    modelo_counts = df_original['Modelo'].value_counts()
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
    if 'Horario' in df_original.columns:
        try:
            # Criar um DataFrame apenas para a visualização da linha do tempo
            df_timeline = pd.DataFrame()
            df_timeline['Horario_dt'] = pd.to_datetime(df_original['Horario'], errors='coerce')
            df_timeline['Casa'] = df_original['Casa']
            df_timeline['Visitante'] = df_original['Visitante']
            df_timeline['Modelo'] = df_original['Modelo']
            df_timeline['Índice de Confiança'] = df_original.get('Índice de Confiança', '')

            # Filtrar e ordenar
            df_timeline = df_timeline.dropna(subset=['Horario_dt'])
            df_timeline = df_timeline.sort_values('Horario_dt')

            # Criar colunas derivadas
            df_timeline['Jogo'] = df_timeline['Casa'] + ' x ' + df_timeline['Visitante']
            df_timeline['Horário Formatado'] = df_timeline['Horario_dt'].dt.strftime('%d/%m %H:%M')

            # Exibir apenas as colunas necessárias
            st.dataframe(df_timeline[['Horário Formatado', 'Jogo', 'Modelo', 'Índice de Confiança']],
                         use_container_width=True)
        except Exception as e:
            st.warning(f"Erro ao processar a coluna Horario: {e}")