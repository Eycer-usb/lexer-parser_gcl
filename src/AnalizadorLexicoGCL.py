import string
import ply.lex as lex
import re

class AnalizadorLexicoGCL:
    """
    Al instanciarse la clase se ejecuta el 
    analisis lexico del archivo recibido como
    argumento y se almacena el resultado del analisis
    en el atributo respuesta como un diccionario

    atributo respuesta:
        estatus: 
            0 = todo termino correctamente
            1 = hubo un error al tratar de analizar
        errores:
            Contiene los errores sintacticos de haberlos.
            Si no hubo un error sintactico entonces estara vacio
        resultado:
            Si todo fue bien, sera un string vacio, si hubo un error
            sintactico contendra el string "Syntaxis Error", si hubo
            error al intentar leer el archivo contendra el string
            "Incorrect extension" o File not found, dependiendo 
            del caso    
    """
    def __init__(self, nombre_archivo):
        self.respuesta = {
            'estatus' : 0,
            'errores': [],
            'resultado': '',
        }
        
        self.tokens = []
        try:
            if nombre_archivo[-4:len(nombre_archivo)] != ".gcl":
                self.respuesta['estatus'] = 3
                self.respuesta['resultado'] = "Incorrect extension"
                return

            self.archivo = open(nombre_archivo)
        
            lexer = self.lexer()
            self.analizarArchivo(lexer)
            self.archivo.close()

        except FileNotFoundError:
            self.respuesta['estatus'] = 2
            self.respuesta['resultado'] = "File not found"
    
    """
    Analizador lexico.
    Examina el archivo almacenado en el atributo self.archivo
    luego almacena los resultados obtenidos en el atributo 
    tokens, si ocurre un error de sintaxis reinicia el atributo
    tokens y almacena todos los errores en respuesta['errores']
    """
    def lexer(self):

        # palabras reservadas
        reservadas = {
            'declare' : 'TkDeclare',
            'if' : 'TkIf',
            'fi' : 'TkFi',
            'for' : 'TkFor',
            'rof' : 'TkRof',
            'do' : 'TkDo',
            'od' : 'TkOd',
            'skip' : 'TkSkip',
            'print' : 'TkPrint',
            'true' : 'TkTrue',
            'false' : 'TkFalse',
            'int' : 'TkInt',
            'array' : 'TkArray',
            'bool' : 'TkBool',
            'in' : 'TkIn',
            'to' : 'TkTo'
        }

        tokens = [
            # Tokens de Tipos
            'TkId',
            'TkNum',
            'TkString',
            
            # Tokens de Simbolos separadores
            'TkOBlock',
            'TkCBlock',
            'TkSoForth',
            'TkComma',
            'TkOpenPar',
            'TkClosePar',
            'TkAsig',
            'TkSemicolon',
            'TkArrow',
            'TkGuard',

            # Tokens de Simbolos de operadores
            'TkPlus',
            'TkMinus',
            'TkMult',
            'TkOr',
            'TkAnd',
            'TkNot',
            'TkLess',
            'TkLeq',
            'TkGeq',
            'TkGreater',
            'TkEqual',
            'TkNEqual',
            'TkOBracket',
            'TkCBracket',
            'TkTwoPoints',
            'TkConcat',

            # Tokens de Signos a ignorar
            'TkComment',
            'TkNewLine',
            'TkSpace'
        ]

        tokens = tokens + list(reservadas.values())

        # Definicion de las expresiones regulares de los tokens
        t_TkString = r'[\'\"]([^\"\\]|\\\\|\\\"|\\n)*[\'\"]'
        t_TkOBlock = r'\|\['
        t_TkCBlock = r'\]\|'
        t_TkSoForth = r'\.\.'
        t_TkComma = r','
        t_TkOpenPar = r'\('
        t_TkClosePar = r'\)'
        t_TkAsig = r':='
        t_TkSemicolon = r';'
        t_TkArrow = r'-->'
        t_TkGuard = r"\[\]"
        

        t_TkPlus = r'\+'
        t_TkMinus = r'-'
        t_TkMult = r'\*'
        t_TkOr = r'\\/'
        t_TkAnd = r'/\\'
        t_TkNot = r'!'
        t_TkLess = r'<'
        t_TkLeq = r'<='
        t_TkGeq = r'>='
        t_TkGreater = r'>'
        t_TkEqual = r'=='
        t_TkNEqual = r'!='
        t_TkOBracket = r'\['
        t_TkCBracket = r'\]'
        t_TkTwoPoints = r':'
        t_TkConcat = r'\.'

        t_ignore_TkComment = r'//.*'
        
        t_ignore_TkNewLine = r'\n+|\r\n+'
        
        t_ignore_TkSpace = r'[ \t\r\n]+'

        # Definicion de reglas sobre los tokens
        
        """
        Analiza el token que se le pase como parametro si 
        es un numero de cualquier cantidad de digito entonces
        toma el valor del token (que es un string) y lo convierte 
        en un int.
        """
        def t_TkNum(t):
            r'\d+'
            t.value = int(t.value)
            return t
                          
        """
        Analiza el token que se le pase como parametro, si es una
        secuencia de caracteres valida (que comience con una letra desde
        la A hasta la z o un "_" y luego venga seguido cualquier cantidad de 
        letras, numeros o el caracter "_") verifica si no esta en las palabras 
        resevadas, en caso de estarlo ese token no se aceptara como un Id, en 
        caso contrario se le tomara como un Id
        """
        def t_TkId(t):
            r'[a-zA-Z_][a-zA-Z_0-9]*'
            t.type = reservadas.get(t.value, 'TkId')
            return t

        """
        Maneja los errores que pueda ocurrir. Hace que el 
        lexer ignore el error y el almacenamiento de este
        ocurre despues
        """
        def t_error(e):
            e.lexer.skip(1)
            return e

        
        # Inicializacion del lexer
        analizador_lexer = lex.lex()
        return analizador_lexer

    """
    Dado un lexer recorre todas las lineas del archivo almacenado
    en self.archivo, si no encutra errores almacenara los tokens
    encontrados en self.tokens, en caso de encontrar un error
    reinicia self.token y almacena todos los errores que encuentre 
    apartir  de ese punto en self.respuesta['errores']
    """    
    def analizarArchivo(self, lexer):
        linea = 1

        for line in self.archivo:
            lexer.input(line)            
            while True:
                token = lexer.token()
                if not token:
                    break
                elif token.type == 'error':
                    if  self.respuesta['estatus'] != 1: 
                        self.respuesta['estatus'] = 1
                        self.respuesta['resultado'] = 'Syntaxis Error'
                    self.respuesta['errores'].append(f"Error: Unexpected character \"{token.value[0]}\" in row {linea}, column {token.lexpos+1}")
                    self.tokens = []
                elif self.respuesta['estatus'] == 0:
                    self.tokens.append(self.formatearToken(token,linea))
            
            linea += 1  

    
    """
    Devuelve la lista de todos los tokens encontrados
    con informacion detallada de su tipo, linea y columna
    """
    def obtenerTokens(self):
        return self.tokens

    """
    Devuelve un string contodos los tokens encontrados
    con informacion detallada de su tipo, linea y columna
    """
    def imprimirTokens(self):
        for token in self.tokens:
            print(token)
    
    """
    Devuelve una tupla donde el primer elemento es un string 
    con todos los errores sintacticos encontrados, y el segundo
    elemento contiene estos errores almacenados en una lista
    """
    def obtenerErrores(self) -> tuple:
        errores_str = '\n'.join(self.respuesta['errores'])
        
        return ( errores_str, self.respuesta['errores'] )
    
    """
    Imprime por pantalla todos los errores sintacticos 
    encontrados
    """
    def imprimirErrores(self):
        print(self.obtenerErrores()[0])

    """
    Dado un token y la linea donde se encontro devuelve un 
    string con toda la informacion necesaria del token en 
    su formato especifico
    """
    def formatearToken(self, token, linea) -> str:
        argumentable = [ 'TkId', 'TkString', 'TkNum' ]
        if (token.type in argumentable):
            if( token.type == 'TkNum' or token.type == 'TkString' ):
                return '{}({}) {} {}'.format(token.type, token.value, linea, token.lexpos+1)
            
            return '{}(\"{}\") {} {}'.format(token.type, token.value, linea, token.lexpos+1)
        return str(token.type) + ' ' +str(linea) + ' '+str(token.lexpos+1)