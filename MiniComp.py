import re
import tkinter as tk
from tkinter import ttk, messagebox

# =====================================================================
# 1. TABLA DE SIMBOLOS Y GESTION DE ESTADO
# =====================================================================
class SymbolTable:
    def __init__(self):
        # {nombre: {'categoria', 'tipo', 'valor', 'estado'}}
        self.symbols = {}

    def declare(self, var_type, name, value=None):
        """Declara una variable. Devuelve False si ya existia (redeclaracion)."""
        if name in self.symbols:
            return False
        self.symbols[name] = {
            'categoria': 'Variable',
            'tipo': var_type,
            'valor': value.strip() if value else "Sin inicializar",
            'estado': 'Inicializada' if value else 'Declarada'
        }
        return True

    def exists(self, name):
        return name in self.symbols

    def update(self, name):
        """Marca la variable como asignada (el valor inicial no se modifica)."""
        if name in self.symbols:
            self.symbols[name]['estado'] = 'Asignada'

    def register_constants(self, tokens):
        """Registra los literales numericos encontrados como constantes."""
        for t in tokens:
            if re.match(r'^\d', t) and t not in self.symbols:
                self.symbols[t] = {
                    'categoria': 'Constante',
                    'tipo': 'decimal' if '.' in t else 'entero',
                    'valor': t,
                    'estado': 'Literal'
                }

    def undeclared(self, tokens):
        """Devuelve los identificadores (sin repetir) que no estan declarados."""
        faltantes = []
        for t in tokens:
            if re.match(r'^[a-zA-Z_]', t) and t not in self.symbols and t not in faltantes:
                faltantes.append(t)
        return faltantes

# =====================================================================
# 2. GENERADOR DE CODIGO INTERMEDIO (Triplos y Cuadruplos)
# =====================================================================
class CodeGenerator:
    def __init__(self):
        self.quadruples = []
        self.triples = []
        self.temp_count = 1

    def new_temp(self):
        t = f"t{self.temp_count}"
        self.temp_count += 1
        return t

    def generate(self, target_var, expr_tokens):
        postfix = ExpressionParser.to_postfix(expr_tokens)
        stack = []
        for token in postfix:
            if token in ExpressionParser.PRECEDENCE:
                op2 = stack.pop()
                op1 = stack.pop()
                t_var = self.new_temp()
                
                val1 = op1['val'] if isinstance(op1, dict) else op1
                val2 = op2['val'] if isinstance(op2, dict) else op2
                
                # Cuadruplo: (Operador, Op1, Op2, Resultado)
                self.quadruples.append((token, val1, val2, t_var))
                
                # Triplo: (Operador, Op1, Op2) referenciado por indice base 1
                ref_op1 = f"({op1['ref']})" if isinstance(op1, dict) else op1
                ref_op2 = f"({op2['ref']})" if isinstance(op2, dict) else op2
                self.triples.append((token, ref_op1, ref_op2))
                t_idx = len(self.triples)
                
                stack.append({'val': t_var, 'ref': t_idx})
            else:
                stack.append(token)
        
        if stack:
            final_res = stack.pop()
            final_val = final_res['val'] if isinstance(final_res, dict) else final_res
            final_ref = f"({final_res['ref']})" if isinstance(final_res, dict) else final_res
            
            # Asignacion final
            self.quadruples.append(('=', final_val, '', target_var))
            self.triples.append(('=', final_ref, target_var))

# =====================================================================
# 3. ANALIZADOR DE EXPRESIONES Y NOTACIONES (Infija, Prefija, Postfija)
# =====================================================================
class ExpressionParser:
    PRECEDENCE = {'+': 1, '-': 1, '*': 2, '/': 2, '<': 0, '>': 0, '==': 0, '!=': 0}

    @staticmethod
    def tokenize(expr_str):
        pattern = r'\s*(\d+\.\d+|\d+|[a-zA-Z_]\w*|==|!=|<=|>=|[+\-*/()<>=])\s*'
        tokens = [t for t in re.findall(pattern, expr_str) if t.strip()]
        return tokens

    @staticmethod
    def check_balanced_parentheses(tokens):
        count = 0
        for token in tokens:
            if token == '(':
                count += 1
            elif token == ')':
                count -= 1
            if count < 0:
                return False
        return count == 0

    @classmethod
    def to_postfix(cls, tokens):
        output, stack = [], []
        for token in tokens:
            if re.match(r'^\d', token) or re.match(r'^[a-zA-Z_]', token):
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack and stack[-1] == '(':
                    stack.pop()
            elif token in cls.PRECEDENCE:
                while (stack and stack[-1] in cls.PRECEDENCE and 
                       cls.PRECEDENCE[stack[-1]] >= cls.PRECEDENCE[token]):
                    output.append(stack.pop())
                stack.append(token)
        while stack:
            output.append(stack.pop())
        return output

    @classmethod
    def to_prefix(cls, tokens):
        reversed_tokens = []
        for token in reversed(tokens):
            if token == '(':
                reversed_tokens.append(')')
            elif token == ')':
                reversed_tokens.append('(')
            else:
                reversed_tokens.append(token)
        
        output, stack = [], []
        for token in reversed_tokens:
            if re.match(r'^\d', token) or re.match(r'^[a-zA-Z_]', token):
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack and stack[-1] == '(':
                    stack.pop()
            elif token in cls.PRECEDENCE:
                while (stack and stack[-1] in cls.PRECEDENCE and 
                       cls.PRECEDENCE[stack[-1]] > cls.PRECEDENCE[token]):
                    output.append(stack.pop())
                stack.append(token)
        while stack:
            output.append(stack.pop())
        return list(reversed(output))

# =====================================================================
# 4. INTERFAZ GRAFICA PRINCIPAL (Dashboard MiniComp)
# =====================================================================
class MiniCompApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MiniComp - Generador de Codigo Intermedio (Unidad 2)")
        self.geometry("1350x850")
        self.configure(bg="#F0F4F8")

        self.symbol_table = SymbolTable()
        self.setup_ui()

    def setup_ui(self):
        # Encabezado Superior
        lbl_titulo = tk.Label(self, text="MiniComp: Generador de Codigo Intermedio y Traductor Automatico", 
                              font=("Segoe UI", 14, "bold"), bg="#007ACC", fg="white", pady=10)
        lbl_titulo.pack(fill=tk.X)

        frame_cuerpo = tk.Frame(self, bg="#F0F4F8")
        frame_cuerpo.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- PANEL IZQUIERDO: Editor de Codigo Pseudolenguaje ---
        self.col_izquierda = tk.Frame(frame_cuerpo, bg="#FFFFFF", bd=1, relief="solid")
        self.col_izquierda.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), ipadx=5, ipady=5)

        tk.Label(self.col_izquierda, text="Codigo de Entrada (Pseudolenguaje):", 
                 font=("Segoe UI", 10, "bold"), bg="#FFFFFF").pack(anchor=tk.W, pady=(5, 2))

        self.txtCodigo = tk.Text(self.col_izquierda, width=44, height=28, font=("Consolas", 10))
        self.txtCodigo.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # El editor se mantiene vacio por defecto

        self.btnAnalizar = tk.Button(self.col_izquierda, text="EJECUTAR ANALISIS COMPLETO", command=self.ejecutar_analisis, 
                                     font=("Segoe UI", 11, "bold"), bg="#007ACC", fg="white", cursor="hand2", bd=0)
        self.btnAnalizar.pack(fill=tk.X, pady=(8, 4), ipady=6)

        self.btnLimpiar = tk.Button(self.col_izquierda, text="Limpiar Todo", command=self.limpiar, 
                                    font=("Segoe UI", 10), bg="#FFFFFF", fg="#333333", cursor="hand2", relief="solid", bd=1)
        self.btnLimpiar.pack(fill=tk.X, pady=(0, 0), ipady=4)

        # --- PANEL DERECHO: Pestanas organizadas por Criterios de Rubrica (Sin emojis ni puntajes) ---
        self.col_derecha = tk.Frame(frame_cuerpo, bg="#D4E2F0")
        self.col_derecha.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.col_derecha)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Pestana 1: Notaciones
        self.tab_not = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_not, text="1. Notaciones")
        self.tabla_not = self.crear_tabla(self.tab_not, ("linea", "infija", "prefija", "postfija"), 
                                          ["Linea", "Infija Original", "Prefija (Polaca)", "Postfija (RPN)"], [60, 220, 220, 220])

        # Pestana 2: Triplos y Cuadruplos
        self.tab_tc = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tc, text="2. Triplos y Cuadruplos")
        self.tabla_tc = self.crear_tabla(self.tab_tc, ("linea", "tipo", "contenido"), 
                                         ["Linea", "Formato Intermedio", "Estructura (Operador, Op1, Op2, Res/Temp)"], [60, 160, 500])

        # Pestana 3: Variables, Expresiones y Tabla de Simbolos
        self.tab_var = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_var, text="3. Tabla de Simbolos")
        self.tabla_var = self.crear_tabla(self.tab_var, ("nombre", "categoria", "tipo", "valor", "estado"),
                                          ["Identificador", "Categoria", "Tipo", "Valor Inicial", "Estado"],
                                          [160, 110, 100, 200, 150])

        # Pestana 4: Control y Funciones
        self.tab_ctrl = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ctrl, text="4. Control y Funciones")
        self.tabla_ctrl = self.crear_tabla(self.tab_ctrl, ("linea", "estructura", "representacion"), 
                                           ["Linea", "Instruccion de Control/Funcion", "Representacion Intermedia (Etiquetas, Saltos, Params)"], [60, 180, 480])

        # Pestana 5: Pruebas y Manejo de Errores
        self.tab_err = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_err, text="5. Pruebas y Errores")
        self.tabla_err = self.crear_tabla(self.tab_err, ("linea", "instruccion", "tipo_error", "mensaje"), 
                                          ["Linea", "Instruccion Evaluada", "Tipo de Alerta/Error", "Mensaje Descriptivo del Sistema"], [60, 180, 150, 330])

        # Panel de Estado Inferior
        self.frame_status = tk.Frame(self, bg="#E2E8F0", bd=1, relief="solid")
        self.frame_status.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.lblStatus = tk.Label(self.frame_status, text="Esperando ejecucion...", font=("Segoe UI", 10, "bold"), bg="#E2E8F0", fg="#333333")
        self.lblStatus.pack(anchor=tk.W, padx=10, pady=2)
        self.lblDetalle = tk.Label(self.frame_status, text="Haz clic en 'EJECUTAR ANALISIS COMPLETO' para evaluar las expresiones y generar el codigo intermedio.", font=("Segoe UI", 9), bg="#E2E8F0", fg="#555555")
        self.lblDetalle.pack(anchor=tk.W, padx=10, pady=(0, 2))

    def crear_tabla(self, parent, columnas, titulos, anchos):
        tabla = ttk.Treeview(parent, columns=columnas, show="headings", selectmode="browse")
        for col, titulo, ancho in zip(columnas, titulos, anchos):
            align = tk.W if col in ("infija", "prefija", "postfija", "contenido", "representacion", "mensaje") else tk.CENTER
            tabla.heading(col, text=titulo, anchor=align)
            tabla.column(col, width=ancho, anchor=align)
        scroll = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tabla.yview)
        tabla.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        tabla.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        return tabla

    def ejecutar_analisis(self):
        # Limpiar tablas previas
        for t in [self.tabla_not, self.tabla_tc, self.tabla_var, self.tabla_ctrl, self.tabla_err]:
            for item in t.get_children():
                t.delete(item)

        self.symbol_table = SymbolTable()
        codigo = self.txtCodigo.get("1.0", tk.END).strip()
        if not codigo:
            messagebox.showwarning("Advertencia", "El editor de codigo esta vacio.")
            return

        lineas = codigo.split("\n")
        total_errores = 0

        for num_linea, linea in enumerate(lineas, 1):
            linea_limpia = linea.strip()
            if not linea_limpia or linea_limpia.startswith("//"):
                continue

            # 1. Deteccion de declaraciones (entero / decimal)
            # Declaracion con '=' pero sin expresion (ej. "entero a = ;")
            if re.match(r'^(entero|decimal)\s+[a-zA-Z_]\w*\s*=\s*;?$', linea_limpia):
                total_errores += 1
                self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Sintactico", "Asignacion sin expresion en la declaracion"))
                continue

            match_decl = re.match(r'^(entero|decimal)\s+([a-zA-Z_]\w*)(?:\s*=\s*([^;]+?))?\s*;?$', linea_limpia)
            if match_decl:
                t_tipo, t_nombre, t_val = match_decl.groups()

                # Redeclaracion
                if self.symbol_table.exists(t_nombre):
                    total_errores += 1
                    self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Semantico", f"La variable '{t_nombre}' ya fue declarada"))
                    continue

                if t_val is not None:
                    tokens_val = ExpressionParser.tokenize(t_val)

                    if not ExpressionParser.check_balanced_parentheses(tokens_val):
                        total_errores += 1
                        self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Sintactico", "Parentesis desbalanceados en la expresion"))
                        continue

                    faltantes = self.symbol_table.undeclared(tokens_val)
                    if faltantes:
                        total_errores += 1
                        self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Semantico", f"Identificador no declarado: '{faltantes[0]}'"))
                        continue

                    # Incompatibilidad de tipos: decimal asignado a entero
                    if t_tipo == "entero" and any(re.match(r'^\d+\.\d+$', t) for t in tokens_val):
                        total_errores += 1
                        self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Semantico", f"No se puede asignar un valor decimal a '{t_nombre}' de tipo entero"))
                        continue

                    self.symbol_table.register_constants(tokens_val)

                self.symbol_table.declare(t_tipo, t_nombre, t_val)
                continue

            # 2. Deteccion de estructura condicional 'si'
            if linea_limpia.startswith("si"):
                match_si = re.search(r'si\s*\((.*?)\)', linea_limpia)
                if match_si:
                    cond = match_si.group(1)
                    tokens = ExpressionParser.tokenize(cond)
                    
                    infija = cond
                    prefija = " ".join(ExpressionParser.to_prefix(tokens))
                    postfija = " ".join(ExpressionParser.to_postfix(tokens))
                    self.tabla_not.insert("", tk.END, values=(num_linea, infija, prefija, postfija))
                    
                    self.tabla_ctrl.insert("", tk.END, values=(num_linea, "Condicional 'si'", f"(CMP, {tokens[0]}, {tokens[2]}, t_cond)"))
                    self.tabla_ctrl.insert("", tk.END, values=(num_linea, "Condicional 'si'", "(IF_FALSE, t_cond, GOTO, L_END)"))
                continue

            # 3. Deteccion de llamadas a funciones (ej. imprimir)
            match_func = re.match(r'^([a-zA-Z_]\w*)\s*\((.*?)\);?$', linea_limpia)
            if match_func:
                f_name, f_arg = match_func.groups()
                self.tabla_ctrl.insert("", tk.END, values=(num_linea, f"Llamada a funcion '{f_name}'", f"(PARAM, {f_arg}, , )"))
                self.tabla_ctrl.insert("", tk.END, values=(num_linea, f"Llamada a funcion '{f_name}'", f"(CALL, {f_name}, 1, )"))
                continue

            # 4. Asignaciones y expresiones aritmeticas
            match_assign = re.match(r'^([a-zA-Z_]\w*)\s*=\s*(.+);?$', linea_limpia)
            if match_assign:
                var_target, expr_str = match_assign.groups()
                expr_str = expr_str.replace(";", "").strip()
                tokens = ExpressionParser.tokenize(expr_str)

                # Validacion de parentesis desbalanceados
                if not ExpressionParser.check_balanced_parentheses(tokens):
                    total_errores += 1
                    self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Sintactico", "Parentesis desbalanceados en la expresion"))
                    continue

                # Validacion semantica: destino y operandos deben estar declarados
                if not self.symbol_table.exists(var_target):
                    total_errores += 1
                    self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Semantico", f"Identificador no declarado: '{var_target}'"))
                    continue

                faltantes = self.symbol_table.undeclared(tokens)
                if faltantes:
                    total_errores += 1
                    self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Semantico", f"Identificador no declarado: '{faltantes[0]}'"))
                    continue

                self.symbol_table.register_constants(tokens)
                self.symbol_table.update(var_target)

                # Generacion de Notaciones
                infija = expr_str
                prefija = " ".join(ExpressionParser.to_prefix(tokens))
                postfija = " ".join(ExpressionParser.to_postfix(tokens))
                self.tabla_not.insert("", tk.END, values=(num_linea, infija, prefija, postfija))

                # Generacion de Triplos y Cuadruplos
                code_gen = CodeGenerator()
                code_gen.generate(var_target, tokens)

                for idx, q in enumerate(code_gen.quadruples, 1):
                    self.tabla_tc.insert("", tk.END, values=(num_linea, f"Cuadruplo [{idx}]", f"({q[0]}, {q[1]}, {q[2]}, {q[3]})"))
                for idx, tr in enumerate(code_gen.triples, 1):
                    self.tabla_tc.insert("", tk.END, values=(num_linea, f"Triplo [{idx}]", f"({tr[0]}, {tr[1]}, {tr[2]})"))
                continue

            # Si no coincide con ninguna instruccion valida
            total_errores += 1
            self.tabla_err.insert("", tk.END, values=(num_linea, linea_limpia, "Error Lexico", "Instruccion no reconocida por el pseudolenguaje"))

        # Actualizar Tabla de Simbolos en su pestana correspondiente
        for nombre, info in self.symbol_table.symbols.items():
            self.tabla_var.insert("", tk.END, values=(nombre, info['categoria'], info['tipo'], info['valor'], info['estado']))

        # Estado Final en Pantalla
        if total_errores > 0:
            self.lblStatus.config(text=f"Analisis completado con {total_errores} error(es) detectados.", fg="#B71C1C")
            self.lblDetalle.config(text="Revisa la pestana '5. Pruebas y Errores' para ver la descripcion detallada de cada alerta.", fg="#B71C1C")
        else:
            self.lblStatus.config(text="Analisis Exitoso: Todos los criterios cumplidos correctamente.", fg="#1B5E20")
            self.lblDetalle.config(text="Explora las pestanas superiores para revisar notaciones, triplos, cuadruplos, tabla de simbolos y control.", fg="#1B5E20")

    def limpiar(self):
        self.txtCodigo.delete(1.0, tk.END)
        for t in [self.tabla_not, self.tabla_tc, self.tabla_var, self.tabla_ctrl, self.tabla_err]:
            for item in t.get_children():
                t.delete(item)
        self.lblStatus.config(text="Esperando ejecucion...", fg="#333333")
        self.lblDetalle.config(text="Haz clic en 'EJECUTAR ANALISIS COMPLETO' para evaluar las expresiones.", fg="#666666")

if __name__ == "__main__":
    app = MiniCompApp()
    app.mainloop()