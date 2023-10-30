from typing import Dict, List
import os
import random

class SecretSanta:
    def __init__(self, participants_n_restriction: Dict[str, List[str]], modality: str) -> None:
        self.__participants_n_restrictions = participants_n_restriction
        self.__modality = modality
        self.__results = self.__generate_results()


    def __repr__(self):
        s = f"RESULTADOS PARA {self.__modality.upper()}\n\n"
        for k in sorted(self.__results.keys()):
            s += f'{k} {(15-len(k))*"-"}> {self.__results[k]}\n'

        return s


    @property
    def participants_n_restrictions(self) -> Dict[str, List[str]]:
        return self.__participants_n_restrictions


    @property
    def modality(self) -> str:
        return self.__modality


    @property
    def results(self) -> Dict[str, str]:
        return self.__results
    
    def __generate_results(self) -> Dict[str, str]:
        results = {}

        while len(results) != len(self.__participants_n_restrictions):
            participants_list = list(self.__participants_n_restrictions.keys())
            available_users = participants_list.copy()
            random.shuffle(participants_list) 

            for participant in participants_list:
                possible_users = set(available_users)
                for p in self.__participants_n_restrictions[participant]:
                    possible_users.discard(p)
                            
                if len(possible_users) == 0:
                    results = {}
                    break
                    
                result = random.choice(list(possible_users))
                results[participant] = result
                available_users.pop(available_users.index(result))

        if set(results.keys()) == set(results.values()):   # Só para ter certeza...
            return results

        else:
            return self.__generate_results()
        

    def export_to_file(self, export_dir: str) -> None:
        if not os.path.isdir(export_dir):
            os.makedirs(export_dir)

        for k, v in self.__results.items():
            with open(f'{export_dir}/{k}-{self.__modality.replace(" ", "_")}.txt', 'w') as file:
                file.write(f'===============================================================\n'
                           f'{k}, você tirou o(a) {v} para {self.__modality}\n'
                           f'===============================================================')