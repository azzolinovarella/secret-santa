import time
import random
from typing import List, Dict, Set
from src.drawers.base import BaseDrawer

class LasVegasDrawer(BaseDrawer):
    def __init__(self, timeout: float = 30):
        self._timeout = timeout

    def _draw(self, participants: List[str], restrictions: Dict[str, Set[str]]) -> Dict[str, str]:
        results = {}

        start_time = time.monotonic()
        while True:
            if time.monotonic() - start_time > self._timeout:
                raise TimeoutError("Sorteio não convergiu dentro do tempo limite. As restrições podem ser impossíveis de satisfazer.")

            participants_list = sorted(participants,  # Heuristica para começarmos pelo mais restritivo 
                                       key=lambda p: (len(restrictions[p]), random.random()),  # Em caso de empate, faz sorteio aleatório
                                       reverse=True)
            available_users = set(participants_list)

            results = {}
            for participant in participants_list:
                possible_users = available_users - restrictions[participant]

                if not possible_users:  # Não há mais usuários a serem sorteados
                    break

                chosen = random.choice(list(possible_users))
                results[participant] = chosen
                available_users.remove(chosen)

            if len(results) == len(participants):
                return results
