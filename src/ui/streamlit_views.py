from typing import Tuple, List, Dict
from ..app.algorithms import get_available_algorithms
import streamlit as st


def render_header():
    st.write("# 🎅🏻 Secret Santa")


def render_waha_error():
    st.error("Serviço do WAHA (WhatsApp) não está funcionando, não foi inicializado corretamente ou ainda está sendo inicializado. " \
             "Inicialize o serviço novamente e reinicie a página quando isso foi realizado.")


def render_participants_num_form(on_click):
    st.write("## ▶️ Configurações iniciais")

    st.text_input(
        "Descreva o identificador do seu sorteio",
        value="Amigo Secreto",
        key="draft.secret_santa.description",  # Draft porque não é o definitivo (definitivo controlado no flow)
    )

    col1, col2 = st.columns([0.69, 0.31], vertical_alignment="bottom")

    col1.number_input(
        "Número de participantes",
        min_value=2,
        key="draft.secret_santa.num_participants",
    )

    col2.button(
        "Gerar lista de participantes",
        key="draft.button.submit_num_participants",
        on_click=on_click
    )


def render_participants_dict_form(num_participants: int):
    st.write("## 📋 Lista de participantes")
    st.info(
        "Informe o nome de cada participante do sorteio. " \
        "Se houver pessoas com o mesmo nome, inclua o sobrenome."
    )

    for i in range(num_participants):
        col1, col2 = st.columns([0.6, 0.4])

        col1.text_input(
            f"Nome do participante {i + 1}",
            placeholder="Fulano da Silva",
            key=f"draft.participants.{i}.name",
        )

        col2.text_input(
            f"Telefone do participante {i + 1}",
            placeholder="55 11 4002 8922",
            key=f"draft.participants.{i}.phone",
        )

    st.button(
        "Gerar lista de restrições de sorteio",
        key="draft.button.submit_participants",
        use_container_width=True,
    )


def render_restrictions_form(participants: List[Dict[str, str]]) -> None:
    st.write("## ❌ Lista de restrições")
    st.info(
        "Informe quais pessoas o referido participante **NÃO** pode tirar (além dele próprio)."
    )

    names = [p["name"] for p in participants]

    for name in names:
        options = [n for n in names if n != name]

        st.multiselect(
            f"Escolha as pessoas que {name} **NÃO** pode tirar (além dele próprio)",
            options=options,
            key=f"draft.restrictions.{name}",
        )
    
    st.button(
        "Submeter lista de restrições",
        key="draft.button.submit_restriction",
        use_container_width=True
    )


def render_algorithm_selection_form():
    st.write("## 👨🏻‍💻 Seleção do algoritmo")

    with st.expander("_Qual algoritmo escolher? Clique aqui para saber mais_"):
        st.write(
            "**Algoritmo de Las Vegas**: Imagine que você está fazendo um sorteio, colocando os "
            "nomes em um chapéu e tirando um de cada vez. Você tenta atribuir cada participante "
            "a alguém aleatoriamente, mas se alguém ficar sem opções válidas, você joga tudo de "
            "volta e sorteia de novo. O Las Vegas é como um jogo de “tente até dar certo”: ele "
            "sempre encontra uma solução correta, mas pode demorar se a sorte não ajudar."
        )

        st.write(
            "**Algoritmo DFS (_Depth-First Search_)**: Agora imagine que você está planejando o "
            "sorteio como um labirinto. Você começa com o primeiro participante e segue escolhendo "
            "quem ele vai tirar. Cada pessoa pega alguém que ainda não foi escolhida e você continua "
            "assim, passo a passo, até que todos tenham alguém. No final, forma-se um ciclo: cada "
            "participante está ligado ao próximo em sequência até voltar ao primeiro, sem ter quebra "
            "na dinâmica."
        )

    st.selectbox(
        "Selecione o algoritmo para sorteio",
        options=list(get_available_algorithms().keys()),
        key="draft.secret_santa.selected_algorithm",
    )

    st.write("Se estiver tudo correto, clique abaixo para realizar o sorteio.")
    st.button(
        "Finalizar sorteio",
        key="draft.button.submit_selected_algorithm",
        use_container_width=True
    )

# def render_restrictions_summary(participants):
#     with st.expander("_Sumário das restrições_"):
#         for p in participants:
#             name = p["name"]
#             res = st.session_state.get(f"restrictions{name}", [])
#             if not res:
#                 st.write(f"{name} não tem restrições")
#             else:
#                 st.write(f"{name} não pode tirar {res}")