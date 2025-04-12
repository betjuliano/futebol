import streamlit as st
import sys
import os

# Adiciona o caminho do diretório atual ao sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from auth import autenticar_usuario
from data import carregar_dados, aplicar_modelos, calcular_indice_confiança
from modules.pages import pagina_dashboard, pagina_graficos

# Configuração da página
st.set_page_config(page_title="Dashboard Futebol PRO", layout="wide")

usuario = autenticar_usuario()
if not usuario:
    st.stop()

df_original = carregar_dados("JogosDia.xlsx")
df = aplicar_modelos(df_original)
df = calcular_indice_confiança(df)

# Verifica os dados carregados
st.write("Dados carregados:")
st.dataframe(df)

pagina = st.sidebar.radio("Escolha a página:", ["Dashboard de Jogos", "Gráficos e Análises"])

# Verifica a página selecionada
st.write(f"Página selecionada: {pagina}")

if pagina == "Dashboard de Jogos":
    pagina_dashboard(df)
elif pagina == "Gráficos e Análises":
    pagina_graficos(df)