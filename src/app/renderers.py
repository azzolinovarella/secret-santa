from typing import List, Dict, Callable
import streamlit as st
from src.app.utils import get_available_algorithms


def render_header():
    st.write("# 🎅🏻 Secret Santa")


def render_waha_error():
    st.error(
        "Serviço do WAHA (WhatsApp) não está funcionando, não foi inicializado corretamente ou ainda está sendo inicializado. "
        "Inicialize o serviço novamente e reinicie a página quando isso foi realizado."
    )


def render_participants_num_form(on_click: Callable):
    st.write("## ▶️ Configurações iniciais")

    st.text_input(
        "Descreva o identificador do seu sorteio",
        value="Amigo Secreto",
        key="draft.secret_santa.description",  # Draft porque não é o definitivo (definitivo controlado no flow)
    )

    st.number_input(
        "Número de participantes",
        min_value=2,
        key="draft.secret_santa.num_participants",
    )

    st.button("Avançar", use_container_width=True, on_click=on_click)


def render_participants_dict_form(
    num_participants: int, on_return: Callable, on_advance: Callable
):
    st.write("## 👥 Participantes")
    st.info(
        "Informe o nome de cada participante do sorteio. "
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

    render_return_advance_buttons(on_return, on_advance)


def render_restrictions_form(
    participants_name: List[str], on_return: Callable, on_advance: Callable
):
    st.write("## ❌ Restrições")
    st.info(
        "Informe quais pessoas o referido participante **NÃO** pode tirar (além dele próprio)."
    )

    for name in participants_name:
        options = [n for n in participants_name if n != name]

        st.multiselect(
            f"Escolha as pessoas que {name} **NÃO** pode tirar (além dele próprio)",
            options=options,
            key=f"draft.restrictions.{name}",
        )

    render_return_advance_buttons(on_return, on_advance)


def render_algorithm_selection_form(on_return: Callable, on_advance: Callable):
    st.write("## 👨🏻‍💻 Seleção do algoritmo")
    st.selectbox(
        "Selecione o algoritmo para sorteio",
        options=list(get_available_algorithms().keys()),
        key="draft.secret_santa.selected_algorithm",
    )

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

    render_return_advance_buttons(on_return, on_advance)


def render_summary(
    description: str,
    num_participants: int,
    selected_algorithm: str,
    participants: list[dict[str, str]],
    restrictions: dict[str, list[str]],
    on_return: Callable,
    on_advance: Callable,
):
    st.write("## 📊 Resumo do sorteio")

    # Configurações
    st.write("### 🎄 Configurações\n")
    st.write(
        f"- **Descrição:** {description}\n"
        f"- **Número de participantes:** {num_participants}\n"
        f"- **Algoritmo selecionado:** {selected_algorithm}\n"
    )
    # st.divider()

    # Participantes
    st.write("### 👥 Participantes")
    participants_text = "\n".join(
        [
            f"- **Participante {i + 1}**: {p['name']} ({p['phone']})"
            for i, p in enumerate(participants)
        ]
    )
    st.write(participants_text)
    # st.divider()

    # Restrições
    st.write("### ❌ Restrições")
    restrictions_text = "\n".join(
        [
            (
                f"- **{name}** não pode tirar _{'_, _'.join(res)}_."
                if res  # Para evitar ficar mostrando que ele não pode tirar ele...
                else f"- **{name}** não tem restrições."
            )
            for name, res in restrictions.items()
        ]
    )
    st.write(restrictions_text)

    render_return_advance_buttons(
        on_return, on_advance, advance_type="primary", advance_label="Realizar sorteio"
    )


def render_results(errors: List[Dict], crypts: List[Dict], on_click: Callable):
    st.write("## 📖 Resultado do sorteio")
    if errors == []:
        st.success("✅ Mensagem encaminhada com sucesso para todos os participantes!")

    else:
        error_msg = f"❌ Houve erro ao enviar o resultado para as seguintes pessoas:\n"
        for e in errors:
            error_msg += f"- {e['name']} ({e['phone']})\n"

        st.error(error_msg)

    crypts_msg = ""
    for c in crypts:
        name = c["name"]
        crypt = c["crypt"]
        seed = c["seed"]
        key = c["key"].decode("utf-8")

        crypts_msg += (
            f"\nResultados de {name}:\n"
            f"{' ' * 4}- Token: {crypt}\n"
            f"{' ' * 4}- Seed:  {seed}\n"
            f"{' ' * 4}- Chave: {key}\n"
        )
    with st.expander("_Resultados criptografados (auditoria)_"):
        st.code(crypts_msg, language=None)

    st.button(
        "Ir para início", use_container_width=True, type="primary", on_click=on_click
    )


def render_return_advance_buttons(
    on_return: Callable,
    on_advance: Callable,
    return_label: str = "Voltar",
    advance_label: str = "Avançar",
    return_type: str = "secondary",
    advance_type: str = "secondary",
):
    col1, col2 = st.columns(2)

    col1.button(
        return_label,
        # key="...",  # TODO: Agora não uso (referencio direto)... Faz sentido passar?
        use_container_width=True,
        type=return_type,
        on_click=on_return,
    )

    col2.button(
        advance_label, use_container_width=True, type=advance_type, on_click=on_advance
    )
