import tkinter as tk
import random

# Constantes del juego
CASILLAS_EXTERNAS = 68
CASILLAS_INTERNAS = 8
TAMANO_VENTANA = 700
MARGEN = 30
TAMANO_CELDA = 35
RADIO_FICHA = 12

class Ficha:
    def __init__(self, jugador, id_ficha):
        self.jugador = jugador
        self.id = id_ficha
        self.posicion = "carcel"
    
    def esta_en_carcel(self):
        return self.posicion == "carcel"
    
    def esta_en_tablero(self):
        return isinstance(self.posicion, int)
    
    def esta_en_hogar(self):
        return isinstance(self.posicion, tuple) and self.posicion[0] == "hogar"
    
    def obtener_posicion_hogar(self):
        if self.esta_en_hogar():
            return self.posicion[1]
        return -1

class Jugador:
    def __init__(self, nombre, color, casilla_salida, casilla_entrada):
        self.nombre = nombre
        self.color = color
        self.casilla_salida = casilla_salida
        self.casilla_entrada = casilla_entrada
        self.fichas = [Ficha(self, i) for i in range(4)]
        self.dobles_consecutivos = 0
        self.movimientos_bonus = 0
        self.ultima_ficha_movida = None
        self.ha_ganado = False
    
    def todas_las_fichas_en_meta(self):
        for ficha in self.fichas:
            if not (ficha.esta_en_hogar() and ficha.obtener_posicion_hogar() == CASILLAS_INTERNAS - 1):
                return False
        return True
    
    def fichas_en_carcel(self):
        return [f for f in self.fichas if f.esta_en_carcel()]
    
    def fichas_en_tablero(self):
        return [f for f in self.fichas if f.esta_en_tablero()]
    
    def fichas_en_hogar(self):
        return [f for f in self.fichas if f.esta_en_hogar()]

class Tablero:
    def __init__(self):
        self.casillas = {i: [] for i in range(CASILLAS_EXTERNAS)}
        self.casillas_seguras = {0, 17, 34, 51}
        self.hogar = {"Rojo": [], "Azul": [], "Verde": [], "Amarillo": []}
    
    def colocar_ficha(self, ficha, posicion):
        if isinstance(posicion, int):
            self.casillas[posicion].append(ficha)
        elif isinstance(posicion, tuple) and posicion[0] == "hogar":
            self.hogar[ficha.jugador.nombre].append(ficha)
        ficha.posicion = posicion
    
    def remover_ficha(self, ficha):
        if ficha.esta_en_tablero():
            pos = ficha.posicion
            if ficha in self.casillas[pos]:
                self.casillas[pos].remove(ficha)
        elif ficha.esta_en_hogar():
            if ficha in self.hogar[ficha.jugador.nombre]:
                self.hogar[ficha.jugador.nombre].remove(ficha)
    
    def hay_bloqueo(self, posicion):
        if len(self.casillas[posicion]) == 2:
            fichas = self.casillas[posicion]
            return fichas[0].jugador == fichas[1].jugador
        return False
    
    def puede_colocar_ficha(self, posicion):
        return len(self.casillas[posicion]) < 2
    
    def verificar_camino_libre(self, inicio, pasos):
        for i in range(1, pasos):
            pos_intermedia = (inicio + i) % CASILLAS_EXTERNAS
            if self.hay_bloqueo(pos_intermedia):
                return False
        return True
    
    def obtener_fichas_enemigas(self, posicion, jugador):
        fichas_enemigas = []
        for ficha in self.casillas[posicion]:
            if ficha.jugador != jugador:
                fichas_enemigas.append(ficha)
        return fichas_enemigas

class CalculadorCoordenadas:
    def __init__(self):
        self.coordenadas_externas = self.calcular_coordenadas_externas()
        self.coordenadas_hogar = self.calcular_coordenadas_hogar()
        self.coordenadas_carcel = self.calcular_coordenadas_carcel()
    
    def calcular_coordenadas_externas(self):
        coords = {}
        casillas_por_lado = 17
        
        # Lado superior
        for i in range(casillas_por_lado):
            x = MARGEN + i * ((TAMANO_VENTANA - 2 * MARGEN) // (casillas_por_lado - 1))
            y = MARGEN
            coords[i] = (x, y)
        
        # Lado derecho
        for i in range(casillas_por_lado):
            x = TAMANO_VENTANA - MARGEN
            y = MARGEN + i * ((TAMANO_VENTANA - 2 * MARGEN) // (casillas_por_lado - 1))
            coords[17 + i] = (x, y)
        
        # Lado inferior
        for i in range(casillas_por_lado):
            x = TAMANO_VENTANA - MARGEN - i * ((TAMANO_VENTANA - 2 * MARGEN) // (casillas_por_lado - 1))
            y = TAMANO_VENTANA - MARGEN
            coords[34 + i] = (x, y)
        
        # Lado izquierdo
        for i in range(casillas_por_lado):
            x = MARGEN
            y = TAMANO_VENTANA - MARGEN - i * ((TAMANO_VENTANA - 2 * MARGEN) // (casillas_por_lado - 1))
            coords[51 + i] = (x, y)
        
        return coords
    
    def calcular_coordenadas_hogar(self):
        centro_x = TAMANO_VENTANA // 2
        centro_y = TAMANO_VENTANA // 2
        
        coords = {
            "Rojo": [(centro_x, centro_y - (i + 1) * TAMANO_CELDA) for i in range(CASILLAS_INTERNAS)],
            "Azul": [(centro_x + (i + 1) * TAMANO_CELDA, centro_y) for i in range(CASILLAS_INTERNAS)],
            "Verde": [(centro_x, centro_y + (i + 1) * TAMANO_CELDA) for i in range(CASILLAS_INTERNAS)],
            "Amarillo": [(centro_x - (i + 1) * TAMANO_CELDA, centro_y) for i in range(CASILLAS_INTERNAS)]
        }
        
        return coords
    
    def calcular_coordenadas_carcel(self):
        return {
            "Rojo": (100, 120),
            "Azul": (TAMANO_VENTANA - 100, 120),
            "Verde": (TAMANO_VENTANA - 100, TAMANO_VENTANA - 120),
            "Amarillo": (100, TAMANO_VENTANA - 120)
        }

class MotorJuego:
    def __init__(self):
        self.jugadores = [
            Jugador("Rojo", "red", 0, 67),
            Jugador("Azul", "blue", 17, 16),
            Jugador("Verde", "green", 34, 33),
            Jugador("Amarillo", "yellow", 51, 50)
        ]
        self.tablero = Tablero()
        self.jugador_actual = 0
        self.dados = []
        self.juego_terminado = False
        self.ganador = None
    
    def obtener_jugador_actual(self):
        return self.jugadores[self.jugador_actual]
    
    def lanzar_dados(self):
        dado1 = random.randint(1, 6)
        dado2 = random.randint(1, 6)
        self.dados = [dado1, dado2]
        
        jugador = self.obtener_jugador_actual()
        
        if dado1 == dado2:
            jugador.dobles_consecutivos += 1
        else:
            jugador.dobles_consecutivos = 0
        
        if jugador.dobles_consecutivos >= 3:
            self.aplicar_penalizacion_tres_dobles(jugador)
            return False
        
        return True
    
    def aplicar_penalizacion_tres_dobles(self, jugador):
        if jugador.ultima_ficha_movida and not jugador.ultima_ficha_movida.esta_en_carcel():
            self.enviar_ficha_a_carcel(jugador.ultima_ficha_movida)
        
        jugador.dobles_consecutivos = 0
        self.dados = []
    
    def enviar_ficha_a_carcel(self, ficha):
        self.tablero.remover_ficha(ficha)
        ficha.posicion = "carcel"
    
    def puede_salir_de_carcel(self, valor_dado):
        return valor_dado == 5
    
    def sacar_ficha_de_carcel(self, ficha):
        if not self.tablero.puede_colocar_ficha(ficha.jugador.casilla_salida):
            return False
        
        self.tablero.colocar_ficha(ficha, ficha.jugador.casilla_salida)
        return True
    
    def calcular_distancia_a_hogar(self, ficha):
        posicion_actual = ficha.posicion
        entrada_hogar = ficha.jugador.casilla_entrada
        
        if entrada_hogar >= posicion_actual:
            return entrada_hogar - posicion_actual
        else:
            return (CASILLAS_EXTERNAS - posicion_actual) + entrada_hogar
    
    def mover_ficha_en_tablero(self, ficha, pasos):
        posicion_actual = ficha.posicion
        distancia_hogar = self.calcular_distancia_a_hogar(ficha)
        
        if pasos == distancia_hogar:
            return self.mover_ficha_a_hogar(ficha)
        elif pasos < distancia_hogar:
            return self.mover_ficha_normal(ficha, pasos)
        else:
            return False, "Movimiento excede la distancia al hogar"
    
    def mover_ficha_a_hogar(self, ficha):
        if not self.tablero.verificar_camino_libre(ficha.posicion, self.calcular_distancia_a_hogar(ficha)):
            return False, "Camino bloqueado"
        
        self.tablero.remover_ficha(ficha)
        self.tablero.colocar_ficha(ficha, ("hogar", 0))
        ficha.jugador.movimientos_bonus += 10
        return True, "Ficha movida al hogar"
    
    def mover_ficha_normal(self, ficha, pasos):
        posicion_actual = ficha.posicion
        nueva_posicion = (posicion_actual + pasos) % CASILLAS_EXTERNAS
        
        if not self.tablero.verificar_camino_libre(posicion_actual, pasos):
            return False, "Camino bloqueado"
        
        fichas_enemigas = self.tablero.obtener_fichas_enemigas(nueva_posicion, ficha.jugador)
        
        if fichas_enemigas and nueva_posicion not in self.tablero.casillas_seguras:
            return self.capturar_fichas(ficha, nueva_posicion, fichas_enemigas)
        
        if not self.tablero.puede_colocar_ficha(nueva_posicion):
            return False, "Casilla ocupada"
        
        self.tablero.remover_ficha(ficha)
        self.tablero.colocar_ficha(ficha, nueva_posicion)
        return True, f"Ficha movida a casilla {nueva_posicion + 1}"
    
    def capturar_fichas(self, ficha, posicion, fichas_enemigas):
        for ficha_enemiga in fichas_enemigas:
            self.enviar_ficha_a_carcel(ficha_enemiga)
        
        self.tablero.colocar_ficha(ficha, posicion)
        
        bonus = 20
        nueva_posicion_bonus = (posicion + bonus) % CASILLAS_EXTERNAS
        
        if (self.tablero.verificar_camino_libre(posicion, bonus) and 
            self.tablero.puede_colocar_ficha(nueva_posicion_bonus)):
            
            self.tablero.remover_ficha(ficha)
            self.tablero.colocar_ficha(ficha, nueva_posicion_bonus)
            return True, f"Captura realizada, ficha movida a casilla {nueva_posicion_bonus + 1}"
        
        return True, f"Captura realizada en casilla {posicion + 1}"
    
    def mover_ficha_en_hogar(self, ficha, pasos):
        posicion_actual = ficha.obtener_posicion_hogar()
        nueva_posicion = posicion_actual + pasos
        
        if nueva_posicion >= CASILLAS_INTERNAS:
            return False, "Movimiento excede las casillas del hogar"
        
        ficha.posicion = ("hogar", nueva_posicion)
        
        if nueva_posicion == CASILLAS_INTERNAS - 1:
            ficha.jugador.movimientos_bonus += 10
            if self.verificar_victoria(ficha.jugador):
                self.juego_terminado = True
                self.ganador = ficha.jugador
                return True, f"¡{ficha.jugador.nombre} ha ganado!"
        
        return True, f"Ficha movida en hogar a posición {nueva_posicion + 1}"
    
    def verificar_victoria(self, jugador):
        return jugador.todas_las_fichas_en_meta()
    
    def mover_ficha(self, ficha, pasos):
        if ficha.esta_en_carcel():
            if not self.puede_salir_de_carcel(pasos):
                return False, "Necesitas un 5 para salir de la cárcel"
            
            if self.sacar_ficha_de_carcel(ficha):
                ficha.jugador.ultima_ficha_movida = ficha
                return True, "Ficha sacada de la cárcel"
            else:
                return False, "Casilla de salida bloqueada"
        
        elif ficha.esta_en_tablero():
            resultado, mensaje = self.mover_ficha_en_tablero(ficha, pasos)
            if resultado:
                ficha.jugador.ultima_ficha_movida = ficha
            return resultado, mensaje
        
        elif ficha.esta_en_hogar():
            resultado, mensaje = self.mover_ficha_en_hogar(ficha, pasos)
            if resultado:
                ficha.jugador.ultima_ficha_movida = ficha
            return resultado, mensaje
        
        return False, "Movimiento inválido"
    
    def usar_movimiento_bonus(self, ficha, cantidad):
        jugador = ficha.jugador
        if cantidad > jugador.movimientos_bonus:
            return False, "No tienes suficientes movimientos bonus"
        
        resultado, mensaje = self.mover_ficha(ficha, cantidad)
        if resultado:
            jugador.movimientos_bonus -= cantidad
        
        return resultado, mensaje
    
    def siguiente_turno(self):
        if not self.hay_dobles():
            self.obtener_jugador_actual().dobles_consecutivos = 0
            self.jugador_actual = (self.jugador_actual + 1) % len(self.jugadores)
        
        self.dados = []
    
    def hay_dobles(self):
        return len(self.dados) == 2 and self.dados[0] == self.dados[1]

class InterfazGrafica:
    def __init__(self):
        self.ventana = tk.Tk()
        self.ventana.title("Parqués - Juego Tradicional")
        self.ventana.geometry(f"{TAMANO_VENTANA + 200}x{TAMANO_VENTANA + 150}")
        self.ventana.resizable(False, False)
        
        self.motor = MotorJuego()
        self.calculadora = CalculadorCoordenadas()
        self.ficha_seleccionada = None
        
        self.crear_interfaz()
        self.actualizar_pantalla()
    
    def crear_interfaz(self):
        # Canvas principal
        self.canvas = tk.Canvas(
            self.ventana, 
            width=TAMANO_VENTANA, 
            height=TAMANO_VENTANA, 
            bg="white",
            relief="ridge",
            bd=2
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Panel de control
        panel_control = tk.Frame(self.ventana, width=180)
        panel_control.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        
        # Información del juego
        self.etiqueta_turno = tk.Label(
            panel_control, 
            text="", 
            font=("Arial", 12, "bold"),
            wraplength=160
        )
        self.etiqueta_turno.pack(pady=10)
        
        self.etiqueta_dados = tk.Label(
            panel_control, 
            text="Dados: -", 
            font=("Arial", 10)
        )
        self.etiqueta_dados.pack(pady=5)
        
        # Botones
        self.boton_lanzar = tk.Button(
            panel_control, 
            text="Lanzar Dados", 
            command=self.lanzar_dados,
            font=("Arial", 10),
            width=15
        )
        self.boton_lanzar.pack(pady=10)
        
        # Frame para botones de dados
        self.frame_dados = tk.Frame(panel_control)
        self.frame_dados.pack(pady=10)
        
        self.boton_terminar = tk.Button(
            panel_control, 
            text="Terminar Turno", 
            command=self.terminar_turno,
            font=("Arial", 10),
            width=15
        )
        self.boton_terminar.pack(pady=10)
        
        self.boton_bonus = tk.Button(
            panel_control, 
            text="Usar Bonus", 
            command=self.usar_bonus,
            font=("Arial", 10),
            width=15
        )
        self.boton_bonus.pack(pady=5)
        
        # Información adicional
        self.etiqueta_info = tk.Label(
            panel_control, 
            text="", 
            font=("Arial", 9),
            wraplength=160,
            justify=tk.LEFT
        )
        self.etiqueta_info.pack(pady=10)
        
        # Bind de eventos
        self.canvas.bind("<Button-1>", self.click_en_canvas)
    
    def crear_botones_dados(self):
        for widget in self.frame_dados.winfo_children():
            widget.destroy()
        
        for i, valor in enumerate(self.motor.dados):
            boton = tk.Button(
                self.frame_dados, 
                text=str(valor), 
                command=lambda v=valor, idx=i: self.usar_dado(v, idx),
                font=("Arial", 12, "bold"),
                width=3,
                height=1
            )
            boton.pack(side=tk.LEFT, padx=2)
    
    def dibujar_tablero(self):
        self.canvas.delete("all")
        
        # Dibujar estructura del tablero
        self.dibujar_estructura_tablero()
        
        # Dibujar casillas externas
        self.dibujar_casillas_externas()
        
        # Dibujar casillas del hogar
        self.dibujar_casillas_hogar()
        
        # Dibujar fichas
        self.dibujar_fichas()
        
        # Dibujar información de cárceles
        self.dibujar_carceles()
    
    def dibujar_estructura_tablero(self):
        # Contorno principal
        self.canvas.create_rectangle(
            MARGEN, MARGEN, 
            TAMANO_VENTANA - MARGEN, TAMANO_VENTANA - MARGEN,
            outline="black", width=3
        )
        
        # Líneas centrales
        centro = TAMANO_VENTANA // 2
        self.canvas.create_line(
            centro, MARGEN, centro, TAMANO_VENTANA - MARGEN,
            fill="black", width=2
        )
        self.canvas.create_line(
            MARGEN, centro, TAMANO_VENTANA - MARGEN, centro,
            fill="black", width=2
        )
        
        # Cuadrado central
        tam_centro = 80
        x1 = centro - tam_centro // 2
        y1 = centro - tam_centro // 2
        x2 = centro + tam_centro // 2
        y2 = centro + tam_centro // 2
        
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", width=2)
        self.canvas.create_line(x1, y1, x2, y2, fill="black", width=1)
        self.canvas.create_line(x2, y1, x1, y2, fill="black", width=1)
    
    def dibujar_casillas_externas(self):
        for posicion, (x, y) in self.calculadora.coordenadas_externas.items():
            # Determinar color de la casilla
            color = "lightgray"
            if posicion in [0, 17, 34, 51]:  # Casillas de salida
                colores_salida = {0: "red", 17: "blue", 34: "green", 51: "yellow"}
                color = colores_salida[posicion]
            elif posicion in self.motor.tablero.casillas_seguras:
                color = "lightyellow"
            
            # Dibujar casilla
            self.canvas.create_rectangle(
                x - 18, y - 18, x + 18, y + 18,
                fill=color, outline="black", width=1
            )
            
            # Número de casilla
            numero = posicion + 1
            self.canvas.create_text(x, y, text=str(numero), font=("Arial", 8))
    
    def dibujar_casillas_hogar(self):
        for jugador in self.motor.jugadores:
            coordenadas = self.calculadora.coordenadas_hogar[jugador.nombre]
            for i, (x, y) in enumerate(coordenadas):
                self.canvas.create_rectangle(
                    x - 15, y - 15, x + 15, y + 15,
                    fill="white", outline="black", width=1
                )
                self.canvas.create_text(x, y, text=str(i + 1), font=("Arial", 8))
    
    def dibujar_fichas(self):
        # Fichas en tablero externo
        for posicion, fichas in self.motor.tablero.casillas.items():
            if fichas:
                x, y = self.calculadora.coordenadas_externas[posicion]
                for i, ficha in enumerate(fichas):
                    offset_x = (i * 8) - 4
                    offset_y = -8
                    self.dibujar_ficha(ficha, x + offset_x, y + offset_y)
        
        # Fichas en hogar
        for jugador in self.motor.jugadores:
            coordenadas = self.calculadora.coordenadas_hogar[jugador.nombre]
            fichas_hogar = jugador.fichas_en_hogar()
            
            for ficha in fichas_hogar:
                pos_hogar = ficha.obtener_posicion_hogar()
                if 0 <= pos_hogar < len(coordenadas):
                    x, y = coordenadas[pos_hogar]
                    self.dibujar_ficha(ficha, x, y)
        
        # Fichas en cárcel
        for jugador in self.motor.jugadores:
            fichas_carcel = jugador.fichas_en_carcel()
            if fichas_carcel:
                x_base, y_base = self.calculadora.coordenadas_carcel[jugador.nombre]
                for i, ficha in enumerate(fichas_carcel):
                    y_offset = i * 25
                    self.dibujar_ficha(ficha, x_base, y_base + y_offset, forma="diamante")
    
    def dibujar_ficha(self, ficha, x, y, forma="circulo"):
        # Determinar si está seleccionada
        borde = 3 if ficha == self.ficha_seleccionada else 1
        
        if forma == "circulo":
            self.canvas.create_oval(
                x - RADIO_FICHA, y - RADIO_FICHA,
                x + RADIO_FICHA, y + RADIO_FICHA,
                fill=ficha.jugador.color, outline="black", width=borde
            )
        else:  # diamante
            puntos = [
                x, y - RADIO_FICHA,
                x + RADIO_FICHA, y,
                x, y + RADIO_FICHA,
                x - RADIO_FICHA, y
            ]
            self.canvas.create_polygon(
                puntos, fill=ficha.jugador.color, outline="black", width=borde
            )
    
    def dibujar_carceles(self):
        for jugador in self.motor.jugadores:
            x, y = self.calculadora.coordenadas_carcel[jugador.nombre]
            self.canvas.create_text(
                x, y - 30, 
                text=f"Cárcel {jugador.nombre}",
                font=("Arial", 10, "bold"),
                fill=jugador.color
            )
    
    def actualizar_pantalla(self):
        self.dibujar_tablero()
        self.actualizar_etiquetas()
    
    def actualizar_etiquetas(self):
        jugador_actual = self.motor.obtener_jugador_actual()
        
        # Etiqueta de turno
        texto_turno = f"Turno: {jugador_actual.nombre}"
        if jugador_actual.movimientos_bonus > 0:
            texto_turno += f"\nBonus: {jugador_actual.movimientos_bonus}"
        self.etiqueta_turno.config(text=texto_turno, fg=jugador_actual.color)
        
        # Etiqueta de dados
        if self.motor.dados:
            texto_dados = f"Dados: {', '.join(map(str, self.motor.dados))}"
        else:
            texto_dados = "Dados: -"
        self.etiqueta_dados.config(text=texto_dados)
        
        # Información adicional
        info_adicional = ""
        if self.ficha_seleccionada:
            info_adicional = f"Seleccionada: {self.ficha_seleccionada.jugador.nombre}{self.ficha_seleccionada.id}"
        
        if jugador_actual.dobles_consecutivos > 0:
            info_adicional += f"\nDobles: {jugador_actual.dobles_consecutivos}/3"
        
        self.etiqueta_info.config(text=info_adicional)
    
    def lanzar_dados(self):
        if self.motor.juego_terminado:
            return
        
        jugador = self.motor.obtener_jugador_actual()
        
        if jugador.movimientos_bonus > 0:
            self.mostrar_mensaje("Debes usar tus movimientos bonus primero")
            return
        
        if self.motor.dados:
            self.mostrar_mensaje("Ya has lanzado los dados")
            return
        
        if self.motor.lanzar_dados():
            self.crear_botones_dados()
            self.actualizar_etiquetas()
        else:
            self.mostrar_mensaje("¡Tres dobles consecutivos! Ficha a la cárcel")
            self.actualizar_pantalla()
    
    def usar_dado(self, valor, indice):
        if not self.ficha_seleccionada:
            self.mostrar_mensaje("Selecciona una ficha primero")
            return
        
        if self.ficha_seleccionada.jugador != self.motor.obtener_jugador_actual():
            self.mostrar_mensaje("No puedes mover fichas de otro jugador")
            return
        
        exito, mensaje = self.motor.mover_ficha(self.ficha_seleccionada, valor)
        
        if exito:
            self.motor.dados.remove(valor)
            self.ficha_seleccionada = None
            
            if not self.motor.dados:
                self.crear_botones_dados()
            else:
                self.crear_botones_dados()
            
            if self.motor.juego_terminado:
                self.mostrar_mensaje(f"¡Juego terminado! {mensaje}")
            else:
                self.mostrar_mensaje(mensaje)
        else:
            self.mostrar_mensaje(f"Error: {mensaje}")
        
        self.actualizar_pantalla()
    
    def usar_bonus(self):
        jugador = self.motor.obtener_jugador_actual()
        
        if jugador.movimientos_bonus <= 0:
            self