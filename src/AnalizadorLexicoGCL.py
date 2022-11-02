import string
import ply.lex as lex
import re

class AnalizadorLexicoGCL:
    """
    Al instanciarse la clase se ejecuta el 
    analisis lexico del archivo recibido como
    argumento y se almacena el resultado del analisis
    en el atributo respuesta como un diccionario
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
    luego almacena los resultados obtenidos en el diccionario
    self.respuesta segun el formato indicado
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
        
        # Kenny: ignora uno o mas saltos de lineas
        #        ademas en windows por algun motivo los saltos 
        #        de linea no son solo \n si no que es \r\n
        #        fuck windows >:V
        t_ignore_TkNewLine = r'\n+|\r\n+'
        
        # Kenny: Version fancy para ignorar espacios y tabulaciones
        t_ignore_TkSpace = r'[ \t\r\n]+'

        # Definicion de reglas sobre los tokens
        
        # Detecta los strings que tenga solo digitos y lo convierte en int's
        # Kenny: Creo que puede ser util pasarlo a int asi que lo agregue
        def t_TkNum(t):
            r'\d+'
            t.value = int(t.value)
            return t
                          
        # Regla para verificar si el Id no es una palabra reservada
        def t_TkId(t):
            r'[a-zA-Z_][a-zA-Z_0-9]*'
            t.type = reservadas.get(t.value, 'TkId')
            return t

        # manejador de errores del lexer
        # solo hace que el lexer ignore el error, el manejo mas
        # detallado del error se hace mas abajo
        def t_error(e):
            e.lexer.skip(1)
            return e

        
        # Inicializacion del lexer
        analizador_lexer = lex.lex()
        return analizador_lexer

    def analizarArchivo(self, lexer):

        # Se almacenan los Tokens

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

    
    def obtenerTokens(self):
        return self.tokens

    def imprimirTokens(self):
        for token in self.tokens:
            print(token)
    
    # Se retorna una tupla de string de errores imprimible y una 
    # lista de strings de errores
    def obtenerErrores(self) -> tuple:
        errores_str = '\n'.join(self.respuesta['errores'])
        
        return ( errores_str, self.respuesta['errores'] )
    
    def imprimirErrores(self):
        print(self.obtenerErrores()[0])

    # Dado un token y su linea en el archivo se almacena el
    # token en el formato solicitado
    def formatearToken(self, token, linea) -> str:
        argumentable = [ 'TkId', 'TkString', 'TkNum' ]
        if (token.type in argumentable):
            if( token.type == 'TkNum' or token.type == 'TkString' ):
                return '{}({}) {} {}'.format(token.type, token.value, linea, token.lexpos+1)
            
            return '{}(\"{}\") {} {}'.format(token.type, token.value, linea, token.lexpos+1)
        return str(token.type) + ' ' +str(linea) + ' '+str(token.lexpos+1)