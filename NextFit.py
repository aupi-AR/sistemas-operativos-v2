import Particion
from Estrategia import Estrategia


class NextFit(Estrategia):
          
    def seleccionarParticion(self, proceso, particiones):
            Vof=False
            if self.ultimaParticion!=None:
                 i=particiones.index(self.ultimaParticion)
                 for i in range (len(particiones)): 
                    if particiones[i].tamano>=proceso.tamano and particiones[i].proceso is None:
                         Vof=True
                         particion=particiones[i]
            if Vof==False:
                for p in particiones:
                    if p.tamano>=proceso.tamano and p.proceso is None:
                        particion=p
                        Vof=True

            if Vof==True:
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
                    index=particiones.index(particion)
                    particiones.insert(index + 1,nuevaParticion)
                return True
            print("sali")
            return False


