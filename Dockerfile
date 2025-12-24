FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev

COPY .streamlit/ .streamlit/
COPY main.py .
COPY src/ src/

EXPOSE ${STREAMLIT_SERVER_PORT}
ENTRYPOINT ["uv", "run", "streamlit", "run", "main.py"]