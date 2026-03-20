import sys
from PyQt6 import QtWidgets, uic
from PyQt6.QtWidgets import QGraphicsScene, QLabel
from PyQt6.QtGui import QPen, QBrush, QColor, QFont
from PyQt6.QtCore import Qt

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


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CompiladorApp()
    window.show()
    sys.exit(app.exec())