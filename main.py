import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene, QLabel, QMessageBox, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QTimer


from Logica.Arboles import CalculadoraArbol
from Logica.Nodo import Nodo
from Logica.Analizador import AnalizadorLexico


class CompiladorApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("Gui/interfaz.ui", self)

        self.calc = CalculadoraArbol()
        self.lexico = AnalizadorLexico()


        # --- CONEXIÓN MÓDULO 1 ---
        # Cambia 'inp_Exp' por el nombre real de tu QLineEdit en la Pestaña 1 si es distinto
        self.inp_Exp.textChanged.connect(self.ejecutar_modulo_1)

        # --- VARIABLES MÓDULO 2 ---
        self.arbol_manual = None
        self.nodo_seleccionado = None
        self.mapa_items_manual = {}  # Para rastrear qué círculo pertenece a qué nodo

        # --- NAVEGACIÓN ---
        self.btn_AExpresion.clicked.connect(lambda: self.cambiar_pestaña(1))

        # --- CONEXIONES MÓDULO 2 ---
        self.btn_agregarAexp.clicked.connect(self.agregar_nodo_manual)
        self.btn_EliminarAexp.clicked.connect(self.eliminar_nodo_manual)
        self.btn_limpiarAexp.clicked.connect(self.limpiar_arbol_manual)

        # Validación en tiempo real del input
        self.inp_nod.textChanged.connect(self.validar_input_manual)

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

    def cambiar_pestaña(self, indice):
        """Navega entre las páginas del stacked widget"""
        self.stackedWidget.setCurrentIndex(indice)

    def eliminar_nodo_manual(self):
        """Elimina el nodo seleccionado y sus hijos del árbol manual"""
        if self.nodo_seleccionado and self.arbol_manual:
            if self.nodo_seleccionado == self.arbol_manual:
                self.arbol_manual = None
            else:
                self.eliminar_referencia(self.arbol_manual, self.nodo_seleccionado)
            self.nodo_seleccionado = None
            self.actualizar_vistas_manual()

    def eliminar_referencia(self, nodo_actual, nodo_a_borrar):
        """Busca al padre del nodo a borrar y corta la conexión"""
        if not nodo_actual: return
        if nodo_actual.izquierda == nodo_a_borrar:
            nodo_actual.izquierda = None
            return
        if nodo_actual.derecha == nodo_a_borrar:
            nodo_actual.derecha = None
            return
        self.eliminar_referencia(nodo_actual.izquierda, nodo_a_borrar)
        self.eliminar_referencia(nodo_actual.derecha, nodo_a_borrar)

    def limpiar_arbol_manual(self):
        """Borra todo el árbol de la pantalla"""
        self.arbol_manual = None
        self.nodo_seleccionado = None
        self.actualizar_vistas_manual()

    def validar_input_manual(self, texto):
        """Aplica filtros estrictos al input del nodo manual"""
        if not texto: return

        char_actual = texto[-1]  # El último carácter escrito

        # 1. Si es un Operador: Solo permite 1 carácter
        if char_actual in self.calc.preferencia or char_actual == '√':
            if len(texto) > 1:
                self.inp_nod.setText(char_actual)

        # 2. Si es una Letra: Solo permite 1 carácter y bloquea números/símbolos
        elif char_actual.isalpha():
            if len(texto) > 1:
                self.inp_nod.setText(char_actual)
            # Asegura que sea mayúscula para consistencia
            if char_actual.islower():
                self.inp_nod.setText(char_actual.upper())

        # 3. Si es un Número: Permite varios dígitos pero bloquea letras/símbolos
        elif char_actual.isdigit():
            # Filtra cualquier cosa que no sea número del texto completo
            solo_numeros = "".join(filter(str.isdigit, texto))
            self.inp_nod.setText(solo_numeros)

        # 4. Cualquier otra cosa: Se borra
        else:
            self.inp_nod.setText(texto[:-1])

    def agregar_nodo_manual(self):
        valor = self.inp_nod.text().strip()
        if not valor: return

        if self.arbol_manual is None:
            # Creamos la raíz
            self.arbol_manual = Nodo(valor)
            self.nodo_seleccionado = self.arbol_manual
        elif self.nodo_seleccionado:
            # REGLA: Los operandos (hojas) no pueden tener hijos
            if self.calc.es_operando(self.nodo_seleccionado.valor):
                QMessageBox.warning(self, "Acción Inválida", "Los números y variables no pueden tener hijos.")
                self.inp_nod.clear()
                return

            # Agregamos hijo izquierdo o derecho
            if self.nodo_seleccionado.izquierda is None:
                self.nodo_seleccionado.izquierda = Nodo(valor)
            elif self.nodo_seleccionado.derecha is None:
                self.nodo_seleccionado.derecha = Nodo(valor)
            else:
                QMessageBox.information(self, "Nodo Lleno", "Este operador ya tiene sus dos hijos.")

        self.inp_nod.clear()
        self.actualizar_vistas_manual()

    def al_seleccionar_nodo_manual(self):
        """Maneja la selección con delay para evitar crasheos de memoria"""
        items = self.grap_Arbol2.scene().selectedItems()
        if items:
            self.nodo_seleccionado = self.mapa_items_manual.get(items[0])
            # Delay de 10ms antes de redibujar
            QTimer.singleShot(10, self.actualizar_vistas_manual)

    def actualizar_vistas_manual(self):
        """Dibuja el árbol manual y muestra la resolución paso a paso"""
        nueva_escena = QGraphicsScene()
        self.grap_Arbol2.setScene(nueva_escena)
        self.mapa_items_manual = {}

        if self.arbol_manual:
            profundidad = self.obtener_profundidad(self.arbol_manual)
            dx_inicial = 35 * (2 ** (profundidad - 2)) if profundidad > 1 else 0
            self.dibujar_nodo_interactivo(self.arbol_manual, nueva_escena, 0, 0, dx_inicial)

            # Conectar el evento de selección
            nueva_escena.selectionChanged.connect(self.al_seleccionar_nodo_manual)

            # --- RESOLUCIÓN PASO A PASO ---
            res, pasos = self.calc.evaluar_con_pasos(self.arbol_manual)
            infija = " ".join(self.calc.obtener_infija(self.arbol_manual))

            proc = f"✅ Expresión Construida: {infija}\n\n⚙️ RESOLUCIÓN:\n"
            proc += "\n".join(pasos) if pasos else "   (Esperando más nodos...)"
            proc += f"\n\n🎯 RESULTADO FINAL: {res}"
            self.actualizar_texto_resultado(self.area_res2, proc)
        else:
            self.limpiar_area_resultado(self.area_res2)

    def dibujar_nodo_interactivo(self, nodo, escena, x, y, dx):
        """Dibuja nodos que se pueden seleccionar con el mouse"""
        if not nodo: return
        radio = 20
        pen = QPen(QColor("#6C5CE7"), 2)

        if nodo.izquierda:
            escena.addLine(x, y, x - dx, y + 60, pen)
            self.dibujar_nodo_interactivo(nodo.izquierda, escena, x - dx, y + 60, dx / 2)
        if nodo.derecha:
            escena.addLine(x, y, x + dx, y + 60, pen)
            self.dibujar_nodo_interactivo(nodo.derecha, escena, x + dx, y + 60, dx / 2)

        # Círculo interactivo
        elipse = escena.addEllipse(x - radio, y - radio, radio * 2, radio * 2, QPen(Qt.GlobalColor.white))
        color = "#00E676" if nodo == self.nodo_seleccionado else "#1E1E1E"
        elipse.setBrush(QBrush(QColor(color)))
        elipse.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        # Guardamos la relación entre el círculo gráfico y el objeto Nodo
        self.mapa_items_manual[elipse] = nodo

        txt = escena.addText(str(nodo.valor), QFont("Arial", 10, QFont.Weight.Bold))
        txt.setDefaultTextColor(Qt.GlobalColor.white)
        txt.setPos(x - txt.boundingRect().width() / 2, y - txt.boundingRect().height() / 2)

    def mostrar_estadisticas(self):
        """Muestra las estadísticas del CÓDIGO FUENTE en un cuadro de diálogo"""

        try:
            reporte = self.lexico.generar_reporte_codigo_fuente()
            QMessageBox.information(self, "Estadísticas del Compilador", reporte)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo analizar el código: {e}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CompiladorApp()
    window.show()
    sys.exit(app.exec())