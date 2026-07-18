"""Interface de chat do Vero, o agente financeiro inteligente."""
import streamlit as st

from agente import carregar_base_conhecimento, responder
from config import NOME_AGENTE

st.set_page_config(page_title=f"{NOME_AGENTE} — Agente Financeiro", page_icon="🌿")

st.title(f"🌿 {NOME_AGENTE}")
st.caption("Seu agente financeiro consultivo — respostas sempre ancoradas nos seus dados.")

# Carrega a base de conhecimento (dados mockados) uma única vez por sessão
if "base" not in st.session_state:
    st.session_state.base = carregar_base_conhecimento()

if "mensagens" not in st.session_state:
    nome_cliente = st.session_state.base["perfil"]["nome"].split()[0]
    st.session_state.mensagens = [
        {
            "role": "assistant",
            "content": (
                f"Oi, {nome_cliente}! Sou o {NOME_AGENTE}, seu assistente financeiro. "
                "Já dei uma olhada nos seus últimos lançamentos e nas suas metas — "
                "posso te ajudar com gastos, investimentos ou dúvidas sobre seus produtos. "
                "Por onde quer começar?"
            ),
        }
    ]

for msg in st.session_state.mensagens:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

pergunta = st.chat_input("Escreva sua pergunta para o Vero...")

if pergunta:
    st.session_state.mensagens.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        with st.spinner("Vero está consultando seus dados..."):
            resposta = responder(st.session_state.mensagens, st.session_state.base)
            st.markdown(resposta)

    st.session_state.mensagens.append({"role": "assistant", "content": resposta})

with st.sidebar:
    st.subheader("Sobre este protótipo")
    st.write(
        "Esta é uma demonstração do Vero usando dados fictícios de um único "
        "cliente (João Silva). Toda resposta é gerada com base nos arquivos "
        "de `data/`, injetados no contexto do modelo — veja `docs/02-base-conhecimento.md`."
    )
    if st.button("Reiniciar conversa"):
        st.session_state.mensagens = []
        st.rerun()
