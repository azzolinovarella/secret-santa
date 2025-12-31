import time
import os
import re
import base64
import streamlit as st
from typing import Any, Optional, Dict, Tuple
from dotenv import load_dotenv
from src import SecretSanta, BaseDrawer, DFSDrawer, LasVegasDrawer, WAHA
from src.exceptions import DrawException
from .renderers import *
from .handlers import *
from .utils import scroll_to_top, waha_is_working, format_secret_santa_message


def run_app():
    render_header()
    initialize_waha()

    if not waha_is_working(st.session_state.get("flow.objects.waha")):
        render_waha_error()
        return

    initialize_step()
    match st.session_state.get("flow.step"): 
        case 1:
            render_participants_num_form(on_click=lambda: handle_and_advance(handle_participants_num_form, next_step=2))

        case 2:
            num_participants = st.session_state.get("flow.secret_santa.num_participants")
            render_participants_dict_form(num_participants=num_participants,
                                          on_return=lambda: go_to_step(1),
                                          on_advance=lambda: handle_and_advance(
                                              lambda: handle_participants_dict_form(num_participants), 
                                              next_step=3))  # TODO: Melhor forma?

        case 3:
            participants_name = [v for k, v in st.session_state.items() if re.match("^flow.participants.\d+.name$", k)]
            render_restrictions_form(participants_name=participants_name,
                                     on_return=lambda: go_to_step(2),
                                     on_advance=lambda: handle_and_advance(
                                         lambda: handle_restrictions_form(participants_name), 
                                         next_step=4))

        case 4:
            render_algorithm_selection_form(on_return=lambda: go_to_step(3),
                                            on_advance=lambda: handle_and_advance(handle_algorithm_selection_form, next_step=5))

        case 5:
            description = st.session_state.get("flow.secret_santa.description")
            num_participants = st.session_state.get("flow.secret_santa.num_participants")
            selected_algorithm = st.session_state.get("flow.secret_santa.selected_algorithm")
            participants = [{"name": st.session_state.get(f"flow.participants.{i}.name"), "phone": st.session_state.get(f"flow.participants.{i}.phone")} for i in range(num_participants)]
            restrictions = {name: st.session_state.get(f"draft.restrictions.{name}", []) for name in [p["name"] for p in participants]}

            # Renderizando o resumo
            render_summary(
                description=description,
                num_participants=num_participants,
                selected_algorithm=selected_algorithm,
                participants=participants,
                restrictions=restrictions,
                on_return=lambda: go_to_step(4),
                on_advance=lambda: handle_and_advance(run_drawing_flow, next_step=6)
            )

        case 6:
            go_to_step(1)


def initialize_waha():
    if "flow.objects.waha" in st.session_state:  # Para evitar múltiplas instâncias do WAHA em cada rerun
        return 
    
    waha = WAHA(
        session_name="default",
        host="waha",  # Vide docker-compose
        api_port=os.environ.get("WHATSAPP_API_PORT"),
        api_key=os.environ.get("WAHA_API_KEY"),
    )

    try:
        code, content = waha.get_session_status()
        if code == 200 and content.get("status") == "STOPPED":
            waha.start_session()
    except Exception:
        # WAHA ainda não está pronto, evita quebrar o app
        pass

    st.session_state["flow.objects.waha"] = waha
    

def initialize_step():
    if "flow.step" not in st.session_state:
        st.session_state["flow.step"] = 1


def handle_and_advance(handler_function: Callable, next_step: int):
    if handler_function():
        go_to_step(next_step)
        scroll_to_top()  # Vai para o topo da página


def go_to_step(step: int):
    if step < 1 or step > 6:
        raise ValueError("Variável step deve estar entre 1 e 6")
    
    st.session_state["flow.step"] = step
    update_drafts_from_flow()  # Assim, quando o usuário clicar em voltar vai aparecer os valores que ele setou antes


def update_drafts_from_flow():
    for k, v in st.session_state.items():
        if k.startswith("flow."):
            draft_key = k.replace("flow.", "draft.")
            st.session_state[draft_key] = v
            # st.session_state.setdefault(draft_key,  v)  # Só troca se não houver default... Pior, mas suprime o warning...


def initialize_secret_santa():
    st.session_state["flow.objects.secret_santa"] = SecretSanta(
        participants=[v for k, v in st.session_state.items() if re.match("^flow.participants.\d+.name$", k)], 
        restrictions={k.split('flow.restrictions.')[1]: set(v) | {k.split('flow.restrictions.')[1]}  # Para add o próprio usuário a sua lista de restrições 
                    for k, v in st.session_state.items() if re.match("^flow.restrictions.*$", k)}, 
        drawer=get_available_algorithms()[st.session_state.get("flow.secret_santa.selected_algorithm")], 
        description=st.session_state.get("flow.secret_santa.description")
    )


def run_drawing_flow(max_retries: int = 3):
    with st.spinner("🎲 Gerando sorteio..."):
        try:
            initialize_secret_santa()
            ss = st.session_state.get("flow.objects.secret_santa")
            _ = ss.draw(redraw=False)
            st.success("✅ Sorteio finalizado com sucesso!")
        
        except DrawException:
            st.error("Não foi possível gerar o sorteio em tempo hábil. É possível que exista uma restrição impossível de ser resolvida. Tente novamente.")
            return False
    
    with st.spinner('📩 Enviando resultados...'):
        waha = st.session_state.get("flow.objects.waha")
        description = st.session_state.get("flow.secret_santa.description")

        for i in range(st.session_state.get("flow.secret_santa.num_participants")):
            name = st.session_state.get(f"flow.participants.{i}.name")
            phone = re.sub(r"[ +()\-\s]", "", st.session_state.get(f"flow.participants.{i}.phone"))  # API do WAHA demanda numero plano

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
                    f"Houve um erro ao enviar a mensagem para {name} ({phone}).\n\n"
                    f"**Resultado mascarado**: {masked}"
                )

        st.success("✅ Resultados enviados com sucesso!")
        return True
