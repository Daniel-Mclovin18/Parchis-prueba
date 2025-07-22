import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import math

NUM_CASILLAS_EXTERNAS = 68
NUM_CASILLAS_INTERNAS = 8
TAMANO_TABLERO = 600
MARGEN = 20
CELDA = 40

# Colores mejorados para la interfaz
COLORES = {
    'fondo_principal': '#2C3E50',
    'fondo_tablero': '#ECF0F1',
    'borde_tablero': '#34495E', 
    'texto_principal': '#2C3E50',
    'texto_secundario': '#7F8C8D',
    'boton_activo': '#3498DB',
    'boton_hover': '#2980B9',
    'casilla_normal': '#BDC3C7',
    'casilla_segura': '#F39C12',
    'via_interna': '#E8F8F5',
    'centro_tablero': '#D5DBDB'
}

COLORES_JUGADORES = {
    'Rojo': {'principal': '#E74C3C', 'claro': '#F1948A', 'oscuro': '#C0392B'},
    'Azul': {'principal': '#3498DB', 'claro': '#85C1E9', 'oscuro': '#2874A6'}, 
    'Verde': {'principal': '#27AE60', 'claro': '#82E0AA', 'oscuro': '#1E8449'},
    'Amarillo': {'principal': '#F1C40F', 'claro': '#F7DC6F', 'oscuro': '#D68910'}
}

class Ficha:
    def __init__(self, jugador, id_ficha):
        self.jugador = jugador
        self.id_ficha = id_ficha
        self.estado = "carcel"
    
    def __str__(self):
        if self.estado == "carcel":
            return f"{self.jugador.nombre}{self.id_ficha}(carcel)"
        elif isinstance(self.estado, int):
            return f"{self.jugador.nombre}{self.id_ficha}(ext {self.estado})"
        elif isinstance(self.estado, tuple) and self.estado[0] == "interna":
            return f"{self.jugador.nombre}{self.id_ficha}(int {self.estado[1]})"
        return f"{self.jugador.nombre}{self.id_ficha}(?)"

class Jugador:
    def __init__(self, nombre, color, salida, entrada_hogar):
        self.nombre = nombre
        self.color = color
        self.salida = salida
        self.entrada_hogar = entrada_hogar
        self.fichas = [Ficha(self, i) for i in range(4)]
        self.contador_dobles = 0
        self.movimientos_extra = 0
        self.ultima_ficha_movida = None
        self.tiempo_turno = 0
        self.movimientos_realizados = 0
        self.capturas_realizadas = 0
        self.fichas_en_meta = 0
    
    def todas_llegaron(self):
        count = 0
        for f in self.fichas:
            if isinstance(f.estado, tuple) and f.estado[0] == "interna" and f.estado[1] == (NUM_CASILLAS_INTERNAS - 1):
                count += 1
        self.fichas_en_meta = count
        return count == 4
    
    def obtener_estadisticas(self):
        return {
            'movimientos': self.movimientos_realizados,
            'capturas': self.capturas_realizadas,
            'fichas_en_meta': self.fichas_en_meta,
            'movimientos_extra': self.movimientos_extra
        }

jugadores = [
    Jugador("Rojo", "red", salida=0, entrada_hogar=67),
    Jugador("Azul", "blue", salida=17, entrada_hogar=16),
    Jugador("Verde", "green", salida=34, entrada_hogar=33),
    Jugador("Amarillo", "yellow", salida=51, entrada_hogar=50),
]

posiciones_de_tablero = {i: [] for i in range(NUM_CASILLAS_EXTERNAS)}
casillas_seguras = {j.salida for j in jugadores}

def es_bloqueo(pos):
    if len(posiciones_de_tablero[pos]) == 2:
        f0, f1 = posiciones_de_tablero[pos]
        if f0.jugador == f1.jugador:
            return True
    return False

def verificar_camino(inicio, pasos):
    for i in range(1, pasos):
        pos_verificar = (inicio + i) % NUM_CASILLAS_EXTERNAS
        if es_bloqueo(pos_verificar):
            return False, pos_verificar
    return True, None

def calcular_coordenadas_tablero():
    coordenadas = {}
    longitud_lado = 17
    top_y = MARGEN
    left_x = MARGEN
    right_x = TAMANO_TABLERO - MARGEN
    bottom_y = TAMANO_TABLERO - MARGEN
    
    for i in range(longitud_lado):
        pos = i
        x = left_x + i * ((right_x - left_x) // (longitud_lado - 1))
        y = top_y
        coordenadas[pos] = (x, y)
    
    for i in range(longitud_lado):
        pos = 17 + i
        x = right_x
        y = top_y + i * ((bottom_y - top_y) // (longitud_lado - 1))
        coordenadas[pos] = (x, y)
    
    for i in range(longitud_lado):
        pos = 34 + i
        x = right_x - i * ((right_x - left_x) // (longitud_lado - 1))
        y = bottom_y
        coordenadas[pos] = (x, y)
    
    for i in range(longitud_lado):
        pos = 51 + i
        x = left_x
        y = bottom_y - i * ((bottom_y - top_y) // (longitud_lado - 1))
        coordenadas[pos] = (x, y)
    
    return coordenadas

def calcular_via_interna_rojo():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x
        y = centro_y - (i + 1) * CELDA
        coords.append((x, y))
    return coords

def calcular_via_interna_azul():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x + (i + 1) * CELDA
        y = centro_y
        coords.append((x, y))
    return coords

def calcular_via_interna_verde():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x
        y = centro_y + (i + 1) * CELDA
        coords.append((x, y))
    return coords

def calcular_via_interna_amarillo():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x - (i + 1) * CELDA
        y = centro_y
        coords.append((x, y))
    return coords

coordenadas_del_tablero_externo = calcular_coordenadas_tablero()

coordenadas_de_la_via_interna = {
    "Rojo": calcular_via_interna_rojo(),
    "Azul": calcular_via_interna_azul(),
    "Verde": calcular_via_interna_verde(),
    "Amarillo": calcular_via_interna_amarillo(),
}

posiciones_de_la_carcel = {
    "Rojo": {"x": 80, "y": 100, "offset_y": 25},
    "Azul": {"x": 500, "y": 100, "offset_y": 25},
    "Verde": {"x": 400, "y": 400, "offset_y": 25},
    "Amarillo": {"x": 150, "y": 400, "offset_y": 25},
}

def puede_colocar(ficha, pos):
    return (len(posiciones_de_tablero[pos]) < 2)

def mover_ficha(ficha, pasos):
    ficha.jugador.movimientos_realizados += 1
    
    if ficha.estado == "carcel":
        if pasos != 5:
            return f"necesitas un 5 para sacar {ficha} de la carcel."
        if puede_colocar(ficha, ficha.jugador.salida):
            ficha.estado = ficha.jugador.salida
            posiciones_de_tablero[ficha.jugador.salida].append(ficha)
            ficha.jugador.ultima_ficha_movida = ficha
            return f"{ficha} sale de la carcel a la casilla {ficha.jugador.salida + 1}."
        else:
            return f"la salida de {ficha.jugador.nombre} esta bloqueada."
    
    if isinstance(ficha.estado, int):
        actual = ficha.estado
        hogar = ficha.jugador.entrada_hogar
        if hogar >= actual:
            d = hogar - actual
        else:
            d = (NUM_CASILLAS_EXTERNAS - actual) + hogar
        
        if pasos == d:
            valido, bloqueado = verificar_camino(actual, pasos)
            if not valido:
                return "movimiento no permitido: camino bloqueado por un bloqueo de dos fichas."
            if ficha in posiciones_de_tablero[actual]:
                posiciones_de_tablero[actual].remove(ficha)
            ficha.estado = ("interna", 0)
            ficha.jugador.movimientos_extra += 10
            ficha.jugador.ultima_ficha_movida = ficha
            return f"{ficha} entra a la via interna."
        elif pasos > d:
            return "movimiento no permitido: se requiere exactitud para entrar a la via interna."
        else:
            nuevo = (actual + pasos) % NUM_CASILLAS_EXTERNAS
            valido, bloqueado = verificar_camino(actual, pasos)
            if not valido:
                return "movimiento no permitido: camino bloqueado por un bloqueo de dos fichas."
            
            if posiciones_de_tablero[nuevo]:
                ocupante = posiciones_de_tablero[nuevo][0]
                if ocupante.jugador != ficha.jugador and nuevo not in casillas_seguras:
                    if ocupante in posiciones_de_tablero[nuevo]:
                        posiciones_de_tablero[nuevo].remove(ocupante)
                    ocupante.estado = "carcel"
                    ficha.jugador.capturas_realizadas += 1
                    if ficha in posiciones_de_tablero[actual]:
                        posiciones_de_tablero[actual].remove(ficha)
                    posiciones_de_tablero[nuevo].append(ficha)
                    ficha.estado = nuevo
                    
                    bonus = 20
                    bonus_dest = (nuevo + bonus) % NUM_CASILLAS_EXTERNAS
                    valido_bonus, bloqueado_bonus = verificar_camino(nuevo, bonus)
                    if not valido_bonus:
                        return "movimiento bonus no permitido: camino bloqueado por un bloqueo de dos fichas."
                    if not puede_colocar(ficha, bonus_dest):
                        return "movimiento bonus no permitido: casilla destino bloqueada."
                    if ficha in posiciones_de_tablero[nuevo]:
                        posiciones_de_tablero[nuevo].remove(ficha)
                    posiciones_de_tablero[bonus_dest].append(ficha)
                    ficha.estado = bonus_dest
                    ficha.jugador.ultima_ficha_movida = ficha
                    return f"{ficha} captura a {ocupante} y se mueve 20 casillas adicionales a la casilla {bonus_dest + 1}."
            
            if ficha in posiciones_de_tablero[actual]:
                posiciones_de_tablero[actual].remove(ficha)
            posiciones_de_tablero[nuevo].append(ficha)
            ficha.estado = nuevo
            ficha.jugador.ultima_ficha_movida = ficha
            return f"{ficha} se mueve de la casilla {actual + 1} a {nuevo + 1}."
    
    if isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
        indice = ficha.estado[1]
        nuevo_indice = indice + pasos
        if nuevo_indice >= NUM_CASILLAS_INTERNAS:
            return "movimiento no valido en la via interna (requiere exactitud)."
        ficha.estado = ("interna", nuevo_indice)
        ficha.jugador.ultima_ficha_movida = ficha
        if nuevo_indice == NUM_CASILLAS_INTERNAS - 1:
            ficha.jugador.movimientos_extra += 10
            ficha.jugador.fichas_en_meta += 1
            return f"{ficha} ha llegado a la meta."
        return f"{ficha} avanza en la via interna a la casilla {nuevo_indice + 1}."
    
    return "movimiento desconocido."

def verificar_ganador():
    for jugador in jugadores:
        if jugador.todas_llegaron():
            return jugador
    return None

def reiniciar_juego():
    global posiciones_de_tablero
    posiciones_de_tablero = {i: [] for i in range(NUM_CASILLAS_EXTERNAS)}
    
    for jugador in jugadores:
        for ficha in jugador.fichas:
            ficha.estado = "carcel"
        jugador.contador_dobles = 0
        jugador.movimientos_extra = 0
        jugador.ultima_ficha_movida = None
        jugador.tiempo_turno = 0
        jugador.movimientos_realizados = 0
        jugador.capturas_realizadas = 0
        jugador.fichas_en_meta = 0

def obtener_fichas_disponibles(jugador, valor_dado):
    fichas_validas = []
    for ficha in jugador.fichas:
        if ficha.estado == "carcel" and valor_dado == 5:
            fichas_validas.append(ficha)
        elif isinstance(ficha.estado, int):
            fichas_validas.append(ficha)
        elif isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
            if ficha.estado[1] + valor_dado < NUM_CASILLAS_INTERNAS:
                fichas_validas.append(ficha)
    return fichas_validas

def calcular_distancia_a_meta(ficha):
    if ficha.estado == "carcel":
        return float('inf')
    elif isinstance(ficha.estado, int):
        actual = ficha.estado
        hogar = ficha.jugador.entrada_hogar
        if hogar >= actual:
            d = hogar - actual
        else:
            d = (NUM_CASILLAS_EXTERNAS - actual) + hogar
        return d + NUM_CASILLAS_INTERNAS
    elif isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
        return NUM_CASILLAS_INTERNAS - 1 - ficha.estado[1]
    return float('inf')

class InterfazParques:
    def __init__(self, maestro):
        self.maestro = maestro
        self.maestro.title("Parques Tradicional - Juego Clasico")
        self.maestro.geometry("800x700")
        
        self.canvas = tk.Canvas(maestro, width=TAMANO_TABLERO, height=TAMANO_TABLERO, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=6)
        
        self.etiqueta_info = tk.Label(maestro, text="", font=("Arial", 12), wraplength=700)
        self.etiqueta_info.grid(row=1, column=0, columnspan=6)
        
        self.etiqueta_estado = tk.Label(maestro, text="", font=("Arial", 10), fg="blue", wraplength=700)
        self.etiqueta_estado.grid(row=2, column=0, columnspan=6)
        
        marco_controles = tk.Frame(maestro)
        marco_controles.grid(row=3, column=0, columnspan=6, pady=10)
        
        self.boton_lanzar = tk.Button(marco_controles, text="Lanzar Dados", command=self.lanzar_dados, font=("Arial", 10))
        self.boton_lanzar.grid(row=0, column=0, padx=5)
        
        self.marco_dados = tk.Frame(marco_controles)
        self.marco_dados.grid(row=0, column=1, padx=10)
        self.botones_dados = []
        
        self.boton_terminar = tk.Button(marco_controles, text="Terminar Turno", command=self.terminar_turno, font=("Arial", 10))
        self.boton_terminar.grid(row=0, column=2, padx=5)
        
        self.boton_estadisticas = tk.Button(marco_controles, text="Ver Estadisticas", command=self.mostrar_estadisticas, font=("Arial", 10))
        self.boton_estadisticas.grid(row=0, column=3, padx=5)
        
        self.boton_ayuda = tk.Button(marco_controles, text="Ayuda", command=self.mostrar_ayuda, font=("Arial", 10))
        self.boton_ayuda.grid(row=0, column=4, padx=5)
        
        self.boton_reiniciar = tk.Button(marco_controles, text="Nuevo Juego", command=self.nuevo_juego, font=("Arial", 10))
        self.boton_reiniciar.grid(row=0, column=5, padx=5)
        
        marco_progreso = tk.Frame(maestro)
        marco_progreso.grid(row=4, column=0, columnspan=6, pady=5)
        
        tk.Label(marco_progreso, text="Progreso de jugadores:", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=4)
        
        self.barras_progreso = {}
        for i, jugador in enumerate(jugadores):
            tk.Label(marco_progreso, text=f"{jugador.nombre}:", fg=jugador.color, font=("Arial", 9)).grid(row=1+i, column=0, sticky="w")
            self.barras_progreso[jugador.nombre] = ttk.Progressbar(marco_progreso, length=150, mode='determinate')
            self.barras_progreso[jugador.nombre].grid(row=1+i, column=1, padx=5)
        
        self.indice_jugador_actual = 0
        self.valores_dados = []
        self.ficha_seleccionada = None
        self.ultimo_doble = False
        self.historial_movimientos = []
        self.inicio_turno = time.time()
        
        self.dibujar_tablero()
        self.actualizar_info()
        self.actualizar_barras_progreso()
        
        self.canvas.bind("<Button-1>", self.al_hacer_click_en_canvas)
        self.canvas.bind("<Motion>", self.mostrar_info_casilla)
    
    def dibujar_tablero(self):
        self.canvas.delete("all")
        self.dibujar_layout_basico()
        self.dibujar_casillas_externas()
        self.dibujar_vias_internas()
        self.dibujar_fichas_externas()
        self.dibujar_fichas_internas()
        self.dibujar_fichas_carcel()
    
    def dibujar_layout_basico(self):
        self.canvas.create_rectangle(MARGEN, MARGEN, TAMANO_TABLERO - MARGEN, TAMANO_TABLERO - MARGEN, width=2)
        centro = TAMANO_TABLERO // 2
        self.canvas.create_line(centro, MARGEN, centro, TAMANO_TABLERO - MARGEN, width=2)
        self.canvas.create_line(MARGEN, centro, TAMANO_TABLERO - MARGEN, centro, width=2)
        
        tam_centro = 100
        c1x = centro - tam_centro // 2
        c1y = centro - tam_centro // 2
        c2x = centro + tam_centro // 2
        c2y = centro + tam_centro // 2
        self.canvas.create_rectangle(c1x, c1y, c2x, c2y, width=2)
        self.canvas.create_line(c1x, c1y, c2x, c2y, width=2)
        self.canvas.create_line(c2x, c1y, c1x, c2y, width=2)
        
        def dibujar_lineas_cuadrante(x1, y1, x2, y2, div=6):
            w = x2 - x1
            h = y2 - y1
            dx = w / div
            dy = h / div
            for i in range(1, div):
                self.canvas.create_line(x1 + i * dx, y1, x1 + i * dx, y2)
            for i in range(1, div):
                self.canvas.create_line(x1, y1 + i * dy, x2, y1 + i * dy)
        
        dibujar_lineas_cuadrante(MARGEN, MARGEN, centro, centro)
        dibujar_lineas_cuadrante(centro, MARGEN, TAMANO_TABLERO - MARGEN, centro)
        dibujar_lineas_cuadrante(MARGEN, centro, centro, TAMANO_TABLERO - MARGEN)
        dibujar_lineas_cuadrante(centro, centro, TAMANO_TABLERO - MARGEN, TAMANO_TABLERO - MARGEN)
    
    def dibujar_casillas_externas(self):
        for pos, (cx, cy) in coordenadas_del_tablero_externo.items():
            x1 = cx - 15
            y1 = cy - 15
            x2 = cx + 15
            y2 = cy + 15
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgray")
            num_casilla = pos + 1
            
            colores_salida = {68: "red", 18: "blue", 35: "green", 52: "yellow"}
            if num_casilla in colores_salida:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colores_salida[num_casilla], outline="black")
            else:
                if pos in casillas_seguras and num_casilla not in {17, 35, 51}:
                    self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="yellow")
                self.canvas.create_text(cx, cy, text=str(num_casilla), font=("Arial", 8))
    
    def dibujar_vias_internas(self):
        for j in jugadores:
            lista_coords = coordenadas_de_la_via_interna[j.nombre]
            for i, (cx, cy) in enumerate(lista_coords):
                x1 = cx - 15
                y1 = cy - 15
                x2 = cx + 15
                y2 = cy + 15
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                self.canvas.create_text(cx, cy, text=str(i + 1), font=("Arial", 8))
    
    def actualizar_info(self, msg=""):
        actual = jugadores[self.indice_jugador_actual]
        texto = f"Turno de: {actual.nombre} ({actual.color}). "
        if self.valores_dados:
            texto += "Dados: " + ", ".join(str(v) for v in self.valores_dados)
        else:
            texto += "Sin dados. Lanza para continuar."
        
        if actual.movimientos_extra > 0:
            texto += f" | Movimientos Extra: {actual.movimientos_extra}"
        
        fichas_disponibles = obtener_fichas_disponibles(actual, max(self.valores_dados) if self.valores_dados else 0)
        if self.valores_dados and not fichas_disponibles:
            texto += " | Sin movimientos validos disponibles"
        
        self.etiqueta_info.config(text=texto)
        self.etiqueta_estado.config(text=msg)
    
    def dibujar_fichas_externas(self):
        for pos, fichas in posiciones_de_tablero.items():
            if fichas:
                for i, ficha in enumerate(fichas):
                    cx, cy = coordenadas_del_tablero_externo[pos]
                    px = cx + (i * 5) - 5
                    py = cy - 5
                    r = 10
                    ancho_contorno = 3 if ficha == self.ficha_seleccionada else 1
                    self.canvas.create_oval(px - r, py - r, px + r, py + r,
                                          fill=ficha.jugador.color, outline="black", width=ancho_contorno)
    
    def dibujar_fichas_internas(self):
        for j in jugadores:
            for ficha in j.fichas:
                if isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
                    indice = ficha.estado[1]
                    cx, cy = coordenadas_de_la_via_interna[j.nombre][indice]
                    r = 10
                    ancho_contorno = 3 if ficha == self.ficha_seleccionada else 1
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                          fill=j.color, outline="black", width=ancho_contorno)
    
    def dibujar_fichas_carcel(self):
        for j in jugadores:
            pos_carcel = posiciones_de_la_carcel[j.nombre]
            self.canvas.create_text(pos_carcel["x"], pos_carcel["y"] - 20,
                                  text=f"Carcel {j.nombre}",
                                  fill=j.color,
                                  font=("Arial", 10, "bold"))
            cont = 0
            for ficha in j.fichas:
                if ficha.estado == "carcel":
                    px = pos_carcel["x"]
                    py = pos_carcel["y"] + cont * pos_carcel["offset_y"]
                    r = 10
                    ancho_contorno = 3 if ficha == self.ficha_seleccionada else 1
                    puntos = [
                        (px, py - r),
                        (px - r, py),
                        (px, py + r),
                        (px + r, py)
                    ]
                    self.canvas.create_polygon(puntos, fill=j.color, outline="black", width=ancho_contorno)
                    cont += 1
    
    def actualizar_barras_progreso(self):
        for jugador in jugadores:
            progreso = 0
            for ficha in jugador.fichas:
                if isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
                    if ficha.estado[1] == NUM_CASILLAS_INTERNAS - 1:
                        progreso += 25
                    else:
                        progreso += 15 + (ficha.estado[1] * 2)
                elif isinstance(ficha.estado, int):
                    progreso += 5
            self.barras_progreso[jugador.nombre]['value'] = min(progreso, 100)
    
    def mostrar_info_casilla(self, event):
        info = ""
        for pos, (cx, cy) in coordenadas_del_tablero_externo.items():
            if (cx - 15) <= event.x <= (cx + 15) and (cy - 15) <= event.y <= (cy + 15):
                if posiciones_de_tablero[pos]:
                    fichas_en_casilla = [f"{f.jugador.nombre}{f.id_ficha}" for f in posiciones_de_tablero[pos]]
                    info = f"Casilla {pos + 1}: {', '.join(fichas_en_casilla)}"
                else:
                    info = f"Casilla {pos + 1}: Vacia"
                break
        
        if info and hasattr(self, 'tooltip'):
            self.canvas.delete(self.tooltip)
        if info:
            self.tooltip = self.canvas.create_text(event.x + 10, event.y - 10, text=info, 
                                                 fill="black", font=("Arial", 8), anchor="w")
    
    def mostrar_estadisticas(self):
        ventana_stats = tk.Toplevel(self.maestro)
        ventana_stats.title("Estadisticas del Juego")
        ventana_stats.geometry("400x300")
        
        tk.Label(ventana_stats, text="Estadisticas de Jugadores", font=("Arial", 14, "bold")).pack(pady=10)
        
        frame_stats = tk.Frame(ventana_stats)
        frame_stats.pack(fill="both", expand=True, padx=20)
        
        for i, jugador in enumerate(jugadores):
            stats = jugador.obtener_estadisticas()
            frame_jugador = tk.Frame(frame_stats, relief="ridge", borderwidth=2)
            frame_jugador.pack(fill="x", pady=5)
            
            tk.Label(frame_jugador, text=f"{jugador.nombre}", font=("Arial", 12, "bold"), fg=jugador.color).pack()
            tk.Label(frame_jugador, text=f"Movimientos realizados: {stats['movimientos']}").pack()
            tk.Label(frame_jugador, text=f"Capturas realizadas: {stats['capturas']}").pack()
            tk.Label(frame_jugador, text=f"Fichas en meta: {stats['fichas_en_meta']}/4").pack()
            tk.Label(frame_jugador, text=f"Movimientos extra disponibles: {stats['movimientos_extra']}").pack()
    
    def mostrar_ayuda(self):
        ventana_ayuda = tk.Toplevel(self.maestro)
        ventana_ayuda.title("Como Jugar Parques")
        ventana_ayuda.geometry("500x400")
        
        texto_ayuda = tk.Text(ventana_ayuda, wrap=tk.WORD, padx=10, pady=10)
        scrollbar = tk.Scrollbar(ventana_ayuda, command=texto_ayuda.yview)
        texto_ayuda.config(yscrollcommand=scrollbar.set)
        
        ayuda_contenido = """
REGLAS DEL JUEGO DE PARQUES

OBJETIVO:
Ser el primer jugador en llevar todas sus 4 fichas a la meta.

COMO JUGAR:
1. Para sacar una ficha de la carcel necesitas sacar un 5 en los dados.
2. Mueves tus fichas por el tablero exterior segun los valores de los dados.
3. Cuando llegues a tu casilla de entrada (del color de tu jugador), puedes entrar a la via interna.
4. En la via interna debes llegar exactamente a la ultima casilla (meta).

REGLAS ESPECIALES:
- Si sacas dobles (mismos numeros en ambos dados), juegas otra vez.
- Si sacas 3 dobles consecutivos, tu ultima ficha movida regresa a la carcel.
- Si capturas una ficha enemiga (excepto en casillas seguras), avanzas 20 casillas adicionales.
- Las casillas de salida son seguras, no se puede capturar alli.
- Al llegar a la meta ganas movimientos extra.

CONTROLES:
- Haz clic en "Lanzar Dados" para tirar los dados.
- Haz clic en una de tus fichas para seleccionarla.
- Haz clic en un boton de dado para mover la ficha seleccionada.
- Usa "Terminar Turno" cuando no quieras usar mas dados.

ESTRATEGIAS:
- Trata de formar bloqueos con dos fichas tuyas en la misma casilla.
- Usa los movimientos extra sabiamente.
- Protege tus fichas cerca de la meta.
"""
        
        texto_ayuda.insert(tk.END, ayuda_contenido)
        texto_ayuda.config(state=tk.DISABLED)
        
        texto_ayuda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def nuevo_juego(self):
        respuesta = messagebox.askyesno("Nuevo Juego", "¿Estas seguro de que quieres iniciar un nuevo juego?")
        if respuesta:
            reiniciar_juego()
            self.indice_jugador_actual = 0
            self.valores_dados = []
            self.ficha_seleccionada = None
            self.ultimo_doble = False
            self.historial_movimientos = []
            self.inicio_turno = time.time()
            
            for boton in self.botones_dados:
                boton.destroy()
            self.botones_dados = []
            
            self.dibujar_tablero()
            self.actualizar_info()
            self.actualizar_barras_progreso()
    
    def verificar_fin_juego(self):
        ganador = verificar_ganador()
        if ganador:
            tiempo_total = time.time() - self.inicio_turno
            mensaje = f"¡Felicidades {ganador.nombre}!\n\nHas ganado el juego.\n"
            mensaje += f"Estadisticas finales:\n"
            mensaje += f"Movimientos realizados: {ganador.movimientos_realizados}\n"
            mensaje += f"Capturas realizadas: {ganador.capturas_realizadas}\n"
            mensaje += f"Tiempo de juego: {int(tiempo_total//60)}:{int(tiempo_total%60):02d}"
            
            messagebox.showinfo("¡Juego Terminado!", mensaje)
            return True
        return False
    
    def lanzar_dados(self):
        actual = jugadores[self.indice_jugador_actual]
        if actual.movimientos_extra > 0:
            self.solicitar_movimientos_extra()
            return
        
        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        self.ultimo_doble = (d1 == d2)
        
        if d1 == d2:
            actual.contador_dobles += 1
        else:
            actual.contador_dobles = 0

        if actual.contador_dobles == 3:
            self.aplicar_penalizacion_tres_dobles(actual)
            return

        self.valores_dados = [d1, d2]
        self.dibujar_botones_dados()
        self.actualizar_info()
    
    def aplicar_penalizacion_tres_dobles(self, actual):
        if actual.ultima_ficha_movida is None:
            if self.ficha_seleccionada is not None:
                actual.ultima_ficha_movida = self.ficha_seleccionada
            else:
                for f in actual.fichas:
                    if f.estado != "carcel":
                        actual.ultima_ficha_movida = f
                        break
                if actual.ultima_ficha_movida is None:
                    actual.ultima_ficha_movida = actual.fichas[0]
        
        ficha_a_carcel = actual.ultima_ficha_movida
        if isinstance(ficha_a_carcel.estado, int):
            pos = ficha_a_carcel.estado
            if ficha_a_carcel in posiciones_de_tablero[pos]:
                posiciones_de_tablero[pos].remove(ficha_a_carcel)
        ficha_a_carcel.estado = "carcel"
        self.actualizar_info("Tres dobles consecutivos: la ficha " + str(ficha_a_carcel) + " regresa a la carcel.")
        actual.contador_dobles = 0
        self.dibujar_tablero()
    
    def solicitar_movimientos_extra(self):
        actual = jugadores[self.indice_jugador_actual]
        ventana_extra = tk.Toplevel(self.maestro)
        ventana_extra.title("Usar Movimientos Extra")
        tk.Label(ventana_extra, text=f"Tienes {actual.movimientos_extra} movimientos extra.\nIngresa la cantidad a usar:").pack(padx=10, pady=10)
        entrada = tk.Entry(ventana_extra)
        entrada.pack(padx=10, pady=10)
        
        def confirmar():
            try:
                val = int(entrada.get())
            except:
                val = 0
            if val < 1 or val > actual.movimientos_extra:
                self.actualizar_info("Cantidad invalida para movimientos extra.")
            else:
                if self.ficha_seleccionada is None:
                    self.actualizar_info("Debes seleccionar una ficha para usar movimientos extra.")
                else:
                    resultado = mover_ficha(self.ficha_seleccionada, val)
                    actual.movimientos_extra -= val
                    self.valores_dados = []
                    self.ficha_seleccionada = None
                    self.actualizar_info(resultado)
                    self.dibujar_tablero()
            ventana_extra.destroy()
        
        tk.Button(ventana_extra, text="Aceptar", command=confirmar).pack(padx=10, pady=10)
    
    def dibujar_botones_dados(self):
        for b in self.botones_dados:
            b.destroy()
        self.botones_dados = []
        for val in self.valores_dados:
            btn = tk.Button(self.marco_dados, text=str(val), command=lambda v=val: self.usar_dado(v))
            btn.pack(side="left", padx=5)
            self.botones_dados.append(btn)
    
    def usar_dado(self, val):
        if self.ficha_seleccionada is None:
            self.actualizar_info("Primero selecciona una ficha.")
            return
        
        resultado = mover_ficha(self.ficha_seleccionada, val)
        self.historial_movimientos.append(f"{self.ficha_seleccionada}: {resultado}")
        jugadores[self.indice_jugador_actual].ultima_ficha_movida = self.ficha_seleccionada
        self.valores_dados.remove(val)
        self.ficha_seleccionada = None
        self.actualizar_info(resultado)
        self.dibujar_tablero()
        self.actualizar_barras_progreso()
        
        if self.verificar_fin_juego():
            return
        
        if not self.valores_dados:
            self.terminar_turno()
    
    def terminar_turno(self):
        self.valores_dados = []
        self.ficha_seleccionada = None
        actual = jugadores[self.indice_jugador_actual]
        
        if not self.ultimo_doble:
            actual.contador_dobles = 0
            self.indice_jugador_actual = (self.indice_jugador_actual + 1) % len(jugadores)
        else:
            self.ultimo_doble = False
        
        self.actualizar_info()
        self.actualizar_barras_progreso()
        self.dibujar_tablero()
        for b in self.botones_dados:
            b.destroy()
        self.botones_dados = []
    
    def al_hacer_click_en_canvas(self, event):
        actual = jugadores[self.indice_jugador_actual]
        ficha_click = None
        
        ficha_click = self.buscar_ficha_en_casillas_externas(event, actual)
        
        if not ficha_click:
            ficha_click = self.buscar_ficha_en_vias_internas(event, actual)
        
        if not ficha_click:
            ficha_click = self.buscar_ficha_en_carcel(event, actual)
        
        if ficha_click:
            self.ficha_seleccionada = ficha_click
            self.actualizar_info(f"Seleccionada {ficha_click}")
            self.dibujar_tablero()
        else:
            self.actualizar_info("No hay ficha tuya en esa posicion.")
    
    def buscar_ficha_en_casillas_externas(self, event, actual):
        for pos, (cx, cy) in coordenadas_del_tablero_externo.items():
            if (cx - 15) <= event.x <= (cx + 15) and (cy - 15) <= event.y <= (cy + 15):
                if posiciones_de_tablero[pos]:
                    for f in posiciones_de_tablero[pos]:
                        if f.jugador == actual:
                            return f
        return None
    
    def buscar_ficha_en_vias_internas(self, event, actual):
        lista_coords = coordenadas_de_la_via_interna[actual.nombre]
        for idx, (cx, cy) in enumerate(lista_coords):
            if (cx - 15) <= event.x <= (cx + 15) and (cy - 15) <= event.y <= (cy + 15):
                for f in actual.fichas:
                    if f.estado == ("interna", idx):
                        return f
        return None
    
    def buscar_ficha_en_carcel(self, event, actual):
        for j in jugadores:
            info_carcel = posiciones_de_la_carcel[j.nombre]
            x_carcel = info_carcel["x"]
            y_carcel = info_carcel["y"]
            offset = info_carcel["offset_y"]
            cont = 0
            for f in j.fichas:
                if f.estado == "carcel":
                    px = x_carcel
                    py = y_carcel + cont * offset
                    cont += 1
                    if (event.x >= px - 15 and event.x <= px + 15 and
                        event.y >= py - 15 and event.y <= py + 15):
                        if f.jugador == actual:
                            return f
        return None

def main():
    raiz = tk.Tk()
    app = InterfazParques(raiz)
    raiz.mainloop()

if __name__ == "__main__":
    main()