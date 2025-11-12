from Particion import Particion
from Proceso import proceso
from Estrategia import Estrategia
import json
from datetime import datetime
from pathlib import Path
import tempfile
import sys

class Memoria:
    def __init__(self, tamano:int, estrategia:Estrategia, tiempoSeleccion:int, PromedioCarga:int, TiempoLiberacion:int, procesos:list[proceso]):
        self.tamano = tamano
        self.estrategia = estrategia
        self.tiempoSeleccion = tiempoSeleccion
        self.PromedioCarga = PromedioCarga
        self.TiempoLiberacion = TiempoLiberacion
        self.particiones: list[Particion] = []
        self.procesos = procesos
        # Ordenar por tiempo de arribo
        self.procesos.sort(key=lambda x: x.getArribo())
        self.vof=False
        self.turno=True
        if tiempoSeleccion == 0 and PromedioCarga == 0 and TiempoLiberacion == 0:
            self.casoTodo0=True
        else:
            self.casoTodo0=False
        

        # Crear partición inicial
        particion_inicial = Particion(
            nombre=0,
            tamano=self.tamano,
            inicio=0,
            fin=self.tamano-1,
            proceso=None
        )
        self.particiones.append(particion_inicial)
        
        # Atributos que uso en la simulación
        self.nroParticion = 1
        self.procesosTerminados = []
        self.fragmentacion = 0
        self.tiempo = 0
        self.tiempos= []
        
        # NUEVO: Listas para almacenar eventos y estados
        self.eventos = []
        self.estados_particiones = []
        
        # Registrar estado inicial
        self.registrarEstadoParticiones("Inicialización del sistema")

    def registrarEvento(self, tipo_evento: str, descripcion: str, proceso_nombre: str = None, particion_id: int = None):
        """
        Registra un evento en el sistema.
        
        Args:
            tipo_evento: Tipo de evento (ej: "SELECCION", "CARGA", "FINALIZACION", "PARTICION_CREADA", "PARTICIONES_UNIDAS")
            descripcion: Descripción detallada del evento
            proceso_nombre: Nombre del proceso involucrado (opcional)
            particion_id: ID de la partición involucrada (opcional)
        """
        evento = {
            "tiempo": self.tiempo,
            "tipo": tipo_evento,
            "descripcion": descripcion,
            "proceso": proceso_nombre,
            "particion": particion_id
        }
        self.eventos.append(evento)
        print(f"[T={self.tiempo}] {tipo_evento}: {descripcion}")

    def registrarEstadoParticiones(self, motivo: str):
        """
        Guarda una instantánea del estado actual de todas las particiones.
        
        Args:
            motivo: Razón por la cual se registra este estado
        """
        estado = {
            "tiempo": self.tiempo,
            "motivo": motivo,
            "particiones": []
        }
        
        for particion in self.particiones:
            info_particion = {
                "id": particion.nombre,
                "direccion_inicio": particion.inicio,
                "direccion_fin": particion.fin,
                "tamano": particion.tamano,
                "estado": particion.estado,
                "proceso": particion.proceso.nombre if particion.proceso else None,
                "tiempo_liberacion": particion.tiempoLiberacion if particion.estado == "ocupado" else None
            }
            estado["particiones"].append(info_particion)
        
        self.estados_particiones.append(estado)

    def _obtener_directorio_salida(self) -> Path:
        """
        Devuelve el directorio donde está ubicado el ejecutable (.exe) o el script Python.
        """
        try:
            if getattr(sys, 'frozen', False):
                base_path = Path(sys.executable).parent
            else:
                base_path = Path(__file__).resolve().parent
        except Exception:
            base_path = Path.cwd()

        return base_path



    def guardarRegistros(self, nombre_archivo: str = "simulacion_memoria"):
        import tkinter.messagebox as messagebox
        import os

        messagebox.showinfo("Ruta actual", f"Intentando guardar en:\n{os.getcwd()}")
        """
        Guarda los eventos y estados en archivos.
        
        Args:
            nombre_archivo: Nombre base para los archivos (sin extensión)
        """
        directorio_salida = self._obtener_directorio_salida()
        base_eventos = directorio_salida / f"{nombre_archivo}_eventos.txt"
        base_estados = directorio_salida / f"{nombre_archivo}_estados.txt"
        base_json = directorio_salida / f"{nombre_archivo}_completo.json"

        # Guardar eventos
        with open(base_eventos, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("REGISTRO DE EVENTOS DE LA SIMULACIÓN\n")
            f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for evento in self.eventos:
                f.write(f"Tiempo: {evento['tiempo']}\n")
                f.write(f"Tipo: {evento['tipo']}\n")
                f.write(f"Descripción: {evento['descripcion']}\n")
                if evento['proceso']:
                    f.write(f"Proceso: {evento['proceso']}\n")
                if evento['particion'] is not None:
                    f.write(f"Partición: {evento['particion']}\n")
                f.write("-"*80 + "\n")
        
        # Guardar estados de particiones
        with open(base_estados, "w", encoding="utf-8") as f:
            f.write("="*80 + "\n")
            f.write("ESTADOS DE LA TABLA DE PARTICIONES\n")
            f.write(f"Generado el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for estado in self.estados_particiones:
                f.write(f"\nTiempo: {estado['tiempo']}\n")
                f.write(f"Motivo: {estado['motivo']}\n")
                f.write("-"*80 + "\n")
                f.write(f"{'ID':<5} {'Inicio':<10} {'Fin':<10} {'Tamaño':<10} {'Estado':<12} {'Proceso':<15} {'T.Lib':<10}\n")
                f.write("-"*80 + "\n")
                
                for part in estado['particiones']:
                    t_lib = str(part['tiempo_liberacion']) if part['tiempo_liberacion'] else "-"
                    proceso_str = part['proceso'] if part['proceso'] else "-"
                    f.write(f"{part['id']:<5} {part['direccion_inicio']:<10} {part['direccion_fin']:<10} "
                           f"{part['tamano']:<10} {part['estado']:<12} {proceso_str:<15} {t_lib:<10}\n")
                f.write("="*80 + "\n")
        
        # Guardar versión JSON para facilitar procesamiento posterior
        with open(base_json, "w", encoding="utf-8") as f:
            datos = {
                "eventos": self.eventos,
                "estados_particiones": self.estados_particiones,
                "estadisticas": {
                    "tiempo_total": self.tiempo,
                    "procesos_terminados": len(self.procesosTerminados),
                    "fragmentacion_total": self.fragmentacion
                }
            }
            json.dump(datos, f, indent=2, ensure_ascii=False)
        
        print(f"\nRegistros guardados en:")
        print(f"  - {base_eventos}")
        print(f"  - {base_estados}")
        print(f"  - {base_json}")

        print("[DEBUG] guardarRegistros ejecutado correctamente.")
        print("[DEBUG] Archivos deberían estar en:", directorio_salida)

    def mostrarInfo(self):
        print("Tamaño de la memoria: ",self.tamano)
        print("Estrategia de asignación: ",self.estrategia)
        print("Tiempo de selección: ",self.tiempoSeleccion)
        print("Promedio de carga: ",self.PromedioCarga)
        print("Tiempo de liberación: ",self.TiempoLiberacion)

    def getTamano(self):
        return self.tamano  
    
    def getEstrategia(self):
        return self.estrategia
    
    def getTiempoSeleccion(self):
        return self.tiempoSeleccion
    
    def getPromedioCarga(self):
        return self.PromedioCarga
    
    def getTiempoLiberacion(self):  
        return self.TiempoLiberacion
    
    def setTamano(self, tamano):
        if not isinstance(tamano, int):
            raise TypeError("Tamaño debe ser un entero (int)")
        if tamano <= 0:
            raise ValueError("Tamaño debe ser mayor que 0")
        self.tamano = tamano

    def setTiempoSeleccion(self, tiempoSeleccion):
        if not isinstance(tiempoSeleccion, (int)):
            raise TypeError("Tiempo de selección debe ser un número")
        tiempoSeleccion = int(tiempoSeleccion)
        if tiempoSeleccion < 0:
            raise ValueError("Tiempo de selección no puede ser negativo")
        self.tiempoSeleccion = tiempoSeleccion

    def setPromedioCarga(self, PromedioCarga):
        if not isinstance(PromedioCarga, (int)):
            raise TypeError("Promedio de carga debe ser un número")
        PromedioCarga = int(PromedioCarga)
        if PromedioCarga < 0:
            raise ValueError("Promedio de carga no puede ser negativo")
        self.PromedioCarga = PromedioCarga

    def setTiempoLiberacion(self, TiempoLiberacion):
        if not isinstance(TiempoLiberacion, (int)):
            raise TypeError("Tiempo de liberación debe ser un número")
        TiempoLiberacion = int(TiempoLiberacion)
        if TiempoLiberacion < 0:
            raise ValueError("Tiempo de liberación no puede ser negativo")
        self.TiempoLiberacion = TiempoLiberacion

    def buscarParticion(self, proceso_buscado):
        """
        Encuentra el índice de la partición que contiene un proceso específico.
        """
        for i, particion in enumerate(self.particiones):
            if particion.proceso is proceso_buscado:
                return i
        return -1

    def unirParticionesLibres(self,particion):
        indice = self.particiones.index(particion)
        particiones_unidas = []
        
        if indice > 0:
            particionAnterior = self.particiones[indice - 1]
            if particionAnterior.proceso is None:
                particiones_unidas.append(particionAnterior.nombre)
                particionAnterior.fin = particion.fin
                particionAnterior.tamano += particion.tamano
                self.particiones.remove(particion)
                particion = particionAnterior
                indice -= 1
                
        if indice < len(self.particiones) - 1:
            particionSiguiente = self.particiones[indice + 1]
            if particionSiguiente.proceso is None:
                particiones_unidas.append(particionSiguiente.nombre)
                particion.fin = particionSiguiente.fin
                particion.tamano += particionSiguiente.tamano
                self.particiones.remove(particionSiguiente)
        
        # NUEVO: Registrar unión de particiones
        if particiones_unidas:
            self.registrarEvento(
                "PARTICIONES_UNIDAS",
                f"Particiones {particiones_unidas} unidas en partición {particion.nombre} (tamaño: {particion.tamano})",
                particion_id=particion.nombre
            )
            self.registrarEstadoParticiones(f"Unión de particiones libres en partición {particion.nombre}")

    def calcularFragmentacion(self,vof):
        frag=0
        if self.procesos:
            for p in self.particiones:
                if p.estado!="ocupado" or p.tiempoLiberacion<=self.tiempo:
                    print("tamano particion=",p.tamano)
                    print("particion nombre p",p.nombre)
                    print("finaliza=",p.tiempoLiberacion)
                    print("tiempo=",self.tiempo)
                    frag+=p.tamano
                    print("frag en for=",frag)
                    print("------------------")
                    
            self.fragmentacion+=frag
            print("calculando fragmentacion",self.fragmentacion)
            print("------------------")
        elif vof==True:
            for p in self.particiones:
                if p.estado!="ocupado" or p.tiempoLiberacion<=self.tiempo:
                    print("tamano particion=",p.tamano)
                    print("particion nombre p",p.nombre)
                    print("finaliza=",p.tiempoLiberacion)
                    print("tiempo=",self.tiempo)
                    frag+=p.tamano
                    print("frag en for=",frag)
                    print("------------------")
                    
            self.fragmentacion+=frag

    def FinalizarProcesos(self):
        for particion in self.particiones:
            if particion.proceso is not None and particion.proceso.tiempoDeFinalizacion <= self.tiempo and particion.proceso.tiempoDeFinalizacion != 0:
                particion.estado="finalizando"
                
                # NUEVO: Registrar inicio de finalización
                self.registrarEvento(
                    "FINALIZACION_INICIO",
                    f"Iniciando finalización del proceso {particion.proceso.nombre} en partición {particion.nombre}",
                    proceso_nombre=particion.proceso.nombre,
                    particion_id=particion.nombre
                )
                
                particion.proceso.cargarEvento(self.tiempo,self.TiempoLiberacion,"finalizacion")
                
                for i in range(self.TiempoLiberacion):
                    self.calcularFragmentacion(self.vof)
                    self.tiempo +=1
                
                proceso_finalizado = particion.proceso.nombre
                self.procesosTerminados.append(particion.proceso)
                particion.limpiarParticion()
                
                # NUEVO: Registrar finalización completada
                self.registrarEvento(
                    "FINALIZACION_COMPLETA",
                    f"Proceso {proceso_finalizado} finalizado y liberado de partición {particion.nombre}",
                    proceso_nombre=proceso_finalizado,
                    particion_id=particion.nombre
                )
                self.registrarEstadoParticiones(f"Liberación de partición {particion.nombre} tras finalizar proceso {proceso_finalizado}")
                
                self.unirParticionesLibres(particion)

    def aceptarNuevosProcesos(self):
        self.FinalizarProcesos()
        if self.procesos and self.procesos[0].arribo <= self.tiempo:
            proceso = self.procesos[0]
            
            # NUEVO: Registrar intento de asignación
            self.registrarEvento(
                "PROCESO_ARRIBO",
                f"Proceso {proceso.nombre} arribó al sistema (tamaño: {proceso.tamano})",
                proceso_nombre=proceso.nombre
            )
            
            if self.estrategia.seleccionarParticion(proceso,self.particiones) and self.turno==True:
                self.turno=False
                self.procesos.pop(0)
                t=self.tiempo
                if len(self.procesos)==0 and t==self.tiempo:
                    self.vof=True
                
                # Encontrar la partición asignada
                indice_particion = self.buscarParticion(proceso)
                particion = self.particiones[indice_particion]
                
                self.registrarEvento(
                    "SELECCION_PARTICION",
                    f"Partición {particion.nombre} seleccionada para proceso {proceso.nombre} (estrategia: {self.estrategia.__class__.__name__})",
                    proceso_nombre=proceso.nombre,
                    particion_id=particion.nombre
                )
                self.registrarEstadoParticiones(f"Partición creada/asignada para proceso {proceso.nombre}")
                
                print("cargado en memoria")    
                proceso.cargarEvento(self.tiempo, self.tiempoSeleccion,"seleccionando")
                print("fors selec")
                
                for i in range(self.tiempoSeleccion):
                    self.calcularFragmentacion(self.vof)
                    self.tiempo +=1

                print("frag fors selec=",self.fragmentacion)


                self.registrarEvento(
                    "CARGA_INICIO",
                    f"Iniciando carga del proceso {proceso.nombre} en partición {particion.nombre}",
                    proceso_nombre=proceso.nombre,
                    particion_id=particion.nombre
                )

                proceso.cargarEvento(self.tiempo, self.PromedioCarga,"cargando") 

                print("fors carg")
                for i in range(self.PromedioCarga):
                    self.calcularFragmentacion(self.vof)
                    self.tiempo +=1
                    
                particion.estado="ocupado"
                print("frag en carga=",self.fragmentacion)
                
                proceso.tiempoDeFinalizacion = self.tiempo+proceso.duracion
                particion.tiempoLiberacion=self.tiempo+proceso.duracion
                print("tiempo de liberacion p{particion.nombre}",particion.tiempoLiberacion)
                
                self.registrarEvento(
                    "CARGA_COMPLETA",
                    f"Proceso {proceso.nombre} cargado en partición {particion.nombre}. Inicio de ejecución",
                    proceso_nombre=proceso.nombre,
                    particion_id=particion.nombre
                )
                self.registrarEstadoParticiones(f"Proceso {proceso.nombre} en ejecución en partición {particion.nombre}")
                
                proceso.cargarEvento(self.tiempo,proceso.duracion,"rafaga")
                self.vof=False
                if self.casoTodo0==True:
                    self.calcularFragmentacion(self.vof)
                    self.tiempo+=1
                
            else:

                self.registrarEvento(
                    "PROCESO_RECHAZADO",
                    f"No hay partición disponible para proceso {proceso.nombre} (tamaño requerido: {proceso.tamano})",
                    proceso_nombre=proceso.nombre
                )
                print("else dentro de aceptar PROCESOS")
                self.calcularFragmentacion(self.vof)
                self.tiempo+=1
        else: 
            self.calcularFragmentacion(self.vof)
            self.tiempo+=1
    
    def imprimir(self):
        for proceso in self.procesos:
            print(proceso.nombre)

    def imprimir2(self):
        for particion in self.particiones:
            if particion.proceso is not None:
                print(particion.proceso.nombre)

    def simulacion(self):
        fin = len(self.procesos)
        
        # NUEVO: Registrar inicio de simulación
        self.registrarEvento(
            "SIMULACION_INICIO",
            f"Inicio de simulación con {fin} procesos"
        )
        
        while len(self.procesosTerminados) < fin:
            self.FinalizarProcesos()
            print("tiempo=",self.tiempo)
            if self.procesos:
                print("entre al primer else")
                self.aceptarNuevosProcesos()
                self.turno=True
            else:
                print("entre al segundo else")
                self.tiempo += 1
            self.imprimir()
        
        # NUEVO: Registrar fin de simulación
        self.registrarEvento(
            "SIMULACION_FIN",
            f"Simulación completada. Tiempo total: {self.tiempo}. Procesos finalizados: {len(self.procesosTerminados)}"
        )

        self.guardarRegistros()
   

