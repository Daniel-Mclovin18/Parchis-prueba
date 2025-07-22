import tkinter as tk
import random

# ---------------------
# PARAMETROS GLOBALES Y CONSTANTES
#
# en este grupo se definen los parametros basicos del juego:
# - el numero total de casillas del tablero exterior (NUM_CASILLAS_EXTERNAS)
#   y del tablero interior (NUM_CASILLAS_INTERNAS).
# - el tamano total del canvas (TAMANO_TABLERO), que determina el espacio de la interfaz grafica.
# - el margen (MARGEN) que se deja alrededor del tablero.
# - el tamano de cada celda (CELDA) usado para dibujar la via interna.
# estos valores son esenciales para calcular las posiciones en las que se dibujan
# las casillas y fichas, asi como para la logica de movimiento.
# ---------------------
NUM_CASILLAS_EXTERNAS = 68
NUM_CASILLAS_INTERNAS = 8
TAMANO_TABLERO = 600   # tamano total del canvas (ventana grafica)
MARGEN = 20           # margen en pixeles alrededor del tablero
CELDA = 40            # tamano aproximado de cada celda en la via interna

# ---------------------
# CLASES DEL JUEGO: FICHA Y JUGADOR
#
# a continuacion se definen las clases fundamentales:
#
# 1. clase Ficha:
#    - representa una pieza del juego.
#    - cada ficha sabe a que jugador pertenece (atributo "jugador").
#    - posee un identificador "id_ficha" para distinguir las fichas de un mismo jugador.
#    - el atributo "estado" indica la posicion actual de la ficha:
#         "carcel": la ficha se encuentra en la carcel (no esta en juego)
#         un entero: posicion en el tablero exterior (de 0 a 67)
#         una tupla ("interna", indice): posicion en la via interna (indice de 0 a 7)
#
# 2. clase Jugador:
#    - almacena los datos del jugador: nombre, color, casilla de salida y entrada a la via interna.
#    - al crearse, genera 4 fichas para el jugador.
#    - usa "contador_dobles" para llevar registro de dobles consecutivos.
#    - acumula "movimientos_extra" ganados al capturar o al llegar a la meta.
#    - guarda "ultima_ficha_movida" para aplicar penalizaciones en caso de tres dobles consecutivos.
# ---------------------
class Ficha:
    def __init__(self, jugador, id_ficha):
        self.jugador = jugador  # referencia al objeto jugador al que pertenece
        self.id_ficha = id_ficha  # identificador de la ficha (0, 1, 2, 3)
        self.estado = "carcel"    # inicialmente, la ficha esta en la carcel
    
    def __str__(self):
        # representa la ficha en formato de texto para mostrar mensajes
        if self.estado == "carcel":
            return f"{self.jugador.nombre}{self.id_ficha}(carcel)"
        elif isinstance(self.estado, int):
            return f"{self.jugador.nombre}{self.id_ficha}(ext {self.estado})"
        elif isinstance(self.estado, tuple) and self.estado[0] == "interna":
            return f"{self.jugador.nombre}{self.id_ficha}(int {self.estado[1]})"
        return f"{self.jugador.nombre}{self.id_ficha}(?)"

class Jugador:
    def __init__(self, nombre, color, salida, entrada_hogar):
        self.nombre = nombre              # nombre del jugador (ej. "Rojo")
        self.color = color                # color de las fichas (ej. "red")
        self.salida = salida              # casilla exterior de salida
        self.entrada_hogar = entrada_hogar  # casilla por donde entran a la via interna
        self.fichas = [Ficha(self, i) for i in range(4)]  # crea 4 fichas para el jugador
        self.contador_dobles = 0          # contador para dobles consecutivos
        self.movimientos_extra = 0        # movimientos extra acumulados
        self.ultima_ficha_movida = None   # guarda la ultima ficha que se movio
    
    def todas_llegaron(self):
        # retorna True si todas las fichas han alcanzado la ultima casilla interna (meta)
        for f in self.fichas:
            if not (isinstance(f.estado, tuple) and f.estado[0] == "interna" and f.estado[1] == (NUM_CASILLAS_INTERNAS - 1)):
                return False
        return True

# ---------------------
# CREACION DE JUGADORES
#
# se instancian los jugadores con sus caracteristicas iniciales:
# cada jugador se crea con nombre, color, y las posiciones (salida y entrada_hogar)
# que definen su posicion inicial y el punto de entrada a la via interna.
# cada jugador recibe 4 fichas creadas automaticamente.
# ---------------------
jugadores = [
    Jugador("Rojo", "red", salida=0, entrada_hogar=67),
    Jugador("Azul", "blue", salida=17, entrada_hogar=16),
    Jugador("Verde", "green", salida=34, entrada_hogar=33),
    Jugador("Amarillo", "yellow", salida=51, entrada_hogar=50),
]

# ---------------------
# TABLERO EXTERNO Y CASILLAS SEGURAS
#
# se crea el diccionario "posiciones_de_tablero" que asocia cada casilla (0 a 67)
# a una lista de fichas presentes en dicha casilla.
# ademas, "casillas_seguras" contiene los indices de las casillas de salida de cada jugador,
# en las que, por regla, no se puede capturar.
# ---------------------
posiciones_de_tablero = {i: [] for i in range(NUM_CASILLAS_EXTERNAS)}
casillas_seguras = {j.salida for j in jugadores}

# ---------------------
# FUNCIONES DE UTILIDAD: BLOQUEO Y VERIFICACION DE CAMINO
#
# la funcion es_bloqueo(pos) determina si en la casilla con indice "pos"
# existen 2 fichas que pertenecen al mismo jugador. en ese caso, se considera
# que la casilla esta bloqueada para el paso de otras fichas.
#
# la funcion verificar_camino(inicio, pasos) recorre las casillas intermedias
# entre la casilla "inicio" y la casilla destino (sin incluirla) y verifica que ninguna
# tenga bloqueo. retorna (True, None) si el camino es valido o (False, pos) si se encuentra bloqueo.
# ---------------------
def es_bloqueo(pos):
    if len(posiciones_de_tablero[pos]) == 2:
        f0, f1 = posiciones_de_tablero[pos]
        if f0.jugador == f1.jugador:
            return True
    return False

def verificar_camino(inicio, pasos):
    for i in range(1, pasos):
        pos_verificar = (inicio + i) % NUM_CASILLAS_EXTERNAS  # uso del modulo para recorrido circular
        if es_bloqueo(pos_verificar):
            return False, pos_verificar
    return True, None

# ---------------------
# COORDENADAS PARA EL DIBUJO DEL TABLERO EXTERNO
#
# se calculan las coordenadas (x, y) para cada casilla del tablero exterior.
# se usa un bucle para cada grupo de casillas (cada lado del tablero), repartiendo
# uniformemente el espacio entre "MARGEN" y "TAMANO_TABLERO - MARGEN".
# las coordenadas se almacenan en el diccionario "coordenadas_del_tablero_externo".
# estas posiciones seran usadas para dibujar cada casilla y posicionar las fichas.
# ---------------------
coordenadas_del_tablero_externo = {}
longitud_lado = 17
top_y = MARGEN
left_x = MARGEN
right_x = TAMANO_TABLERO - MARGEN
bottom_y = TAMANO_TABLERO - MARGEN

for i in range(longitud_lado):
    pos = i
    x = left_x + i * ((right_x - left_x) // (longitud_lado - 1))
    y = top_y
    coordenadas_del_tablero_externo[pos] = (x, y)
for i in range(longitud_lado):
    pos = 17 + i
    x = right_x
    y = top_y + i * ((bottom_y - top_y) // (longitud_lado - 1))
    coordenadas_del_tablero_externo[pos] = (x, y)
for i in range(longitud_lado):
    pos = 34 + i
    x = right_x - i * ((right_x - left_x) // (longitud_lado - 1))
    y = bottom_y
    coordenadas_del_tablero_externo[pos] = (x, y)
for i in range(longitud_lado):
    pos = 51 + i
    x = left_x
    y = bottom_y - i * ((bottom_y - top_y) // (longitud_lado - 1))
    coordenadas_del_tablero_externo[pos] = (x, y)

# ---------------------
# COORDENADAS DE LA VIA INTERNA PARA CADA JUGADOR
#
# se definen funciones para calcular las posiciones en el canvas para la via interna,
# que es la ruta que deben recorrer las fichas al acercarse a la meta.
#
# a continuacion se explican cada una:
#
# - construir_coordenadas_de_la_via_interna_rojo():
#   parte del centro del tablero y genera "NUM_CASILLAS_INTERNAS" posiciones
#   que se desplazan verticalmente hacia arriba (disminuyendo el valor de y).
#
def construir_coordenadas_de_la_via_interna_rojo():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x            # la posicion x se mantiene constante (centro)
        y = centro_y - (i + 1) * CELDA  # se desplaza hacia arriba
        coords.append((x, y))
    return coords

# - construir_coordenadas_de_la_via_interna_azul():
#   parte del centro del tablero y genera las posiciones para la via interna de "azul",
#   desplazandose horizontalmente hacia la derecha (aumentando el valor de x).
def construir_coordenadas_de_la_via_interna_azul():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x + (i + 1) * CELDA  # se desplaza hacia la derecha
        y = centro_y                   # la posicion y se mantiene en el centro
        coords.append((x, y))
    return coords

# - construir_coordenadas_de_la_via_interna_verde():
#   genera las posiciones para la via interna del jugador "verde",
#   desplazandose verticalmente hacia abajo (aumentando el valor de y).
def construir_coordenadas_de_la_via_interna_verde():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x            # la posicion x permanece constante
        y = centro_y + (i + 1) * CELDA  # se desplaza hacia abajo
        coords.append((x, y))
    return coords

# - construir_coordenadas_de_la_via_interna_amarillo():
#   genera las posiciones para la via interna del jugador "amarillo",
#   desplazandose horizontalmente hacia la izquierda (disminuyendo el valor de x).
def construir_coordenadas_de_la_via_interna_amarillo():
    coords = []
    centro_x = TAMANO_TABLERO // 2
    centro_y = TAMANO_TABLERO // 2
    for i in range(NUM_CASILLAS_INTERNAS):
        x = centro_x - (i + 1) * CELDA  # se desplaza hacia la izquierda
        y = centro_y                   # la posicion y se mantiene en el centro
        coords.append((x, y))
    return coords

# se agrupan las coordenadas de la via interna en un diccionario, donde cada clave es
# el nombre del jugador.
coordenadas_de_la_via_interna = {
    "Rojo": construir_coordenadas_de_la_via_interna_rojo(),
    "Azul": construir_coordenadas_de_la_via_interna_azul(),
    "Verde": construir_coordenadas_de_la_via_interna_verde(),
    "Amarillo": construir_coordenadas_de_la_via_interna_amarillo(),
}

# ---------------------
# POSICIONES EN LA CARCEL (PARA DIBUJO)
#
# en este grupo se asignan las posiciones (coordenadas x, y) donde se mostraran
# las fichas que se encuentren en la carcel. cada jugador tiene una posicion de referencia
# y un "offset" para separar visualmente varias fichas.
# ---------------------
posiciones_de_la_carcel = {
    "Rojo": {"x": 80, "y": 100, "offset_y": 25},
    "Azul": {"x": 500, "y": 100, "offset_y": 25},
    "Verde": {"x": 400, "y": 400, "offset_y": 25},
    "Amarillo": {"x": 150, "y": 400, "offset_y": 25},
}

# ---------------------
# LOGICA DE MOVIMIENTO: BLOQUEO, CAPTURA Y MOVIMIENTO BONUS
#
# la funcion puede_colocar(ficha, pos) retorna True si en la casilla "pos"
# hay menos de 2 fichas, lo que significa que es posible colocar una nueva ficha.
#
# la funcion mover_ficha(ficha, pasos) gestiona los siguientes casos:
#
# 1. ficha en la carcel:
#    - solo se puede salir de la carcel si el valor de "pasos" es 5.
#    - si se cumple, la ficha se mueve a la casilla de salida del jugador.
#
# 2. ficha en el tablero exterior (estado es un entero):
#    - se calcula la cantidad de pasos necesarios (d) para llegar a la casilla de entrada a la via interna.
#    - si "pasos" es exactamente igual a d:
#         * se verifica que el camino este libre de bloqueos (usando verificar_camino).
#         * se retira la ficha de la casilla actual y se coloca en la primera casilla de la via interna ("interna", 0).
#         * se otorgan movimientos extra.
#    - si "pasos" es menor que d:
#         * se mueve la ficha a la casilla destino normal, comprobando que el camino este libre.
#         * si en la casilla destino hay una ficha enemiga (y la casilla no es segura),
#           se captura la ficha enemiga (se la envia a la carcel) y se aplica un movimiento bonus de 20 casillas.
#    - si "pasos" es mayor que d, el movimiento es invalido.
#
# 3. ficha en la via interna (estado es una tupla):
#    - se suma "pasos" al indice actual de la via interna.
#    - se requiere exactitud; si el movimiento excede el numero de casillas internas, es invalido.
#    - si la ficha alcanza la ultima casilla de la via interna, se otorgan movimientos extra.
#
# la funcion retorna un mensaje descriptivo del resultado del movimiento.
# ---------------------
def puede_colocar(ficha, pos):
    return (len(posiciones_de_tablero[pos]) < 2)

def mover_ficha(ficha, pasos):
    # caso: ficha en la carcel (solo se permite salir con 5)
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
    
    # caso: ficha en el tablero exterior
    if isinstance(ficha.estado, int):
        actual = ficha.estado
        hogar = ficha.jugador.entrada_hogar
        if hogar >= actual:
            d = hogar - actual
        else:
            d = (NUM_CASILLAS_EXTERNAS - actual) + hogar
        
        # intento de entrar a la via interna (se requiere exactitud)
        if pasos == d:
            valido, bloqueado = verificar_camino(actual, pasos)
            if not valido:
                return "movimiento no permitido: camino bloqueado por un bloqueo de dos fichas."
            if ficha in posiciones_de_tablero[actual]:
                posiciones_de_tablero[actual].remove(ficha)
            ficha.estado = ("interna", 0)
            ficha.jugador.movimientos_extra += 10  # se otorgan movimientos extra al entrar a la via interna
            ficha.jugador.ultima_ficha_movida = ficha
            return f"{ficha} entra a la via interna."
        elif pasos > d:
            return "movimiento no permitido: se requiere exactitud para entrar a la via interna."
        else:
            nuevo = (actual + pasos) % NUM_CASILLAS_EXTERNAS
            valido, bloqueado = verificar_camino(actual, pasos)
            if not valido:
                return "movimiento no permitido: camino bloqueado por un bloqueo de dos fichas."
            # si hay fichas en la casilla destino, se verifica la posibilidad de captura
            if posiciones_de_tablero[nuevo]:
                ocupante = posiciones_de_tablero[nuevo][0]
                if ocupante.jugador != ficha.jugador and nuevo not in casillas_seguras:
                    # captura: se retira la ficha enemiga y se la envia a la carcel
                    if ocupante in posiciones_de_tablero[nuevo]:
                        posiciones_de_tablero[nuevo].remove(ocupante)
                    ocupante.estado = "carcel"
                    if ficha in posiciones_de_tablero[actual]:
                        posiciones_de_tablero[actual].remove(ficha)
                    posiciones_de_tablero[nuevo].append(ficha)
                    ficha.estado = nuevo
                    # se aplica movimiento bonus de 20 casillas tras capturar
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
            # movimiento normal sin captura
            if ficha in posiciones_de_tablero[actual]:
                posiciones_de_tablero[actual].remove(ficha)
            posiciones_de_tablero[nuevo].append(ficha)
            ficha.estado = nuevo
            ficha.jugador.ultima_ficha_movida = ficha
            return f"{ficha} se mueve de la casilla {actual + 1} a {nuevo + 1}."
    
    # caso: ficha en la via interna
    if isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
        indice = ficha.estado[1]
        nuevo_indice = indice + pasos
        if nuevo_indice >= NUM_CASILLAS_INTERNAS:
            return "movimiento no valido en la via interna (requiere exactitud)."
        ficha.estado = ("interna", nuevo_indice)
        ficha.jugador.ultima_ficha_movida = ficha
        if nuevo_indice == NUM_CASILLAS_INTERNAS - 1:
            ficha.jugador.movimientos_extra += 10
            return f"{ficha} ha llegado a la meta."
        return f"{ficha} avanza en la via interna a la casilla {nuevo_indice + 1}."
    
    return "movimiento desconocido."

# ---------------------
# INTERFAZ GRAFICA DEL JUEGO (TKINTER)
#
# en este grupo se define la clase interfaz_parques que maneja la parte grafica del juego:
# - se crea la ventana principal y el canvas donde se dibuja el tablero.
# - se definen etiquetas para mostrar la informacion del turno y estado del juego.
# - se crean botones para lanzar dados y terminar el turno.
# - se implementan metodos para dibujar el tablero, actualizar la informacion, y detectar clicks
#   para seleccionar fichas.
# - se controla la logica del turno, incluyendo la regla de continuar el turno al sacar dobles,
#   y la penalizacion de tres dobles consecutivos (la ficha correspondiente se envia a la carcel).
# ---------------------
class InterfazParques:
    def __init__(self, maestro):
        self.maestro = maestro
        self.maestro.title("parques tradicional (tablero clasico)")
        
        # se crea el canvas principal
        self.canvas = tk.Canvas(maestro, width=TAMANO_TABLERO, height=TAMANO_TABLERO, bg="white")
        self.canvas.grid(row=0, column=0, columnspan=4)
        
        # se crean las etiquetas para mostrar informacion y estado del juego
        self.etiqueta_info = tk.Label(maestro, text="", font=("Arial", 12))
        self.etiqueta_info.grid(row=1, column=0, columnspan=4)
        
        self.etiqueta_estado = tk.Label(maestro, text="", font=("Arial", 10), fg="blue")
        self.etiqueta_estado.grid(row=2, column=0, columnspan=4)
        
        # boton para lanzar los dados
        self.boton_lanzar = tk.Button(maestro, text="lanzar dados", command=self.lanzar_dados)
        self.boton_lanzar.grid(row=3, column=0)
        
        # marco para colocar los botones de los dados
        self.marco_dados = tk.Frame(maestro)
        self.marco_dados.grid(row=3, column=1, columnspan=2)
        self.botones_dados = []
        
        # boton para terminar el turno
        self.boton_terminar = tk.Button(maestro, text="terminar turno", command=self.terminar_turno)
        self.boton_terminar.grid(row=3, column=3)
        
        # variables para llevar el control del turno y seleccion de fichas
        self.indice_jugador_actual = 0
        self.valores_dados = []
        self.ficha_seleccionada = None
        self.ultimo_doble = False  # bandera para saber si se obtuvo un doble en el lanzamiento
        
        self.dibujar_tablero()
        self.actualizar_info()
        
        # se asocia la funcion de deteccion de clicks en el canvas
        self.canvas.bind("<Button-1>", self.al_hacer_click_en_canvas)
    
    def dibujar_tablero(self):
        # limpia el canvas y dibuja el layout basico
        self.canvas.delete("all")
        self.dibujar_layout_tradicional()
        
        # ---------------------
        # dibujar casillas externas
        # se recorre el diccionario de coordenadas y se dibuja cada casilla como un rectangulo,
        # o como un ovalo en las casillas seguras; se muestra el numero de casilla.
        # ---------------------
        for pos, (cx, cy) in coordenadas_del_tablero_externo.items():
            x1 = cx - 15
            y1 = cy - 15
            x2 = cx + 15
            y2 = cy + 15
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightgray")
            num_casilla = pos + 1
            if num_casilla == 68:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="red", outline="black")
            elif num_casilla == 18:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="blue", outline="black")
            elif num_casilla == 35:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="green", outline="black")
            elif num_casilla == 52:
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="yellow", outline="black")
            else:
                if pos in casillas_seguras and num_casilla not in {17, 35, 51}:
                    self.canvas.create_oval(cx - 10, cy - 10, cx + 10, cy + 10, fill="yellow")
                self.canvas.create_text(cx, cy, text=str(num_casilla), font=("Arial", 8))
        
        # ---------------------
        # dibujar vias internas
        # para cada jugador se dibujan las casillas de la via interna con sus respectivos indices.
        # ---------------------
        for j in jugadores:
            lista_coords = coordenadas_de_la_via_interna[j.nombre]
            for i, (cx, cy) in enumerate(lista_coords):
                x1 = cx - 15
                y1 = cy - 15
                x2 = cx + 15
                y2 = cy + 15
                self.canvas.create_rectangle(x1, y1, x2, y2, fill="white", outline="black")
                self.canvas.create_text(cx, cy, text=str(i + 1), font=("Arial", 8))
        
        # ---------------------
        # dibujar fichas en casillas externas
        # se posicionan las fichas sobre las casillas del tablero exterior, usando
        # las coordenadas calculadas previamente.
        # ---------------------
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
        
        # ---------------------
        # dibujar fichas en la via interna
        # se recorren las fichas de cada jugador y se dibujan las que tengan estado "interna",
        # usando las coordenadas calculadas para la via interna.
        # ---------------------
        for j in jugadores:
            for ficha in j.fichas:
                if isinstance(ficha.estado, tuple) and ficha.estado[0] == "interna":
                    indice = ficha.estado[1]
                    cx, cy = coordenadas_de_la_via_interna[j.nombre][indice]
                    r = 10
                    ancho_contorno = 3 if ficha == self.ficha_seleccionada else 1
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                            fill=j.color, outline="black", width=ancho_contorno)
        
        # ---------------------
        # dibujar fichas en la carcel
        # se muestran las fichas en la carcel en la posicion asignada al jugador,
        # separadas por un offset.
        # ---------------------
        for j in jugadores:
            pos_carcel = posiciones_de_la_carcel[j.nombre]
            self.canvas.create_text(pos_carcel["x"], pos_carcel["y"] - 20,
                                    text=f"carcel {j.nombre}",
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
    
    def dibujar_layout_tradicional(self):
        # dibuja el contorno principal del tablero y las lineas centrales
        self.canvas.create_rectangle(MARGEN, MARGEN, TAMANO_TABLERO - MARGEN, TAMANO_TABLERO - MARGEN, width=2)
        centro = TAMANO_TABLERO // 2
        self.canvas.create_line(centro, MARGEN, centro, TAMANO_TABLERO - MARGEN, width=2)
        self.canvas.create_line(MARGEN, centro, TAMANO_TABLERO - MARGEN, centro, width=2)
        
        # dibuja el cuadrado central (zona de meta)
        tam_centro = 100
        c1x = centro - tam_centro // 2
        c1y = centro - tam_centro // 2
        c2x = centro + tam_centro // 2
        c2y = centro + tam_centro // 2
        self.canvas.create_rectangle(c1x, c1y, c2x, c2y, width=2)
        self.canvas.create_line(c1x, c1y, c2x, c2y, width=2)
        self.canvas.create_line(c2x, c1y, c1x, c2y, width=2)
        
        # dibuja lineas de subdivision en cada cuadrante
        def dibujar_lineas(x1, y1, x2, y2, div=6):
            w = x2 - x1
            h = y2 - y1
            dx = w / div
            dy = h / div
            for i in range(1, div):
                self.canvas.create_line(x1 + i * dx, y1, x1 + i * dx, y2)
            for i in range(1, div):
                self.canvas.create_line(x1, y1 + i * dy, x2, y1 + i * dy)
        
        dibujar_lineas(MARGEN, MARGEN, centro, centro)
        dibujar_lineas(centro, MARGEN, TAMANO_TABLERO - MARGEN, centro)
        dibujar_lineas(MARGEN, centro, centro, TAMANO_TABLERO - MARGEN)
        dibujar_lineas(centro, centro, TAMANO_TABLERO - MARGEN, TAMANO_TABLERO - MARGEN)
    
    def actualizar_info(self, msg=""):
        # actualiza la informacion mostrada en la interfaz, indicando el turno del jugador actual
        # y, si existen, los valores de los dados.
        actual = jugadores[self.indice_jugador_actual]
        texto = f"turno de: {actual.nombre} ({actual.color}). "
        if self.valores_dados:
            texto += "dados: " + ", ".join(str(v) for v in self.valores_dados)
        else:
            texto += "sin dados. lanza para continuar."
        self.etiqueta_info.config(text=texto)
        self.etiqueta_estado.config(text=msg)
    
    def lanzar_dados(self):
        actual = jugadores[self.indice_jugador_actual]
        # si el jugador tiene movimientos extra pendientes, se solicitan antes de lanzar dados
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

        # regla de tres dobles consecutivos: se penaliza enviando a la carcel la ultima ficha movida
        if actual.contador_dobles == 3:
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
            self.actualizar_info("tres dobles consecutivos: la ficha " + str(ficha_a_carcel) + " regresa a la carcel.")
            actual.contador_dobles = 0
            self.dibujar_tablero()
            return

        self.valores_dados = [d1, d2]
        self.dibujar_botones_dados()
        self.actualizar_info()
    
    def solicitar_movimientos_extra(self):
        actual = jugadores[self.indice_jugador_actual]
        top = tk.Toplevel(self.maestro)
        top.title("usar movimientos extra")
        tk.Label(top, text=f"tienes {actual.movimientos_extra} movimientos extra.\ningresa la cantidad a usar:").pack(padx=10, pady=10)
        entry = tk.Entry(top)
        entry.pack(padx=10, pady=10)
        def submit():
            try:
                val = int(entry.get())
            except:
                val = 0
            if val < 1 or val > actual.movimientos_extra:
                self.actualizar_info("cantidad invalida para movimientos extra.")
            else:
                if self.ficha_seleccionada is None:
                    self.actualizar_info("debes seleccionar una ficha para usar movimientos extra.")
                else:
                    resultado = mover_ficha(self.ficha_seleccionada, val)
                    actual.movimientos_extra -= val
                    self.valores_dados = []
                    self.ficha_seleccionada = None
                    self.actualizar_info(resultado)
                    self.dibujar_tablero()
            top.destroy()
        tk.Button(top, text="aceptar", command=submit).pack(padx=10, pady=10)
    
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
            self.actualizar_info("primero selecciona una ficha.")
            return
        resultado = mover_ficha(self.ficha_seleccionada, val)
        jugadores[self.indice_jugador_actual].ultima_ficha_movida = self.ficha_seleccionada
        self.valores_dados.remove(val)
        self.ficha_seleccionada = None
        self.actualizar_info(resultado)
        self.dibujar_tablero()
        if not self.valores_dados:
            self.terminar_turno()
    
    def terminar_turno(self):
        self.valores_dados = []
        self.ficha_seleccionada = None
        actual = jugadores[self.indice_jugador_actual]
        # si en el ultimo lanzamiento no salio doble, se pasa el turno al siguiente jugador
        if not self.ultimo_doble:
            actual.contador_dobles = 0
            self.indice_jugador_actual = (self.indice_jugador_actual + 1) % len(jugadores)
        else:
            self.ultimo_doble = False
        self.actualizar_info()
        self.dibujar_tablero()
        for b in self.botones_dados:
            b.destroy()
        self.botones_dados = []
    
    def al_hacer_click_en_canvas(self, event):
        actual = jugadores[self.indice_jugador_actual]
        ficha_click = None
        
        # buscar en casillas externas:
        for pos, (cx, cy) in coordenadas_del_tablero_externo.items():
            if (cx - 15) <= event.x <= (cx + 15) and (cy - 15) <= event.y <= (cy + 15):
                if posiciones_de_tablero[pos]:
                    for f in posiciones_de_tablero[pos]:
                        if f.jugador == actual:
                            ficha_click = f
                            break
            if ficha_click:
                break
        
        # buscar en vias internas:
        if not ficha_click:
            lista_coords = coordenadas_de_la_via_interna[actual.nombre]
            for idx, (cx, cy) in enumerate(lista_coords):
                if (cx - 15) <= event.x <= (cx + 15) and (cy - 15) <= event.y <= (cy + 15):
                    for f in actual.fichas:
                        if f.estado == ("interna", idx):
                            ficha_click = f
                            break
                if ficha_click:
                    break
        
        # buscar en la carcel:
        if not ficha_click:
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
                                ficha_click = f
                                break
                if ficha_click:
                    break
        
        if ficha_click:
            self.ficha_seleccionada = ficha_click
            self.actualizar_info(f"seleccionada {ficha_click}")
            self.dibujar_tablero()
        else:
            self.actualizar_info("no hay ficha tuya en esa posicion.")

def main():
    raiz = tk.Tk()
    app = InterfazParques(raiz)
    raiz.mainloop()

if __name__ == "__main__":
    main()
