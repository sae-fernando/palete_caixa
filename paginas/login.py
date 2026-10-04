import streamlit as st # como é front end, então usamos o streamlit
from banco_dados.db import autenticar

def pagina_login():
    st.title("🔐 Login")
    with st.form("form_login"):
        usuario = st.text_input("Usuario")
        senha = st.text_input("Senha", type="password")
        entrar = st.form_submit_button("Entrar")

    if entrar:
        print(f"{usuario = } | {senha = } | {entrar = }")
        if not usuario or not senha:
            st.warning("Preencha usuário e senha.")
            return  #não deixa o streamlit ler o resto da página

        resultado = autenticar(usuario, senha)
        print(resultado)

        if resultado is None:
            st.error("Usuario ou senha inválidos")
        elif "erro" in resultado:
            st.error(resultado["erro"])
        else:
            st.session_state.usuario = resultado
            st.rerun()