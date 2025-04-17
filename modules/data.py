import pandas as pd

def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1bnyG54WZ_ggkvekqwIicZGFdR-KXCffWEcXcQ4v0KcI/export?format=xlsx"
    df = pd.read_excel(url, sheet_name="Jogos")
    df.fillna(0, inplace=True)

    # Exibir as primeiras linhas e tipos de dados
    st.write("Primeiras linhas do DataFrame:", df.head())
    st.write("Tipos de dados das colunas:", df.dtypes)

    # Converter colunas relevantes para numérico
    colunas_numericas = ['XG CASA', 'XG VISITANTE', 'ODD1', 'ODD2', 'ODD3', '%PARTIDAS GOLS CASA HT', '%PARTIDAS GOLS VISIT HT']
    for col in colunas_numericas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')  # Converte para numérico, substitui erros por NaN

            # Verificar se há valores NaN após a conversão
            if df[col].isnull().any():
                st.warning(f"A coluna '{col}' contém valores não numéricos. Valores convertidos para NaN.")

    # Opcional: Remover linhas com NaN nas colunas numéricas
    df.dropna(subset=colunas_numericas, inplace=True)

    return df

def aplicar_modelos(df):
    def classificar_modelo(row):
        # Lay 0x1 com Pressão da Casa (Alta Gols)
        if (row['XG CASA'] > row['XG VISITANTE'] and
            row['XG TOTAL'] > 1.5 and
            row['%PARTIDAS GOLS CASA HT'] > 0.6 and
            row['%PARTIDAS GOLS VISIT HT'] > 0.6 and
            row[['0x0', '0x1', '0x2']].nlargest(3).sum() == 0 and
            row['ODD2'] > 4 and
            row['PROJEÇÃO GOL CASA'] > 0.5 and
            row['PROJEÇÃO GOL VISITANTE'] < 0.5):
            return "Lay 0x1 com Pressão da Casa (Alta Gols)"

        # Lay 1x0 com Pressão do Visitante (Alta Gols)
        if (row['XG VISITANTE'] > row['XG CASA'] and
            row['XG TOTAL'] > 1.5 and
            row['%PARTIDAS GOLS CASA HT'] > 0.6 and
            row['%PARTIDAS GOLS VISIT HT'] > 0.6 and
            row[['0x0', '1x0', '2x0']].nlargest(4).sum() == 0 and
            row['ODD2'] > 4 and
            row['PROJEÇÃO GOL VISITANTE'] > 0.5 and
            row['PROJEÇÃO GOL CASA'] < 0.5):
            return "Lay 1x0 com Pressão do Visitante (Alta Gols)"

        # Lay Casa
        if (row['%PARTIDAS GOLS CASA HT'] < 0.7 and
            row['%GOLS VISITANTE'] > 0.7 and
            row['%JOGOS VENCIDOS VISITANTE'] > 0.5 and
            row['%JOGOS PERDIDOS CASA'] > 0.5 and
            row['PROJEÇÃO PTS CASA'] < 0.5 and
            row['PROJEÇÃO PTS VISITANTE'] > 0.5):
            return "Lay Casa"

        # Lay Visitante
        if (row['%PARTIDAS GOLS CASA HT'] > 0.7 and
            row['%GOLS VISITANTE'] < 0.7 and
            row['%JOGOS VENCIDOS CASA'] > 0.5 and
            row['%JOGOS PERDIDOS VISITANTE'] > 0.5 and
            row['PROJEÇÃO PTS CASA'] > 0.5 and
            row['PROJEÇÃO PTS VISITANTE'] < 0.5):
            return "Lay Visitante"

        # Lay Goleada Casa
        if (row['XG CASA'] > row['XG VISITANTE'] and
            row['XG TOTAL'] > 1.5 and
            row['%PARTIDAS GOLS CASA HT'] > 0.6 and
            row[['0x0', '0x1', '0x2']].nlargest(3).sum() == 0 and
            row['GOLEADA CASA'] < 0.04):
            return "Lay Goleada Casa"

        # Alta probabilidade de gols
        if (row.get('0x0', 1) < 0.05 and
            row.get('0x1', 1) < 0.05 and
            row.get('1x0', 1) < 0.05 and
            row['XG TOTAL'] > 1.5):
            if row.get('GOLEADA CASA', 0) > 0.1 or row.get('GOLEADA VISITANTE', 0) > 0.1:
                return "Alta Confiança de Gols (Potencial Goleada)"
            return "Alta Confiança de Gols"

        # Possível Goleada Casa ou Visitante
        if row.get('GOLEADA CASA', 0) > 0.2 and row.get('XG CASA', 0) > 1.8:
            return "Possível Goleada da Casa"
        if row.get('GOLEADA VISITANTE', 0) > 0.2 and row.get('XG VISITANTE', 0) > 1.8:
            return "Possível Goleada do Visitante"

        return "Sem Classificação"

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

    df.drop(columns=['Índice Bruto'], inplace=True)

    return df