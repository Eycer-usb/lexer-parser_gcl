from src.AnalizadorSemantico import *
import re

global SymbolTables
global esp
global ids
global dummys_usados

SymbolTables = [] # un stack con las tablas de simbolos

esp = []
ids = []
dummys_usados = 0


def translate(ast):
    return translate_rec(ast)
    

def translate_rec(ast):

    global SymbolTables
    global esp
    global ids

    hijos = ast.sons
    hijos.reverse()
    if ast.name == "Literal" and ast.type == "bool":
        if ast.key == "true":
            return "c_{8}"
        else: 
            return "c_{9}"
    
    elif ast.name == "Literal" and ast.type == "int":
        return int_create(ast.key)
    
    elif ast.name == "Not":
        return "(c_{7} " + f"({translate_rec(hijos[0])}))"

    elif ast.name == "Block":
        if len(hijos) == 1:
            if hijos[0].name == "Symbols Table":
                # si el bloque solo tiene declaraciones ignoramos estas declaraciones y lo tratamos como 
                # si fuese un skip
                return translate_rec(nodito("Skip",[]))
            else:
                return translate_rec(hijos[0])
        else:
            # creamos el espacio estado y asignamos un numero para cada id
            añadir_coordenadas_esp_ids(hijos[1].symbolTable)

            # calculamos la semantica del codigo dentro del bloque
            resultadoHijos = translate(hijos[0])
            
            # verificamos si hay que proyectar, esto es lo mismo que ver si el espacio
            # antes de agregar las nuevas coordenadas era vacio o no

            if len(esp) - len(hijos[1].symbolTable.values()) > 0: # el espacio estado original no esta vacio
                resultadoHijos = proyectar(len(hijos[1].symbolTable), resultadoHijos)

            # ya terminamos de calcular la semantica y vamos a salir del bloque por lo
            # que tenemos que eliminar las variables que agregamos de este bloque
            esp = esp[:len(esp)-len(hijos[1].symbolTable)]
            ids = ids[:len(ids)-len(hijos[1].symbolTable)]

            # devolvemos la semantica del codigo dentro del bloque
            return resultadoHijos
    
    elif ast.name == "Asig":
        # buscamos el index de la ultima declaracion de la variable
        index = buscar_variable(hijos[1].key)

        # creamos un nuevo id mayor que todos los demas para ser usado en el 
        # conjunto por compresion y que no choque con ningun otro x_i de la formula
        numero = len(ids)+1
        
        # creamos la traduccion del espacio estado 
        traduccion_espacio_estado = traducir_esp()
        

        # creamos el producto crus Esp x Esp
        dominio_estado =  "c_{32} " + "(" + traduccion_espacio_estado + ") (" + traduccion_espacio_estado + ")"

        # devolvemos la semantica
        return "c_{24} " + "(c_{20} (c_{31}( c_{40}) (c_{40})))" +"(c_{19} " + "(\lambda x_{" + str(numero) + "}"   + "." + crear_existenciales_semantica_asignacion(index, hijos[0], numero) + ") " + "(\lambda x_{" +  str(numero) + "}" + "." + dominio_estado + "))"

    
    elif ast.name == "If":
        condiciones = []
        instrucciones = []
        
        conseguir_condiciones_instrucciones(hijos[0], condiciones, instrucciones)
        
        tis = []
        
        for condicion in condiciones:
            tis.append(crear_Ti(condicion))
        
        
        unario_sem_idti = crear_unario_sem_idTi(instrucciones,tis)
        unario_ti = crear_unario_Ti(tis)

        complemento_unario_ti = "c_{41} (c_{33} " + unario_ti +")"
        segunda_parte_semantica_if = "(c_{32} (c_{20} (c_{40})) (" + complemento_unario_ti +"))"
        
        return "(c_{24} " + segunda_parte_semantica_if + unario_sem_idti +")"

    elif ast.name == "Do":
        global dummys_usados

        if hijos[0].name == "Then":
            # Como la semantica del do es tan grande separaremos la expresion y la construiremos por partes 
            
            # por comodidad usare algunas variables para hacer referencia a los dummys en la semantica  
            
            limite = len(ids) + 1 + 10 + dummys_usados # nos aseguramos que ningun dummy se repite
            
            x = "x_{" + str(len(ids)+1) + "}" # este no es un dummy pero es util tenerlo
            
            z = "x_{"+ str(limite + 1) +"}"
            y = "x_{"+ str(limite + 2) +"}"
            c = "x_{"+ str(limite + 3) +"}"
            i = "x_{"+ str(limite + 4) +"}"
            d = "x_{"+ str(limite + 5) +"}"
            m = "x_{"+ str(limite + 6) +"}"

            dummys_usados += 6 # indicamos que ya estamos usando 6 dummys por si acaso se anidan do's
            
            
            # creamos un nodo ficticio para obtener Do_0, lo haremos por partes
            # primero crearemos !<condicion>
            nodo_ficticio_not = noditoExpresion("Not",[hijos[0].sons[0]],"bool")
            
            # creamos el !condicion --> skip
            nodo_ficticio_then = nodito("Then",[nodo_ficticio_not, nodito("Skip",[])])
            
            #Creamos if !condicion --> skip fi
            nodo_ficticio_if = nodito("If", [nodo_ficticio_then])

            # calculamos la semantica de Do_0
            semantica_do0 = translate_rec(nodo_ficticio_if)

            # Creamos un nodo ficticio para obtener I f
            # para esto usaremos el nodo ficticion de !<condicion> --> skip

            # como ya tenemos <condicion> --> instruccion y !<condicion> --> skip hay que unirlos y meterlos
            # en un if 

            # primero creamos un nodo guard para el if
            nodo_ficticio_guard = nodito("Guard",[hijos[0], nodo_ficticio_then])

            # creamos el if
            nodo_ficticio_if_1 = nodito("If", [nodo_ficticio_guard])

            # calculamos la semantica
            semantica_I_f = translate_rec(nodo_ficticio_if_1)

            # Apartir de aqui algunos nombres de variables no tendran mucho sentido las usare para ir
            # creando poco a poco la semantica 
            espacio = traducir_esp()
            espacio_extendido = "(c_{24} " + "(c_{20} (c_{40})) " + f"({espacio}))"

            a = "(c_{32} " + f"({espacio_extendido}) ({espacio_extendido}))"

            b = "(c_{66} (c_{42}) "+ f"({i}))"

            c2 = "(c_{38} " + "(c_{59} " + i + " c_{42}) (c_{38} " + f"{espacio_extendido} {espacio_extendido}))"
            
            d2 = "(c_{5} (c_{64} " + i + " " + m + ") (c_{64} " + m + " c_{42}))"

            e = "(c_{5} (c_{15} " + f"({semantica_do0})" + " (c_{54} " + d + " (c_{33} " + m + "))) (c_{15} c_{42} " + m + "))"
            
            f = "(c_{5} (c_{15} (c_{34} " + semantica_I_f + " (c_{54} " + d + " (c_{33} (c_{56} c_{43} " + m + ")))) (c_{54} " + d + " (c_{33} " + m + "))) (c_{65} c_{42} " + m + "))"

            g = "(c_{39} (c_{19} (\lambda " + x + ".c_{17} (c_{54} " + d + " (c_{54} (c_{33} " + i + ") (c_{33} (c_{20} " + x + ")))) c_{40}) (\lambda " + x + "." + espacio + ")))"
            
            h = "(c_{20} (c_{31} c_{40} c_{40}))"

            i2 = "(c_{16} (c_{24} (c_{33} (c_{32} (c_{20} c_{40}) (c_{41} (c_{61} " + y + ")))) " + y + ") " + z + ")"

            j = "(c_{12} (\lambda " + m + ".c_{4} " + f + " " + e + ") (\lambda " + m + "." + d2 + "))"
            
            k = "(c_{15} (c_{34} (c_{24} " + h + " " + g + ") (c_{54} " + d + " (c_{33} " + i + "))) " + c + ")"

            l = "(c_{14} (\lambda " + d + ".c_{5} " + k + " " + j + ") (\lambda " + d + ".c_{16} " + c2 + " " + d + "))"

            m2 = "c_{14} (\lambda " + i + "." + l + ") (\lambda " + i + "." + b + ")"

            
            dummys_usados -= 6 # Como ya terminamos de crear la semantica de este do podemos liberar los dummys
            
            return "c_{9}"
            


        else:
            pass   
    
    elif ast.name == "ReadArray":
        return f"{translate_rec(hijos[1])} ({translate_rec(hijos[0])})"
    
    elif ast.name == "WriteArray":
        limites = hijos[0].sons

        return "(c_{58} " + f"({translate_rec(limites[1])}) " + f"({translate_rec(limites[0])}) " + f"({translate_rec(hijos[1])}))"
    
    elif ast.name == "Sequencing":
        return "c_{34} " + f"({translate_rec(hijos[0])}) " + f"({translate_rec(hijos[1])})"
    
    elif ast.name == "Ident":
        index = buscar_variable(ast.key)
        return "x_{" + str(index) + "}"

    elif ast.name == "Plus":
        return "(c_{55}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
    
    elif ast.name == "Minus":
        if len(hijos) == 2:
            return "(c_{56}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
        else:
            return "(c_{60}"+ f" ({translate_rec(hijos[0])}))"
    
    elif ast.name == "Mult":
        return "(c_{57}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"

    elif ast.name == "Or":
        return "(c_{4}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
    
    elif ast.name == "And":
        return "(c_{5}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
    
    elif ast.name == "Less":
        return "(c_{63}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"

    elif ast.name == "Leq":
        return "(c_{64}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"

    elif ast.name == "Greater":
        return "(c_{65}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
    
    elif ast.name == "Geq":
        return "(c_{66}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
    
    elif ast.name == "Equal":
        return "(c_{15}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
    
    elif ast.name == "NotEqual":
        return "(c_{62}"+ f"({translate_rec(hijos[0])}) ({translate_rec(hijos[1])}))"
    
    elif ast.name == "Skip":
        return "c_{39}" + "(c_{24}" + "(c_{20} (c_{40}))" + f"({traducir_esp()})" + ")"


'''

    Crea el unario de Ti necesario para la semantica del if
    
    Parametros: 
    - tis: una lista con todos los Ti necesarios para crear el unario

'''
def crear_unario_Ti(tis):
    if len(tis) == 1:            
            return f"({tis[0]})"
    else:
        return "(c_{24} " + f"{crear_unario_Ti(tis[1:])} " + f"({tis[0]}))"


'''

    Crea el unario de la composicion entre la instruccion i y su Ti. Necesario para 
    la semantica del if
    
    Parametros: 
    - instrucciones: Lista de instrucciones necesarias para crear el unario
    - tis: una lista con todos los Ti necesarios para crear el unario

'''
def crear_unario_sem_idTi(instrucciones, tis):
        if len(instrucciones) == 1:            
            return "(c_{34}" + "(c_{39} " + f"({tis[0]})) " + f"({instrucciones[0]}))"
        else:
            return "(c_{24} " + f"({crear_unario_sem_idTi(instrucciones[1:],tis[1:])}) " +  "(c_{34}" + "(c_{39} " + f"({tis[0]})) " + f"({instrucciones[0]})))"

'''
    Dada una tabla de simbolos añade los tipos al espacio estado y 
    los nombres de las variables las añade a ids.
    los tipos se codifican de la siguiente manera
    - enteros -> "int"
    - booleanos -> "bool"
    - array[N..M] -> ["N","M"]
'''
def añadir_coordenadas_esp_ids(symbolTable):

    global eps
    global ids

    ids += list(symbolTable.keys())

    for id in symbolTable:
        if "array" in symbolTable[id]:
            esp.append(re.findall("-*[1-9][0-9]*",symbolTable[id]))
        else:
            esp.append(symbolTable[id])
    


'''
    Dada la traduccion de una condicion, crea la traduccion de su Ti

    parametros:
    - condicion_i: la condicion a la cual se le creara un Ti
'''
def crear_Ti(condicion_i):
    global ids
    numero = len(ids)+1

    return "c_{19}"+ "(\lambda x_{" + str(numero) + "}." + f"({condicion_i}))" + "(\lambda x_{" + str(numero) + "}." + f"({traducir_esp()}))" 


'''
    Dado un ast de una instruccion If recorre todas las ramas del If y añade a las
    listas condiciones e instrucciones las condiciones de cada rama y su respectiva
    instruccion

    - ast: Un ast de una instruccion If
    - condiciones: la lista donde se almacenara todas las condiciones
    - instrucciones: la lista donde se almacenara todas las instrucciones

'''
def conseguir_condiciones_instrucciones(ast, condiciones, instrucciones):
    if ast.name == "Then":
        condiciones.append(translate_rec(ast.sons[0]))
        instrucciones.append(translate_rec(ast.sons[1]))
    else: 
        conseguir_condiciones_instrucciones(ast.sons[0], condiciones, instrucciones)
        conseguir_condiciones_instrucciones(ast.sons[1], condiciones, instrucciones)



'''
    Crea el codigo de la proyeccion de un bloque.
    parametros:
    
    - Repeticiones: contiene la cantidad de veces que va a proyectar sober el contenido
    - contenido: es el codigo del contenido sobre el cual estamos proyectando
'''   
def proyectar(repeticiones, contenido):
    if repeticiones == 0:
        return contenido
    else:
        return "c_{34} "+ f"({proyectar(repeticiones-1,contenido)}) " + "(c_{67})"

'''
    Crea todos los existenciales usados en la semantica de asignaciones

    Parametros:
    - variable: el indice de la variable a modificar
    - valor: el nuebo valor de la variable
    - dummy_principal: la variable ligada del conjunto por compresion de la
                       semantica de la asignacion

'''
def crear_existenciales_semantica_asignacion(variable, valor, dummy_principal):
    global ids

    def crear_existencial(dummy, variable):
        if dummy == len(ids)-1:
            return "c_{13} " + "(\lambda x_{" + str(dummy) + "}.c_{15} (" + "c_{31} " + "(c_{33}" + f"({crear_nuevo_estado(variable,valor)}))" + "(c_{33}" + f"({traducir_ids()}))" + ") x_{" + str(dummy_principal) + "}" + ")" 
        else:
            return "c_{13} " + "(\lambda x_{" + str(dummy) + "}."+ crear_existencial(dummy+1,variable) + ")" 

    return crear_existencial(0,variable)


'''
    Crea un nuevo estado muy parecido al estado actual pero que solo modifica una
    entrada de la tupla

    Parametros:
    - cambio: el inidce de la entrada a cambiar
    - valor: la traduccion del nuevo valor que ira en la entrada indicada en "cambio"
'''

def crear_nuevo_estado(cambio,valor):
    
    global ids

    def traduccion_ids(index, final, cambio,valor):
        agregar = "(x_{" + str(index) +"})"
        
        if index == cambio:
            if valor.name == "Comma":
                agregar = crear_asignacion_array(index,valor)
            else:
                agregar = f"({translate_rec(valor)})"

        if index == final:
            return agregar
        else:
            return "(c_{21} " +"(" + traduccion_ids(index+1,final,cambio,valor)+ ")" + " " + f"{agregar})"
    

    '''
        Crear el conjunto de pares ordenados necesario para mostrar la semantica de asignacion
        para la inicializacion de un arreglo

        Parametros:
        - index: El inidice en ids donde se mostrara el conjunto de pares ordenados
        - valor: La inicializacion del arreglo
    
    '''
    def crear_asignacion_array(index, valor):
        
        global esp

        def crear_lista_valores_array(ast, lista_valores):
            for hijo in ast.sons:
                if hijo.name == "Comma":
                    crear_lista_valores_array(hijo,lista_valores)
                else:
                    lista_valores.append(translate_rec(hijo))

        
        lista_valores = []
        lista_pares_ordenados = []
        limites = esp[index]

        crear_lista_valores_array(valor,lista_valores)

        for indice in range(int(limites[0]), int(limites[1]) + 1):
            lista_pares_ordenados.append("(c_{31} "+ f"({lista_valores[indice - int(limites[0])]})" +f"({int_create(str(indice))}))")
        
        
        def crear_conjunto_pares_ordenados(lista):
            if len(lista) == 1:
                return lista[0]
            elif len(lista) == 2:
                return "c_{21} " + lista[1] + " " + lista[0]
            else:
                return "c_{21} " + f"({crear_conjunto_pares_ordenados(lista[1:])}) " + lista[0]       
        
        return "(c_{20} (" + crear_conjunto_pares_ordenados(lista_pares_ordenados) + "))"

    
    return traduccion_ids(0,len(ids)-1,cambio,valor)

    
'''
    traduce el estado actual (lo que esta contenido en ids)
'''
def traducir_ids():
    global ids

    def traduccion_id(index,final):
        if index == final:
            return "x_{" + str(index) + "}"
        else:
            return "c_{21} " +"(" + traduccion_id(index+1,final)+ ")" + " (x_{" + str(index) +"})"
    
    return traduccion_id(0,len(ids)-1)


'''
    traduce el espacio estado actual (lo que esta contenido en esp)
'''
def traducir_esp():
    global esp
    lista_tipos = esp
    
    tipos_basicos = {
                    "int" : "c_{36}",
                    "bool" : "c_{37}"
                }
    
    def traduccion_tipos(lista):
        if len(lista) == 1:
            return traductions(lista[0])
        elif len(lista) == 2:
            return "c_{32} " + traductions(lista[1]) + " " + traductions(lista[0])
        else:
            return "c_{32} " + f"({traduccion_tipos(lista[1:])}) " + traductions(lista[0])
    
    def traductions(valor):
        if type(valor) == str:
            return tipos_basicos[valor]
        else:
            return "(c_{38} " + "(c_{59}" + f"({int_create(valor[1])})" + f"({int_create(valor[0])}))" + " c_{36})"

    return traduccion_tipos(lista_tipos)


'''
    Devuelve el indice de ids que cumpla que es la ultima aparicion de "nombre" en ids

    Parametros:
    - nombre: el nombre que se buscara dentro de ids
'''
def buscar_variable(nombre):
    global ids

    index = len(ids)-1
    while index != -1:
        if ids[index] == nombre:
            return index
        
        index -= 1
    
'''
    Dado un string numerico, devuelve la traduccion a codifo PreApp que represente
    ese mismo string numerico.

    parametros:
    - key: El string numerico a traducir
'''
def int_create(key):
    traductions = {
                    "0" : "c_{42}",
                    "1" : "c_{43}",
                    "2" : "c_{44}",
                    "3" : "c_{45}",
                    "4" : "c_{46}",
                    "5" : "c_{47}",
                    "6" : "c_{48}",
                    "7" : "c_{49}",
                    "8" : "c_{50}",
                    "9" : "c_{51}",
                }
    
    def int_translate (digits_list):
        if len(digits_list) == 1:
            return traductions[digits_list[0]]
        elif len(digits_list) == 2:
            return "c_{54} " + f"({traductions[digits_list[0]]}) ({traductions[digits_list[1]]})"
        else:
            return "c_{54} " + f"({traductions[digits_list[0]]}) ({int_translate(digits_list[1:])})"
    return int_translate(list(key))

    

    