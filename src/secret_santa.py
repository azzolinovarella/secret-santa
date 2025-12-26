import os
import time
import random
from typing import Dict, List


class SecretSanta:
    def __init__(
        self,
        participants: List[str],
        restrictions: Dict[str, List[str]],
        description: str = "Amigo Secreto",
    ) -> None:
        self._participants = participants
        self._restrictions = self._validate_restrictions(restrictions)
        self._description = description
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
    def participants(self) -> List[str]:
        return self._participants

    @property
    def restrictions(self) -> Dict[str, List[str]]:
        return self._restrictions

    @property
    def description(self) -> str:
        return self._description

    @property
    def results(self) -> Dict[str, str]:
        return self._results

    def _validate_restrictions(self, restrictions: Dict[str, List[str]]):
        validated_restrictions = {}

        for p in self._participants:
            r_list = restrictions.get(p)

            if r_list is None:
                raise ValueError(
                    "Toda pessoa deve estar na lista de restrições, mesmo que não tenha nenhuma."
                )

            if not isinstance(r_list, list):
                raise TypeError(f"As restrições de {p} devem ser uma lista.")

            if not set(r_list).issubset(self._participants):
                raise ValueError(
                    f"Toda pessoa na lista de restrições de {p} deve ser um participante."
                )

            validated_restrictions[p] = list(
                dict.fromkeys(r_list + [p])
            )  # Por padrão p não pode tirar p

        return validated_restrictions

    def generate_drawing(self, timeout: int = 30) -> Dict[str, str]:
        start_time = time.monotonic()
        results = {}
        while True:
            if time.monotonic() - start_time > timeout:
                raise TimeoutError(
                    "Sorteio não convergiu dentro do tempo limite. "
                    "Isto pode ter acontecido por haver uma restrição impossível."
                )

            participants_list = self._participants.copy()
            available_users = participants_list.copy()
            random.shuffle(participants_list)

            results = {}
            for participant in participants_list:
                possible_users = set(available_users) - set(
                    self._restrictions[participant]
                )

                if not possible_users:  # Não há mais usuários a serem sorteados
                    break

                chosen = random.choice(list(possible_users))
                results[participant] = chosen
                available_users.remove(chosen)

            if len(results) == len(self._participants):
                self._results = results
                return results

    def is_drawn(self) -> bool:
        return self._results != {}

    def get_result(self, participant: str) -> str:
        if not self.is_drawn():
            raise ValueError(
                "Sorteio ainda não realizado. Execute o método generate_drawing antes de chamar este método."
            )

        res = self._results.get(participant)
        if res is None:
            raise ValueError("Participante inexistente.")

        return res

    def export_to_file(self, export_dir: str) -> None:
        if not os.path.isdir(export_dir):
            os.makedirs(export_dir)

        for k, v in self._results.items():
            with open(
                f'{export_dir}/{k}-{self._description.replace(" ", "_")}.txt', "w"
            ) as file:
                file.write(
                    f"===============================================================\n"
                    f"{k}, você tirou o(a) {v} para {self._description}\n"
                    f"==============================================================="
                )
