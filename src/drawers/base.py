from abc import ABC, abstractmethod
from typing import List, Dict, Set
from src.exceptions.draw_exceptions import InvalidRestrictionsException

class BaseDrawer(ABC):
    def draw(self, participants: List[str], restrictions: Dict[str, Set[str]]) -> Dict[str, str]:
        self._validate_restrictions(participants, restrictions)
        return self._draw(participants, restrictions)

    def _validate_restrictions(self, participants: List[str], restrictions: Dict[str, Set[str]]):
        participants_set = set(participants)
        missing = participants_set - restrictions.keys()
        if missing:
            raise InvalidRestrictionsException(f"Participantes sem restrições definidas: {', '.join(missing)}")

        for p in participants:
            r = restrictions[p]

            if not isinstance(r, set):
                raise TypeError(f"As restrições de '{p}' devem ser do tipo set.")

            if p not in r:
                raise InvalidRestrictionsException(f"'{p}' deve estar em sua própria lista de restrições.")

            invalid = r - participants_set
            if invalid:
                raise InvalidRestrictionsException(f"Restrições inválidas para '{p}': {', '.join(invalid)} não existe(m) nos participantes.")

            if participants_set - r == set():
                raise InvalidRestrictionsException(f"'{p}' não pode tirar ninguém (restrições impossíveis).")

    @abstractmethod
    def _draw(self, participants: List[str], restrictions: Dict[str, Set[str]]) -> Dict[str, str]:
        ...  # Deve ser implementado pelas filhas
