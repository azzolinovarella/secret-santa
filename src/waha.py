import requests
import os
import time
import base64
from io import BytesIO
from PIL import Image
from typing import Dict, Any
from dotenv import load_dotenv

class Waha:
    def __init__(self, api_key: str, host: str, api_port: int, 
                 session_name: str = "default"):
        self._session_name = session_name
        self._host = host
        self._api_port = api_port
        self._api_key = api_key


    
    def _process_response(self, url, method, payload=None):
        headers = {
            "accept": "application/json",
            "X-Api-Key": self._api_key,
        }

        response = requests.request(
            url=url,
            method=method,
            headers=headers,
            timeout=60,
            json=payload
        )

        status_code = response.status_code,
        try:
            content = response.json()
        except requests.exceptions.JSONDecodeError:
            content = None

        return status_code, content
        
    def create_session(self) -> Dict[str, Any]:
        payload = {"name": self._session_name}
        url = f"http://{self._host}:{self._api_port}/api/sessions"
        return self._process_response(url, "POST", payload=payload)

    def start_session(self) -> Dict[str, Any]:
        url = f"http://{self._host}:{self._api_port}/api/sessions/{self._session_name}/start"
        return self._process_response(url, "POST")
    
    def get_session_status(self) -> Dict[str, Any]:
        url = f"http://{self._host}:{self._api_port}/api/sessions/{self._session_name}"
        return self._process_response(url, "GET")
    
    def authenticate(self) -> Dict[str, Any]:  
        url = f"http://{self._host}:{self._api_port}/api/{self._session_name}/auth/qr"
        return self._process_response(url, "GET")
    
    def send_msg(self, phone_number, content) -> Dict[str, Any]:
        payload = {
            "chatId": f"{phone_number}@c.us",
            "text": content,
            "session": self._session_name
        }

        url = f"http://{self._host}:{self._api_port}/api/sendText"
        return self._process_response(url, "POST", payload=payload)
    
    def stop_session(self) -> Dict[str, Any]:
        url = f"http://{self._host}:{self._api_port}/api/sessions/{self._session_name}/stop"
        return self._process_response(url, "POST")

    def logout_session(self) -> Dict[str, Any]:
        url = f"http://{self._host}:{self._api_port}/api/sessions/{self._session_name}/logout"
        return self._process_response(url, "POST")

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
        
    phone_number = input('Insira o número do destinatário: ')
    msg = input('Escreva sua mensagem: ')
    msg_code, msg_content = waha.send_msg(phone_number, msg)
    print(msg_code, msg_content)

    result_stop = waha.stop_session()
    print(result_stop)