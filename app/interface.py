import streamlit as st
import requests
import pandas as pd

API_URL = "http://api:8000"

st.title("Estoque - Produtos")

resposta = requests.get(f"{API_URL}/produtos/")
produtos = resposta.json()

if produtos:
    df = pd.DataFrame(produtos)
    st.dataframe(df)
else:
    st.info("Nenhum produto cadastrado ainda.")

st.subheader("Cadastrar novo produto")
with st.form("novo_produto"):
    nome = st.text_input("Nome")
    categoria = st.text_input("Categoria")
    quantidade = st.number_input("Quantidade", min_value=0.0)
    unidade = st.text_input("Unidade", value="unidade")
    estoque_minimo = st.number_input("Estoque mínimo", min_value=0.0)
    preco_custo = st.number_input("Preço de custo", min_value=0.0)
    preco_venda = st.number_input("Preço de venda", min_value=0.0)

    enviar = st.form_submit_button("Cadastrar")

    if enviar:
        payload = {
            "nome": nome,
            "categoria": categoria,
            "quantidade": quantidade,
            "unidade": unidade,
            "estoque_minimo": estoque_minimo,
            "preco_custo": preco_custo,
            "preco_venda": preco_venda,
        }
        r = requests.post(f"{API_URL}/produtos/", json=payload)
        if r.status_code == 200:
            st.success("Produto cadastrado!")
            st.rerun()
        else:
            st.error(f"Erro: {r.text}")