import pandas as pd
import requests

def listar_arquivos_drive(folder_id):
    # URL da API do Google Drive para listar arquivos
    url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}' in parents&key=AIzaSyBowt-JKmhwHOT7fUBi9ILKh_XR6_xKUCw"
    response = requests.get(url)

    # Verificar a resposta da API
    if response.status_code == 200:
        files = response.json().get('files', [])
        return {file['name']: file['id'] for file in files}
    else:
        # Exibir mensagem de erro detalhada
        raise Exception(f"Erro ao acessar a API do Google Drive: {response.status_code} - {response.text}")

def carregar_dados(file_id):
    url = f"https://drive.google.com/uc?id={file_id}"

    # Carregar o arquivo Excel usando openpyxl
    response = requests.get(url)
    if response.status_code == 200:
        # Usar io.BytesIO para ler o conteúdo do arquivo
        excel_file = io.BytesIO(response.content)
        workbook = load_workbook(filename=excel_file, data_only=True)

        # Acessar a primeira aba (ou a aba desejada)
        sheet = workbook.active

        # Desocultar colunas
        for column in sheet.columns:
            if column[0].hidden:  # Verifica se a coluna está oculta
                column[0].hidden = False  # Desoculta a coluna

        # Salvar as alterações em um novo arquivo
        temp_file = io.BytesIO()
        workbook.save(temp_file)
        temp_file.seek(0)  # Voltar ao início do arquivo

        # Carregar o DataFrame com Pandas
        df = pd.read_excel(temp_file)
        df.fillna(0, inplace=True)
        return df
    else:
        raise Exception("Erro ao acessar o arquivo no Google Drive.")

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