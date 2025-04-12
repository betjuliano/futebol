import streamlit as st
import sys
import os

# Adicionando o diretório atual ao sys.path
# Limpar e configurar corretamente o path
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, 'modules')

# Remover duplicatas de 'modules' no sys.path
sys.path = [p for p in sys.path if p != 'modules']
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)

# Importar após configurar o path
from auth import autenticar_usuario
from data import carregar_dados, aplicar_modelos, calcular_indice_confiança
from pages import pagina_dashboard, pagina_graficos

# Configuração da página
st.set_page_config(page_title="Dashboard Futebol PRO", layout="wide")

# Autenticação
usuario = autenticar_usuario()
if not usuario:
    st.stop()

# Carregar dados
try:
    df_original = carregar_dados("JogosDia.xlsx")
    df = aplicar_modelos(df_original)
    df = calcular_indice_confiança(df)
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

# Interface principal
pagina = st.sidebar.radio("Escolha a página:", ["Dashboard de Jogos", "Gráficos e Análises"])

if pagina == "Dashboard de Jogos":
    pagina_dashboard(df)
elif pagina == "Gráficos e Análises":
    pagina_graficos(df)