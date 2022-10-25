import ply.lex as lex
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
    def lexer():
        tokens = [
            # Tokens de Palabras Reservadas
            'TkDeclare',
            'TkIf',
            'TkFi',
            'TkFor',
            'TkRof',
            'TkDo',
            'TkOd',
            'TkSkip',
            'TkPrint',

            # Tokens de Tipos
            'TkId',
            'TkNum',
            'TkString',
            'TkTrue',
            'TkFalse',
            
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
        ]
        # Definicion de las expresiones regulares de los tokens
        t_TkDeclare = r''
        t_TkIf = r''
        t_TkFi = r''
        t_TkFor = r''
        t_TkRof = r''
        t_TkDo = r''
        t_TkOd = r''
        t_TkSkip = r''
        t_TkPrint = r''
        t_TkId = r''
        t_TkNum = r''
        t_TkString = r''
        t_TkTrue = r''
        t_TkFalse = r''

        t_TkOBlock = r''
        t_TkCBlock = r''
        t_TkSoForth = r''
        t_TkComma = r''
        t_TkOpenPar = r''
        t_TkClosePar = r''
        t_TkAsig = r''
        t_TkSemicolon = r''
        t_TkArrow = r''

        t_TkPlus = r''
        t_TkMinus = r''
        t_TkMult = r''
        t_TkOr = r''
        t_TkAnd = r''
        t_TkNot = r''
        t_TkLess = r''
        t_TkLeq = r''
        t_TkGeq = r''
        t_TkGreater = r''
        t_TkEqual = r''
        t_TkNEqual = r''
        t_TkOBracket = r''
        t_TkCBracket = r''
        t_TkTwoPoints = r''
        t_TkConcat = r''

        t_ignore_TkComment = r''

        #Definicion de reglas sobre los tokens
        pass
        



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




