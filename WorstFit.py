import Particion
from Estrategia import Estrategia

class WorstFit(Estrategia):

    def seleccionarParticion(self, proceso, particiones):
            bigger=Particion.Particion(1,None,tamano=0,inicio=0,fin=0)
            for particion in particiones:
                if particion.tamano>=proceso.tamano and particion.tamano>bigger.tamano and particion.proceso is None:
                      index_bigger=particiones.index(particion)
                      bigger=particion

            print("entre a la aprte critica")
            if bigger.tamano!=0:
                particion=particiones[index_bigger]

                if particion.tamano==proceso.tamano:
                    particion.proceso=proceso
                    particion.proceso.inicioP=particion.inicio
                    particion.proceso.finP=particion.fin
                elif particion.tamano > proceso.tamano:
                    particion.proceso=proceso
                    nuevaParticion= Particion.Particion(
                        nombre=particion.nombre+1,
                        proceso = None,
                        tamano=particion.tamano - proceso.tamano,
                        inicio=particion.inicio + proceso.tamano,
                        fin=particion.fin
                    )
                    particion.fin=particion.inicio + proceso.tamano -1
                    particion.tamano=proceso.tamano
                    particion.proceso.inicioP=particion.inicio
                    particion.proceso.finP=particion.fin
                    particiones.insert(index_bigger + 1,nuevaParticion)
                return True
    
            print("sali")
            return False

            
