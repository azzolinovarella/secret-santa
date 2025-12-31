from typing import Dict
from src import BaseDrawer, DFSDrawer, LasVegasDrawer

def get_available_algorithms() -> Dict[str, BaseDrawer]:
    return {
        "Algoritmo de Las Vegas": LasVegasDrawer(),
        "Algoritmo DFS": DFSDrawer()
    }
