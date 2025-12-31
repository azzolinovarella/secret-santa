import time
import os
import base64
import streamlit as st
from typing import Any, Optional, Dict, Tuple
from dotenv import load_dotenv
from src import SecretSanta, BaseDrawer, DFSDrawer, LasVegasDrawer, WAHA

def initialize_states():
    defaults = {
        # Variáveis
        "participants": [],
        "restrictions": {},
        "selected_algorithm": None,
        "description": None,
        # Para controle de fluxo
        "show_participants": False,
        "show_restrictions": False,
        "enable_res_generation": False,
        "messages_sent": False,
        # Objetos
        # "waha": None,  # Instanciado depois
        "drawer": None,
        "secret_santa": None
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Objetos complexos (objeto já instanciado com alguns valores padrão)
    if "waha" not in st.session_state:
        set_waha()


def set_waha():
    waha = WAHA(
        session_name="default",
        host="waha",  # Vide docker-compose
        api_port=os.environ.get("WHATSAPP_API_PORT"),
        api_key=os.environ.get("WAHA_API_KEY"),
    )
    waha.start_session()
    st.session_state.waha = waha


def get_waha() -> WAHA:
    return st.session_state.waha
        

def get_available_algorithms() -> Dict[str, BaseDrawer]:
    return {
        "Algoritmo de Las Vegas": LasVegasDrawer(),
        "Algoritmo DFS": DFSDrawer()
    }


def set_drawer(drawer_alias: str):
    available_algoritms = get_available_algorithms()
    try:
        drawer = available_algoritms[drawer_alias]
    except KeyError:
        raise NotImplementedError("O algoritmo de sorteio deve ser um dentre Las Vegas e DFS.") 

    st.session_state.drawer = drawer   


def get_drawer() -> BaseDrawer:
    return st.session_state.drawer


def get_secret_santa(): 
    return st.session_state.secret_santa


def waha_is_working() -> bool:
    try:
        waha = get_waha()
        code, content = waha.get_session_status()
        return code == 200 and content.get("status") == "WORKING"
    except Exception:
        return False


def render_header():
    st.write("# 🎅🏻 Secret Santa")


def render_waha_error():
    st.error("Serviço do WAHA (WhatsApp) não está funcionando, não foi inicializado corretamente ou ainda está sendo inicializado. " \
             "Inicialize o serviço novamente e reinicie a página quando isso foi realizado.")


def render_participants_num_form() -> Tuple[int, bool, str]:
    ss_desc = st.text_input(
        "Descreva o identificador do seu sorteio", value="Amigo Secreto"
    )
    if ss_desc is None:
        ss_desc = "Amigo Secreto"

    col1, col2 = st.columns([0.69, 0.31], vertical_alignment="bottom")
    num_participants = col1.number_input("Número de participantes", min_value=2)
    clicked_generate_list = col2.button("Gerar lista de participantes", key="base_list")

    return num_participants, clicked_generate_list, ss_desc


def handle_participants_num_form(num_participants: int, description: str):
    st.session_state.show_participants = True
    st.session_state.show_restrictions = (
        False  # Reseta para garantir que vai sumir com o menu para nova geração
    )
    st.session_state.num_participants = num_participants
    st.session_state.participants = [""] * st.session_state.num_participants
    del st.session_state.restrictions
    st.session_state.enable_res_generation = False
    st.session_state.description = description


def render_participants_form() -> bool:
    st.write("## 📋 Lista de participantes")
    st.info(
        """Informe o nome de cada participante do sorteio. 
            Se houver pessoas com o mesmo nome, inclua o sobrenome."""
    )

    # Gera campo a campo para informar os nomes
    for i in range(st.session_state.num_participants):
        col1, col2 = st.columns([0.6, 0.4])
        participant_name = col1.text_input(
            f"Insira o nome do participante {i + 1}",
            placeholder="Fulano da Silva",
            key=f"participant_name_{i}",
        )
        participant_phone = col2.text_input(
            f"Insira o telefone do participante {i + 1}",
            placeholder="55 11 4002 8922",
            key=f"participant_phone_{i}",
        )

        participant_name = participant_name.strip()
        participant_phone = participant_phone.replace(" ", "").replace("-", "").replace("+", "").replace("(", "").replace(")", "")

        st.session_state.participants[i] = {  # TODO: Melhor forma de fazer isso?
            "name": participant_name,
            "phone": participant_phone,
        }

    # Botão para gerar restrições
    clicked_generate_restrictions = st.button(
        "Gerar lista de restrições de sorteio",
        key="restriction_list",
        use_container_width=True,
    )

    return clicked_generate_restrictions


def handle_participants_form():
    st.session_state.show_restrictions = False  # Começa por padrão considerando que não vai

    names = [p["name"] for p in st.session_state.participants]
    phones = [p["phone"] for p in st.session_state.participants]

    if not all(names):
        del st.session_state.restrictions
        st.error("Para avançar é necessário fornecer o nome de todas as pessoas.")

        return

    try:
        _ = [int(p) for p in phones]
    except ValueError:
        del st.session_state.restrictions
        st.error("Todos os números fornecidos devem ser válidos")

        return

    st.session_state.show_restrictions = True
    if ("restrictions" not in st.session_state):  # Inicializa dicionário das restrições (apenas 1 vez)
        st.session_state.restrictions = {
            p["name"]: [] for p in st.session_state.participants
        }


def render_restrictions_form():
    st.write("## ❌ Lista de restrições")
    st.info(
        "Informe quais pessoas o referido participante **NÃO** pode tirar (além dele próprio)."
    )

    possible_participants = [p["name"] for p in st.session_state.participants]
    for participant_dict in st.session_state.participants:
        participant = participant_dict["name"]

        participant_opts = possible_participants.copy()
        participant_opts.remove(participant)
        st.session_state.restrictions[participant] = st.multiselect(
            f"Escolha as pessoas que {participant} **NÃO** pode tirar (além dele próprio)",
            options=participant_opts,
            default=None,
            key=f"{participant}_restrictions",
        )

    with st.expander("_Sumário das restrições_"):
        for p in st.session_state.restrictions.keys():
            restrictions = st.session_state.restrictions[p]
            if restrictions == []:
                st.write(f"{p} não tem restrições")
            else:
                st.write(f"{p} não pode tirar {restrictions}")


def render_algorithm_selection_form():
    st.write("## 👨🏻‍💻 Seleção do algoritmo")
    
    with st.expander("_Qual algoritmo escolher? Clique aqui para saber mais_"):
        st.write('**Algoritmo de Las Vegas**: Imagine que você está fazendo um sorteio, colocando os ' \
                 'nomes em um chapéu e tirando um de cada vez. Você tenta atribuir cada participante ' \
                 'a alguém aleatoriamente, mas se alguém ficar sem opções válidas, você joga tudo de ' \
                 'volta e sorteia de novo. O Las Vegas é como um jogo de “tente até dar certo”: ele ' \
                 'sempre encontra uma solução correta, mas pode demorar se a sorte não ajudar.')
        
        st.write("**Algoritmo DFS (_Depth-First Search_)**: Agora imagine que você está planejando o " \
                 "sorteio como um labirinto. Você começa com o primeiro participante e segue escolhendo " \
                 "quem ele vai tirar. Cada pessoa pega alguém que ainda não foi escolhida e você continua " \
                 "assim, passo a passo, até que todos tenham alguém. No final, forma-se um ciclo: cada " \
                 "participante está ligado ao próximo em sequência até voltar ao primeiro, sem ter quebra "
                 "na dinâmica.")
    
    available_algorithms = get_available_algorithms()
    st.session_state.selected_algorithm = st.selectbox("Selecione o algoritmo para sorteio", 
                                           options=available_algorithms.keys())
    

    st.write("Se estiver tudo correto, clique abaixo para realizar o sorteio.")
    clicked_generate_secret_santa = st.button(
        "Finalizar sorteio", key="submit_secret_santa", use_container_width=True
    )

    return clicked_generate_secret_santa


def handle_restrictions_form():
    st.session_state.enable_res_generation = False  # Começa por padrão considerando que não vai

    if all(
        len(st.session_state.restrictions[p["name"]])
        < len(st.session_state.participants)
        for p in st.session_state.participants
    ):
        st.session_state.enable_res_generation = True

    else:
        st.error(
            "Para avançar é necessário que o usuário possa tirar pelo menos uma pessoa."
        )

def handle_algorithm_selection_form():
    set_drawer(st.session_state.selected_algorithm)


def generate_res():
    participants = [p["name"] for p in st.session_state.participants]
    restrictions = {p: set(r) | {p} for p, r in st.session_state.restrictions.items()}

    ss = SecretSanta(participants, restrictions, drawer=st.session_state.drawer, description=st.session_state.description)
    with st.spinner("🎲 Gerando sorteio..."):
        try:
            _ = ss.draw()
            st.session_state.secret_santa = ss
            st.success("✅ Sorteio finalizado com sucesso!")

        except TimeoutError:
            st.error(
                "Não foi possível gerar o sorteio em tempo hábil. É possível que exista uma restrição impossível de ser resolvida. Tente novamente."
            )

def render_send_messages() -> WAHA:
    send_messages_clicked = st.button(
        "Clique aqui para enviar os resultados via WhatsApp",
        use_container_width=True,
    )

    return send_messages_clicked

def send_messages(max_retries: int = 3):
    ss = get_secret_santa()
    waha = get_waha()

    with st.spinner('📩 Enviando resultados...'):
        for p in st.session_state.participants:
            name = p["name"]
            phone = p["phone"]

            result = ss.get_result(name)

            msg = format_secret_santa_message(name, result, st.session_state.description)
            success = False

            for attempt in range(max_retries + 1):
                status_code, _ = waha.send_msg(phone, msg)

                if status_code == 201:
                    success = True
                    break

                time.sleep(5 * attempt)  # Backoff para retry

            if not success:
                masked = base64.b64encode(msg.encode()).decode()
                st.error(
                    f"Houve um erro ao enviar a mensagem para {name} ({phone}).\n\n"
                    f"**Resultado mascarado**: {masked}"
                )

    st.session_state.messages_sent = True
    st.success("✅ Resultados enviados com sucesso!")


def format_secret_santa_message(
    recipient_name: str, drawn_name: str, description: str = "Amigo Secreto"
) -> str:
    return (
        "*_[🤖 MENSAGEM AUTOMÁTICA - NÃO RESPONDA 🤖]_*\n\n"
        f"Olá, {recipient_name}! 🎁\n"
        f"No sorteio ({description}), você tirou: *{drawn_name}*.\n\n"
        "Guarde segredo 🤫"
    )


def render_audit_res():
    ss = get_secret_santa()
    b64_general_res = base64.b64encode(repr(ss).encode()).decode()
    b64_participants_res = {}

    participants = [p["name"] for p in st.session_state.participants]
    for p in participants:
        p_res = ss.get_result(p)
        base_msg = f"{p}, você tirou {p_res} no sorteio."
        b64_p_res = base64.b64encode(base_msg.encode()).decode()

        b64_participants_res[p] = b64_p_res

    with st.expander("Encode dos resultados (auditoria)"):
        st.write(f"**Resultado GERAL**: {b64_general_res}")
        for pp in b64_participants_res.keys():
            st.write(f"**Resultado {pp}**: {b64_participants_res[pp]}")


def terminate(waha: WAHA):
    terminate_pressed = st.button('Clique aqui para encerrar o sorteio', use_container_width=True,
                                  type='primary') 
    if terminate_pressed:
        if waha is not None:
            try:
                waha.logout_session()
            except Exception:
                pass
            
        st.session_state.clear()
        initialize_states()
        st.rerun()


def main():
    # Inicializa estados (necessário para poder trabalhar com múltiplos botoões)
    initialize_states()

    render_header()
    if waha_is_working():
        # Entrada de número de participantes
        num_participants, clicked_generate_list, ss_desc = render_participants_num_form()

        # Quando clicar no primeiro botão
        if clicked_generate_list:
            handle_participants_num_form(num_participants, ss_desc)

        # Se deve mostrar os campos de participante
        if st.session_state.show_participants:
            clicked_generate_restrictions = render_participants_form()

            if clicked_generate_restrictions:
                handle_participants_form()

            #  Mostrar tela de restrições (fora do botão)
            if st.session_state.show_restrictions:
                render_restrictions_form()
                clicked_generate_secret_santa = render_algorithm_selection_form()

                if clicked_generate_secret_santa:
                    handle_restrictions_form()
                    handle_algorithm_selection_form()

            if st.session_state.enable_res_generation:
                generate_res()
                send_messages()               
                render_audit_res()
                    
    else:
        render_waha_error()

if __name__ == "__main__":
    load_dotenv()
    main()
