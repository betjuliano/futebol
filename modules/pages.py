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
    df = df.copy()  # Criar uma cópia completa do DataFrame
    df['Modelo'] = df['Modelo'].astype(str).str.strip()

    # Converter a coluna Horario para datetime se existir
    if 'Horario' in df.columns:
        try:
            # Primeiro, verificar o formato da coluna Horario
            amostra_horario = df['Horario'].iloc[0] if not df.empty else ""
            st.write(f"Formato da coluna Horario: {amostra_horario}")

            # Tentar converter para datetime com diferentes formatos
            try:
                df['Horario_dt'] = pd.to_datetime(df['Horario'], format='%d/%m/%Y %H:%M', errors='coerce')
            except:
                try:
                    df['Horario_dt'] = pd.to_datetime(df['Horario'], errors='coerce')
                except Exception as e:
                    st.warning(f"Erro ao converter horários: {e}")
                    df['Horario_dt'] = pd.NaT
        except Exception as e:
            st.warning(f"Erro ao processar a coluna Horario: {e}")
            df['Horario_dt'] = pd.NaT

    # Filtro por modelo
    modelos = ["Todos"] + sorted(df['Modelo'].dropna().unique())
    modelo = st.selectbox("Filtrar por Modelo:", modelos)

    # Aplica o filtro por modelo
    if modelo != "Todos":
        df_filtrado = df[df['Modelo'] == modelo].copy()
    else:
        df_filtrado = df.copy()

    # Verifica se há dados após o filtro por modelo
    if df_filtrado.empty:
        st.warning("Nenhum jogo encontrado para esse modelo.")
        return

    # Filtro por horário
    if 'Horario_dt' in df_filtrado.columns:
        # Obter horário atual
        agora = pd.Timestamp.now()

        # Mostrar o horário atual para debug
        st.write(f"Horário atual: {agora.strftime('%d/%m/%Y %H:%M')}")

        # Mostrar alguns exemplos de horários do DataFrame para debug
        if not df_filtrado.empty:
            st.write("Exemplos de horários no DataFrame:")
            for i, row in df_filtrado.head(3).iterrows():
                if pd.notna(row.get('Horario_dt')):
                    st.write(f"Horario original: {row.get('Horario', 'N/A')}, Horario_dt: {row.get('Horario_dt').strftime('%d/%m/%Y %H:%M')}")

        # Criar opções de filtro de horário
        opcoes_horario = [
            "Todos os horários",
            "Próximas 2 horas",
            "Últimas 2 horas",
            "Últimas 2h e próximas 2h",
            "Hoje",
            "Amanhã"
        ]

        filtro_horario = st.selectbox("Filtrar por Horário:", opcoes_horario)

        if filtro_horario != "Todos os horários":
            # Remover linhas com horário inválido
            df_filtrado = df_filtrado.dropna(subset=['Horario_dt']).copy()

            if filtro_horario == "Próximas 2 horas":
                # Jogos nas próximas 2 horas
                inicio = agora
                fim = agora + pd.Timedelta(hours=2)
                df_filtrado = df_filtrado[(df_filtrado['Horario_dt'] >= inicio) &
                                         (df_filtrado['Horario_dt'] <= fim)].copy()
                st.info(f"Mostrando jogos entre {inicio.strftime('%d/%m/%Y %H:%M')} e {fim.strftime('%d/%m/%Y %H:%M')}")

            elif filtro_horario == "Últimas 2 horas":
                # Jogos nas últimas 2 horas
                inicio = agora - pd.Timedelta(hours=2)
                fim = agora
                df_filtrado = df_filtrado[(df_filtrado['Horario_dt'] >= inicio) &
                                         (df_filtrado['Horario_dt'] <= fim)].copy()
                st.info(f"Mostrando jogos entre {inicio.strftime('%d/%m/%Y %H:%M')} e {fim.strftime('%d/%m/%Y %H:%M')}")

            elif filtro_horario == "Últimas 2h e próximas 2h":
                # Jogos nas últimas 2 horas e próximas 2 horas
                inicio = agora - pd.Timedelta(hours=2)
                fim = agora + pd.Timedelta(hours=2)
                df_filtrado = df_filtrado[(df_filtrado['Horario_dt'] >= inicio) &
                                         (df_filtrado['Horario_dt'] <= fim)].copy()
                st.info(f"Mostrando jogos entre {inicio.strftime('%d/%m/%Y %H:%M')} e {fim.strftime('%d/%m/%Y %H:%M')}")

            elif filtro_horario == "Hoje":
                # Jogos de hoje
                hoje_inicio = pd.Timestamp(agora.date())
                hoje_fim = hoje_inicio + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                df_filtrado = df_filtrado[(df_filtrado['Horario_dt'] >= hoje_inicio) &
                                         (df_filtrado['Horario_dt'] <= hoje_fim)].copy()
                st.info(f"Mostrando jogos de hoje ({hoje_inicio.strftime('%d/%m/%Y')})")

            elif filtro_horario == "Amanhã":
                # Jogos de amanhã
                amanha_inicio = pd.Timestamp(agora.date()) + pd.Timedelta(days=1)
                amanha_fim = amanha_inicio + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                df_filtrado = df_filtrado[(df_filtrado['Horario_dt'] >= amanha_inicio) &
                                         (df_filtrado['Horario_dt'] <= amanha_fim)].copy()
                st.info(f"Mostrando jogos de amanhã ({amanha_inicio.strftime('%d/%m/%Y')})")

        # Verifica se há dados após o filtro de horário
        if df_filtrado.empty:
            st.warning("Nenhum jogo encontrado para o horário selecionado.")
            return

    # Filtro por TIP
    exibir_so_com_tip = st.checkbox("Exibir apenas jogos com TIP", value=False)

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
        df_filtrado = df_filtrado[df_filtrado['TIP'].str.strip() != ''].copy()

    # Verifica se há dados após o filtro TIP
    if df_filtrado.empty:
        st.warning("Nenhum jogo encontrado com os filtros aplicados.")
        return

    # Filtro por campeonato
    if 'Campeonato' in df_filtrado.columns:
        campeonatos = ["Todos"] + sorted(df_filtrado['Campeonato'].dropna().unique())
        campeonato = st.selectbox("Filtrar por Campeonato:", campeonatos)
        if campeonato != "Todos":
            df_filtrado = df_filtrado[df_filtrado['Campeonato'] == campeonato].copy()

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

    # Criar um novo DataFrame para exibição
    df_exibicao = df_filtrado[colunas_existentes].copy()

    # Formatar as colunas percentuais
    for col in colunas_percentuais:
        if col in df_exibicao.columns:
            try:
                df_exibicao[col] = (df_exibicao[col].astype(float) * 100).round(1).astype(str) + '%'
            except Exception as e:
                st.warning(f"Erro ao formatar a coluna {col}: {e}")

    # Exibe os dados finais no dashboard
    st.dataframe(df_exibicao, use_container_width=True)


def pagina_graficos(df):
    st.header("Gráficos de Análise de Jogos")

    # Criar uma cópia do DataFrame
    df = df.copy()

    # Verifica se a coluna 'Modelo' existe
    if 'Modelo' not in df.columns:
        st.error("A coluna 'Modelo' não foi encontrada no DataFrame.")
        return

    # Converter a coluna Horario para datetime se existir
    if 'Horario' in df.columns:
        try:
            df['Horario_dt'] = pd.to_datetime(df['Horario'], errors='coerce')
        except Exception as e:
            st.warning(f"Erro ao converter horários: {e}")
            df['Horario_dt'] = pd.NaT

    # Filtro por horário
    if 'Horario_dt' in df.columns:
        # Obter horário atual
        agora = pd.Timestamp.now()

        # Criar opções de filtro de horário
        opcoes_horario = [
            "Todos os horários",
            "Próximas 2 horas",
            "Últimas 2 horas",
            "Últimas 2h e próximas 2h",
            "Hoje",
            "Amanhã"
        ]

        filtro_horario = st.selectbox("Filtrar por Horário:", opcoes_horario)

        if filtro_horario != "Todos os horários":
            if filtro_horario == "Próximas 2 horas":
                # Jogos nas próximas 2 horas
                inicio = agora
                fim = agora + pd.Timedelta(hours=2)
                df = df[(df['Horario_dt'] >= inicio) &
                        (df['Horario_dt'] <= fim)].copy()
                st.info(f"Mostrando jogos entre {inicio.strftime('%H:%M')} e {fim.strftime('%H:%M')} de hoje")

            elif filtro_horario == "Últimas 2 horas":
                # Jogos nas últimas 2 horas
                inicio = agora - pd.Timedelta(hours=2)
                fim = agora
                df = df[(df['Horario_dt'] >= inicio) &
                        (df['Horario_dt'] <= fim)].copy()
                st.info(f"Mostrando jogos entre {inicio.strftime('%H:%M')} e {fim.strftime('%H:%M')} de hoje")

            elif filtro_horario == "Últimas 2h e próximas 2h":
                # Jogos nas últimas 2 horas e próximas 2 horas
                inicio = agora - pd.Timedelta(hours=2)
                fim = agora + pd.Timedelta(hours=2)
                df = df[(df['Horario_dt'] >= inicio) &
                        (df['Horario_dt'] <= fim)].copy()
                st.info(f"Mostrando jogos entre {inicio.strftime('%H:%M')} e {fim.strftime('%H:%M')}")

            elif filtro_horario == "Hoje":
                # Jogos de hoje
                hoje_inicio = pd.Timestamp(agora.date())
                hoje_fim = hoje_inicio + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                df = df[(df['Horario_dt'] >= hoje_inicio) &
                        (df['Horario_dt'] <= hoje_fim)].copy()
                st.info(f"Mostrando jogos de hoje ({hoje_inicio.strftime('%d/%m/%Y')})")

            elif filtro_horario == "Amanhã":
                # Jogos de amanhã
                amanha_inicio = pd.Timestamp(agora.date()) + pd.Timedelta(days=1)
                amanha_fim = amanha_inicio + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
                df = df[(df['Horario_dt'] >= amanha_inicio) &
                        (df['Horario_dt'] <= amanha_fim)].copy()
                st.info(f"Mostrando jogos de amanhã ({amanha_inicio.strftime('%d/%m/%Y')})")

        # Verifica se há dados após o filtro de horário
        if df.empty:
            st.warning("Nenhum jogo encontrado para o horário selecionado.")
            return

    # Frequência de Modelos
    st.subheader("Frequência de Modelos")
    modelo_counts = df['Modelo'].value_counts()
    fig1, ax1 = plt.subplots()

    # Definir o dicionário de cores corretamente
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
            # Criar um novo DataFrame para a linha do tempo
            df_timeline = pd.DataFrame()
            df_timeline['Horario_dt'] = pd.to_datetime(df['Horario'], errors='coerce')
            df_timeline['Casa'] = df['Casa']
            df_timeline['Visitante'] = df['Visitante']
            df_timeline['Modelo'] = df['Modelo']
            if 'Índice de Confiança' in df.columns:
                df_timeline['Índice de Confiança'] = df['Índice de Confiança']

            # Filtrar e ordenar
            df_timeline = df_timeline.dropna(subset=['Horario_dt'])
            df_timeline = df_timeline.sort_values('Horario_dt')

            # Criar colunas derivadas
            df_timeline['Jogo'] = df_timeline['Casa'] + ' x ' + df_timeline['Visitante']
            df_timeline['Horário Formatado'] = df_timeline['Horario_dt'].dt.strftime('%d/%m %H:%M')

            # Selecionar colunas para exibição
            colunas_timeline = ['Horário Formatado', 'Jogo', 'Modelo']
            if 'Índice de Confiança' in df_timeline.columns:
                colunas_timeline.append('Índice de Confiança')

            st.dataframe(df_timeline[colunas_timeline], use_container_width=True)
        except Exception as e:
            st.warning(f"Erro ao processar a coluna Horario: {e}")