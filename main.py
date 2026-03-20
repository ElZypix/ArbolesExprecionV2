import sys
import re
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene, QLabel
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtCore import Qt, QTimer

from Logica.Arboles import CalculadoraArbol
from Logica.Nodo import Nodo


class CompiladorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Gui/interfaz.ui", self)

        self.calc = CalculadoraArbol()


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

    def ejecutar_modulo_1(self, ecuacion):
        """Lógica estable del Módulo 1: Expresión -> Árbol + Resolución Paso a Paso"""
        texto_limpio = ecuacion.strip()

        # Anti-Crasheo: Si el usuario borra todo, limpiamos de forma segura
        if not texto_limpio:
            if self.grap_GenArbol1.scene():
                self.grap_GenArbol1.scene().clear()
            self.limpiar_area_resultado(self.area_Res1)
            return

        try:
            # 1. Construir Lógica
            posfija = self.calc.infija_a_posfija(texto_limpio)
            arbol = self.calc.construir_arbol(posfija)

            if arbol:
                # 2. Dibujar Árbol (en escena nueva para evitar conflictos)
                nueva_escena = QGraphicsScene()
                self.grap_GenArbol1.setScene(nueva_escena)

                # --- MAGIA ANTI-COLISIONES ---
                profundidad = self.obtener_profundidad(arbol)
                # Entre más profundo sea el árbol, más se abren las ramas iniciales (dx)
                dx_inicial = 35 * (2 ** (profundidad - 2)) if profundidad > 1 else 0

                self.dibujar_nodo(arbol, nueva_escena, 0, 0, dx_inicial)

                # 3. Evaluar Matemáticamente / Algebraicamente
                res_final, pasos = self.calc.evaluar_con_pasos(arbol)

                # 4. Construir el panel de Procedimiento
                proc = "⚙️ PROCEDIMIENTO PASO A PASO:\n\n"
                proc += f"1. Infix ➔ Postfix:\n   {' '.join(posfija)}\n\n"
                proc += "2. Construcción del Árbol en Memoria\n\n"
                proc += "3. Resolución:\n"

                if pasos:
                    proc += "\n".join(pasos)
                else:
                    proc += "   (No hay operaciones pendientes)"

                proc += f"\n\n🎯 RESULTADO FINAL: {res_final}"

                self.actualizar_texto_resultado(self.area_Res1, proc)

        except Exception:
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
        nueva_escena = QGraphicsScene(self)  # <-- (self) evita el crasheo de memoria
        self.grap_Arbol2.setScene(nueva_escena)
        self.mapa_items_manual = {}

        if self.arbol_manual:
            profundidad = self.obtener_profundidad(self.arbol_manual)
            dx_inicial = 35 * (2 ** (profundidad - 2)) if profundidad > 1 else 0
            self.dibujar_nodo_interactivo(self.arbol_manual, nueva_escena, 0, 0, dx_inicial)

            # Conectamos el clic al sistema seguro
            nueva_escena.selectionChanged.connect(self.al_seleccionar_nodo_manual)

            res, pasos = self.calc.evaluar_con_pasos(self.arbol_manual)
            try:
                infija = " ".join(self.calc.obtener_infija(self.arbol_manual))
            except:
                infija = "(Expresión Incompleta)"

            proc = f"✅ Expresión Construida: {infija}\n\n⚙️ RESOLUCIÓN:\n"
            proc += "\n".join(pasos) if pasos else "   (Esperando más nodos...)"
            proc += f"\n\n🎯 RESULTADO FINAL: {res}"
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

        # ==========================================
        # NUEVO: RESOLUCIÓN MATEMÁTICA Y SIMPLIFICACIÓN
        # ==========================================
        try:
            # Usamos el cerebro del Módulo 1 para resolver la ecuación silenciosamente
            posfija_temp = self.calc.infija_a_posfija(ecuacion)
            arbol_temp = self.calc.construir_arbol(posfija_temp)
            res_eval, pasos_eval = self.calc.evaluar_con_pasos(arbol_temp)

            self.resolucion_m3 = "🧮 RESOLUCIÓN MATEMÁTICA Y SIMPLIFICACIÓN:\n"
            if pasos_eval:
                self.resolucion_m3 += "\n".join(pasos_eval)
            else:
                self.resolucion_m3 += "   (Sin operaciones pendientes)"
            self.resolucion_m3 += f"\n\n🎯 RESULTADO FINAL: {res_eval}"
        except Exception:
            self.resolucion_m3 = "🧮 RESOLUCIÓN MATEMÁTICA:\n   (No se pudo evaluar matemáticamente)"
        # ==========================================

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
    def generar_frames_postfija(self, tokens):
        frames = []
        entrada = list(tokens)
        pila = []
        salida = []
        log = "Iniciando Shunting Yard (Infija -> Postfija)\n"

        def tomar_foto(mensaje=""):
            nonlocal log
            if mensaje: log += " > " + mensaje + "\n"
            frames.append({"entrada": list(entrada), "pila_operadores": list(pila), "salida": list(salida), "log": log})

        tomar_foto()

        for token in tokens:
            entrada.pop(0)
            if self.calc.es_operando(token):
                salida.append(token)
                tomar_foto(f"El operando '{token}' pasa directo a la salida.")
            elif token == '(':
                pila.append(token)
                tomar_foto("Se abre paréntesis, entra a la pila.")
            elif token == ')':
                while pila and pila[-1] != '(':
                    salida.append(pila.pop())
                    tomar_foto("Se vacía la pila hasta el paréntesis.")
                if pila: pila.pop()
            else:
                while (pila and pila[-1] != '(' and
                       self.calc.preferencia.get(pila[-1], 0) >= self.calc.preferencia.get(token, 0)):
                    salida.append(pila.pop())
                    tomar_foto(f"Sale operador por jerarquía.")
                pila.append(token)
                tomar_foto(f"Operador '{token}' entra a la pila.")

        while pila:
            salida.append(pila.pop())
            tomar_foto("Vaciando restos de la pila.")

        return frames

    def generar_frames_prefija(self, tokens):
        frames = []
        entrada = list(tokens[::-1])
        for i in range(len(entrada)):
            if entrada[i] == '(': entrada[i] = ')'
            elif entrada[i] == ')': entrada[i] = '('

        pila = []
        salida = []
        log = "Iniciando Shunting Yard Inverso (Infija -> Prefija)\nSe lee de Derecha a Izquierda.\n"

        def tomar_foto(mensaje=""):
            nonlocal log
            if mensaje: log += " > " + mensaje + "\n"
            frames.append({
                "entrada": list(entrada[::-1]),
                "pila_operadores": list(pila),
                "salida": list(salida[::-1]),
                "log": log
            })

        tomar_foto()

        for token in list(entrada):
            entrada.pop(0)
            if self.calc.es_operando(token):
                salida.append(token)
                tomar_foto(f"Operando '{token}' a la salida.")
            elif token == '(':
                pila.append(token)
            elif token == ')':
                while pila and pila[-1] != '(': salida.append(pila.pop())
                if pila: pila.pop()
            else:
                while (pila and pila[-1] != '(' and
                       self.calc.preferencia.get(pila[-1], 0) > self.calc.preferencia.get(token, 0)):
                    salida.append(pila.pop())
                pila.append(token)
                tomar_foto(f"Operador '{token}' a la pila.")

        while pila: salida.append(pila.pop())
        tomar_foto("Se invierte el resultado final.")
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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CompiladorApp()
    window.show()
    sys.exit(app.exec())