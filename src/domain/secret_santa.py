from typing import Dict, List, Set
from ..drawers import BaseDrawer


class SecretSanta:
    def __init__(
        self,
        participants: List[str],
        restrictions: Dict[str, Set[str]],
        drawer: BaseDrawer,
        description: str = "Amigo Secreto",
    ) -> None:
        self._participants = participants.copy()
        self._restrictions = {
            k: set(v) for k, v in restrictions.items()
        }  # Para fazer deep copy dos sets tb
        self._description = description
        self._drawer = drawer
        self._results = {}

    def __repr__(self):
        if not self.is_drawn():
            s = f"SORTEIO AINDA NÃO REALIZADO PARA {self._description.upper()}\n\n"
            for p in sorted(self._participants):
                s += f'{p} {(15-len(p))*"-"}> TBD\n'

            return s

        s = f"RESULTADOS PARA {self._description.upper()}\n\n"
        for k in sorted(self._results.keys()):
            s += f'{k} {(15-len(k))*"-"}> {self._results[k]}\n'

        return s

    @property
    def results(self) -> Dict[str, str]:
        return (
            self._results.copy()
        )  # Para garantir que o usuário não acesse o valor diretamente

    def draw(self, redraw: bool = False) -> Dict[str, str]:
        if self.is_drawn() and not redraw:
            return self.results

        self._results = self._drawer.draw(self._participants, self._restrictions)
        return self.results

    def is_drawn(self) -> bool:
        return bool(self._results)

    def get_result(self, participant: str) -> str:
        if not self.is_drawn():
            raise ValueError(
                "Sorteio ainda não realizado. Execute o método generate_drawing antes de chamar este método."
            )

        try:
            return self._results[participant]
        except KeyError:
            raise ValueError(f"Participante '{participant}' não encontrado.")
