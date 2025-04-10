import streamlit as st

EMAILS_PERMITIDOS = {
    "admjulianoo@gmail.com",
    "riparg2000@gmail.com",
    "seu_email@exemplo.com"
}

def autenticar_usuario():
    st.sidebar.subheader("Autenticação")
    email = st.sidebar.text_input("Digite seu email para acessar o dashboard")

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if email in EMAILS_PERMITIDOS:
        st.session_state.authenticated = True
        st.sidebar.success(f"Bem-vindo(a), {email}!")
        return email
    elif email:  # Se digitou algo, mas não está na lista
        st.sidebar.warning("Email não autorizado.")
        return None
    else:  # Se ainda não digitou
        st.sidebar.info("Insira seu email para acessar o conteúdo.")
        return None