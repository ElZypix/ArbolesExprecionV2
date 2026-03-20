import re
import os


class AnalizadorLexico:
    def __init__(self):
        # Aquí le decimos qué archivos .py de tu proyecto debe leer
        self.archivos_proyecto = [
            'main.py',
            'Logica/Arboles.py',
            'Logica/Analizador.py',
            'Logica/Generador.py',
            'Logica/Nodo.py'
        ]
        self.palabras_control = {'if', 'else', 'elif', 'while', 'for', 'try', 'except', 'return', 'break', 'continue',
                                 'class', 'import', 'from', 'pass', 'def'}

    def generar_reporte_codigo_fuente(self):
        conteos = {
            "Variables (Identificadores)": 0,
            "Constantes (Números/Textos)": 0,
            "Expresiones (Operadores)": 0,
            "Inst. de Asignación (=)": 0,
            "Inst. de Control (if, for...)": 0,
            "Funciones": 0
        }

        for ruta in self.archivos_proyecto:
            if not os.path.exists(ruta): continue
            with open(ruta, 'r', encoding='utf-8') as archivo:
                codigo = archivo.read()
                codigo_limpio = re.sub(r'\"[^\"]*\"|\'[^\']*\'', '""', codigo)

                # Constantes
                conteos["Constantes (Números/Textos)"] += len(re.findall(r'\"[^\"]*\"|\'[^\']*\'', codigo)) + len(
                    re.findall(r'\b\d+(?:\.\d+)?\b', codigo))
                # Asignaciones
                conteos["Inst. de Asignación (=)"] += len(re.findall(r'(?<![=<>!])=(?![=])', codigo_limpio))
                # Funciones
                funciones = re.findall(r'\b([a-zA-Z_]\w*)\s*\(', codigo_limpio)
                conteos["Funciones"] += len(funciones)

                # Operadores
                for op in ['+', '-', '*', '/', '%', '^', '<', '>', '==', '!=', '<=', '>=']:
                    conteos["Expresiones (Operadores)"] += codigo_limpio.count(op)

                # Variables y Control
                palabras = re.findall(r'\b[a-zA-Z_]\w*\b', codigo_limpio)
                for p in palabras:
                    if p in self.palabras_control:
                        conteos["Inst. de Control (if, for...)"] += 1
                    elif p not in funciones:
                        conteos["Variables (Identificadores)"] += 1

        # Construir reporte sin f-strings complejos para compatibilidad
        res = "📊 ESTADÍSTICAS GLOBALES DEL CÓDIGO FUENTE (.py)\n\n"
        for k, v in conteos.items():
            res += f" ├─ {k}: {v}\n"
        return res