# app.py - Arquivo principal do Streamlit
import streamlit as st
from modules.auth import autenticar_usuario
from modules.data import carregar_dados, aplicar_modelos, calcular_indice_confiança
from modules.pages import pagina_dashboard, pagina_graficos

# Configuração da página
st.set_page_config(page_title="Dashboard Futebol PRO", layout="wide")

# Autenticação por email (via sidebar)
usuario = autenticar_usuario()
if not usuario:
    st.stop()

# Carrega dados da planilha
df_original = carregar_dados("jogos1104.xlsx")

# Aplica modelos e cálculos no dataframe
df = aplicar_modelos(df_original)
df = calcular_indice_confiança(df)

# Menu de navegação lateral
pagina = st.sidebar.radio("Escolha a página:", ["Dashboard de Jogos", "Gráficos e Análises"])

# Renderiza a página selecionada
if pagina == "Dashboard de Jogos":
    pagina_dashboard(df)
elif pagina == "Gráficos e Análises":
    pagina_graficos(df)
