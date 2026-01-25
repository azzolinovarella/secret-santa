import re
import logging
import streamlit as st
from typing import List
from src.domain import SecretSanta
from src.app.utils import (
    validate_name,
    format_name,
    validate_phone,
    format_phone
)

logger = logging.getLogger(__name__)

def handle_participants_num_form() -> bool:
    description = st.session_state.get("draft.secret_santa.description")
    num_participants = st.session_state.get("draft.secret_santa.num_participants")

    st.session_state["flow.secret_santa.description"] = description
    st.session_state["flow.secret_santa.num_participants"] = num_participants

    logger.info("Dados básicos do amigo secreto definidos")
    logger.debug(
        "Session state atualizado (participants_num_form)",
        extra={
            "description": description,
            "num_participants": num_participants,
        },
    )

    return True


def handle_participants_dict_form(num_participants: int) -> bool:
    all_valid = True

    for i in range(num_participants):
        participant_name = st.session_state.get(f"draft.participants.{i}.name")
        participant_phone = st.session_state.get(f"draft.participants.{i}.phone")
        participant_upper_size = st.session_state.get(f"draft.participants.{i}.upper_size")
        participant_bottom_size = st.session_state.get(f"draft.participants.{i}.bottom_size")
        participant_shoe_size = st.session_state.get(f"draft.participants.{i}.shoe_size")

        if not validate_name(participant_name):
            popup_error(f"Nome inválido no participante {i+1}")
            all_valid = False

        if not validate_phone(participant_phone):
            popup_error(
                f"Telefone inválido no participante {i+1}"
            )
            all_valid = False
        
        if participant_upper_size.strip() == "":
            popup_error(
                f"Tamanho de camisa inválido do participante {i+1}"
            )
            all_valid = False
        
        if participant_bottom_size.strip() == "":
            popup_error(
                f"Tamanho de calça inválido do participante {i+1}"
            )
            all_valid = False
        
        if participant_shoe_size.strip() == "":
            popup_error(
                f"Tamanho de tênis inválido do participante {i+1}"
            )
            all_valid = False

    if not all_valid:
        logger.info("Validação de participantes falhou")
        return False

    participants_logged = {}

    for i in range(num_participants):
        name = format_name(
            st.session_state.get(f"draft.participants.{i}.name")
        )
        phone = format_phone(
            st.session_state.get(f"draft.participants.{i}.phone")
        )
        upper_size = st.session_state.get(f"draft.participants.{i}.upper_size").strip()
        bottom_size = st.session_state.get(f"draft.participants.{i}.bottom_size").strip()
        shoe_size = st.session_state.get(f"draft.participants.{i}.shoe_size").strip()

        st.session_state[f"flow.participants.{i}.name"] = name
        st.session_state[f"flow.participants.{i}.phone"] = phone
        st.session_state[f"flow.participants.{i}.upper_size"] = upper_size
        st.session_state[f"flow.participants.{i}.bottom_size"] = bottom_size
        st.session_state[f"flow.participants.{i}.shoe_size"] = shoe_size

        participants_logged[i] = {
            "name": name,
            "phone": phone,
            "upper_size": upper_size,
            "bottom_size": bottom_size,
            "shoe_size": shoe_size
        }

    logger.info("Participantes salvos com sucesso")
    logger.debug(
        "Session state atualizado (participants_dict_form)",
        extra={"participants": participants_logged},
    )

    return True


def handle_restrictions_form(participants_name: List[str]) -> bool:
    all_valid = True
    num_participants = len(participants_name)

    for participant in participants_name:
        participant_restrictions = st.session_state.get(
            f"draft.restrictions.{participant}", []
        )

        if len(participant_restrictions) == num_participants - 1:
            popup_error(
                f"O participante {participant} deve poder tirar pelo menos uma pessoa."
            )
            all_valid = False

    if not all_valid:
        logger.info("Validação de restrições falhou")
        return False

    restrictions_logged = {}

    for participant in participants_name:
        restrictions = st.session_state.get(f"draft.restrictions.{participant}")

        st.session_state[f"flow.restrictions.{participant}"] = restrictions
        restrictions_logged[participant] = restrictions

    logger.info("Restrições salvas com sucesso")
    logger.debug(
        "Session state atualizado (restrictions_form)",
        extra={"restrictions": restrictions_logged},
    )

    return True


def handle_algorithm_selection_form() -> bool:
    algorithm = st.session_state.get("draft.secret_santa.selected_algorithm")
    st.session_state["flow.secret_santa.selected_algorithm"] = algorithm

    logger.info("Algoritmo selecionado")
    logger.debug(
        "Session state atualizado (algorithm)",
        extra={"selected_algorithm": algorithm},
    )

    return True


def popup_error(error_msg: str):
    st.toast(error_msg, icon="❗️", duration="short")
