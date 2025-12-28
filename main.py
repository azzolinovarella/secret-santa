import time
import os
import base64
import streamlit as st
from typing import Any, Optional, Dict, Tuple
from dotenv import load_dotenv
from src import SecretSanta, BaseDrawer, DFSDrawer, LasVegasDrawer, WAHA

def initialize_states():
    if "show_participants" not in st.session_state:
        st.session_state.show_participants = False

    if "show_restrictions" not in st.session_state:
        st.session_state.show_restrictions = False

    if "participants" not in st.session_state:
        st.session_state.participants = []

    if "restrictions" not in st.session_state:
        st.session_state.restrictions = {}

    if "drawer" not in st.session_state:
        st.session_state.drawer = None

    if "enable_res_generation" not in st.session_state:
        st.session_state.enable_res_generation = False

    if "waha_initialized" not in st.session_state:
        st.session_state.waha_initialized = False

    if "messages_sent" not in st.session_state:
        st.session_state.messages_sent = False


def render_header() -> Tuple[int, bool, str]:
    st.write("# 🎅🏻 Secret Santa")

    ss_desc = st.text_input(
        "Descreva o identificador do seu sorteio", value="Amigo Secreto"
    )
    if ss_desc is None:
        ss_desc = "Amigo Secreto"

    col1, col2 = st.columns([0.69, 0.31], vertical_alignment="bottom")
    num_participants = col1.number_input("Número de participantes", min_value=2)
    clicked_generate_list = col2.button("Gerar lista de participantes", key="base_list")

    return num_participants, clicked_generate_list, ss_desc


def handle_header(num_participants: int):
    st.session_state.show_participants = True
    st.session_state.show_restrictions = (
        False  # Reseta para garantir que vai sumir com o menu para nova geração
    )
    st.session_state.num_participants = num_participants
    st.session_state.participants = [""] * st.session_state.num_participants
    del st.session_state.restrictions
    st.session_state.enable_res_generation = False


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
            placeholder="551140028922",
            key=f"participant_phone_{i}",
        )

        participant_name = participant_name.strip()
        participant_phone = participant_phone.replace(" ", "").replace("-", "").replace("+", "")

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


def render_restrictions_form() -> bool:
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

    st.session_state.drawer = st.selectbox("Selecione a forma de sorteio", 
                                           options=["Algoritmo de Las Vegas", "DFS"])

    st.write("Se estiver tudo correto, clique abaixo para gerar os arquivos.")
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


def get_drawer():
    match st.session_state.drawer:
        case "Algoritmo de Las Vegas":
            return LasVegasDrawer()
        
        case "DFS":
            return DFSDrawer()
        
        case _:
            raise NotImplementedError("O algoritmo de sorteio deve ser um dentre Las Vegas e DFS.")


def generate_res(drawer: BaseDrawer, ss_desc: str) -> Optional[SecretSanta]:
    participants = [p["name"] for p in st.session_state.participants]
    restrictions = {p: set(r) | {p} for p, r in st.session_state.restrictions.items()}

    ss = SecretSanta(participants, restrictions, drawer, description=ss_desc)
    with st.spinner("🎲 Gerando sorteio..."):
        try:
            _ = ss.draw()
            st.success("✅ Sorteio finalizado com sucesso!")
            return ss

        except TimeoutError:
            st.error(
                "Não foi possível gerar o sorteio em tempo hábil. É possível que exista uma restrição impossível de ser resolvida. Tente novamente."
            )
    

def render_waha_start() -> WAHA:
    waha = WAHA(
        session_name="default",
        host="waha",  # Vide docker-compose
        api_port=os.environ.get("WHATSAPP_API_PORT"),
        api_key=os.environ.get("WAHA_API_KEY"),
    )

    start_waha_placeholder = st.empty()
    start_waha = start_waha_placeholder.button(
        "Clique aqui para inicializar o serviço WhatsApp e enviar os resultados",
        use_container_width=True,
    )
    if start_waha:
        with st.spinner("⚙️ Inciando serviço no WhatsApp..."):
            text_placeholder = st.empty()
            _, center, _ = st.columns([0.2, 0.6, 0.2])
            img_placeholder = center.empty()

            try:
                initialize_waha(waha)
            except TimeoutError as e:
                waha.logout_session()
                st.warning(str(e))
                return

            qr_data_bytes = get_qr_code_bytes(waha)

        text_placeholder.write(
            "⏳ Escaneie a imagem abaixo no WhatsApp para continuar..."
        )
        img_placeholder.image(qr_data_bytes, width="stretch")

        try:
            wait_authentication(waha)
        except TimeoutError as e:
            waha.logout_session()
            st.warning(str(e))
            return

        text_placeholder.empty()
        img_placeholder.empty()
        start_waha_placeholder.empty()
        st.session_state.waha_initialized = True

        return waha


def initialize_waha(waha: WAHA, timeout: int = 120):
    try:
        waha.logout_session()
    except Exception:
        pass

    waha.create_session()
    waha.start_session()
    _, session_status_content = waha.get_session_status()

    status = session_status_content.get("status", "STARTING")
    start_time = time.monotonic()
    while status != "SCAN_QR_CODE":
        if time.monotonic() - start_time > timeout:
            raise TimeoutError(
                f"Execução durou mais do que o esperado! Necessário reiniciar o processo."
            )

        time.sleep(1)
        _, session_status_content = waha.get_session_status()
        status = session_status_content.get("status", "STARTING")


def get_qr_code_bytes(waha: WAHA) -> bytes:
    _, auth_content = waha.authenticate()

    qr_data = auth_content.get("data")
    return base64.b64decode(qr_data)


def wait_authentication(waha: WAHA, timeout: int = 120):
    _, session_status_content = waha.get_session_status()
    status = session_status_content.get("status", "SCAN_QR_CODE")

    start_time = time.monotonic()
    while status != "WORKING":
        if time.monotonic() - start_time > timeout:
            raise TimeoutError(
                f"Autenticação demorou mais do que esperado! Necessário reiniciar o processo."
            )

        time.sleep(1)
        _, session_status_content = waha.get_session_status()
        status = session_status_content.get("status", "SCAN_QR_CODE")


def send_messages(ss: SecretSanta, waha: WAHA, description: str, max_retries: int = 3):
    with st.spinner('📩 Enviando resultados...'):
        for p in st.session_state.participants:
            name = p["name"]
            phone = p["phone"]

            result = ss.get_result(name)

            msg = format_secret_santa_message(name, result, description)
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
                    f"Houve um erro ao enviar a mensagem para {name} ({phone}).<br>"
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


def render_audit_res(ss: SecretSanta):
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

    # Entrada de número de participantes
    num_participants, clicked_generate_list, ss_desc = render_header()

    # Quando clicar no primeiro botão
    if clicked_generate_list:
        handle_header(num_participants)

    # Se deve mostrar os campos de participante
    if st.session_state.show_participants:
        clicked_generate_restrictions = render_participants_form()

        if clicked_generate_restrictions:
            handle_participants_form()

        #  Mostrar tela de restrições (fora do botão)
        if st.session_state.show_restrictions:
            clicked_generate_secret_santa = render_restrictions_form()

            if clicked_generate_secret_santa:
                handle_restrictions_form()

            if st.session_state.enable_res_generation:
                # Se for para enviar os resultados via WhatsApp (descontinuado formato de arquivos)
                drawer = get_drawer()
                ss = generate_res(drawer, ss_desc)
                waha = render_waha_start()

                if st.session_state.waha_initialized and waha is not None:
                    send_messages(ss, waha, ss_desc)
                    render_audit_res(ss)
                    
                if st.session_state.messages_sent:
                    terminate(waha)


if __name__ == "__main__":
    load_dotenv()
    main()
