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
        
        self.respuesta = {
            'estatus' : -1,
            'errores': [],
            'resultado': '',
        }
        self.lexer()
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
            't_TkTrue' : 'true',
            't_TkFalse' : 'false'
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
        t_TkString = r'\w+'

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
        def t_TkId(t): # por algun motivo extraño no funciona bien
            r'[a-zA-Z_][a-zA-z_0-9]*'
            t.type = reservadas.get(t.value, 'TkId')
            return t

        # manejador de errores del lexer
        def t_error(e):
            print("Error con el caracter '%s'" % e.value[0])
            e.lexer.skip(1)

        
        # Inicializacion del lexer
        analizador_lexer = lex.lex()
        
        # solo para comprobar la salida
        for line in self.archivo:
            analizador_lexer.input(line)
            while True:
                token = analizador_lexer.token()
                if not token:
                    break
                else:
                    print(token)


    """
    Lista de estatus de la respuesta:
    0: Analisis Exitoso
        Errores es una lista vacia
        Resultado contiene el string del analisis
        
    1: Analisis Fallido por error en sintaxis
        Errores Almacenados en respuesta['errores']
        Resultado indica que exite error de sintaxis

    2: Archivo no encontrado
        Errores es una lista vacia
        Resultado indica que no se encontro el archivo

    3: Archivo no admitido (Extension invalida)
        Errores es una lista vacia
        Resultado indica que el archivo no es valido
    """
    def obtenerResultado(self) -> str:
        pass
    def obtenerEstatus(self) -> int:
        pass

    
    def obtenerErrores(self) -> tuple:
        errores_str = ''
        # Se retorna una tupla de string de errores imprimible y una 
        # lista de strings de errores
        return ( errores_str, self.respuesta['errores'] )




