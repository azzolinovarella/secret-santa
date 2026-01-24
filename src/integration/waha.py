import requests
from typing import Any, Optional, Dict, Tuple


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
            "POST", f"/api/sessions/{self._session_name}/start"
        )

    def get_session_status(self) -> Dict[str, Any]:
        return self._process_response("GET", f"/api/sessions/{self._session_name}")

    def authenticate(self) -> Dict[str, Any]:
        return self._process_response("GET", f"/api/{self._session_name}/auth/qr")

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
            "POST", f"/api/sessions/{self._session_name}/logout"
        )
