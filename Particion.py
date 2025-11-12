from typing import Optional
from Proceso import proceso
class Particion:

    def __init__(self,nombre :int ,proceso: Optional[proceso],tamano:int,inicio:int,fin:int):
        self.nombre=nombre
        self.proceso=proceso
        self.tamano=tamano
        self.inicio=inicio
        self.fin=fin
        self.estado="libre"
        self.tiempoLiberacion=0

    def setEstado(self,estado):
        self.estado=estado

    def limpiarParticion(self):            
        self.proceso=None
        self.estado="libre"
       