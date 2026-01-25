import os
import re
import random
import logging
import string
import base64
import phonenumbers
import hashlib
import streamlit.components.v1 as components
from cryptography.fernet import Fernet
from typing import Dict
from src.drawers import BaseDrawer, DFSDrawer, LasVegasDrawer
from src.integration import WAHA


def waha_is_working(waha: WAHA) -> bool:
    try:
        code, content = waha.get_session_status()
        return code == 200 and content.get("status") == "WORKING"
    except Exception:
        return False


def get_available_algorithms() -> Dict[str, BaseDrawer]:
    return {"Algoritmo de Las Vegas": LasVegasDrawer(), "Algoritmo DFS": DFSDrawer()}


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
    formated_number = phonenumbers.format_number(
        parsed_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL
    )
    return formated_number


def format_secret_santa_message(
    recipient_name: str, drawn_name: str, description: str,
    draw_upper_size: str, draw_bottom_size: str, draw_shoe_size: str
) -> str:
    return (
        "*_[🤖 MENSAGEM AUTOMÁTICA - NÃO RESPONDA 🤖]_*\n\n"
        f"Olá, {recipient_name}! 🎁\n"
        f"No sorteio ({description}), você tirou: *{drawn_name}*.\n\n"
        "*Informações úteis*:\n"
        f"- Tamanho de camiseta: {draw_upper_size}\n"
        f"- Tamanho de calça/shorts: {draw_bottom_size}\n"
        f"- Tamanho de tênis/chinelo: {draw_shoe_size}\n\n"
        "Guarde segredo 🤫"
    )


def encrypt_res(text: str, seed: str) -> str:
    key = seed_to_key(seed)
    f = Fernet(key)  # Exige 32 bytes codificados em base 64
    return f.encrypt(text.encode()).decode()


def seed_to_key(seed: str) -> bytes:
    digest = hashlib.sha256(seed.encode()).digest()
    return base64.urlsafe_b64encode(digest)


def decrypt_result(token: str, seed: str) -> str:
    key = seed_to_key(seed)
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()


def generate_random_seed(length: int = 30) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


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
