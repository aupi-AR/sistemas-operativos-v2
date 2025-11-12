
from abc import abstractmethod


class Estrategia:
    def __init__(self):
        self.ultimaParticion=None
    @abstractmethod
    def seleccionarParticion(self,proceso, particiones)-> bool:
        pass