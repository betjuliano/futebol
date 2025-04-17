import streamlit as st
import sys
import os
from auth import autenticar_usuario
from data import listar_arquivos_drive, carregar_dados
from pages import pagina_dashboard, pagina_graficos

# Configurações iniciais
os.environ['GIT_TERMINAL_PROMPT'] = '0'
current_dir = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.join(current_dir, 'modules')

# Limpar sys.path e adicionar o diretório de módulos
sys.path = [p for p in sys.path if p != 'modules']
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)

# Configuração da página
st.set_page_config(page_title="Dashboard Futebol PRO", layout="wide")

# Autenticação
email = autenticar_usuario()
if email is None:
    st.stop()  # Para a execução se o usuário não estiver autenticado

# Listar arquivos na pasta do Google Drive
folder_id = '1wj4HZ35KQrSRIlCBQxRPlRtbeu2FCi2V'  # ID da pasta
try:
    arquivos = listar_arquivos_drive(folder_id)
except Exception as e:
    st.error(f"Erro ao listar arquivos: {e}")
    st.stop()

# Selecionar a data
data_selecionada = st.selectbox("Selecione a data:", list(arquivos.keys()))

# Carregar dados da planilha correspondente
if data_selecionada:
    file_id = arquivos[data_selecionada]
    try:
        df = carregar_dados(file_id)
        df = aplicar_modelos(df)
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