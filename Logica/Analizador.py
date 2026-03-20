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
        import re, os
        # Diccionario con las palabras exactas que la ingeniera quiere ver
        keywords = {
            "Sentencias de Control": ["if", "elif", "else", "match", "case"],
            "Ciclos e Iteración": ["for", "while", "continue", "break"],
            "Estructura y Clases": ["class", "def", "import", "from", "lambda"],
            "Manejo de Errores": ["try", "except", "finally", "raise", "with"]
        }

        reporte = "📊 DESGLOSE TÉCNICO DEL CÓDIGO\n" + "=" * 35 + "\n"
        totales = {cat: 0 for cat in keywords}
        lineas_totales = 0

        # Escanear archivos de tu proyecto
        for ruta in self.archivos_proyecto:
            if not os.path.exists(ruta): continue
            with open(ruta, 'r', encoding='utf-8') as f:
                codigo = f.read()
                lineas_totales += len(codigo.splitlines())

                for categoria, lista in keywords.items():
                    reporte += f"\n🔹 {categoria}:\n"
                    cat_sum = 0
                    for word in lista:
                        # Regex para buscar la palabra exacta y no fragmentos
                        count = len(re.findall(rf'\b{word}\b', codigo))
                        if count > 0:
                            reporte += f"   - {word}: {count}\n"
                            cat_sum += count
                    totales[categoria] += cat_sum
                    reporte += f"   > Subtotal: {cat_sum}\n"

        reporte += "\n" + "=" * 35 + "\n"
        reporte += f"📈 TOTAL LÍNEAS DE CÓDIGO: {lineas_totales}\n"
        reporte += f"🛠️ TOTAL PALABRAS CLAVE: {sum(totales.values())}\n"
        return reporte