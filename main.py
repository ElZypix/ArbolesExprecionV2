import sys
import re
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene, QLabel
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt, QTimer

from Logica.Arboles import CalculadoraArbol
from Logica.Nodo import Nodo
from Logica.Analizador import AnalizadorLexico #


class CompiladorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Gui/interfaz.ui", self)

        self.calc = CalculadoraArbol()
        self.analizador = AnalizadorLexico()  #
        self.btn_Info.clicked.connect(self.mostrar_estadisticas)


        # --- CONEXIÓN MÓDULO 1 ---
        # Cambia 'inp_Exp' por el nombre real de tu QLineEdit en la Pestaña 1 si es distinto
        self.inp_Exp.textChanged.connect(self.ejecutar_modulo_1)

        # --- VARIABLES MÓDULO 2 ---
        self.arbol_manual = None
        self.nodo_seleccionado = None
        self.mapa_items_manual = {}

        # --- NAVEGACIÓN ---
        # Botón para ir al Módulo 1 (Índice 0)
        self.btn_EArbol.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btn_AExpresion.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # --- CONEXIONES MÓDULO 2 (En modo prueba) ---
        self.btn_agregarAexp.clicked.connect(self.agregar_nodo_manual)
        self.btn_EliminarAexp.clicked.connect(self.eliminar_nodo_manual)
        self.btn_limpiarAexp.clicked.connect(self.limpiar_arbol_manual)
        self.inp_nod.textChanged.connect(self.validar_input_manual)
        self.inp_nod.returnPressed.connect(self.agregar_nodo_manual)

        # ==========================================
        # VARIABLES Y CONEXIONES MÓDULO 3
        # ==========================================
        # Navegación
        self.btn_ENotacion.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))

        # Motor de animación
        self.timer_animacion = QTimer()
        self.timer_animacion.timeout.connect(self.ejecutar_paso_animacion)

        # Variables de estado para las 3 pilas
        self.estado_animacion = {
            "entrada": [],
            "pila_operadores": [],
            "salida": [],
            "paso_actual": 0
        }

        # Conectar botones de Módulo 3 (Verifica que estos sean los nombres en tu .ui)
        self.pushButton_12.clicked.connect(lambda: self.iniciar_animacion_m3("Prefija"))
        self.pushButton_10.clicked.connect(lambda: self.iniciar_animacion_m3("Infija"))
        self.pushButton_11.clicked.connect(lambda: self.iniciar_animacion_m3("Postfija"))

        # ==========================================
        # VARIABLES Y CONEXIONES MÓDULO 4
        # ==========================================
        self.arbol_m4 = None
        self.nodo_sel_m4 = None
        self.mapa_items_m4 = {}
        self.btn_ANotacion.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(3))

        # Botones de creación del árbol
        self.btn_AgregarANota.clicked.connect(self.agregar_nodo_m4)
        self.btn_EliminarANota.clicked.connect(self.eliminar_nodo_m4)
        self.btn_LimpiarANota.clicked.connect(self.limpiar_arbol_m4)

        # Input de validación
        self.int_NodoANota.textChanged.connect(self.validar_input_m4)
        self.int_NodoANota.returnPressed.connect(self.agregar_nodo_m4)
        self.btn_infijaANota.clicked.connect(lambda: self.iniciar_animacion_m4("Infija"))
        self.btn_postfijaANota.clicked.connect(lambda: self.iniciar_animacion_m4("Postfija"))
        self.btn_PrefijaANota.clicked.connect(lambda: self.iniciar_animacion_m4("Prefija"))

        # Navegación Módulo 5 (Índice 4)
        self.btn_Ecodigo.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(4))

        # Botones de Acción
        self.btn_CuadruplosECodigo.clicked.connect(lambda: self.generar_intermedio("Cuadruplos"))
        self.btn_expTriplos.clicked.connect(lambda: self.generar_intermedio("Triplos"))
        self.btn_CodpECod.clicked.connect(lambda: self.generar_intermedio("CodigoP"))
        self.tab_1.setShowGrid(True)

        # ==========================================
        # VARIABLES Y CONEXIONES MÓDULO 6
        # ==========================================
        self.arbol_m6 = None
        self.nodo_sel_m6 = None
        self.mapa_items_m6 = {}

        # Navegación al Módulo 6 (Asumiendo índice 5 en el stacked principal)
        self.btn_ACodigo.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(5))

        # Botones de construcción del árbol
        self.btn_AgregarACode.clicked.connect(self.agregar_nodo_m6)
        self.btn_EliminarACode.clicked.connect(self.eliminar_nodo_m6)
        self.btn_LimpiarACode.clicked.connect(self.limpiar_arbol_m6)

        # Botones de código intermedio (Cambian el stackedWidget interno al índice 1)
        self.btn_CuadruplosACode.clicked.connect(lambda: self.generar_m6("Cuadruplos"))
        self.btn_TriplosACode.clicked.connect(lambda: self.generar_m6("Triplos"))
        self.btn_CodePACode.clicked.connect(lambda: self.generar_m6("CodigoP"))

        # Input de validación y tecla Enter para el Módulo 6
        self.int_NodoACode.textChanged.connect(self.validar_input_m6)
        self.int_NodoACode.returnPressed.connect(self.agregar_nodo_m6)

    def ejecutar_modulo_1(self, ecuacion):
        """Lógica del Módulo 1: Expresión -> Árbol + Resolución por Jerarquía Estricta"""
        texto_limpio = ecuacion.strip()

        # Anti-Crasheo: Si el usuario borra todo, limpiamos de forma segura
        if not texto_limpio:
            if self.grap_GenArbol1.scene():
                self.grap_GenArbol1.scene().clear()
            self.limpiar_area_resultado(self.area_Res1)
            return

        try:
            # 1. Construir la Lógica del Árbol (Para el dibujo)
            posfija = self.calc.infija_a_posfija(texto_limpio)
            arbol = self.calc.construir_arbol(posfija)

            if arbol:
                # 2. Dibujar Árbol
                nueva_escena = QGraphicsScene()
                self.grap_GenArbol1.setScene(nueva_escena)

                profundidad = self.obtener_profundidad(arbol)
                dx_inicial = 35 * (2 ** (profundidad - 2)) if profundidad > 1 else 0

                self.dibujar_nodo(arbol, nueva_escena, 0, 0, dx_inicial)

                # 3. Evaluar Matemáticamente usando la NUEVA función de jerarquía
                # Importamos 're' aquí por si acaso, o asegúrate de que 'import re' esté al inicio del archivo
                import re
                tokens_infijos = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", texto_limpio)

                res_final, pasos = self.calc.evaluar_jerarquia_estricta(tokens_infijos)

                # 4. Construir el panel de Procedimiento
                proc = "⚙️ PROCEDIMIENTO POR JERARQUÍA ESTRICTA:\n\n"

                if pasos:
                    for i, paso in enumerate(pasos):
                        proc += f" Paso {i + 1}: {paso}\n"
                else:
                    proc += "   (No hay operaciones pendientes)\n"

                proc += f"\n🎯 RESULTADO FINAL: {res_final}"

                self.actualizar_texto_resultado(self.area_Res1, proc)

        except Exception as e:
            # Ignoramos silenciosamente si la ecuación está incompleta (ej: "5 + ")
            pass

    def actualizar_texto_resultado(self, widget_scroll, texto):
        """Pone texto dentro del QScrollArea de forma segura"""
        label = QLabel(texto)
        label.setStyleSheet("color: #00E676; font-family: 'Consolas'; font-size: 14px; padding: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        widget_scroll.setWidget(label)

    def limpiar_area_resultado(self, widget_scroll):
        vacio = QLabel("")
        widget_scroll.setWidget(vacio)

    def obtener_profundidad(self, nodo):
        """Calcula la profundidad máxima del árbol para evitar colisiones visuales"""
        if not nodo: return 0
        return 1 + max(self.obtener_profundidad(nodo.izquierda), self.obtener_profundidad(nodo.derecha))

    def dibujar_nodo(self, nodo, escena, x, y, dx):
        """Dibuja el árbol recursivamente sin amontonar nodos."""
        if not nodo: return
        radio = 20
        pen = QPen(QColor("#6C5CE7"), 2)

        # Ahora dividimos exactamente a la mitad (dx / 2) en cada nivel
        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 60, pen)
            self.dibujar_nodo(nodo.izquierda, escena, x - dx, y + 60, dx / 2)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 60, pen)
            self.dibujar_nodo(nodo.derecha, escena, x + dx, y + 60, dx / 2)

        # Círculo
        escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, QPen(Qt.GlobalColor.white),
                          QBrush(QColor("#1E1E1E")))
        # Texto
        txt = escena.addText(str(nodo.valor), QFont("Arial", 11, QFont.Weight.Bold))
        txt.setDefaultTextColor(Qt.GlobalColor.white)
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)

    # ==========================================
    # LÓGICA MÓDULO 2 (Árbol Manual y Validaciones)
    # ==========================================
    def validar_input_manual(self, texto):
        """Vigila lo que escribe el usuario y bloquea errores"""
        if not texto: return
        char_actual = texto[-1]

        self.inp_nod.blockSignals(True)  # Evita que Python se trabe corrigiendo

        if char_actual in self.calc.preferencia or char_actual == '√':
            if len(texto) > 1: self.inp_nod.setText(char_actual)  # Solo 1 operador
        elif char_actual.isalpha():
            if len(texto) > 1: self.inp_nod.setText(char_actual)  # Solo 1 letra
            if char_actual.islower(): self.inp_nod.setText(char_actual.upper())
        elif char_actual.isdigit():
            solo_numeros = "".join(filter(str.isdigit, texto))
            self.inp_nod.setText(solo_numeros)  # Permite números largos (ej: 123)
        else:
            self.inp_nod.setText(texto[:-1])  # Borra símbolos raros

        self.inp_nod.blockSignals(False)

    def agregar_nodo_manual(self):
        valor = self.inp_nod.text().strip()
        if not valor: return

        # --- NUEVA REGLA: La raíz DEBE ser un operador ---
        if self.arbol_manual is None:
            es_operador = valor in self.calc.preferencia or valor == '√'
            if not es_operador:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Raíz Inválida",
                    "La raíz del árbol debe ser un operador (+, -, *, /, ^, √) para que el árbol pueda crecer."
                )
                self.inp_nod.clear()
                return

            self.arbol_manual = Nodo(valor)
            self.nodo_seleccionado = self.arbol_manual

        elif self.nodo_seleccionado:
            # REGLA: Los operandos (números/letras) son hojas y no tienen hijos
            if self.calc.es_operando(self.nodo_seleccionado.valor):
                QtWidgets.QMessageBox.warning(self, "Inválido", "Los números y variables no pueden tener hijos.")
                self.inp_nod.clear()
                return

            if self.nodo_seleccionado.izquierda is None:
                self.nodo_seleccionado.izquierda = Nodo(valor)
            elif self.nodo_seleccionado.derecha is None:
                self.nodo_seleccionado.derecha = Nodo(valor)
            else:
                QtWidgets.QMessageBox.information(self, "Lleno", "Este operador ya tiene sus dos hijos.")

        self.inp_nod.clear()
        self.actualizar_vistas_manual()

        self.inp_nod.clear()
        self.actualizar_vistas_manual()

    def eliminar_nodo_manual(self):
        if self.nodo_seleccionado and self.arbol_manual:
            if self.nodo_seleccionado == self.arbol_manual:
                self.arbol_manual = None
            else:
                self.eliminar_referencia(self.arbol_manual, self.nodo_seleccionado)
            self.nodo_seleccionado = None
            self.actualizar_vistas_manual()

    def eliminar_referencia(self, nodo_actual, nodo_a_borrar):
        if not nodo_actual: return
        if nodo_actual.izquierda == nodo_a_borrar:
            nodo_actual.izquierda = None;
            return
        if nodo_actual.derecha == nodo_a_borrar:
            nodo_actual.derecha = None;
            return
        self.eliminar_referencia(nodo_actual.izquierda, nodo_a_borrar)
        self.eliminar_referencia(nodo_actual.derecha, nodo_a_borrar)

    def limpiar_arbol_manual(self):
        self.arbol_manual = None
        self.nodo_seleccionado = None
        self.actualizar_vistas_manual()

    def actualizar_vistas_manual(self):
        escena = QGraphicsScene(self)
        self.grap_Arbol2.setScene(escena)
        self.mapa_items_manual = {}
        if self.arbol_manual:
            prof = self.obtener_profundidad(self.arbol_manual)
            dx = 35 * (2 ** (prof - 2)) if prof > 1 else 0
            self.dibujar_nodo_interactivo(self.arbol_manual, escena, 0, 0, dx)
            escena.selectionChanged.connect(self.al_seleccionar_nodo_manual)

            try:
                infija_tokens = self.calc.obtener_infija(self.arbol_manual)
            except:
                infija_tokens = ["(Expresión incompleta)"]

            # --- NUEVA JERARQUÍA AQUÍ ---
            res_final, pasos = self.calc.evaluar_jerarquia_estricta(infija_tokens)
            proc = f"✅ EXPRESIÓN: {' '.join(infija_tokens)}\n\n⚙️ JERARQUÍA ESTRICTA:\n\n"
            if pasos:
                for i, paso in enumerate(pasos):
                    proc += f" Paso {i + 1}: {paso}\n"
            else:
                proc += "   (Esperando nodos...)"

            proc += f"\n\n🎯 RESULTADO FINAL: {res_final}"
            self.actualizar_texto_resultado(self.area_res2, proc)
        else:
            self.limpiar_area_resultado(self.area_res2)

    def dibujar_nodo_interactivo(self, nodo, escena, x, y, dx):
        """Dibuja el árbol y permite que los círculos se puedan seleccionar"""
        from PyQt6.QtWidgets import QGraphicsItem
        if not nodo: return
        radio = 20
        pen = QPen(QColor("#6C5CE7"), 2)

        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 60, pen)
            self.dibujar_nodo_interactivo(nodo.izquierda, escena, x - dx, y + 60, dx / 2)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 60, pen)
            self.dibujar_nodo_interactivo(nodo.derecha, escena, x + dx, y + 60, dx / 2)

        elipse = escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, QPen(Qt.GlobalColor.white))

        # --- LÓGICA DE CONTRASTE DE COLORES ---
        es_seleccionado = (nodo == self.nodo_seleccionado)
        color_fondo = "#00E676" if es_seleccionado else "#1E1E1E"
        color_texto = "#000000" if es_seleccionado else "#FFFFFF"  # Negro si está verde, Blanco si es gris

        elipse.setBrush(QBrush(QColor(color_fondo)))
        elipse.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        txt = escena.addText(str(nodo.valor), QFont("Arial", 11, QFont.Weight.Bold))
        txt.setDefaultTextColor(QColor(color_texto))
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)

        # ¡NUEVO! Ahora guardamos una tupla (nodo, texto) para poder cambiar el color de la letra después
        self.mapa_items_manual[elipse] = (nodo, txt)

    def al_seleccionar_nodo_manual(self):
        """Sistema Seguro Anti-Crasheos con cambio de contraste de texto"""
        if not self.grap_Arbol2.scene(): return
        items = self.grap_Arbol2.scene().selectedItems()

        if items:
            datos = self.mapa_items_manual.get(items[0])
            if datos:
                self.nodo_seleccionado = datos[0]  # datos[0] es el nodo

                # Recorremos todos los elementos para actualizar fondo Y texto
                for elipse, (nodo, txt) in self.mapa_items_manual.items():
                    if nodo == self.nodo_seleccionado:
                        elipse.setBrush(QBrush(QColor("#00E676")))  # Fondo Verde
                        txt.setDefaultTextColor(QColor("#000000"))  # Texto Negro
                    else:
                        elipse.setBrush(QBrush(QColor("#1E1E1E")))  # Fondo Gris
                        txt.setDefaultTextColor(QColor("#FFFFFF"))  # Texto Blanco

        # ==========================================
        # LÓGICA MÓDULO 3 (Animación + Procedimientos + Conversión Inversa)
        # ==========================================
    def iniciar_animacion_m3(self, tipo_notacion):
        ecuacion = self.lineEdit_3.text().strip()
        if not ecuacion:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Por favor, escribe una expresión primero.")
            return

        tokens = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", ecuacion)
        try:
            res_eval, pasos_eval = self.calc.evaluar_jerarquia_estricta(tokens)
            self.resolucion_m3 = "🧮 JERARQUÍA MATEMÁTICA:\n"
            for i, p in enumerate(pasos_eval):
                self.resolucion_m3 += f" Paso {i + 1}: {p}\n"
            self.resolucion_m3 += f"\n🎯 RESULTADO FINAL: {res_eval}"
        except Exception:
            self.resolucion_m3 = "🧮 (Expresión inválida)"

        self.frames_animacion = []
        if tipo_notacion == "Postfija":
            self.frames_animacion = self.generar_frames_postfija(tokens)
        elif tipo_notacion == "Prefija":
            self.frames_animacion = self.generar_frames_prefija(tokens)
        elif tipo_notacion == "Infija":
            self.frames_animacion = self.generar_frames_infija_inteligente(tokens)

        if not self.frames_animacion: return

        self.pushButton_12.setEnabled(False)
        self.pushButton_10.setEnabled(False)
        self.pushButton_11.setEnabled(False)
        self.timer_animacion.start(800)

    def ejecutar_paso_animacion(self):
        if not self.frames_animacion:
            self.timer_animacion.stop()
            self.pushButton_12.setEnabled(True)
            self.pushButton_10.setEnabled(True)
            self.pushButton_11.setEnabled(True)
            return

        estado_actual = self.frames_animacion.pop(0)
        self.dibujar_estado_pilas(estado_actual)

    def dibujar_estado_pilas(self, estado):
        """Dibuja las columnas gráficas y manda el texto al panel de Procedimientos"""
        escena = QGraphicsScene(self)
        self.graphicsView_3.setScene(escena)

        fuente_titulo = QFont("Arial", 12, QFont.Weight.Bold)
        fuente_item = QFont("Consolas", 14, QFont.Weight.Bold)
        pen_borde = QPen(QColor("#6C5CE7"), 2)
        brush_caja = QBrush(QColor("#1E1E1E"))
        brush_pila = QBrush(QColor("#00E676"))

        # --- COLUMNA 1: ENTRADA ---
        t1 = escena.addText("ENTRADA", fuente_titulo)
        t1.setDefaultTextColor(Qt.GlobalColor.white)
        t1.setPos(50, 20)

        y_offset = 60
        for token in estado["entrada"]:
            escena.addRect(50, y_offset, 80, 30, pen_borde, brush_caja)
            txt = escena.addText(token, fuente_item)
            txt.setDefaultTextColor(Qt.GlobalColor.white)
            txt.setPos(80, y_offset + 2)
            y_offset += 40

        # --- COLUMNA 2: PILA DE OPERADORES ---
        t2 = escena.addText("PILA (Memoria)", fuente_titulo)
        t2.setDefaultTextColor(Qt.GlobalColor.white)
        t2.setPos(220, 20)

        y_base = 350
        for token in estado["pila_operadores"]:
            escena.addRect(230, y_base, 100, 30, pen_borde, brush_pila)
            txt = escena.addText(token, fuente_item)
            txt.setDefaultTextColor(Qt.GlobalColor.black)
            txt.setPos(240, y_base + 2)
            y_base -= 40

            # --- COLUMNA 3: SALIDA ---
        t3 = escena.addText("SALIDA", fuente_titulo)
        t3.setDefaultTextColor(Qt.GlobalColor.white)
        t3.setPos(400, 20)

        y_offset = 60
        for token in estado["salida"]:
            escena.addRect(420, y_offset, 150, 30, pen_borde, brush_caja)
            txt = escena.addText(token, fuente_item)
            txt.setDefaultTextColor(Qt.GlobalColor.white)
            txt.setPos(430, y_offset + 2)
            y_offset += 40

        # ==========================================
        # CONSTRUCCIÓN DEL TEXTO DEL PANEL (Shunting Yard + Matemáticas)
        # ==========================================
        proc = "⚙️ CONVERSIÓN DE NOTACIÓN (PILAS):\n\n" + estado.get("log", "")

        # Le pegamos la resolución matemática que calculamos en iniciar_animacion_m3
        if hasattr(self, 'resolucion_m3'):
            proc += "\n\n" + ("=" * 40) + "\n\n" + self.resolucion_m3

        try:
            self.actualizar_texto_resultado(self.area_res3, proc)
        except AttributeError:
            pass

    # ==========================================
    # ALGORITMOS CON REGISTRO DE PROCEDIMIENTOS
    # ==========================================


    def generar_frames_prefija(self, tokens):
        frames = []
        # Invertimos y cambiamos paréntesis para el algoritmo de prefija
        entrada_rev = list(tokens[::-1])
        for i in range(len(entrada_rev)):
            if entrada_rev[i] == '(': entrada_rev[i] = ')'
            elif entrada_rev[i] == ')': entrada_rev[i] = '('

        pila = []
        salida = []
        log = "Iniciando Infija -> Prefija (Lectura inversa)\n"

        def tomar_foto(mensaje=""):
            nonlocal log
            if mensaje: log += f" > {mensaje}\n"
            # Al dibujar invertimos la salida para que se vea la prefija real
            frames.append({
                "entrada": list(entrada_rev[::-1]),
                "pila_operadores": list(pila),
                "salida": list(salida[::-1]),
                "log": log
            })

        tomar_foto()
        entrada_trabajo = list(entrada_rev)
        for token in entrada_trabajo:
            entrada_rev.pop(0)
            if self.calc.es_operando(token):
                salida.append(token)
                tomar_foto(f"Operando '{token}' a salida.")
            elif token == '(':
                pila.append(token)
                tomar_foto("Entra '(' a la pila.")
            elif token == ')':
                while pila and pila[-1] != '(':
                    salida.append(pila.pop())
                    tomar_foto("Vaciando hasta encontrar '('...")
                if pila and pila[-1] == '(':
                    pila.pop() # Saca el (
                    tomar_foto("Se elimina '(' de la pila.") # ¡FOTO PARA LIMPIAR EL ( !
            else:
                while (pila and pila[-1] != '(' and
                       self.calc.preferencia.get(pila[-1], 0) > self.calc.preferencia.get(token, 0)):
                    salida.append(pila.pop())
                    tomar_foto("Sale por jerarquía.")
                pila.append(token)
                tomar_foto(f"Operador '{token}' a la pila.")

        while pila:
            salida.append(pila.pop())
            tomar_foto("Vaciando pila final.")
        return frames

    def generar_frames_infija_inteligente(self, tokens):
        """Detecta si el usuario escribió Postfija/Prefija y la convierte a Infija resolviéndola con Pilas"""
        frames = []
        entrada = list(tokens)
        pila = []
        salida = []
        log = ""

        # Detección heurística básica
        es_prefija = tokens[0] in self.calc.preferencia if tokens else False
        es_postfija = tokens[-1] in self.calc.preferencia if tokens else False

        def tomar_foto(mensaje=""):
            nonlocal log
            if mensaje: log += " > " + mensaje + "\n"
            frames.append({"entrada": list(entrada), "pila_operadores": list(pila), "salida": list(salida), "log": log})

        if es_postfija:
            log = "🧠 Detectada Notación POSTFIJA (Se evalúa de Izq a Der)\nConvirtiendo a Infija...\n"
            tomar_foto()
            for token in tokens:
                entrada.pop(0)
                if self.calc.es_operando(token):
                    pila.append(token)
                    tomar_foto(f"Apilando operando: {token}")
                else:
                    if len(pila) >= 2:
                        op2 = pila.pop()
                        op1 = pila.pop()
                        nuevo = f"({op1} {token} {op2})"
                        pila.append(nuevo)
                        tomar_foto(f"Aplicar '{token}': Uniendo {op1} y {op2} ➔ {nuevo}")
            if pila: salida.append(pila.pop())
            tomar_foto("Conversión finalizada.")

        elif es_prefija:
            log = "🧠 Detectada Notación PREFIJA (Se evalúa de Der a Izq)\nConvirtiendo a Infija...\n"
            entrada = list(tokens[::-1]) # Volteamos para la animación
            tomar_foto()
            for token in reversed(tokens):
                entrada.pop(0)
                if self.calc.es_operando(token):
                    pila.append(token)
                    tomar_foto(f"Apilando operando: {token}")
                else:
                    if len(pila) >= 2:
                        op1 = pila.pop()
                        op2 = pila.pop()
                        nuevo = f"({op1} {token} {op2})"
                        pila.append(nuevo)
                        tomar_foto(f"Aplicar '{token}': Uniendo {op1} y {op2} ➔ {nuevo}")
            if pila: salida.append(pila.pop())
            tomar_foto("Conversión finalizada.")

        else:
            log = "La expresión ya está en INFIJA normal.\n"
            tomar_foto()
            for token in tokens:
                entrada.pop(0)
                salida.append(token)
                tomar_foto()

        return frames

    # ==========================================
    # LÓGICA MÓDULO 4 (Fase 2: Animación Sincronizada)
    # ==========================================
    def iniciar_animacion_m4(self, tipo_notacion):
        """Lee el árbol construido, genera la expresión y arranca las pilas"""
        if not self.arbol_m4:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Primero construye un árbol.")
            return

        # 1. Extraemos la expresión del árbol que dibujaste
        try:
            tokens = self.calc.obtener_infija(self.arbol_m4)
            res_eval, pasos_eval = self.calc.evaluar_jerarquia_estricta(tokens)
            self.res_mat_m4 = f"🧮 JERARQUÍA MATEMÁTICA ESTRICTA:\n"
            for i, p in enumerate(pasos_eval):
                self.res_mat_m4 += f" Paso {i + 1}: {p}\n"
            self.res_mat_m4 += f"\n🎯 RESULTADO FINAL: {res_eval}"
        except Exception:
            return

        # 2. Preparamos la Resolución Matemática (Procedimiento 3)
        res_eval, pasos_eval = self.calc.evaluar_con_pasos(self.arbol_m4)
        self.res_mat_m4 = f"🧮 RESOLUCIÓN MATEMÁTICA:\n"
        self.res_mat_m4 += "\n".join(pasos_eval) if pasos_eval else "   (Sin operaciones)"
        self.res_mat_m4 += f"\n\n🎯 RESULTADO FINAL: {res_eval}"

        # 3. Generamos los fotogramas de las pilas (Procedimiento 2)
        self.frames_m4 = []
        if tipo_notacion == "Postfija":
            self.frames_m4 = self.generar_frames_postfija(tokens)
        elif tipo_notacion == "Prefija":
            self.frames_m4 = self.generar_frames_prefija(tokens)
        elif tipo_notacion == "Infija":
            self.frames_m4 = self.generar_frames_infija_inteligente(tokens)

        # 4. Bloquear controles e iniciar reloj
        self.btn_infijaANota.setEnabled(False)
        self.btn_postfijaANota.setEnabled(False)
        self.btn_PrefijaANota.setEnabled(False)

        # Usamos un timer específico para el módulo 4
        if not hasattr(self, 'timer_m4'):
            self.timer_m4 = QTimer()
            self.timer_m4.timeout.connect(self.ejecutar_paso_animacion_m4)

        self.timer_m4.start(800)

    def ejecutar_paso_animacion_m4(self):
        """Mueve las pilas y hace brillar el nodo del árbol correspondiente"""
        if not self.frames_m4:
            self.timer_m4.stop()
            self.btn_infijaANota.setEnabled(True)
            self.btn_postfijaANota.setEnabled(True)
            self.btn_PrefijaANota.setEnabled(True)
            return

        estado_actual = self.frames_m4.pop(0)

        # Identificar qué token se está procesando para iluminar el árbol
        token_activo = ""
        log = estado_actual.get("log", "")
        lineas = log.strip().split('\n')
        if lineas:
            # Buscamos el token entre comillas simples en la última línea del log
            match = re.search(r"'(.*?)'", lineas[-1])
            if match: token_activo = match.group(1)

        self.dibujar_todo_m4(estado_actual, token_activo)

    def dibujar_todo_m4(self, estado, token_activo):
        """Dibuja el Árbol (Izq) y las Pilas (Der) con nombres claros"""
        escena = QGraphicsScene(self)
        self.grap_3.setScene(escena)

        # 1. Dibujar el Árbol (Lado Izquierdo)
        if self.arbol_m4:
            profundidad = self.obtener_profundidad(self.arbol_m4)
            dx_inicial = 30 * (2 ** (profundidad - 2)) if profundidad > 1 else 0
            # Posicionamos el árbol bien a la izquierda
            self.dibujar_nodo_sincronizado(self.arbol_m4, escena, -150, 40, dx_inicial, token_activo)

        # 2. Dibujar las Pilas (Lado Derecho)
        fuente_tit = QFont("Arial", 11, QFont.Weight.Bold)
        fuente_it = QFont("Consolas", 12, QFont.Weight.Bold)
        pen = QPen(QColor("#6C5CE7"), 2)
        off_x = 140  # Inicio de las columnas

        # Etiquetas de las Pilas
        t_ent = escena.addText("ENTRADA", fuente_tit)
        t_ent.setDefaultTextColor(QColor("#FFFFFF"))
        t_ent.setPos(off_x, 10)

        t_pil = escena.addText("PILA (Signos)", fuente_tit)
        t_pil.setDefaultTextColor(QColor("#00E676"))
        t_pil.setPos(off_x + 95, 10)

        t_sal = escena.addText("SALIDA", fuente_tit)
        t_sal.setDefaultTextColor(QColor("#FFFFFF"))
        t_sal.setPos(off_x + 210, 10)

        # Dibujo de Entrada (Cajas grises)
        for i, t in enumerate(estado["entrada"]):
            escena.addRect(off_x, 45 + (i * 35), 70, 30, pen, QBrush(QColor("#1E1E1E")))
            txt = escena.addText(t, fuente_it)
            txt.setDefaultTextColor(Qt.GlobalColor.white)
            txt.setPos(off_x + 25, 45 + (i * 35))

        # Dibujo de Pila (Cajas verdes - De abajo hacia arriba)
        y_base_pila = 350
        for i, t in enumerate(estado["pila_operadores"]):
            escena.addRect(off_x + 100, y_base_pila - (i * 35), 80, 30, pen, QBrush(QColor("#00E676")))
            txt = escena.addText(t, fuente_it)
            txt.setDefaultTextColor(Qt.GlobalColor.black)
            txt.setPos(off_x + 125, y_base_pila - (i * 35))

        # Dibujo de Salida (Cajas grises)
        for i, t in enumerate(estado["salida"]):
            escena.addRect(off_x + 210, 45 + (i * 35), 140, 30, pen, QBrush(QColor("#1E1E1E")))
            txt = escena.addText(t, fuente_it)
            txt.setDefaultTextColor(Qt.GlobalColor.white)
            txt.setPos(off_x + 220, 45 + (i * 35))

        # 3. Procedimientos al Panel Lateral
        infija_arbol = " ".join(self.calc.obtener_infija(self.arbol_m4))
        texto_panel = f"🌳 1. EXPRESIÓN RECONSTRUIDA DEL ÁRBOL:\n   {infija_arbol}\n\n"
        texto_panel += f"⚙️ 2. PROCEDIMIENTO DE PILAS:\n{estado.get('log', '')}\n\n"
        texto_panel += f"{('=' * 40)}\n\n{getattr(self, 'res_mat_m4', '')}"

        self.actualizar_texto_resultado(self.area_res4, texto_panel)

    def generar_frames_postfija(self, tokens):
        frames = []
        entrada = list(tokens)
        pila = []
        salida = []
        log = "Iniciando Infija -> Postfija\n"

        def tomar_foto(mensaje=""):
            nonlocal log
            if mensaje: log += f" > {mensaje}\n"
            frames.append({"entrada": list(entrada), "pila_operadores": list(pila), "salida": list(salida), "log": log})

        tomar_foto()
        for token in tokens:
            entrada.pop(0)
            if self.calc.es_operando(token):
                salida.append(token)
                tomar_foto(f"Operando '{token}' a salida.")
            elif token == '(':
                pila.append(token)
                tomar_foto("Paréntesis '(' entra a la pila.")
            elif token == ')':
                while pila and pila[-1] != '(':
                    salida.append(pila.pop())
                    tomar_foto("Vaciando operadores...")
                if pila and pila[-1] == '(':
                    pila.pop()  # Saca el (
                    tomar_foto("Se elimina '(' de la pila.")  # ¡FOTO PARA LIMPIAR EL ( !
            else:
                while (pila and pila[-1] != '(' and
                       self.calc.preferencia.get(pila[-1], 0) >= self.calc.preferencia.get(token, 0)):
                    salida.append(pila.pop())
                    tomar_foto("Sale operador por jerarquía.")
                pila.append(token)
                tomar_foto(f"Operador '{token}' a la pila.")

        while pila:
            salida.append(pila.pop())
            tomar_foto("Vaciando pila final.")
        return frames

    def dibujar_nodo_sincronizado(self, nodo, escena, x, y, dx, token_activo):
        """Dibuja nodos y los ilumina en dorado si coinciden con el token activo"""
        if not nodo: return
        radio = 18

        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 50, QPen(QColor("#6C5CE7"), 2))
            self.dibujar_nodo_sincronizado(nodo.izquierda, escena, x - dx, y + 50, dx / 2, token_activo)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 50, QPen(QColor("#6C5CE7"), 2))
            self.dibujar_nodo_sincronizado(nodo.derecha, escena, x + dx, y + 50, dx / 2, token_activo)

        # Lógica de iluminación
        es_activo = (str(nodo.valor) == token_activo)
        color_fondo = "#FFD700" if es_activo else "#1E1E1E"  # Dorado si está activo
        color_texto = "#000000" if es_activo else "#FFFFFF"

        escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, QPen(Qt.GlobalColor.white),
                          QBrush(QColor(color_fondo)))
        txt = escena.addText(str(nodo.valor), QFont("Arial", 9, QFont.Weight.Bold))
        txt.setDefaultTextColor(QColor(color_texto))
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)

    def validar_input_m4(self, texto):
        if not texto: return
        char_actual = texto[-1]
        self.int_NodoANota.blockSignals(True)
        if char_actual in self.calc.preferencia or char_actual == '√':
            if len(texto) > 1: self.int_NodoANota.setText(char_actual)
        elif char_actual.isalpha():
            if len(texto) > 1: self.int_NodoANota.setText(char_actual)
            if char_actual.islower(): self.int_NodoANota.setText(char_actual.upper())
        elif char_actual.isdigit():
            solo_numeros = "".join(filter(str.isdigit, texto))
            self.int_NodoANota.setText(solo_numeros)
        else:
            self.int_NodoANota.setText(texto[:-1])
        self.int_NodoANota.blockSignals(False)

    def agregar_nodo_m4(self):
        valor = self.int_NodoANota.text().strip()
        if not valor: return

        if self.arbol_m4 is None:
            es_operador = valor in self.calc.preferencia or valor == '√'
            if not es_operador:
                QtWidgets.QMessageBox.warning(self, "Inválido", "La raíz debe ser un operador.")
                self.int_NodoANota.clear()
                return
            self.arbol_m4 = Nodo(valor)
            self.nodo_sel_m4 = self.arbol_m4
        elif self.nodo_sel_m4:
            if self.calc.es_operando(self.nodo_sel_m4.valor):
                QtWidgets.QMessageBox.warning(self, "Inválido", "Los números/letras no tienen hijos.")
                self.int_NodoANota.clear()
                return
            if self.nodo_sel_m4.izquierda is None:
                self.nodo_sel_m4.izquierda = Nodo(valor)
            elif self.nodo_sel_m4.derecha is None:
                self.nodo_sel_m4.derecha = Nodo(valor)
            else:
                QtWidgets.QMessageBox.information(self, "Lleno", "El operador ya tiene dos hijos.")

        self.int_NodoANota.clear()
        self.actualizar_vistas_m4()

    def eliminar_nodo_m4(self):
        if self.nodo_sel_m4 and self.arbol_m4:
            if self.nodo_sel_m4 == self.arbol_m4:
                self.arbol_m4 = None
            else:
                self.eliminar_referencia(self.arbol_m4, self.nodo_sel_m4)
            self.nodo_sel_m4 = None
            self.actualizar_vistas_m4()

    def limpiar_arbol_m4(self):
        self.arbol_m4 = None
        self.nodo_sel_m4 = None
        self.actualizar_vistas_m4()

    def actualizar_vistas_m4(self):
        nueva_escena = QGraphicsScene(self)
        self.grap_3.setScene(nueva_escena)
        self.mapa_items_m4 = {}

        if self.arbol_m4:
            profundidad = self.obtener_profundidad(self.arbol_m4)
            dx_inicial = 35 * (2 ** (profundidad - 2)) if profundidad > 1 else 0

            # Dibujamos en el lado izquierdo (-100 en X)
            self.dibujar_nodo_m4(self.arbol_m4, nueva_escena, -100, 20, dx_inicial)
            nueva_escena.selectionChanged.connect(self.al_seleccionar_nodo_m4)

            # Extraemos la expresión para prepararla para la animación de las pilas
            try:
                infija = " ".join(self.calc.obtener_infija(self.arbol_m4))
            except:
                infija = "(Expresión Incompleta)"

            # Mostramos en area_res4
            proc = f"🌳 ÁRBOL CONSTRUIDO:\nExpresión: {infija}\n\n(A la espera de los botones de animación...)"
            try:
                self.actualizar_texto_resultado(self.area_res4, proc)
            except AttributeError:
                pass
        else:
            self.limpiar_area_resultado(self.area_res4)

    def dibujar_nodo_m4(self, nodo, escena, x, y, dx):
        from PyQt6.QtWidgets import QGraphicsItem
        if not nodo: return
        radio = 18
        pen = QPen(QColor("#6C5CE7"), 2)

        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 45, pen)
            self.dibujar_nodo_m4(nodo.izquierda, escena, x - dx, y + 45, dx / 2)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 45, pen)
            self.dibujar_nodo_m4(nodo.derecha, escena, x + dx, y + 45, dx / 2)

        elipse = escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, QPen(Qt.GlobalColor.white))

        es_seleccionado = (nodo == self.nodo_sel_m4)
        color_fondo = "#00E676" if es_seleccionado else "#1E1E1E"
        color_texto = "#000000" if es_seleccionado else "#FFFFFF"

        elipse.setBrush(QBrush(QColor(color_fondo)))
        elipse.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        txt = escena.addText(str(nodo.valor), QFont("Arial", 10, QFont.Weight.Bold))
        txt.setDefaultTextColor(QColor(color_texto))
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)

        self.mapa_items_m4[elipse] = (nodo, txt)

    def al_seleccionar_nodo_m4(self):
        if not self.grap_3.scene(): return
        items = self.grap_3.scene().selectedItems()

        if items:
            datos = self.mapa_items_m4.get(items[0])
            if datos:
                self.nodo_sel_m4 = datos[0]
                for elipse, (nodo, txt) in self.mapa_items_m4.items():
                    if nodo == self.nodo_sel_m4:
                        elipse.setBrush(QBrush(QColor("#00E676")))
                        txt.setDefaultTextColor(QColor("#000000"))
                    else:
                        elipse.setBrush(QBrush(QColor("#1E1E1E")))
                        txt.setDefaultTextColor(QColor("#FFFFFF"))

    def generar_intermedio(self, tipo):
        ecuacion = self.inp_ExpCodigo.text().strip()
        if not ecuacion:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Escribe una expresión primero.")
            return

        try:
            posfija = self.calc.infija_a_posfija(ecuacion)
            datos = []
            cabeceras = []

            # Diccionario para guardar los resultados de T0, T1, (0), (1), etc.
            valores_pasos = {}
            procedimiento = f"⚙️ PROCEDIMIENTO DETALLADO ({tipo.upper()}):\n\n"

            infija_tokens = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", ecuacion)

            if tipo == "Cuadruplos":
                cabeceras = ["ID", "Operador", "Op1", "Op2", "Resultado"]
                filas = self.calc.generar_cuadruplos_estricto(infija_tokens)
                datos = [[str(i)] + f for i, f in enumerate(filas)]
            elif tipo == "Triplos":
                cabeceras = ["ID", "Operador", "Op1", "Op2"]
                filas = self.calc.generar_triplos_estricto(infija_tokens)
                datos = [[str(i)] + f for i, f in enumerate(filas)]
            elif tipo == "CodigoP":
                cabeceras = ["ID", "Instrucción", "Variable", "-", "-"]
                # Usamos los cuádruplos como base para que el Código P respete el orden humano
                cuad_base = self.calc.generar_cuadruplos_estricto(infija_tokens)
                filas = self.calc.generar_codigo_p_estricto(cuad_base)
                datos = [[str(i)] + f for i, f in enumerate(filas)]

            # --- Llenado de Tabla tab_1 ---
            self.tab_1.setRowCount(len(datos))
            self.tab_1.setColumnCount(len(cabeceras))
            self.tab_1.setHorizontalHeaderLabels(cabeceras)
            header = self.tab_1.horizontalHeader()
            if len(cabeceras) > 0:
                # La primera columna (ID) se ajusta al texto
                header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
                # Las demás se estiran para llenar el resto
                for i in range(1, len(cabeceras)):
                    header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Stretch)

            for i, fila in enumerate(datos):
                for j, valor in enumerate(fila):
                    item = QtWidgets.QTableWidgetItem(str(valor))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    item.setForeground(QBrush(QColor("#FFFFFF")))
                    self.tab_1.setItem(i, j, item)

            infija_tokens = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", ecuacion)
            res_final, pasos = self.calc.evaluar_jerarquia_estricta(infija_tokens)

            proc = f"⚙️ CÓDIGO {tipo.upper()} GENERADO EN LA TABLA.\n\n"
            proc += "🧮 RESOLUCIÓN MATEMÁTICA (JERARQUÍA ESTRICTA):\n\n"
            for i, paso in enumerate(pasos):
                proc += f" Paso {i + 1}: {paso}\n"

            proc += "\n" + ("=" * 45) + f"\n🎯 RESULTADO FINAL: {res_final}"

            self.actualizar_texto_resultado(self.area_res5, proc)

        except Exception as e:
            print(f"Error: {e}")

    def mostrar_estadisticas(self):
        """Muestra las estadísticas en una ventana con scroll y diseño oscuro"""
        try:
            reporte = self.analizador.generar_reporte_codigo_fuente()

            # 1. Crear ventana de diálogo personalizada
            dialogo = QtWidgets.QDialog(self)
            dialogo.setWindowTitle("Estadísticas del Compilador")
            dialogo.resize(450, 550)  # Tamaño ideal para lectura
            dialogo.setStyleSheet("background-color: #2D2D2D;")

            layout = QtWidgets.QVBoxLayout(dialogo)

            # 2. Crear área de texto con Scroll Integrado
            area_texto = QtWidgets.QTextEdit(dialogo)
            area_texto.setReadOnly(True)
            area_texto.setPlainText(reporte)

            # Estilo oscuro y verde neón para combinar con tu app
            area_texto.setStyleSheet("""
                QTextEdit {
                    background-color: #1E1E1E;
                    color: #00E676;
                    font-family: 'Consolas';
                    font-size: 14px;
                    border: 2px solid #6C5CE7;
                    padding: 10px;
                }
                QScrollBar:vertical {
                    background: #2D2D2D;
                    width: 14px;
                }
                QScrollBar::handle:vertical {
                    background: #6C5CE7;
                    border-radius: 5px;
                }
            """)
            layout.addWidget(area_texto)

            # 3. Botón para cerrar
            btn_cerrar = QtWidgets.QPushButton("Aceptar", dialogo)
            btn_cerrar.setStyleSheet("""
                QPushButton {
                    background-color: #6C5CE7;
                    color: white;
                    font-weight: bold;
                    font-size: 14px;
                    padding: 10px;
                    border-radius: 5px;
                }
                QPushButton:hover { background-color: #5A4BCE; }
            """)
            btn_cerrar.clicked.connect(dialogo.accept)
            layout.addWidget(btn_cerrar)

            # 4. Mostrar la ventana
            dialogo.exec()

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error", f"Fallo al generar reporte: {e}")

    #modulo 6
    def agregar_nodo_m6(self):
        # Si la tabla estaba visible, regresamos al árbol para seguir editando
        self.stackedWidget_2.setCurrentIndex(0)  # stackedWidget interno

        valor = self.int_NodoACode.text().strip()  # <--- Verifica este nombre
        if not valor: return

        if self.arbol_m6 is None:
            if not (valor in self.calc.preferencia or valor == '√'):
                QtWidgets.QMessageBox.warning(self, "Error", "La raíz debe ser un operador.")
                return
            self.arbol_m6 = Nodo(valor)
            self.nodo_sel_m6 = self.arbol_m6
        elif self.nodo_sel_m6:
            if self.calc.es_operando(self.nodo_sel_m6.valor):
                QtWidgets.QMessageBox.warning(self, "Error", "Las hojas no tienen hijos.")
                return
            if self.nodo_sel_m6.izquierda is None:
                self.nodo_sel_m6.izquierda = Nodo(valor)
            elif self.nodo_sel_m6.derecha is None:
                self.nodo_sel_m6.derecha = Nodo(valor)

        self.int_NodoACode.clear()
        self.actualizar_vistas_m6()

    def eliminar_nodo_m6(self):
        if self.nodo_sel_m6 and self.arbol_m6:
            if self.nodo_sel_m6 == self.arbol_m6:
                self.arbol_m6 = None
            else:
                self.eliminar_referencia(self.arbol_m6, self.nodo_sel_m6)
            self.nodo_sel_m6 = None
            self.actualizar_vistas_m6()

    def limpiar_arbol_m6(self):
        self.arbol_m6 = None
        self.nodo_sel_m6 = None
        self.actualizar_vistas_m6()
        self.stackedWidget_2.setCurrentIndex(0)

    def actualizar_vistas_m6(self):
        escena = QGraphicsScene(self)
        self.grap_Arbol4.setScene(escena)
        self.mapa_items_m6 = {}
        if self.arbol_m6:
            prof = self.obtener_profundidad(self.arbol_m6)
            dx = 35 * (2 ** (prof - 2)) if prof > 1 else 0
            self.dibujar_nodo_m6(self.arbol_m6, escena, 0, 0, dx)
            escena.selectionChanged.connect(self.al_seleccionar_m6)

    def dibujar_nodo_m6(self, nodo, escena, x, y, dx):
        from PyQt6.QtWidgets import QGraphicsItem
        if not nodo: return
        radio = 18
        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 50, QPen(QColor("#6C5CE7"), 2))
            self.dibujar_nodo_m6(nodo.izquierda, escena, x - dx, y + 50, dx / 2)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 50, QPen(QColor("#6C5CE7"), 2))
            self.dibujar_nodo_m6(nodo.derecha, escena, x + dx, y + 50, dx / 2)

        elipse = escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, QPen(Qt.GlobalColor.white))
        sel = (nodo == self.nodo_sel_m6)
        elipse.setBrush(QBrush(QColor("#00E676" if sel else "#1E1E1E")))
        elipse.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        txt = escena.addText(str(nodo.valor), QFont("Arial", 10, QFont.Weight.Bold))
        txt.setDefaultTextColor(QColor("#000000" if sel else "#FFFFFF"))
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)
        self.mapa_items_m6[elipse] = (nodo, txt)

    def al_seleccionar_m6(self):
        if not self.grap_Arbol4.scene(): return
        items = self.grap_Arbol4.scene().selectedItems()
        if items:
            datos = self.mapa_items_m6.get(items[0])
            if datos:
                self.nodo_sel_m6 = datos[0]
                for elipse, (n, t) in self.mapa_items_m6.items():
                    sel = (n == self.nodo_sel_m6)
                    elipse.setBrush(QBrush(QColor("#00E676" if sel else "#1E1E1E")))
                    t.setDefaultTextColor(QColor("#000000" if sel else "#FFFFFF"))

    def generar_m6(self, tipo):
        """Genera el código intermedio (Cuadruplos, Triplos o Código P) desde el Árbol Manual"""
        if not self.arbol_m6:
            QtWidgets.QMessageBox.warning(self, "Aviso", "Primero construye el árbol en el canvas.")
            return

        # Cambiamos a la vista de tabla en el stackedWidget_2 (página 1)
        self.stackedWidget_2.setCurrentIndex(1)

        try:
            # 1. Obtenemos la posfija directamente del árbol construido
            posfija = self.calc.obtener_posfija(self.arbol_m6)

            datos = []
            cabeceras = []
            valores_pasos = {}
            proc = f"🧪 RESOLUCIÓN DESDE EL ÁRBOL ({tipo.upper()}):\n\n"

            # --- LÓGICA DE CUADRUPLOS ---
            if tipo == "Cuadruplos":
                cabeceras = ["ID", "Operador", "Op1", "Op2", "Resultado"]
                filas = self.calc.generar_cuadruplos(posfija)
                for i, f in enumerate(filas):
                    v1 = valores_pasos.get(f[1], f[1])
                    v2 = valores_pasos.get(f[2], f[2])
                    res = self.calc.resolver_operacion_simple(f[0], v1, v2)
                    valores_pasos[f[3]] = res
                    datos.append([str(i), f[0], f[1], f[2], f[3]])
                    proc += f" {i}. Se aplica '{f[0]}' a '{f[1]}' y '{f[2]}', guardando en {f[3]}. -> {res}\n"

            # --- LÓGICA DE TRIPLOS ---
            elif tipo == "Triplos":
                cabeceras = ["ID", "Operador", "Op1", "Op2"]
                filas = self.calc.generar_triplos(posfija)
                for i, f in enumerate(filas):
                    v1 = valores_pasos.get(f[1], f[1])
                    v2 = valores_pasos.get(f[2], f[2])
                    res = self.calc.resolver_operacion_simple(f[0], v1, v2)
                    valores_pasos[f"({i})"] = res  # Los triplos se referencian por su ID entre paréntesis
                    datos.append([str(i), f[0], f[1], f[2]])
                    proc += f" {i}. Operación '{f[0]}' entre '{f[1]}' y '{f[2]}'. -> {res}\n"

            # --- LÓGICA DE CÓDIGO P ---
            elif tipo == "CodigoP":
                cabeceras = ["ID", "Instrucción", "Variable", "-"]
                filas = self.calc.generar_codigo_p(posfija)
                pila_sim = []
                for i, f in enumerate(filas):
                    if f[0] == "LOD":
                        pila_sim.append(f[1])
                        proc += f" {i}. LOD: Carga '{f[1]}' a la pila.\n"
                    elif f[0] == "STO":
                        proc += f" {i}. STO: Almacena resultado en '{f[1]}'.\n"
                    else:
                        op2 = pila_sim.pop()
                        op1 = pila_sim.pop()
                        simb = {'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/', 'POW': '^'}.get(f[0], f[0])
                        res = self.calc.resolver_operacion_simple(simb, op1, op2)
                        pila_sim.append(str(res))
                        proc += f" {i}. {f[0]}: Operación '{op1}' {simb} '{op2}'. -> {res}\n"
                    datos.append([str(i), f[0], f[1], "-"])
                valores_pasos["final"] = pila_sim[-1] if pila_sim else "0"

            # 2. Configuración y Llenado de la Tabla tab_2
            self.tab_2.setRowCount(len(datos))
            self.tab_2.setColumnCount(len(cabeceras))
            self.tab_2.setHorizontalHeaderLabels(cabeceras)

            # Ajuste de ancho de columnas
            header = self.tab_2.horizontalHeader()
            if len(cabeceras) > 0:
                header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
                for j in range(1, len(cabeceras)):
                    header.setSectionResizeMode(j, QtWidgets.QHeaderView.ResizeMode.Stretch)

            for i, fila in enumerate(datos):
                for j, val in enumerate(fila):
                    item = QtWidgets.QTableWidgetItem(str(val))
                    item.setForeground(QBrush(QColor("#FFFFFF")))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tab_2.setItem(i, j, item)

            # 3. Mostrar el Resultado Final en el panel
            tokens_infijos = self.calc.obtener_infija(self.arbol_m6)
            res_final, pasos = self.calc.evaluar_jerarquia_estricta(tokens_infijos)

            proc = f"🧪 CÓDIGO {tipo.upper()} GENERADO DESDE EL ÁRBOL.\n(Ver detalles en la tabla adjunta).\n\n"
            proc += "🧮 RESOLUCIÓN MATEMÁTICA (JERARQUÍA ESTRICTA):\n\n"
            for i, paso in enumerate(pasos):
                proc += f" Paso {i + 1}: {paso}\n"

            proc += "\n" + ("=" * 45) + f"\n🎯 RESULTADO FINAL: {res_final}"

            self.actualizar_texto_resultado(self.area_res6, proc)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Fallo al generar código: {e}")

    def validar_input_m6(self, texto):
        """Vigila lo que escribe el usuario en el Módulo 6 y bloquea errores"""
        if not texto: return
        char_actual = texto[-1]

        self.int_NodoACode.blockSignals(True)

        if char_actual in self.calc.preferencia or char_actual == '√':
            if len(texto) > 1: self.int_NodoACode.setText(char_actual)
        elif char_actual.isalpha():
            if len(texto) > 1: self.int_NodoACode.setText(char_actual)
            if char_actual.islower(): self.int_NodoACode.setText(char_actual.upper())
        elif char_actual.isdigit():
            solo_numeros = "".join(filter(str.isdigit, texto))
            self.int_NodoACode.setText(solo_numeros)
        else:
            self.int_NodoACode.setText(texto[:-1])

        self.int_NodoACode.blockSignals(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CompiladorApp()
    window.show()
    sys.exit(app.exec())