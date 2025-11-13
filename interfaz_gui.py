import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from Memoria import Memoria
from Proceso import proceso
from FirstFit import FirstFit
from WorstFit import WorstFit
from BestFit import BestFit
from NextFit import NextFit
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import sys
import os
import atexit


# --- Ajustar la carpeta de trabajo correctamente ---
if getattr(sys, 'frozen', False):
    # Si es un ejecutable (.exe o .app), usar la carpeta donde está el ejecutable
    base_dir = os.path.dirname(sys.executable)
else:
    # Si se ejecuta directamente con Python, usar la carpeta del script
    base_dir = os.path.dirname(os.path.abspath(__file__))

os.chdir(base_dir)

    
class MemorySimulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Gestión de Memoria")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        
        self.json_data = None
        self.lista_procesos = []
        
        # Variables para navegación interactiva del gráfico
        self.pan_active = False
        self.press_event = None
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        self.crear_interfaz()
    
    def validar_solo_enteros(self, texto):
        """Valida que solo se ingresen números enteros (sin punto ni coma)"""
        if texto == "":
            return True
        # Permite solo dígitos (sin punto ni coma)
        return texto.isdigit()
    
    def crear_interfaz(self):
        # Registrar la función de validación
        vcmd = (self.root.register(self.validar_solo_enteros), '%P')
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Simulador de Gestión de Memoria", 
                          font=('Arial', 18, 'bold'))
        titulo.pack(pady=(0, 20))
        
        # Frame de configuración
        config_frame = ttk.LabelFrame(main_frame, text="Configuración de Memoria", 
                                     padding="15")
        config_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Tamaño de memoria
        ttk.Label(config_frame, text="Tamaño de Memoria:").grid(row=0, column=0, 
                                                                sticky=tk.W, pady=5)
        self.tamano_var = tk.IntVar(value=500)
        tamano_entry = ttk.Entry(config_frame, textvariable=self.tamano_var, width=15,
                                validate='key', validatecommand=vcmd)
        tamano_entry.grid(row=0, column=1, padx=10, pady=5)
        tamano_entry.bind('<FocusOut>', lambda e: self.validar_positivo(self.tamano_var))
        
        # Estrategia
        ttk.Label(config_frame, text="Estrategia:").grid(row=0, column=2, 
                                                         sticky=tk.W, pady=5, padx=(20, 0))
        self.estrategia_var = tk.StringVar(value="FirstFit")
        estrategia_combo = ttk.Combobox(config_frame, textvariable=self.estrategia_var,
                                       values=["FirstFit", "BestFit", "WorstFit", "NextFit"],
                                       state="readonly", width=12)
        estrategia_combo.grid(row=0, column=3, padx=10, pady=5)
        
        # Tiempo de selección
        ttk.Label(config_frame, text="Tiempo de Selección:").grid(row=1, column=0, 
                                                                  sticky=tk.W, pady=5)
        self.tiempo_sel_var = tk.IntVar(value=1)
        tiempo_sel_entry = ttk.Entry(config_frame, textvariable=self.tiempo_sel_var, width=15,
                                     validate='key', validatecommand=vcmd)
        tiempo_sel_entry.grid(row=1, column=1, padx=10, pady=5)
        tiempo_sel_entry.bind('<FocusOut>', lambda e: self.validar_no_negativo(self.tiempo_sel_var))
        
        # Promedio de carga
        ttk.Label(config_frame, text="Promedio de Carga:").grid(row=1, column=2, 
                                                                sticky=tk.W, pady=5, padx=(20, 0))
        self.promedio_carga_var = tk.IntVar(value=1)
        promedio_entry = ttk.Entry(config_frame, textvariable=self.promedio_carga_var, width=12,
                                   validate='key', validatecommand=vcmd)
        promedio_entry.grid(row=1, column=3, padx=10, pady=5)
        promedio_entry.bind('<FocusOut>', lambda e: self.validar_no_negativo(self.promedio_carga_var))
        
        # Tiempo de liberación
        ttk.Label(config_frame, text="Tiempo de Liberación:").grid(row=2, column=0, 
                                                                   sticky=tk.W, pady=5)
        self.tiempo_lib_var = tk.IntVar(value=1)
        tiempo_lib_entry = ttk.Entry(config_frame, textvariable=self.tiempo_lib_var, width=15,
                                     validate='key', validatecommand=vcmd)
        tiempo_lib_entry.grid(row=2, column=1, padx=10, pady=5)
        tiempo_lib_entry.bind('<FocusOut>', lambda e: self.validar_no_negativo(self.tiempo_lib_var))
        
        # Frame de archivo JSON
        json_frame = ttk.LabelFrame(main_frame, text="Archivo de Procesos", padding="15")
        json_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(json_frame, text="Cargar archivo JSON con los procesos:").pack(anchor=tk.W)
        
        file_frame = ttk.Frame(json_frame)
        file_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.file_label = ttk.Label(file_frame, text="Ningún archivo seleccionado", 
                                    foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(file_frame, text="Seleccionar JSON", 
                  command=self.cargar_json).pack(side=tk.LEFT)
        
        # Frame de información del JSON
        self.info_frame = ttk.LabelFrame(main_frame, text="Procesos Cargados", padding="15")
        self.info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Text widget con scrollbar
        text_frame = ttk.Frame(self.info_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.info_text = tk.Text(text_frame, height=8, width=70, 
                                yscrollcommand=scrollbar.set, state=tk.DISABLED)
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.info_text.yview)
        
     
        self.resultados_frame = ttk.LabelFrame(main_frame, text="Resultados de la Simulación", 
                                               padding="15")
        self.resultados_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Label para mostrar fragmentación
        resultado_inner = ttk.Frame(self.resultados_frame)
        resultado_inner.pack(fill=tk.X)
        
        ttk.Label(resultado_inner, text="Fragmentación Total:", 
                 font=('Arial', 11, 'bold')).pack(side=tk.LEFT, padx=(0, 10))
        
        self.fragmentacion_label = ttk.Label(resultado_inner, text="-- ", 
                                            font=('Arial', 11),
                                            foreground='blue')
        self.fragmentacion_label.pack(side=tk.LEFT)
        
        # Botón de simulación - GRANDE Y VISIBLE
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.btn_simular = tk.Button(btn_frame, 
                                     text=" EJECUTAR SIMULACIÓN Y MOSTRAR GANTT", 
                                     command=self.ejecutar_simulacion, 
                                     state=tk.DISABLED,
                                     bg='#4CAF50',
                                     fg='white',
                                     font=('Arial', 14, 'bold'),
                                     height=2,
                                     cursor='hand2')
        self.btn_simular.pack(fill=tk.X, ipady=5)
        
        # Estilo para el botón
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12, 'bold'))
    
    def validar_positivo(self, var):
        """Valida que el valor sea positivo (mayor que 0)"""
        try:
            valor = var.get()
            if valor <= 0:
                var.set(1)
        except:
            var.set(1)
    
    def validar_no_negativo(self, var):
        """Valida que el valor no sea negativo (mayor o igual a 0)"""
        try:
            valor = var.get()
            if valor < 0:
                var.set(0)
        except:
            var.set(0)
    
    def cargar_json(self):
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo JSON",
            filetypes=(("Archivos JSON", "*.json"), ("Todos los archivos", "*.*"))
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    self.json_data = json.load(f)
                
                # Validar que sea una lista
                if not isinstance(self.json_data, list):
                    raise ValueError("El JSON debe contener una lista de procesos")
                
                if len(self.json_data) == 0:
                    raise ValueError("El JSON está vacío, no contiene procesos")
                
                self.file_label.config(text=filename.split('/')[-1], foreground="green")
                self.crear_procesos()
                
                # Validar que se crearon procesos
                if len(self.lista_procesos) == 0:
                    raise ValueError("No se pudieron crear procesos desde el JSON")
                
                self.mostrar_info_procesos()
                self.btn_simular.config(state=tk.NORMAL)
                # Resetear fragmentación al cargar nuevo archivo
                self.fragmentacion_label.config(text="-- ")
                
                messagebox.showinfo("Éxito", f"Se cargaron {len(self.lista_procesos)} procesos correctamente")
                
            except json.JSONDecodeError as e:
                messagebox.showerror("Error de JSON", f"El archivo no es un JSON válido:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar el archivo JSON:\n{str(e)}\n\nVerifica que el formato sea correcto.")
    
    def crear_procesos(self):
        self.lista_procesos = []
        
        if isinstance(self.json_data, list):
            for i, proc_data in enumerate(self.json_data):
                try:
                    # Buscar el nombre del proceso
                    nombre = proc_data.get('nombre', proc_data.get('Nombre', f'P{i+1}'))
                    
                    # Buscar tiempo de arribo
                    arribo = proc_data.get('tiempo_arribo', proc_data.get('arribo', 
                             proc_data.get('Tiempo_arribo', proc_data.get('Arribo', 0))))
                    arribo = int(arribo)
                    
                    # Buscar duración
                    duracion = proc_data.get('duracion', proc_data.get('rafaga',
                               proc_data.get('Duracion', proc_data.get('Rafaga', 0))))
                    duracion = int(duracion)
                    
                    # Buscar tamaño
                    tamano = proc_data.get('memoria_requerida', proc_data.get('tamano',
                             proc_data.get('Memoria_requerida', proc_data.get('Tamano', 0))))
                    tamano = int(tamano)
                    
                    if tamano <= 0:
                        print(f"Advertencia: Proceso {nombre} tiene tamaño inválido: {tamano}")
                        continue
                    
                    proc = proceso(nombre, arribo, duracion, tamano)
                    self.lista_procesos.append(proc)
                    print(f"Proceso cargado: {nombre}, arribo={arribo}, duracion={duracion}, tamano={tamano}")
                    
                except Exception as e:
                    print(f"Error al procesar proceso {i}: {e}")
                    print(f"Datos del proceso: {proc_data}")
                    continue
    
    def obtener_proceso_mas_grande(self):
        """Retorna el tamaño del proceso más grande"""
        if not self.lista_procesos:
            return 0
        return max(p.tamano for p in self.lista_procesos)
    
    def mostrar_info_procesos(self):
        self.info_text.config(state=tk.NORMAL)
        self.info_text.delete(1.0, tk.END)
        
        if self.lista_procesos:
            self.info_text.insert(tk.END, f"Total de procesos: {len(self.lista_procesos)}\n\n")
            
            for proc in self.lista_procesos:
                self.info_text.insert(tk.END, 
                    f"• {proc.nombre}: Arribo={proc.arribo}, "
                    f"Duración={proc.duracion}, Tamaño={proc.tamano}\n")
        else:
            self.info_text.insert(tk.END, "No hay procesos cargados.")
        
        self.info_text.config(state=tk.DISABLED)
    
    def ejecutar_simulacion(self):
        try:
            # Verificar que haya procesos cargados
            if not self.lista_procesos:
                messagebox.showerror("Error", "No hay procesos cargados. Carga un archivo JSON primero.")
                return
            
            print(f"\n{'='*60}")
            print(f"INICIANDO SIMULACIÓN CON {len(self.lista_procesos)} PROCESOS")
            print(f"{'='*60}")
            for p in self.lista_procesos:
                print(f"  - {p.nombre}: arribo={p.arribo}, duración={p.duracion}, tamaño={p.tamano}")
            print(f"{'='*60}\n")
            
            # VALIDAR: Verificar que la memoria sea suficiente para el proceso más grande
            proceso_mas_grande = self.obtener_proceso_mas_grande()
            tamano_memoria = self.tamano_var.get()
            
            if tamano_memoria < proceso_mas_grande:
                messagebox.showerror(
                    "Error de Configuración",
                    f"El tamaño de memoria ({tamano_memoria}) es insuficiente.\n\n"
                    f"El proceso más grande requiere {proceso_mas_grande} unidades.\n"
                    f"La memoria debe ser al menos {proceso_mas_grande} unidades."
                )
                return
            
            # Crear estrategia
            estrategia_nombre = self.estrategia_var.get()
            if estrategia_nombre == "FirstFit":
                estrategia = FirstFit()
            elif estrategia_nombre == "BestFit":
                estrategia = BestFit()
            elif estrategia_nombre == "WorstFit":
                estrategia = WorstFit()
            else:
                estrategia = NextFit()
            
            # IMPORTANTE: Crear una COPIA de la lista de procesos
            # porque la simulación modifica la lista original
            import copy
            procesos_para_simulacion = copy.deepcopy(self.lista_procesos)
            
            # Crear objeto Memoria
            simulacion = Memoria(
                tamano_memoria,
                estrategia,
                self.tiempo_sel_var.get(),
                self.promedio_carga_var.get(),
                self.tiempo_lib_var.get(),
                procesos_para_simulacion
            )
            
            # EJECUTAR SIMULACIÓN
            print("\nEjecutando simulación...")
            simulacion.simulacion()
            print("Simulación completada!\n")
            
            
            self.fragmentacion_label.config(
                text=f"{simulacion.fragmentacion} unidades",
                foreground='darkgreen'
            )
            
            # Imprimir resultados en consola
            print(f"\nFragmentación total: {simulacion.fragmentacion}")
            print(f"Procesos terminados: {len(simulacion.procesosTerminados)}")
            self.imprimir_eventos(simulacion.procesosTerminados)
            
            # GENERAR GANTT
            self.generar_gantt(simulacion)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la simulación:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def imprimir_eventos(self, lista_procesos):
        print("\n===== LISTA DE EVENTOS =====")
        for p in lista_procesos:
            if p is None:
                continue
            
            print(f"\nProceso: {p.nombre}")
            print("-" * 30)

            if len(p.evento) == 0:
                print("  (No tiene eventos)")
                continue
            
            for inicio, duracion, tipo in p.evento:
                print(f"  Evento: {tipo:12} | Inicio: {inicio:3} | Fin: {inicio+duracion:3} | Duración: {duracion}")
    
    def configurar_navegacion_interactiva(self, fig, ax):
        """Configura la navegación interactiva del gráfico Gantt"""
        
        def on_scroll(event):
            """Zoom con la ruedita del ratón"""
            if event.inaxes != ax:
                return
            
            # Factor de zoom
            base_scale = 1.2
            
            # Obtener límites actuales
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            
            # Obtener posición del cursor
            xdata = event.xdata
            ydata = event.ydata
            
            if event.button == 'up':
                # Zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'down':
                # Zoom out
                scale_factor = base_scale
            else:
                return
            
            # Calcular nuevos límites
            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor
            
            # Centrar el zoom en la posición del cursor
            relx = (cur_xlim[1] - xdata) / (cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata) / (cur_ylim[1] - cur_ylim[0])
            
            ax.set_xlim([xdata - new_width * (1 - relx), xdata + new_width * relx])
            ax.set_ylim([ydata - new_height * (1 - rely), ydata + new_height * rely])
            
            fig.canvas.draw_idle()
        
        def on_press(event):
            """Inicia el arrastre con click izquierdo"""
            if event.inaxes != ax:
                return
            if event.button == 1:  # Click izquierdo
                self.pan_active = True
                self.press_event = event
                fig.canvas.set_cursor(1)  # Cursor de mano
        
        def on_release(event):
            """Termina el arrastre"""
            self.pan_active = False
            self.press_event = None
            fig.canvas.set_cursor(0)  # Cursor normal
        
        def on_motion(event):
            """Arrastra el gráfico"""
            if not self.pan_active or self.press_event is None:
                return
            if event.inaxes != ax:
                return
            
            # Calcular el desplazamiento
            dx = event.xdata - self.press_event.xdata
            dy = event.ydata - self.press_event.ydata
            
            # Obtener límites actuales
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()
            
            # Aplicar desplazamiento
            ax.set_xlim(cur_xlim[0] - dx, cur_xlim[1] - dx)
            ax.set_ylim(cur_ylim[0] - dy, cur_ylim[1] - dy)
            
            fig.canvas.draw_idle()
        
        # Conectar eventos
        fig.canvas.mpl_connect('scroll_event', on_scroll)
        fig.canvas.mpl_connect('button_press_event', on_press)
        fig.canvas.mpl_connect('button_release_event', on_release)
        fig.canvas.mpl_connect('motion_notify_event', on_motion)
    
    def generar_gantt(self, simulacion):
        lista_procesos_terminados = simulacion.procesosTerminados
        
        colores_eventos = {
            "seleccionando": "skyblue",
            "cargando": "orange",
            "rafaga": "green",
            "finalizacion": "red"
        }
        
        gantt = []
        for p in lista_procesos_terminados:
            if p is None:
                continue
            
            inicio_mem = p.inicioP
            fin_mem = p.finP
            altura_mem = (fin_mem - inicio_mem) + 1
            
            for inicio_t, duracion, tipo in p.evento:
                if tipo in ["seleccionando", "cargando", "rafaga", "finalizacion"]:
                    fin_t = inicio_t + duracion 
                    gantt.append((p.nombre, inicio_t, fin_t, tipo, inicio_mem, altura_mem))
        
        if not gantt:
            messagebox.showwarning("Sin datos", "No hay eventos para graficar.")
            return
        
        # GRAFICAR GANTT
        fig, ax = plt.subplots(figsize=(14, 7))
        
        for nombre, inicio_t, fin_t, tipo, inicio_m, altura_m in gantt:
            color = colores_eventos.get(tipo, "gray")
            duracion_tiempo = fin_t - inicio_t

            ax.barh(
                inicio_m,
                duracion_tiempo,
                left=inicio_t,
                height=altura_m,
                color=color,
                edgecolor="black",
                align='edge'
            )
            
            if tipo == 'rafaga':
                x_center = inicio_t + duracion_tiempo / 2
                y_center = inicio_m + altura_m / 2
                ax.text(x_center, y_center, f"{nombre}-{tipo}", va='center', ha='center',
                       fontsize=9, color='white', fontweight='bold')
        
        ax.set_xlabel("Tiempo")
        ax.set_ylabel("Tamaño de Memoria")
        ax.set_title("Diagrama de Gantt - Uso de Memoria vs. Tiempo\n(Usa la ruedita para zoom y arrastra para mover)")
        
        total_memoria = simulacion.tamano
        max_time = max(g[2] for g in gantt)
        
        ax.set_ylim(0, total_memoria)
        ax.set_xlim(0, max_time + 1)
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.grid(axis='x', linestyle="--", alpha=0.4)
        
        handles = [plt.Rectangle((0,0),1,1,color=c) for c in colores_eventos.values()]
        labels = list(colores_eventos.keys())
        ax.legend(handles, labels, title="Eventos en Memoria", 
                 bbox_to_anchor=(1.02, 1), loc='upper left')
        
        # HABILITAR NAVEGACIÓN INTERACTIVA
        self.configurar_navegacion_interactiva(fig, ax)
        
        plt.tight_layout()
        plt.show()


def main():
    root = tk.Tk()
    app = MemorySimulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()