import re
import phonenumbers
import streamlit.components.v1 as components
from typing import Dict
from src import WAHA, SecretSanta, BaseDrawer, DFSDrawer, LasVegasDrawer


def waha_is_working(waha: WAHA) -> bool:
    try:
        code, content = waha.get_session_status()
        return code == 200 and content.get("status") == "WORKING"
    except Exception:
        return False


def get_available_algorithms() -> Dict[str, BaseDrawer]:
    return {
        "Algoritmo de Las Vegas": LasVegasDrawer(),
        "Algoritmo DFS": DFSDrawer()
    }


def validate_name(name: str) -> bool:
    return name != ""


def format_name(name: str) -> bool:
    formated_name = re.sub(r"  +", "", name.strip()).title()
    return formated_name


def validate_phone(phone: str) -> bool:
    try:
        if not phone.startswith("+"):
            phone = "+" + phone
        
        parsed_number = phonenumbers.parse(phone)
        return phonenumbers.is_valid_number(parsed_number)
    
    except phonenumbers.NumberParseException:
        return False


def format_phone(phone: str) -> bool:
    if not phone.startswith("+"):
        phone = "+" + phone

    parsed_number = phonenumbers.parse(phone)
    formated_number = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    return formated_number


def format_secret_santa_message(
    recipient_name: str, drawn_name: str, description: str = "Amigo Secreto"
) -> str:
    return (
        "*_[🤖 MENSAGEM AUTOMÁTICA - NÃO RESPONDA 🤖]_*\n\n"
        f"Olá, {recipient_name}! 🎁\n"
        f"No sorteio ({description}), você tirou: *{drawn_name}*.\n\n"
        "Guarde segredo 🤫"
    )


def scroll_to_top():  # TODO: Melhor lugar para colocar?
    components.html(
        """
        <script>
        window.scrollTo(0, 0);
        </script>
        """,
        height=0,
        width=0,
    )
