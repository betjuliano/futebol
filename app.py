# filepath: /workspaces/futebol/app.py
# app.py - Arquivo principal do Streamlit
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
from modules.auth import autenticar_usuario
from modules.data import carregar_dados, aplicar_modelos, calcular_indice_confiança

# Configuração da página
st.set_page_config(page_title="Dashboard Futebol PRO", layout="wide")

# Autenticação por email (via sidebar)
usuario = autenticar_usuario()
if not usuario:
    st.stop()

# Carrega dados da planilha
df_original = carregar_dados("JogosDia.xlsx")

# Aplica modelos e cálculos no dataframe
df = aplicar_modelos(df_original)
df = calcular_indice_confiança(df)

# Menu de navegação lateral
pagina = st.sidebar.radio("Escolha a página:", ["Dashboard de Jogos", "Gráficos e Análises"])

def pagina_dashboard(df):
    # Código para renderizar o dashboard
    st.title("Dashboard de Jogos")
    st.write(df)

def pagina_graficos(df):
    # Código para renderizar os gráficos
    st.title("Gráficos e Análises")
    st.line_chart(df)

# Renderiza a página selecionada
if pagina == "Dashboard de Jogos":
    pagina_dashboard(df)
elif pagina == "Gráficos e Análises":
    pagina_graficos(df)