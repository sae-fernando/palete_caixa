from enum import auto

import streamlit as st
from banco_dados.db import (criar_usuario, listar_tipos_status, listar_tipos_usuario)

def pagina_criar():
    st.header(":heavy_plus_sign: Criar Usuário")

    opcoes_tipo_usuarios = listar_tipos_usuario()

    with st.form("form_criar"):
        col1, col2 = st.columns(2) #Aqui
        cnpj = col1.text_input("CNPJ (14 dígitos, sem pontuação)", placeholder="12345678000144") # O "placeholder" ajuda a colocar uma dica de preenchimento
        razao_social = col2.text_input("Razão Social")
        nome_fantasia = col1.text_input("Nome Fantasia")
        nome_contato = col2.text_input("Nome Contato")
        telefone = col1.text_input("Telefone", type="phone", autocomplete="tel")
        email = col2.text_input("E-mail")

        st.divider()
        col1, col2 = st.columns(2) # Aqui vai sobreescrever as variáveis para colocar o divider na posição correta

        nome_usuario = col1.text_input("Nome de usuário")
        tipo = col2.selectbox("Tipo do Usuário", opcoes_tipo_usuarios)
        senha = col1.text_input("Senha", type="password", placeholder="Pelo menos 6 caracteres")
        confirmar = col2.text_input("Confirmar senha", type="password")

        criar = st.form_submit_button("Criar Usuário")

    if criar:
        erros = []
        if not cnpj or len(cnpj) != 14 or not cnpj.isdigit():
            erros.append("CNPJ deve ter exatamente 14 digitos numericos")

        if not razao_social:
            erros.append("Razão Social pe obrigatória")

        if not nome_usuario:
            erros.append("Nome de usuário é obrigatório")

        if not senha:
            erros.append("Senha é obrigatória")
        elif len(senha) < 6:
            erros.append("Senha deve ter pelo menos 6 caracteres")
        elif senha != confirmar:
            erros.append("Senhas não conferem")
        if erros:
            for e in erros:
                st.warning(f":warning: {e}")
            return

        dados = {
            "cnpj": cnpj,
            "razao_social": razao_social,
            "nome_fantasia": nome_fantasia,
            "nome_contato": nome_contato,
            "telefone_contato": telefone,
            "nome_usuario": nome_usuario,
            "status": "ativo",
            "tipo": tipo,
        }
        erro = criar_usuario(dados, senha)
        if erro:
            st.error(erro)
        else:
            st.success(f"Usuário **{nome_usuario}** criado com sucesso!")
        


