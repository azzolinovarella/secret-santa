from src import run_app
from src.logger import configure_logging  # TODO: Colocar no __init__?

if __name__ == "__main__":
    configure_logging()
    run_app()
