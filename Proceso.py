class proceso:
    def __init__(self, nombre, arribo, duracion, tamano):
        self.nombre = nombre
        self.arribo = arribo
        self.tiempoDeFinalizacion = 0
        self.duracion = duracion
        self.tamano = tamano
        self.evento  =[]
        self.inicioP=0
        self.finP=0
    
    def mostrarInfo(self):
        print("Nombre del proceso: ",self.nombre)
        print("Tiempo de arribo: ",self.arribo)
        print("Duración del proceso: ",self.duracion)
        print("Tamaño del proceso: ",self.tamano)
        print("---------------------------")

    def getNombre(self):                
        return self.nombre

    def getArribo(self):
        return self.arribo

    def getDuracion(self):
        return self.duracion

    def getTamano(self):
        return self.tamano
    
    def setNombre(self, nombre):
        if not isinstance(nombre, str):
            raise TypeError("Nombre debe ser una cadena de texto (string)")
        self.nombre = nombre

    def setArribo(self, arribo):
        if not isinstance(arribo, (int)):
            raise TypeError("Arribo debe ser un número real")
        self.arribo = int(arribo)

    def setDuracion(self, duracion):
        if not isinstance(duracion, (int)):
            raise TypeError("Duración debe ser un número real")
        self.duracion = int(duracion)

    def setTamano(self, tamano):
        if not isinstance(tamano, int):
            raise TypeError("Tamaño debe ser un entero (int)")
        self.tamano = tamano


    def cargarEvento(self,inicio,duracion,tipo):
        self.evento.append((inicio,duracion,tipo))
        pass
    def cargarTamano(self,ini,fini):
        self.inicioP=ini 
        self.finP=fini  

    def cargarProceso(self, nombre, arribo, duracion, tamano,cantidadProcesos):
        try:
            arribo = int(arribo)
            duracion = int(duracion)
            tamano = int(tamano)
            self.setNombre(nombre)
            self.setArribo(arribo)
            self.setDuracion(duracion)
            self.setTamano(tamano)

            print("Proceso cargado exitosamente:")
            self.mostrarInfo()
            return self 
        except ValueError as e:
            print("Error al cargar el proceso:", e)
            return None