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
    Jugador("Rojo", COLORES_JUGADORES['Rojo']['principal'], salida=0, entrada_hogar=67),
    Jugador("Azul", COLORES_JUGADORES['Azul']['principal'], salida=17, entrada_hogar=16),
    Jugador("Verde", COLORES_JUGADORES['Verde']['principal'], salida=34, entrada_hogar=33),
    Jugador("Amarillo", COLORES_JUGADORES['Amarillo']['principal'], salida=51, entrada_hogar=50),
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
        self.maestro.title("🎲 Parques Tradicional - Juego Clásico 🏆")
        self.maestro.geometry("850x750")
        self.maestro.configure(bg=COLORES['fondo_principal'])
        self.maestro.resizable(False, False)
        
        # Configurar estilo para ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Crear frame principal con diseño mejorado
        frame_principal = tk.Frame(maestro, bg=COLORES['fondo_principal'], padx=10, pady=10)
        frame_principal.pack(fill='both', expand=True)
        
        # Título del juego
        titulo = tk.Label(frame_principal, 
                         text="🎲 PARQUES TRADICIONAL 🎲", 
                         font=("Arial", 16, "bold"),
                         bg=COLORES['fondo_principal'], 
                         fg='white')
        titulo.pack(pady=(0, 10))
        
        # Canvas con borde decorativo
        canvas_frame = tk.Frame(frame_principal, bg=COLORES['borde_tablero'], padx=3, pady=3)
        canvas_frame.pack()
        
        self.canvas = tk.Canvas(canvas_frame, 
                               width=TAMANO_TABLERO, 
                               height=TAMANO_TABLERO, 
                               bg=COLORES['fondo_tablero'],
                               highlightthickness=0)
        self.canvas.pack()
        
        # Panel de información mejorado
        info_frame = tk.Frame(frame_principal, bg=COLORES['fondo_principal'])
        info_frame.pack(fill='x', pady=10)
        
        self.etiqueta_info = tk.Label(info_frame, 
                                    text="", 
                                    font=("Arial", 11, "bold"),
                                    bg=COLORES['fondo_principal'], 
                                    fg='white',
                                    wraplength=800)
        self.etiqueta_info.pack()
        
        self.etiqueta_estado = tk.Label(info_frame, 
                                      text="", 
                                      font=("Arial", 10),
                                      bg=COLORES['fondo_principal'], 
                                      fg=COLORES['texto_secundario'],
                                      wraplength=800)
        self.etiqueta_estado.pack()
        
        # Panel de controles con diseño mejorado
        self.crear_panel_controles(frame_principal)
        
        # Panel de progreso mejorado
        self.crear_panel_progreso(frame_principal)
        
        # Variables de juego
        self.indice_jugador_actual = 0
        self.valores_dados = []
        self.ficha_seleccionada = None
        self.ultimo_doble = False
        self.historial_movimientos = []
        self.inicio_turno = time.time()
        self.efectos_animacion = []
        
        self.dibujar_tablero()
        self.actualizar_info()
        self.actualizar_barras_progreso()
        
        self.canvas.bind("<Button-1>", self.al_hacer_click_en_canvas)
        self.canvas.bind("<Motion>", self.mostrar_info_casilla)
        self.canvas.bind("<Leave>", self.limpiar_tooltip)
    
    def crear_panel_controles(self, parent):
        controles_frame = tk.Frame(parent, bg=COLORES['fondo_principal'])
        controles_frame.pack(pady=10)
        
        # Frame para botones principales
        botones_principales = tk.Frame(controles_frame, bg=COLORES['fondo_principal'])
        botones_principales.pack()
        
        # Estilo personalizado para botones
        botones_config = {
            'font': ("Arial", 10, "bold"),
            'pady': 8,
            'padx': 15,
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        self.boton_lanzar = tk.Button(botones_principales, 
                                    text="🎲 Lanzar Dados", 
                                    command=self.lanzar_dados,
                                    bg=COLORES['boton_activo'],
                                    fg='white',
                                    **botones_config)
        self.boton_lanzar.grid(row=0, column=0, padx=5)
        
        # Frame para dados con mejor diseño
        self.marco_dados = tk.Frame(botones_principales, bg=COLORES['fondo_principal'])
        self.marco_dados.grid(row=0, column=1, padx=20)
        self.botones_dados = []
        
        self.boton_terminar = tk.Button(botones_principales, 
                                      text="⏭️ Terminar Turno", 
                                      command=self.terminar_turno,
                                      bg=COLORES['texto_secundario'],
                                      fg='white',
                                      **botones_config)
        self.boton_terminar.grid(row=0, column=2, padx=5)
        
        # Frame para botones secundarios
        botones_secundarios = tk.Frame(controles_frame, bg=COLORES['fondo_principal'])
        botones_secundarios.pack(pady=(10, 0))
        
        botones_secundarios_config = {
            'font': ("Arial", 9),
            'pady': 5,
            'padx': 10,
            'relief': 'flat',
            'cursor': 'hand2'
        }
        
        self.boton_estadisticas = tk.Button(botones_secundarios, 
                                          text="📊 Estadísticas", 
                                          command=self.mostrar_estadisticas,
                                          bg='#9B59B6',
                                          fg='white',
                                          **botones_secundarios_config)
        self.boton_estadisticas.grid(row=0, column=0, padx=5)
        
        self.boton_ayuda = tk.Button(botones_secundarios, 
                                   text="❓ Ayuda", 
                                   command=self.mostrar_ayuda,
                                   bg='#16A085',
                                   fg='white',
                                   **botones_secundarios_config)
        self.boton_ayuda.grid(row=0, column=1, padx=5)
        
        self.boton_reiniciar = tk.Button(botones_secundarios, 
                                       text="🔄 Nuevo Juego", 
                                       command=self.nuevo_juego,
                                       bg='#E67E22',
                                       fg='white',
                                       **botones_secundarios_config)
        self.boton_reiniciar.grid(row=0, column=2, padx=5)
    
    def crear_panel_progreso(self, parent):
        progreso_frame = tk.Frame(parent, bg=COLORES['fondo_principal'], padx=10, pady=10)
        progreso_frame.pack(fill='x')
        
        # Título del progreso
        tk.Label(progreso_frame, 
                text="📈 Progreso de Jugadores", 
                font=("Arial", 12, "bold"),
                bg=COLORES['fondo_principal'],
                fg='white').pack()
        
        # Frame para las barras de progreso
        barras_frame = tk.Frame(progreso_frame, bg=COLORES['fondo_principal'])
        barras_frame.pack(fill='x', pady=10)
        
        self.barras_progreso = {}
        
        for i, jugador in enumerate(jugadores):
            # Frame individual para cada jugador
            jugador_frame = tk.Frame(barras_frame, bg=COLORES['fondo_principal'])
            jugador_frame.pack(fill='x', pady=2)
            
            # Etiqueta del jugador con mejor diseño
            etiqueta_jugador = tk.Label(jugador_frame, 
                                      text=f"🎯 {jugador.nombre}:",
                                      fg=jugador.color,
                                      bg=COLORES['fondo_principal'],
                                      font=("Arial", 10, "bold"),
                                      width=12,
                                      anchor='w')
            etiqueta_jugador.pack(side='left', padx=(0, 10))
            
            # Barra de progreso personalizada
            self.barras_progreso[jugador.nombre] = ttk.Progressbar(
                jugador_frame, 
                length=200, 
                mode='determinate',
                style='Horizontal.TProgressbar'
            )
            self.barras_progreso[jugador.nombre].pack(side='left', fill='x', expand=True)
            
            # Etiqueta de porcentaje
            self.crear_etiqueta_porcentaje(jugador_frame, jugador.nombre)
    
    def crear_etiqueta_porcentaje(self, parent, nombre_jugador):
        etiqueta_porcentaje = tk.Label(parent, 
                                     text="0%",
                                     fg='white',
                                     bg=COLORES['fondo_principal'],
                                     font=("Arial", 9),
                                     width=5)
        etiqueta_porcentaje.pack(side='right', padx=(10, 0))
        return etiqueta_porcentaje
    
    def dibujar_tablero(self):
        self.canvas.delete("all")
        self.dibujar_fondo_con_gradiente()
        self.dibujar_layout_mejorado()
        self.dibujar_casillas_externas_mejoradas()
        self.dibujar_vias_internas_mejoradas()
        self.dibujar_fichas_externas_mejoradas()
        self.dibujar_fichas_internas_mejoradas()
        self.dibujar_fichas_carcel_mejoradas()
        self.agregar_decoraciones()
    
    def dibujar_fondo_con_gradiente(self):
        # Crear efecto de gradiente sutil
        for i in range(TAMANO_TABLERO):
            color_intensidad = int(240 + (i / TAMANO_TABLERO) * 15)
            color_hex = f"#{color_intensidad:02x}{color_intensidad:02x}{color_intensidad:02x}"
            if i % 10 == 0:  # Solo cada 10 líneas para optimizar
                self.canvas.create_line(0, i, TAMANO_TABLERO, i, fill=color_hex, width=1)
    
    def dibujar_layout_mejorado(self):
        # Borde principal con gradiente
        self.canvas.create_rectangle(MARGEN-2, MARGEN-2, 
                                   TAMANO_TABLERO - MARGEN+2, TAMANO_TABLERO - MARGEN+2, 
                                   fill=COLORES['borde_tablero'], outline=COLORES['borde_tablero'], width=3)
        
        self.canvas.create_rectangle(MARGEN, MARGEN, 
                                   TAMANO_TABLERO - MARGEN, TAMANO_TABLERO - MARGEN, 
                                   fill=COLORES['fondo_tablero'], outline=COLORES['borde_tablero'], width=2)
        
        centro = TAMANO_TABLERO // 2
        
        # Líneas divisorias con mejor estilo
        self.canvas.create_line(centro, MARGEN, centro, TAMANO_TABLERO - MARGEN, 
                               fill=COLORES['borde_tablero'], width=3)
        self.canvas.create_line(MARGEN, centro, TAMANO_TABLERO - MARGEN, centro, 
                               fill=COLORES['borde_tablero'], width=3)
        
        # Centro del tablero con efecto 3D
        tam_centro = 120
        c1x = centro - tam_centro // 2
        c1y = centro - tam_centro // 2
        c2x = centro + tam_centro // 2
        c2y = centro + tam_centro // 2
        
        # Sombra del centro
        self.canvas.create_rectangle(c1x+3, c1y+3, c2x+3, c2y+3, 
                                   fill='#BDC3C7', outline='', width=0)
        
        # Centro principal
        self.canvas.create_rectangle(c1x, c1y, c2x, c2y, 
                                   fill=COLORES['centro_tablero'], 
                                   outline=COLORES['borde_tablero'], width=2)
        
        # Diagonales del centro con estilo
        self.canvas.create_line(c1x, c1y, c2x, c2y, 
                               fill=COLORES['borde_tablero'], width=2)
        self.canvas.create_line(c2x, c1y, c1x, c2y, 
                               fill=COLORES['borde_tablero'], width=2)
        
        # Texto central decorativo
        self.canvas.create_text(centro, centro, text="🎲\nPARQUES\n🏆", 
                              fill=COLORES['texto_principal'], font=("Arial", 12, "bold"))
        
        # Líneas decorativas en cuadrantes
        self.dibujar_cuadrantes_decorativos(centro)
    
    def dibujar_cuadrantes_decorativos(self, centro):
        cuadrantes = [
            (MARGEN, MARGEN, centro, centro),               # Superior izquierdo
            (centro, MARGEN, TAMANO_TABLERO - MARGEN, centro),     # Superior derecho  
            (MARGEN, centro, centro, TAMANO_TABLERO - MARGEN),     # Inferior izquierdo
            (centro, centro, TAMANO_TABLERO - MARGEN, TAMANO_TABLERO - MARGEN)  # Inferior derecho
        ]
        
        for x1, y1, x2, y2 in cuadrantes:
            self.dibujar_lineas_cuadrante(x1, y1, x2, y2, div=8)
    
    def dibujar_lineas_cuadrante(self, x1, y1, x2, y2, div=8):
        w = x2 - x1
        h = y2 - y1
        dx = w / div
        dy = h / div
        
        for i in range(1, div):
            # Líneas verticales con opacidad
            self.canvas.create_line(x1 + i * dx, y1, x1 + i * dx, y2, 
                                  fill='#D5D8DC', width=1)
            # Líneas horizontales con opacidad  
            self.canvas.create_line(x1, y1 + i * dy, x2, y1 + i * dy, 
                                  fill='#D5D8DC', width=1)
    
    def dibujar_casillas_externas_mejoradas(self):
        for pos, (cx, cy) in coordenadas_del_tablero_externo.items():
            # Determinar tipo y color de casilla
            num_casilla = pos + 1
            es_salida = pos in casillas_seguras
            
            # Tamaño de casilla
            size = 18
            x1, y1 = cx - size, cy - size
            x2, y2 = cx + size, cy + size
            
            # Sombra de casilla
            self.canvas.create_rectangle(x1+2, y1+2, x2+2, y2+2, 
                                       fill='#AEB6BF', outline='', width=0)
            
            # Colores especiales para casillas de salida
            colores_salida = {68: 'Rojo', 18: 'Azul', 35: 'Verde', 52: 'Amarillo'}
            
            if num_casilla in colores_salida:
                color_jugador = colores_salida[num_casilla]
                color_principal = COLORES_JUGADORES[color_jugador]['principal']
                color_claro = COLORES_JUGADORES[color_jugador]['claro']
                
                # Casilla de salida con gradiente
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                           fill=color_principal, 
                                           outline=COLORES['borde_tablero'], width=2)
                
                # Efecto de brillo
                self.canvas.create_rectangle(x1+3, y1+3, x2-3, y2-3, 
                                           fill=color_claro, 
                                           outline='', width=0)
                
                # Texto de número
                self.canvas.create_text(cx, cy, text=str(num_casilla), 
                                      font=("Arial", 8, "bold"), fill='white')
                
                # Indicador de salida
                self.canvas.create_text(cx, cy-25, text="🏠", font=("Arial", 10))
                
            else:
                # Casilla normal
                if es_salida:
                    fill_color = COLORES['casilla_segura']
                    self.canvas.create_oval(cx - 12, cy - 12, cx + 12, cy + 12, 
                                          fill=fill_color, 
                                          outline=COLORES['borde_tablero'], width=2)
                    
                    # Indicador de seguridad
                    self.canvas.create_text(cx, cy-18, text="🛡️", font=("Arial", 8))
                else:
                    fill_color = COLORES['casilla_normal']
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                               fill=fill_color, 
                                               outline=COLORES['borde_tablero'], width=1)
                
                # Número de casilla
                self.canvas.create_text(cx, cy, text=str(num_casilla), 
                                      font=("Arial", 7), fill=COLORES['texto_principal'])
    
    def dibujar_vias_internas_mejoradas(self):
        for jugador in jugadores:
            color_principal = jugador.color
            color_claro = COLORES_JUGADORES[jugador.nombre]['claro']
            lista_coords = coordenadas_de_la_via_interna[jugador.nombre]
            
            for i, (cx, cy) in enumerate(lista_coords):
                size = 16
                x1, y1 = cx - size, cy - size
                x2, y2 = cx + size, cy + size
                
                # Sombra
                self.canvas.create_rectangle(x1+1, y1+1, x2+1, y2+1, 
                                           fill='#BDC3C7', outline='', width=0)
                
                # Casilla de vía interna con color del jugador
                if i == len(lista_coords) - 1:  # Última casilla (meta)
                    # Meta con efecto especial
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                               fill=color_principal, 
                                               outline='gold', width=3)
                    
                    # Estrella de meta
                    self.canvas.create_text(cx, cy, text="⭐", font=("Arial", 12))
                else:
                    # Casilla normal de vía interna
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                               fill=color_claro, 
                                               outline=color_principal, width=2)
                    
                    self.canvas.create_text(cx, cy, text=str(i + 1), 
                                          font=("Arial", 8, "bold"), 
                                          fill=color_principal)
    
    def actualizar_info(self, msg=""):
        actual = jugadores[self.indice_jugador_actual]
        
        # Texto principal con emojis
        texto = f"🎯 Turno de: {actual.nombre} "
        
        # Indicador visual del color del jugador
        color_jugador = actual.color
        
        if self.valores_dados:
            dados_texto = " ".join([self.obtener_cara_dado(v) for v in self.valores_dados])
            texto += f"| Dados: {dados_texto}"
        else:
            texto += "| 🎲 Lanza los dados para continuar"
        
        if actual.movimientos_extra > 0:
            texto += f" | ⭐ Extras: {actual.movimientos_extra}"
        
        # Verificar fichas disponibles
        fichas_disponibles = obtener_fichas_disponibles(actual, max(self.valores_dados) if self.valores_dados else 0)
        if self.valores_dados and not fichas_disponibles:
            texto += " | ❌ Sin movimientos válidos"
        
        self.etiqueta_info.config(text=texto, fg=color_jugador)
        
        # Mensaje de estado con color
        if msg:
            if "captura" in msg.lower():
                self.etiqueta_estado.config(text=f"⚔️ {msg}", fg='#E74C3C')
            elif "meta" in msg.lower():
                self.etiqueta_estado.config(text=f"🏆 {msg}", fg='#F39C12')
            elif "carcel" in msg.lower():
                self.etiqueta_estado.config(text=f"🏢 {msg}", fg='#9B59B6')
            else:
                self.etiqueta_estado.config(text=f"💭 {msg}", fg='white')
        else:
            self.etiqueta_estado.config(text="")
    
    def dibujar_fichas_externas_mejoradas(self):
        for pos, fichas in posiciones_de_tablero.items():
            if fichas:
                cx, cy = coordenadas_del_tablero_externo[pos]
                for i, ficha in enumerate(fichas):
                    # Posición de la ficha con separación mejorada
                    offset_x = (i * 8) - 4 if len(fichas) > 1 else 0
                    offset_y = -3
                    px = cx + offset_x
                    py = cy + offset_y
                    
                    # Radio y configuración
                    r = 12
                    color_principal = ficha.jugador.color
                    color_claro = COLORES_JUGADORES[ficha.jugador.nombre]['claro']
                    color_oscuro = COLORES_JUGADORES[ficha.jugador.nombre]['oscuro']
                    
                    # Sombra de la ficha
                    self.canvas.create_oval(px - r + 1, py - r + 1, px + r + 1, py + r + 1,
                                          fill='#34495E', outline='', width=0)
                    
                    # Ficha principal con gradiente simulado
                    self.canvas.create_oval(px - r, py - r, px + r, py + r,
                                          fill=color_principal, outline=color_oscuro, width=2)
                    
                    # Brillo interior
                    self.canvas.create_oval(px - r + 4, py - r + 4, px + 4, py + 4,
                                          fill=color_claro, outline='', width=0)
                    
                    # Borde especial si está seleccionada
                    if ficha == self.ficha_seleccionada:
                        # Efecto de selección pulsante
                        self.canvas.create_oval(px - r - 3, py - r - 3, px + r + 3, py + r + 3,
                                              fill='', outline='gold', width=3)
                        self.canvas.create_oval(px - r - 6, py - r - 6, px + r + 6, py + r + 6,
                                              fill='', outline='white', width=2)
                    
                    # Número de ficha
                    self.canvas.create_text(px, py, text=str(ficha.id_ficha + 1),
                                          font=("Arial", 7, "bold"), fill='white')
    
    def dibujar_fichas_internas_mejoradas(self):
        for jugador in jugadores:
            color_principal = jugador.color
            color_claro = COLORES_JUGADORES[jugador.nombre]['claro']
            color_oscuro = COLORES_JUGADORES[jugador.nombre]['oscuro']
            
            for ficha in jugador.fichas:
                if isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
                    indice = ficha.estado[1]
                    cx, cy = coordenadas_de_la_via_interna[jugador.nombre][indice]
                    
                    r = 12
                    
                    # Sombra
                    self.canvas.create_oval(cx - r + 1, cy - r + 1, cx + r + 1, cy + r + 1,
                                          fill='#34495E', outline='', width=0)
                    
                    # Ficha principal
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                          fill=color_principal, outline=color_oscuro, width=2)
                    
                    # Brillo
                    self.canvas.create_oval(cx - r + 3, cy - r + 3, cx + 3, cy + 3,
                                          fill=color_claro, outline='', width=0)
                    
                    # Selección
                    if ficha == self.ficha_seleccionada:
                        self.canvas.create_oval(cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
                                              fill='', outline='gold', width=3)
                    
                    # Si está en la meta, agregar corona
                    if indice == NUM_CASILLAS_INTERNAS - 1:
                        self.canvas.create_text(cx, cy - 20, text="👑", font=("Arial", 12))
                    
                    # Número de ficha
                    self.canvas.create_text(cx, cy, text=str(ficha.id_ficha + 1),
                                          font=("Arial", 7, "bold"), fill='white')
    
    def dibujar_fichas_carcel_mejoradas(self):
        for jugador in jugadores:
            pos_carcel = posiciones_de_la_carcel[jugador.nombre]
            color_principal = jugador.color
            color_claro = COLORES_JUGADORES[jugador.nombre]['claro']
            
            # Título de la cárcel con diseño mejorado
            self.canvas.create_rectangle(pos_carcel["x"]-40, pos_carcel["y"]-35,
                                       pos_carcel["x"]+40, pos_carcel["y"]-15,
                                       fill=color_principal, outline=COLORES['borde_tablero'], width=2)
            
            self.canvas.create_text(pos_carcel["x"], pos_carcel["y"] - 25,
                                  text=f"🏢 {jugador.nombre}",
                                  fill='white',
                                  font=("Arial", 9, "bold"))
            
            cont = 0
            for ficha in jugador.fichas:
                if ficha.estado == "carcel":
                    px = pos_carcel["x"]
                    py = pos_carcel["y"] + cont * pos_carcel["offset_y"]
                    r = 10
                    
                    # Sombra
                    self.canvas.create_polygon([
                        px + 1, py - r + 1,
                        px - r + 1, py + 1,
                        px + 1, py + r + 1,
                        px + r + 1, py + 1
                    ], fill='#34495E', outline='', width=0)
                    
                    # Ficha en forma de rombo (prisión)
                    puntos = [
                        (px, py - r),
                        (px - r, py),
                        (px, py + r),
                        (px + r, py)
                    ]
                    
                    self.canvas.create_polygon(puntos, 
                                             fill=color_principal, 
                                             outline=COLORES['borde_tablero'], width=2)
                    
                    # Brillo interior
                    puntos_brillo = [
                        (px, py - r + 3),
                        (px - r + 3, py),
                        (px, py + r - 3),
                        (px + r - 3, py)
                    ]
                    self.canvas.create_polygon(puntos_brillo, 
                                             fill=color_claro, outline='', width=0)
                    
                    # Selección
                    if ficha == self.ficha_seleccionada:
                        puntos_seleccion = [
                            (px, py - r - 3),
                            (px - r - 3, py),
                            (px, py + r + 3),
                            (px + r + 3, py)
                        ]
                        self.canvas.create_polygon(puntos_seleccion, 
                                                 fill='', outline='gold', width=3)
                    
                    # Barras de prisión
                    for barra in range(3):
                        self.canvas.create_line(px - 6 + barra * 4, py - 6, 
                                              px - 6 + barra * 4, py + 6,
                                              fill='white', width=1)
                    
                    # Número de ficha
                    self.canvas.create_text(px, py, text=str(ficha.id_ficha + 1),
                                          font=("Arial", 6, "bold"), fill='white')
                    cont += 1
    
    def agregar_decoraciones(self):
        # Agregar elementos decorativos en las esquinas
        esquinas = [
            (MARGEN + 10, MARGEN + 10),           # Superior izquierda
            (TAMANO_TABLERO - MARGEN - 10, MARGEN + 10),     # Superior derecha
            (MARGEN + 10, TAMANO_TABLERO - MARGEN - 10),     # Inferior izquierda
            (TAMANO_TABLERO - MARGEN - 10, TAMANO_TABLERO - MARGEN - 10)  # Inferior derecha
        ]
        
        decoraciones = ["🎯", "🎲", "🏆", "⭐"]
        
        for i, (x, y) in enumerate(esquinas):
            self.canvas.create_text(x, y, text=decoraciones[i], 
                                  font=("Arial", 16), fill=COLORES['texto_secundario'])
    
    def limpiar_tooltip(self, event):
        if hasattr(self, 'tooltip'):
            self.canvas.delete(self.tooltip)
    
    def actualizar_barras_progreso(self):
        for jugador in jugadores:
            progreso = 0
            # Cálculo mejorado del progreso
            for ficha in jugador.fichas:
                if isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
                    if ficha.estado[1] == NUM_CASILLAS_INTERNAS - 1:
                        progreso += 25  # Ficha en meta
                    else:
                        progreso += 15 + (ficha.estado[1] * 1.5)  # Progreso en vía interna
                elif isinstance(ficha.estado, int):
                    # Progreso en tablero externo basado en proximidad a entrada
                    distancia_entrada = calcular_distancia_a_meta(ficha)
                    if distancia_entrada != float('inf'):
                        progreso += max(3, 10 - (distancia_entrada / 10))
            
            progreso_final = min(int(progreso), 100)
            self.barras_progreso[jugador.nombre]['value'] = progreso_final
            
            # Actualizar etiqueta de porcentaje (si existe)
            # Esto requeriría guardar referencias a las etiquetas, por simplicidad se omite aquí
    
    def mostrar_info_casilla(self, event):
        # Limpiar tooltip anterior
        if hasattr(self, 'tooltip'):
            self.canvas.delete(self.tooltip)
        
        info = ""
        color_tooltip = COLORES['fondo_principal']
        
        # Buscar información de la casilla
        for pos, (cx, cy) in coordenadas_del_tablero_externo.items():
            if (cx - 18) <= event.x <= (cx + 18) and (cy - 18) <= event.y <= (cy + 18):
                if posiciones_de_tablero[pos]:
                    fichas_info = []
                    for f in posiciones_de_tablero[pos]:
                        fichas_info.append(f"🔸 {f.jugador.nombre}{f.id_ficha + 1}")
                    info = f"📍 Casilla {pos + 1}\n" + "\n".join(fichas_info)
                    
                    # Color del tooltip según el tipo de casilla
                    if pos in casillas_seguras:
                        color_tooltip = COLORES['casilla_segura']
                    elif len(posiciones_de_tablero[pos]) == 2 and posiciones_de_tablero[pos][0].jugador == posiciones_de_tablero[pos][1].jugador:
                        color_tooltip = '#E74C3C'  # Rojo para bloqueo
                else:
                    info = f"📍 Casilla {pos + 1}\n💭 Vacía"
                    if pos in casillas_seguras:
                        info += "\n🛡️ Casilla Segura"
                break
        
        # Mostrar tooltip mejorado
        if info:
            # Fondo del tooltip
            bbox = self.canvas.create_rectangle(event.x + 5, event.y - 25, 
                                              event.x + 120, event.y + 10,
                                              fill=color_tooltip, outline='white', width=2)
            
            # Texto del tooltip
            self.tooltip = self.canvas.create_text(event.x + 10, event.y - 10, 
                                                 text=info,
                                                 fill='white',
                                                 font=("Arial", 8, "bold"),
                                                 anchor="w")
    
    def dibujar_botones_dados(self):
        for b in self.botones_dados:
            b.destroy()
        self.botones_dados = []
        
        for i, val in enumerate(self.valores_dados):
            btn = tk.Button(self.marco_dados, 
                          text=f"🎲\n{val}",
                          command=lambda v=val: self.usar_dado(v),
                          font=("Arial", 12, "bold"),
                          width=4, height=2,
                          bg='white', fg=COLORES['texto_principal'],
                          relief='raised', bd=3, cursor='hand2')
            btn.pack(side="left", padx=3)
            self.botones_dados.append(btn)
    
    def mostrar_estadisticas(self):
        ventana_stats = tk.Toplevel(self.maestro)
        ventana_stats.title("📊 Estadísticas del Juego")
        ventana_stats.geometry("450x350")
        ventana_stats.configure(bg=COLORES['fondo_principal'])
        
        tk.Label(ventana_stats, text="📈 ESTADÍSTICAS DE JUGADORES", 
                font=("Arial", 14, "bold"), bg=COLORES['fondo_principal'], fg='white').pack(pady=10)
        
        for jugador in jugadores:
            stats = jugador.obtener_estadisticas()
            frame_jugador = tk.Frame(ventana_stats, bg=jugador.color, relief="ridge", bd=2)
            frame_jugador.pack(fill="x", padx=20, pady=5)
            
            tk.Label(frame_jugador, text=f"🎯 {jugador.nombre}", 
                    font=("Arial", 12, "bold"), bg=jugador.color, fg='white').pack()
            
            stats_text = f"📊 Movimientos: {stats['movimientos']} | 🎯 Capturas: {stats['capturas']} | 🏆 En meta: {stats['fichas_en_meta']}/4"
            tk.Label(frame_jugador, text=stats_text, bg=jugador.color, fg='white').pack()
    
    def nuevo_juego(self):
        if messagebox.askyesno("🔄 Nuevo Juego", "¿Estás seguro de reiniciar?"):
            reiniciar_juego()
            self.indice_jugador_actual = 0
            self.valores_dados = []
            self.ficha_seleccionada = None
            self.ultimo_doble = False
            for b in self.botones_dados:
                b.destroy()
            self.botones_dados = []
            self.dibujar_tablero()
            self.actualizar_info()
            self.actualizar_barras_progreso()
    
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