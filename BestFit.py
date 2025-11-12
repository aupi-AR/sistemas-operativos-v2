import Particion
from Estrategia import Estrategia

class BestFit(Estrategia):
        
        def seleccionarParticion(self, proceso, particiones):
            melior=Particion.Particion(1,None,tamano=0,inicio=0,fin=0)
            index_melior=-1
            for particion in particiones:
                if particion.tamano>=proceso.tamano and particion.proceso is None:
                        if melior.tamano==0:
                            melior=particion
                            index_melior=particiones.index(particion)
                        if particion.tamano<melior.tamano:
                            index_melior=particiones.index(particion)
                            melior=particion

            print("entre a la aprte critica")
            if melior.tamano!=0:
                particion=particiones[index_melior]

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
                    particiones.insert(index_melior + 1,nuevaParticion)
                return True
    
            print("sali")
            return False