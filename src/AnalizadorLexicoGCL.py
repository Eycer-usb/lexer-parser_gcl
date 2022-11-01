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
        self.archivo = open(nombre_archivo)
        
        self.tokens = []
        lexer = self.lexer()
        self.analizarArchivo(lexer)
        self.archivo.close()
    
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

        t_TkNum = r'\d+'
        t_TkString = r'[\'\"]\w+[\'\"]'

        t_TkOBlock = r'\|\['
        t_TkCBlock = r'\]\|'
        t_TkSoForth = r'\.\.'
        t_TkComma = r','
        t_TkOpenPar = r'\('
        t_TkClosePar = r'\)'
        t_TkAsig = r':='
        t_TkSemicolon = r';'
        t_TkArrow = r'-->'
        

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
        t_TkEqual = r'='
        t_TkNEqual = r'!='
        t_TkOBracket = r'\['
        t_TkCBracket = r'\]'
        t_TkTwoPoints = r':'
        t_TkConcat = r'\.'

        t_ignore_TkComment = r'//.*'
        t_ignore_TkNewLine = r'\n'
        t_ignore_TkSpace = r'\ '

        # Kenny: podemos ahorrarnos todos los ignore anteriores si hacemos
        # Eros: Si podemos, pero si los tenemos por separado podriamos saber especificamente
        # que estamos ignorando XD
        # T_ignore = r '//| |\n'

        # Definicion de reglas sobre los tokens
        
        # Regla para verificar si el Id no es una palabra reservada
        def t_TkId(t):
            r'[a-zA-Z_][a-zA-z_0-9]*'
            t.type = reservadas.get(t.value, 'TkId')
            return t

        # manejador de errores del lexer
        def t_error(e):
            print("Error con el caracter '%s'" % e.value[0])
            e.lexer.skip(1)

        
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
                else:
                    token_formato = self.formatearToken(token, linea)
                    self.tokens.append(token_formato)
            linea += 1

    def obtenerTokens(self):
        return self.tokens

    def imprimirTokens(self):
        for token in self.tokens:
            print(token)
    
    def obtenerErrores(self) -> tuple:
        errores_str = ''
        # Se retorna una tupla de string de errores imprimible y una 
        # lista de strings de errores
        return ( errores_str, self.respuesta['errores'] )

    # Dado un token y su linea en el archivo se almacena el
    # token en el formato solicitado
    def formatearToken(self, token, linea) -> string:
        argumentable = [ 'TkId', 'TkString', 'TkNum' ]
        if (token.type in argumentable):
            return '{}(\'{}\') {} {}'.format(token.type, token.value, linea, token.lexpos+1)
        return str(token.type) + ' ' +str(linea) + ' '+str(token.lexpos+1)