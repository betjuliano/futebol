import streamlit as st
import sys
import os

# CORREÇÃO: Desativar a atualização automática do git
os.environ['GIT_TERMINAL_PROMPT'] = '0'

print("Caminho atual:", os.getcwd())
print("Caminho do sys.path:", sys.path)

# Limpar sys.path e adicionar apenas uma vez o diretório de módulos
modules_path = os.path.join(os.path.dirname(__file__), 'modules')
if modules_path not in sys.path:
    sys.path.append(modules_path)

from auth import autenticar_usuario
from data import carregar_dados, aplicar_modelos, calcular_indice_confiança
from modules.pages import pagina_dashboard, pagina_graficos

# Configuração da página
st.set_page_config(page_title="Dashboard Futebol PRO", layout="wide")

usuario = autenticar_usuario()
if not usuario:
    st.stop()

try:
    df_original = carregar_dados("JogosDia.xlsx")
    df = aplicar_modelos(df_original)
    df = calcular_indice_confiança(df)
except FileNotFoundError as e:
    st.error(f"Erro ao carregar o arquivo: {e}")
except KeyError as e:
    st.error(f"Erro ao processar os dados: {e}")

pagina = st.sidebar.radio("Escolha a página:", ["Dashboard de Jogos", "Gráficos e Análises"])

if pagina == "Dashboard de Jogos":
    pagina_dashboard(df)
elif pagina == "Gráficos e Análises":
    pagina_graficos(df)