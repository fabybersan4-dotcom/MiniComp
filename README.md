# Nombres de Equipo
Bernal Sanchez Fabiola
Cardoza Ezquivel Emmanuel
Carranza Avila Perla Monserrat
Gutiérrez Padilla Angel Gabriel 
Orozco Maya Omar

# Número de Equipo
Equipo 2

# MiniComp
Mini compilador en Python con interfaz gráfica que lee un pseudolenguaje y genera notaciones (infija, prefija y postfija), triplos, cuádruplos, tabla de símbolos, representación de estructuras de control y un reporte de errores.

## Características
- Interfaz gráfica con editor de código y cinco pestañas de resultados.
- Declaración de variables de tipo `entero` y `decimal`.
- Conversión de expresiones a notación infija, prefija y postfija.
- Generación de triplos y cuádruplos con temporales (`t1`, `t2`, ...).
- Tabla de símbolos con variables y constantes.
- Representación intermedia de la condicional `si` y de llamadas a funciones.
- Detección de errores léxicos, sintácticos y semánticos con el número de línea.

## Flujo del compilador
El programa lee el código línea por línea (las líneas vacías y los comentarios `//` se ignoran) y evalúa cada una en este orden:

1. **Declaración** (`entero` / `decimal`): valida la redeclaración, los paréntesis, los identificadores no declarados y el tipo. Si es válida, la guarda en la tabla de símbolos.
2. **Condicional `si`**: genera la notación de la condición y su representación intermedia.
3. **Llamada a función**: genera `PARAM` y `CALL`.
4. **Asignación**: valida paréntesis e identificadores, genera las notaciones, los triplos y los cuádruplos y actualiza la tabla de símbolos.
5. **Ninguna de las anteriores**: se reporta como error léxico.

Al final se llena la tabla de símbolos y la barra inferior muestra el total de errores.

## Lenguaje soportado

| Elemento | Forma |
|----------|-------|
| Declaración | `entero a = 5;`  `decimal b;`  `decimal c = 2.5 + a;` |
| Asignación | `r = a + b * 2;` |
| Condicional | `si (a > b)` |
| Llamada a función | `imprimir(r);` |
| Comentario | `// texto` |
| Operadores | `+`  `-`  `*`  `/`  `<`  `>`  `==`  `!=` |
| Paréntesis | `(` `)` |

El punto y coma al final es opcional.

## Requisitos
- Python 3
- tkinter (viene incluido en el instalador de Python para Windows)
- Módulos `re` y `tkinter`, ambos de la biblioteca estándar: no hay que instalar nada más.

## Uso
1. Ejecutar el programa:
   ```
   python minicomp.py
   ```
2. Escribir el código en el cuadro **Código de Entrada (Pseudolenguaje)**.
3. Presionar **EJECUTAR ANALISIS COMPLETO**.
4. Revisar las pestañas: *1. Notaciones*, *2. Triplos y Cuadruplos*, *3. Tabla de Simbolos*, *4. Control y Funciones* y *5. Pruebas y Errores*.
5. Presionar **Limpiar Todo** para borrar la entrada y los resultados.

Si el editor está vacío, se muestra una advertencia.

## Ejemplo
Entrada:

```
entero a = 5;
entero b = 3;
decimal c = 2.5;
entero r;
r = a + b * 2;
si (a > b)
imprimir(r);
```

**1. Notaciones**

| Línea | Infija | Prefija | Postfija |
|-------|--------|---------|----------|
| 5 | a + b * 2 | + a * b 2 | a b 2 * + |
| 6 | a > b | > a b | a b > |

**2. Triplos y Cuádruplos** (línea 5)

| Formato | Estructura |
|---------|------------|
| Cuadruplo [1] | (*, b, 2, t1) |
| Cuadruplo [2] | (+, a, t1, t2) |
| Cuadruplo [3] | (=, t2, , r) |
| Triplo [1] | (*, b, 2) |
| Triplo [2] | (+, a, (1)) |
| Triplo [3] | (=, (2), r) |

**3. Tabla de Símbolos**

| Identificador | Categoría | Tipo | Valor inicial | Estado |
|---------------|-----------|------|---------------|--------|
| 5 | Constante | entero | 5 | Literal |
| a | Variable | entero | 5 | Inicializada |
| 3 | Constante | entero | 3 | Literal |
| b | Variable | entero | 3 | Inicializada |
| 2.5 | Constante | decimal | 2.5 | Literal |
| c | Variable | decimal | 2.5 | Inicializada |
| r | Variable | entero | Sin inicializar | Asignada |
| 2 | Constante | entero | 2 | Literal |

**4. Control y Funciones**

| Línea | Instrucción | Representación |
|-------|-------------|----------------|
| 6 | Condicional 'si' | (CMP, a, b, t_cond) |
| 6 | Condicional 'si' | (IF_FALSE, t_cond, GOTO, L_END) |
| 7 | Llamada a funcion 'imprimir' | (PARAM, r, , ) |
| 7 | Llamada a funcion 'imprimir' | (CALL, imprimir, 1, ) |

Estado final: `Analisis Exitoso: Todos los criterios cumplidos correctamente.`

### Ejemplo de error
Entrada:

```
entero a = 5;
entero a = 3;
b = a + 1;
entero x = 2.5;
r = (a + 2;
mostrar a
```

Pestaña **5. Pruebas y Errores**:

| Línea | Instrucción | Tipo | Mensaje |
|-------|-------------|------|---------|
| 2 | entero a = 3; | Error Semantico | La variable 'a' ya fue declarada |
| 3 | b = a + 1; | Error Semantico | Identificador no declarado: 'b' |
| 4 | entero x = 2.5; | Error Semantico | No se puede asignar un valor decimal a 'x' de tipo entero |
| 5 | r = (a + 2; | Error Sintactico | Parentesis desbalanceados en la expresion |
| 6 | mostrar a | Error Lexico | Instruccion no reconocida por el pseudolenguaje |

Estado final: `Analisis completado con 5 error(es) detectados.`

## Errores detectados

| Tipo | Mensaje | Ejemplo |
|------|---------|---------|
| Error Sintactico | Asignacion sin expresion en la declaracion | `entero a = ;` |
| Error Sintactico | Parentesis desbalanceados en la expresion | `r = (a + 2;` |
| Error Semantico | La variable 'x' ya fue declarada | `entero a = 5;` dos veces |
| Error Semantico | Identificador no declarado: 'x' | `b = a + 1;` sin declarar `b` |
| Error Semantico | No se puede asignar un valor decimal a 'x' de tipo entero | `entero x = 2.5;` |
| Error Lexico | Instruccion no reconocida por el pseudolenguaje | `mostrar a` |

## Estructura del código

```
MiniComp/
├── minicomp.py
└── README.md
```

| Clase | Función |
|-------|---------|
| `SymbolTable` | Tabla de símbolos: declara variables (`declare`), consulta si existen (`exists`), marca asignaciones (`update`), registra constantes numéricas (`register_constants`) y encuentra identificadores no declarados (`undeclared`) |
| `CodeGenerator` | Convierte una expresión a postfija y genera los cuádruplos y triplos con temporales (`generate`, `new_temp`) |
| `ExpressionParser` | Separa una expresión en tokens (`tokenize`), revisa que los paréntesis estén balanceados (`check_balanced_parentheses`) y convierte a postfija (`to_postfix`) y prefija (`to_prefix`) con la precedencia de los operadores |
| `MiniCompApp` | Interfaz gráfica (`setup_ui`, `crear_tabla`), análisis línea por línea (`ejecutar_analisis`) y limpieza (`limpiar`) |

## Limitaciones
- Solo existen los tipos `entero` y `decimal`.
- Los operadores `<=` y `>=` se separan al leer, pero no se procesan en las notaciones.
- La condicional `si` solo genera la comparación y el salto (`CMP` e `IF_FALSE`); no tiene cuerpo, `sino` ni ciclos. La condición debe tener la forma `operando operador operando` y no se valida que sus variables estén declaradas.
- Cualquier línea que empiece con `si` se trata como condicional (por ejemplo, una variable llamada `sigma`).
- Las llamadas a función aceptan cualquier nombre con un solo argumento, y no se valida ese argumento.
- Solo se revisa la compatibilidad de tipos al declarar un `entero` con un literal decimal, no en las asignaciones posteriores.
- No calcula resultados: solo genera el código intermedio.

## Autor
Proyecto académico — Instituto Tecnológico de Zitácuaro (TecNM) Lenguajes y Autómatas II — Unidad 2
