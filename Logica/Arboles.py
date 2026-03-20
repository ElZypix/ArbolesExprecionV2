import re
from Logica.Nodo import Nodo


class CalculadoraArbol:
    def __init__(self):
        # Prioridad de operadores (Jerarquía de signos)
        self.preferencia = {'^': 3, '√': 3, '*': 2, '/': 2, '+': 1, '-': 1, '(': 0}

    def es_operando(self, token):
        """Reconoce si es una variable (letras) o un número."""
        if token.isalpha(): return True
        if token.replace('.', '', 1).isdigit(): return True
        return False

    def infija_a_posfija(self, ecuacion):
        """Convierte la expresión del usuario a Notación Polaca Inversa."""
        tokens_originales = re.findall(r"([a-zA-Z]+|\d+(?:\.\d+)?|[/√+*^()-])", ecuacion)
        tokens = []
        operadores = ['+', '-', '*', '/', '^', '√']

        # --- PARCHE PARA EL BUG DE LA RAÍZ ---
        for i, token in enumerate(tokens_originales):
            if token == '√':
                # Si es el primer token, o si viene después de un operador o un '('
                if i == 0 or tokens_originales[i - 1] in operadores or tokens_originales[i - 1] == '(':
                    tokens.append('2') # Le inyectamos el índice 2 automáticamente
            tokens.append(token)
        # --------------------------------------

        salida = []
        pila = []

        for token in tokens:
            if self.es_operando(token):
                salida.append(token)
            elif token == '(':
                pila.append(token)
            elif token == ')':
                while pila and pila[-1] != '(':
                    salida.append(pila.pop())
                if pila: pila.pop()
            else:
                while pila and pila[-1] != '(' and self.preferencia.get(pila[-1], 0) >= self.preferencia.get(token, 0):
                    salida.append(pila.pop())
                pila.append(token)

        while pila:
            salida.append(pila.pop())
        return salida

    def construir_arbol(self, lista_posfija):
        """Toma la lista postfija y crea la estructura de nodos del árbol."""
        if not lista_posfija: return None
        pila_arbol = []

        try:
            for token in lista_posfija:
                if self.es_operando(token):
                    pila_arbol.append(Nodo(token))
                else:
                    nodo = Nodo(token)
                    nodo.derecha = pila_arbol.pop()
                    nodo.izquierda = pila_arbol.pop()
                    pila_arbol.append(nodo)
            return pila_arbol.pop()
        except:
            return None

    # ==========================================
    # EVALUACIÓN MATEMÁTICA Y SIMPLIFICACIÓN
    # ==========================================
    def evaluar(self, nodo):
        res, _ = self.evaluar_con_pasos(nodo)
        return res

    def evaluar_con_pasos(self, nodo):
        """Devuelve (resultado, lista_de_pasos) soportando números y variables"""
        if not nodo: return "", []

        # Caso Base: Es una hoja (Número o Letra)
        if nodo.izquierda is None and nodo.derecha is None:
            try:
                num = float(nodo.valor)
                return int(num) if num.is_integer() else num, []
            except ValueError:
                return str(nodo.valor), []

        # Paso Recursivo: Evaluar hijos
        val_izq, pasos_izq = self.evaluar_con_pasos(nodo.izquierda) if nodo.izquierda else ("", [])
        val_der, pasos_der = self.evaluar_con_pasos(nodo.derecha) if nodo.derecha else ("", [])

        op = nodo.valor
        paso_texto = ""
        res = ""
        son_numeros = isinstance(val_izq, (int, float)) and isinstance(val_der, (int, float))

        try:
            if son_numeros:
                if op == '+':
                    res = val_izq + val_der
                elif op == '-':
                    res = val_izq - val_der
                elif op == '*':
                    res = val_izq * val_der
                elif op == '/':
                    if val_der == 0: raise ValueError("División por cero")
                    res = val_izq / val_der
                elif op == '^':
                    res = pow(val_izq, val_der)
                elif op == '√':
                    res = pow(val_der, 1 / val_izq) if val_izq != 0 else 0

                if isinstance(res, float) and res.is_integer(): res = int(res)
                paso_texto = f" ✔ Operación: {val_izq} {op} {val_der} = {res}"
            else:
                if op == '√':
                    res = f"√{val_der}" if val_izq in [2, "2"] else f"{val_izq}√{val_der}"
                else:
                    # Simplificación básica
                    if op == '+' and val_izq == 0:
                        res = val_der
                    elif op == '+' and val_der == 0:
                        res = val_izq
                    elif op == '*' and val_izq == 1:
                        res = val_der
                    elif op == '*' and val_der == 1:
                        res = val_izq
                    elif op == '*' and (val_izq == 0 or val_der == 0):
                        res = 0
                    else:
                        res = f"({val_izq} {op} {val_der})"
                paso_texto = f" 📌 Agrupando: {val_izq} y {val_der} con '{op}' ➔ {res}"
        except Exception as e:
            raise ValueError(f"Error en '{op}': {str(e)}")

        return res, pasos_izq + pasos_der + [paso_texto]

    def obtener_infija(self, nodo):
        """Recorre el árbol y extrae la expresión matemática con paréntesis"""
        if not nodo: return []
        # Si es una hoja (número o letra), solo la devuelve
        if not nodo.izquierda and not nodo.derecha:
            return [str(nodo.valor)]

        res = []
        if nodo.izquierda:
            res.extend(["("] + self.obtener_infija(nodo.izquierda))

        res.append(str(nodo.valor))

        if nodo.derecha:
            res.extend(self.obtener_infija(nodo.derecha) + [")"])

        return res

    def generar_cuadruplos(self, posfija):
        cuadruplos = []
        pila = []
        temporal_count = 0

        for token in posfija:
            if self.es_operando(token):
                pila.append(token)
            else:
                op2 = pila.pop()
                op1 = pila.pop()
                res = f"T{temporal_count}"
                # Formato: (Operador, Op1, Op2, Resultado)
                cuadruplos.append([token, op1, op2, res])
                pila.append(res)
                temporal_count += 1
        return cuadruplos

    def generar_triplos(self, posfija):
        triplos = []
        pila = []
        indice = 0

        for token in posfija:
            if self.es_operando(token):
                pila.append(token)
            else:
                op2 = pila.pop()
                op1 = pila.pop()
                # Formato: (Operador, Op1, Op2) -> El resultado es el índice de la fila
                triplos.append([token, op1, op2])
                pila.append(f"({indice})")
                indice += 1
        return triplos

    def generar_codigo_p(self, posfija):
        codigo_p = []
        pila = []
        temp_count = 0

        for token in posfija:
            if self.es_operando(token):
                codigo_p.append(["LOD", token, "-", "-"])
                pila.append(token)
            else:
                op2 = pila.pop()
                op1 = pila.pop()
                instruccion = {
                    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '^': 'POW'
                }.get(token, 'OP')

                res = f"T{temp_count}"
                codigo_p.append([instruccion, "-", "-", "-"])
                codigo_p.append(["STO", res, "-", "-"])
                pila.append(res)
                temp_count += 1
        return codigo_p

    def resolver_operacion_simple(self, op, val1, val2):
        """Resuelve una operación simple entre dos valores (pueden ser números o letras)"""
        try:
            # Intentar resolver como números
            n1, n2 = float(val1), float(val2)
            if op == '+': return n1 + n2
            if op == '-': return n1 - n2
            if op == '*': return n1 * n2
            if op == '/': return n1 / n2 if n2 != 0 else "Error"
            if op == '^': return n1 ** n2
        except:
            # Si hay letras, devolver simplificado
            return f"({val1}{op}{val2})"

    def obtener_posfija(self, nodo, resultado=None):
        """Recorrido Post-orden: Izquierda -> Derecha -> Raíz"""
        if resultado is None:
            resultado = []

        if nodo:
            # 1. Primero visitamos todo el subárbol izquierdo
            self.obtener_posfija(nodo.izquierda, resultado)
            # 2. Luego todo el subárbol derecho
            self.obtener_posfija(nodo.derecha, resultado)
            # 3. Al final guardamos el valor de la raíz
            resultado.append(str(nodo.valor))

        return resultado