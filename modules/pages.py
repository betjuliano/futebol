# modules/pages.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def pagina_dashboard(df):
    st.title("Dashboard de Jogos")
    st.write("Aqui está o dashboard de jogos:")
    st.dataframe(df)

def pagina_graficos(df):
    # Código para renderizar os gráficos
    pass
