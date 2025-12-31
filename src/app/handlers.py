import streamlit as st
from typing import List
from .utils import validate_name, format_name, validate_phone, format_phone

def handle_participants_num_form() -> bool:
    st.session_state["flow.secret_santa.description"] = st.session_state.get("draft.secret_santa.description")
    st.session_state["flow.secret_santa.num_participants"] = st.session_state.get("draft.secret_santa.num_participants")
    return True


def handle_participants_dict_form(num_participants: int) -> bool:
    all_valid = True
    for i in range(num_participants):
        participant_name = st.session_state.get(f"draft.participants.{i}.name")
        participant_phone = st.session_state.get(f"draft.participants.{i}.phone")

        if not validate_name(participant_name):
            popup_error(f'Nome inválido no participante {i+1}: "{participant_name}"')
            all_valid = False
        
        if not validate_phone(participant_phone):
            popup_error(f'Telefone inválido no participante {i+1}: "{participant_phone}"')
            all_valid = False

    if not all_valid:
        return False

    for i in range(num_participants):
        st.session_state[f"flow.participants.{i}.name"] = format_name(st.session_state.get(f"draft.participants.{i}.name"))
        st.session_state[f"flow.participants.{i}.phone"] = format_phone(st.session_state.get(f"draft.participants.{i}.phone"))

    return True


def handle_restrictions_form(participants_name: List[str]) -> bool:
    all_valid = True

    num_participants = len(participants_name)
    for participant in participants_name:
        participant_restrictions = st.session_state.get(f"draft.restrictions.{participant}", [])

        if len(participant_restrictions) == num_participants - 1:  # Descontando ele próprio
            popup_error(f"O participante {participant} deve poder tirar pelo menos uma pessoa.")
            all_valid = False

    if not all_valid:
        return False

    for participant in participants_name:
        st.session_state[f"flow.restrictions.{participant}"] = st.session_state.get(f"draft.restrictions.{participant}")

    return True


def handle_algorithm_selection_form() -> bool:
    st.session_state["flow.secret_santa.selected_algorithm"] = st.session_state.get("draft.secret_santa.selected_algorithm")
    return True


def popup_error(error_msg: str):
    st.toast(error_msg, icon="❗️", duration="short")
