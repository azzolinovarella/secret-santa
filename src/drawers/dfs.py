import random
from typing import List, Dict, Set
from .base import BaseDrawer
from ..exceptions import NoValidCycleException


class DFSDrawer(BaseDrawer):
    def _draw(
        self, participants: List[str], restrictions: Dict[str, Set[str]]
    ) -> Dict[str, str]:
        possible_values_sorted = sorted(
            participants, key=lambda p: len(restrictions[p]), reverse=True
        )

        path = [possible_values_sorted[0]]
        unused = set(possible_values_sorted[1:])

        if self._dfs(
            path, unused, restrictions, len(participants)
        ):  # Variável path é atualizada na função
            results = self._get_results_from_path(path)
            return results

        raise NoValidCycleException(
            "Não é possível realizar o sorteio garantindo ciclicidade."
        )

    def _dfs(
        self,
        path: List[str],
        unused: Set[str],
        restrictions: Dict[str, Set[str]],
        n: int,
    ):
        if len(path) == n:
            return path[0] not in restrictions[path[-1]]

        candidates = list(unused - restrictions[path[-1]])
        random.shuffle(candidates)

        for c in candidates:
            path.append(c)
            unused.remove(c)

            if self._dfs(path, unused, restrictions, n):
                return True

            path.pop()
            unused.add(c)

        return False

    def _get_results_from_path(self, path: List[str]) -> Dict[str, str]:
        results = {}
        for idx in range(len(path)):
            if idx < len(path) - 1:
                results[path[idx]] = path[idx + 1]

            else:
                results[path[idx]] = path[0]

        return results
