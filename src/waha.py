import requests
import os
import time
import base64
from io import BytesIO
from PIL import Image
from typing import Any, Optional, Dict, Tuple
from dotenv import load_dotenv

class WAHA:
    def __init__(
        self,
        api_key: str,
        host: str,
        api_port: int,
        session_name: str = "default",
        timeout: int = 60,
    ):
        self._session_name = session_name
        self._base_url = f"http://{host}:{api_port}"
        self._api_key = api_key
        self._timeout = timeout

    def _process_response(
        self, method: str, endpoint: str, payload: Optional[dict] = None
    ) -> Tuple[int, Optional[Dict[str, Any]]]:
        headers = {
            "accept": "application/json",
            "X-Api-Key": self._api_key,
        }

        response = requests.request(
            method=method,
            url=f"{self._base_url}{endpoint}",
            headers=headers,
            json=payload,
            timeout=self._timeout,
        )

        try:
            content = response.json()
        except requests.exceptions.JSONDecodeError:
            content = None

        return response.status_code, content

    def create_session(self):
        return self._process_response(
            "POST", "/api/sessions", payload={"name": self._session_name}
        )

    def start_session(self) -> Dict[str, Any]:
        return self._process_response(
            "POST" f"/api/sessions/{self._session_name}/start",
        )

    def get_session_status(self) -> Dict[str, Any]:
        return self._process_response(
            "GET" f"/api/sessions/{self._session_name}",
        )

    def authenticate(self) -> Dict[str, Any]:
        return self._process_response(
            "GET" f"/api/{self._session_name}/auth/qr",
        )

    def send_msg(self, phone_number, content) -> Dict[str, Any]:
        return self._process_response(
            "POST",
            "/api/sendText",
            payload={
                "chatId": f"{phone_number}@c.us",
                "text": content,
                "session": self._session_name,
            },
        )

    def stop_session(self) -> Dict[str, Any]:
        return self._process_response(
            "POST" f"/api/sessions/{self._session_name}/stop",
        )

    def logout_session(self) -> Dict[str, Any]:
        return self._process_response(
            "POST" f"/api/sessions/{self._session_name}/logout",
        )


if __name__ == "__main__":
    load_dotenv()

    waha = Waha(
        session_name="default",
        api_key=os.environ.get("WAHA_API_KEY"),
        host="localhost",
        api_port=os.environ.get("WHATSAPP_API_PORT"),
    )

    try:
        waha.logout_session()
    except Exception:
        pass

    create_session_code, create_session_content = waha.create_session()
    print(create_session_code, create_session_content)

    start_session_code, start_session_content = waha.start_session()
    print(start_session_code, start_session_content)

    session_status_code, session_status_content = waha.get_session_status()
    print(session_status_code, session_status_content)

    status = session_status_content.get("status", "STARTING")
    while status == "STARTING":
        time.sleep(5)
        session_status_code, session_status_content = waha.get_session_status()
        status = session_status_content.get("status", "STARTING")
        print(session_status_code, session_status_content)

    auth_code, auth_content = waha.authenticate()
    print(auth_code, auth_content)

    qr_data = auth_content.get("data")
    qr_data_bytes = base64.b64decode(qr_data)
    qr_image = Image.open(BytesIO(qr_data_bytes))
    qr_image.show()

    while status == "SCAN_QR_CODE":
        time.sleep(15)
        session_status_code, session_status_content = waha.get_session_status()
        status = session_status_content.get("status", "SCAN_QR_CODE")

        try:
            auth_code, auth_content = waha.authenticate()
            print(auth_code, auth_content)

            qr_data = auth_content.get("data")
            qr_data_bytes = base64.b64decode(qr_data)
            qr_image = Image.open(BytesIO(qr_data_bytes))
            qr_image.show()

        except Exception:
            break  # Já autenticado

    phone_number = input("Insira o número do destinatário: ")
    msg = input("Escreva sua mensagem: ")
    msg_code, msg_content = waha.send_msg(phone_number, msg)
    print(msg_code, msg_content)

    result_stop = waha.stop_session()
    print(result_stop)
