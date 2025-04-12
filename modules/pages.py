import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def pagina_dashboard(df_input):
    st.header("Dashboard de Jogos por Modelo")

    # Verificar se o DataFrame é válido
    if df_input is None or df_input.empty:
        st.error("Nenhum dado disponível para exibição.")
        return

    # Verificar se a coluna 'Modelo' existe
    if 'Modelo' not in df_input.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Criar uma cópia completa para trabalhar
    df = df_input.copy()

    # Padronizar a coluna 'Modelo'
    df['Modelo'] = df['Modelo'].astype(str).str.strip()

    # Preparar filtros
    modelos = ["Todos"] + sorted(df['Modelo'].dropna().unique().tolist())
    modelo_selecionado = st.selectbox("Filtrar por Modelo:", modelos)

    exibir_so_com_tip = st.checkbox("Exibir apenas jogos com TIP", value=False)

    # Criar máscara de filtro
    mask = pd.Series(True, index=df.index)

    if modelo_selecionado != "Todos":
        mask = mask & (df['Modelo'] == modelo_selecionado)

    # Adicionar coluna TIP se necessário
    if all(col in df.columns for col in ['0x0', '1x0', '0x1']):
        def calcular_tip(row):
            tips = []
            if row.get('0x0', 1.0) < 0.04:
                tips.append('0-0')
            if row.get('1x0', 1.0) < 0.04:
                tips.append('1-0')
            if row.get('0x1', 1.0) < 0.04:
                tips.append('0-1')
            return ', '.join(tips)

        df['TIP'] = df.apply(calcular_tip, axis=1)
    else:
        st.warning("Colunas necessárias para calcular 'TIP' estão ausentes.")
        df['TIP'] = ''

    # Aplicar filtro de TIP
    if exibir_so_com_tip:
        mask = mask & (df['TIP'].str.strip() != '')

    # Aplicar filtro de campeonato se disponível
    if 'Campeonato' in df.columns:
        campeonatos = ["Todos"] + sorted(df.loc[mask, 'Campeonato'].dropna().unique().tolist())
        campeonato_selecionado = st.selectbox("Filtrar por Campeonato:", campeonatos)

        if campeonato_selecionado != "Todos":
            mask = mask & (df['Campeonato'] == campeonato_selecionado)

    # Aplicar todos os filtros
    df_filtrado = df.loc[mask].copy()

    # Verificar se há dados após os filtros
    if df_filtrado.empty:
        st.warning("Nenhum jogo encontrado com os filtros aplicados.")
        return

    # Definir colunas a exibir
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

    # Filtrar apenas colunas existentes
    colunas_existentes = [col for col in colunas_exibir if col in df_filtrado.columns]

    # Criar DataFrame de exibição
    df_exibicao = pd.DataFrame()

    # Colunas percentuais para formatação
    colunas_percentuais = [
        'PROJEÇÃO PTS CASA', 'PROJEÇÃO PTS VISITANTE',
        'PROJEÇÃO VIT CASA', 'PROJEÇÃO VIT VISITANTE',
        'PROJEÇÃO GOL CASA FEITO', 'PROJEÇÃO GOL VISITANTE FEITO',
        '%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT',
        '0x0', '0x1', '1x0'
    ]

    # Processar cada coluna individualmente
    for col in colunas_existentes:
        if col in colunas_percentuais:
            try:
                # Formatar como percentual
                df_exibicao[col] = (df_filtrado[col].astype(float) * 100).round(1).astype(str) + '%'
            except Exception as e:
                # Em caso de erro, usar o valor original
                df_exibicao[col] = df_filtrado[col]
        else:
            # Copiar diretamente para colunas não percentuais
            df_exibicao[col] = df_filtrado[col]

    # Exibir o DataFrame final
    st.dataframe(df_exibicao, use_container_width=True)


def pagina_graficos(df_input):
    st.header("Gráficos de Análise de Jogos")

    # Verificar se o DataFrame é válido
    if df_input is None or df_input.empty:
        st.error("Nenhum dado disponível para exibição.")
        return

    # Verificar se a coluna 'Modelo' existe
    if 'Modelo' not in df_input.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Criar uma cópia completa para trabalhar
    df = df_input.copy()

    # Frequência de Modelos
    st.subheader("Frequência de Modelos")

    # Calcular contagem de modelos
    modelo_counts = df['Modelo'].value_counts()

    # Criar figura
    fig1, ax1 = plt.subplots(figsize=(10, 6))

    # Definir cores para cada modelo
    cores_dict = {
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

    # Atribuir cores aos modelos
    colors = [cores_dict.get(modelo, "#90a4ae") for modelo in modelo_counts.index]

    # Criar gráfico de barras horizontais
    ax1.barh(modelo_counts.index, modelo_counts.values, color=colors)
    ax1.set_xlabel("Número de Jogos")
    ax1.set_title("Frequência de Modelos")

    # Exibir o gráfico
    st.pyplot(fig1)

    # Linha do Tempo dos Jogos
    st.subheader("Linha do Tempo dos Jogos")

    if 'Horario' in df.columns:
        try:
            # Criar DataFrame específico para a linha do tempo
            timeline_data = {
                'Horario': df['Horario'],
                'Casa': df['Casa'],
                'Visitante': df['Visitante'],
                'Modelo': df['Modelo']
            }

            # Adicionar Índice de Confiança se existir
            if 'Índice de Confiança' in df.columns:
                timeline_data['Índice de Confiança'] = df['Índice de Confiança']

            # Criar DataFrame
            df_timeline = pd.DataFrame(timeline_data)

            # Converter horário para datetime
            df_timeline['Horario_dt'] = pd.to_datetime(df_timeline['Horario'], errors='coerce')

            # Remover linhas com horário inválido
            df_timeline = df_timeline.dropna(subset=['Horario_dt'])

            # Ordenar por horário
            df_timeline = df_timeline.sort_values('Horario_dt')

            # Criar colunas derivadas
            df_timeline['Jogo'] = df_timeline['Casa'] + ' x ' + df_timeline['Visitante']
            df_timeline['Horário Formatado'] = df_timeline['Horario_dt'].dt.strftime('%d/%m %H:%M')

            # Selecionar colunas para exibição
            colunas_timeline = ['Horário Formatado', 'Jogo', 'Modelo']
            if 'Índice de Confiança' in df_timeline.columns:
                colunas_timeline.append('Índice de Confiança')

            # Exibir tabela
            st.dataframe(df_timeline[colunas_timeline], use_container_width=True)

        except Exception as e:
            st.warning(f"Erro ao processar a coluna Horario: {e}")
    else:
        st.warning("Coluna 'Horario' não encontrada para criar a linha do tempo.")