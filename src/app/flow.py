import time
import os
import base64
import streamlit as st
from typing import Any, Optional, Dict, Tuple
from dotenv import load_dotenv
from src import SecretSanta, BaseDrawer, DFSDrawer, LasVegasDrawer, WAHA
from ..ui.streamlit_views import *


# def initialize_states():
#     defaults = {
#         # Variáveis
#         "participants": [],
#         "restrictions": {},
#         "selected_algorithm": None,
#         "description": None,
#         # Para controle de fluxo
#         "show_participants": False,
#         "show_restrictions": False,
#         "enable_res_generation": False,
#         "messages_sent": False,
#         # Objetos
#         # "waha": None,  # Instanciado depois
#         "drawer": None,
#         "secret_santa": None
#     }

#     for key, value in defaults.items():
#         if key not in st.session_state:
#             st.session_state[key] = value

#     # Objetos complexos (objeto já instanciado com alguns valores padrão)
#     if "waha" not in st.session_state:
#         set_waha()


def set_waha():
    if "waha" in st.session_state:  # Para evitar múltiplas instâncias do WAHA em cada rerun
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

    st.session_state.waha = waha


def get_waha() -> WAHA:
    return st.session_state.waha


def waha_is_working() -> bool:
    try:
        waha = get_waha()
        code, content = waha.get_session_status()
        return code == 200 and content.get("status") == "WORKING"
    except Exception:
        return False


def get_available_algorithms() -> Dict[str, BaseDrawer]:
    return {
        "Algoritmo de Las Vegas": LasVegasDrawer(),
        "Algoritmo DFS": DFSDrawer()
    }

def generate_res():
    participants = [p["name"] for p in st.session_state.participants]
    restrictions = {p: set(r) | {p} for p, r in st.session_state.restrictions.items()}

    ss = SecretSanta(participants, restrictions, drawer=st.session_state.drawer, description=st.session_state.description)
    # with st.spinner("🎲 Gerando sorteio..."):
    try:
        _ = ss.draw()
        st.session_state.secret_santa = ss
        # st.success("✅ Sorteio finalizado com sucesso!")

    except TimeoutError:
        # st.error(
        #     "Não foi possível gerar o sorteio em tempo hábil. É possível que exista uma restrição impossível de ser resolvida. Tente novamente."
        # )
        ...

def run_app():
    initialize_states()
    
    render_header()
    if st.session_state.get("flow.step") == 1:
        render_participants_num_form()

    elif st.session_state.get("flow.step") == 2:
        render_participants_dict_form(st.session_state.get("flow.secret_santa.num_participants"))

    elif st.session_state.get("flow.step") == 3:
        render_algorithm_selection_form()

    elif st.session_state.get("flow.step") == 4:
        filtered_states = {k: v for k, v in st.session_state.items() if "flow." in k}
        st.write(filtered_states)

    handle_participants_num_form()
    handle_participants_dict_form(st.session_state.get("flow.secret_santa.num_participants"))
    handle_algorithm_selection_form()

def initialize_states():
    if "flow.step" not in st.session_state:
        st.session_state["flow.step"] = 1
       

def handle_participants_num_form():
    # TODO: Implementar validações (migrar de main para cá)
    if st.session_state.get("draft.button.submit_num_participants"):
        st.session_state["flow.step"] = 2  # Avança para o passo 2
        st.session_state["flow.secret_santa.description"] = st.session_state.get("draft.secret_santa.description")
        st.session_state["flow.secret_santa.num_participants"] = st.session_state.get("draft.secret_santa.num_participants")


def handle_participants_dict_form(num_participants):
    # TODO: Implementar validações (migrar de main para cá)
    if st.session_state.get("draft.button.submit_participants"):
        st.session_state["flow.step"] = 3
        for i in range(num_participants):
            st.session_state[f"flow.participants.{i}.name"] = st.session_state.get(f"draft.participants.{i}.name")
            st.session_state[f"flow.participants.{i}.phone"] = st.session_state.get(f"draft.participants.{i}.phone")


def handle_algorithm_selection_form():
    # TODO: Idem...
    if st.session_state.get("draft.button.submit_selected_algorithm"):
        st.session_state["flow.step"] = 4
        st.session_state["flow.secret_santa.selected_algorithm"] = st.session_state.get("draft.secret_santa.selected_algorithm")

