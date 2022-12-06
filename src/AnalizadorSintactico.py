
import ply.yacc as yacc
import re
from src.AnalizadorSemantico import *

class analizadorSintactico: 

    # El constructor de clase crea el parser, y evalua el
    # archivo recibido como argumento. 
    def __init__(self, nombre_archivo,tokens):        
                
        parser = self.parser(tokens)
        self.nombre_archivo = nombre_archivo
        archivo = open(nombre_archivo)
        contenido = archivo.read()
        archivo.close()
        self.noLineas = sum(1 for line in open(nombre_archivo)) - 1
        self.ast = parser.parse(contenido)

    # Se define el parser con su gramatica, precedencia y estructura
    def parser(self, tokens):


        precedence = (
            ("left","TkComma"),
            ("left","TkOr"),
            ("left","TkAnd"),
            ('right', "TkNot"),
            ("left","TkEqual","TkNEqual"),
            ("left","TkLess","TkLeq","TkGeq","TkGreater"),
            ("left","TkPlus","TkMinus"),
            ("left","TkMult"),
            ("right","UMinus")
        )
        
        start = 'program'
        
        global symbolTables
        symbolTables = []

        # symbolTables[0] = Direccion a la tabla anterior
        # symbolTables[1] = valor de la tabla actual

        def p_program(p):
            '''
                program : instBlock 
            '''
            p[0] = p[1]

        # El programa vacio no es reconocido como valido
        # El apartado declare es opcional, pero si 
        # existe debe tener al menos una declaracion
        def p_instBlock(p):
            '''
            instBlock : TkOBlock declare TkCBlock
                      | TkOBlock declare code TkCBlock
                      | TkOBlock code TkCBlock
            '''

            global symbolTables

            if len(p) == 5:
                #p[0] = ["Block", p[2], p[3]]
                p[0] = noditoBlock("Block",[p[2],p[3]])
                p[0].sons[0].father = p[0]
                p[0].sons[1].father = p[0]
            else:
                #p[0] = ["Block",p[2]]
                p[0] = noditoBlock("Block",[p[2]])
                p[0].sons[0].father = p[0]
            
            symbolTables.pop(0)

        # Sentencia de Declaracion
        def p_declare(p):
            '''
                declare : TkDeclare declaration
                        | TkDeclare seqDeclare
            '''
            #p[0] = ["Declare",p[2]]
            
            global symbolTables

            if len(symbolTables) == 0 :
                symbolTables = [p[2]]
            else:
                symbolTables = [p[2],*symbolTables]
            
            p[0] = noditoDeclare("Symbols Table",[], symbolTables)
            
        # Instruccion de Declaracion
        def p_declaration(p):
            '''
                declaration : DeclaList TkTwoPoints type
            '''

            global symbolTables
            tabla = {}

            # Se agregan las nuevas declaraciones y se 
            # enmascara si es necesario
            for i in p[1]:
                tabla[i] = p[3]
            
            p[0] = tabla


        # Lista de Declaraciones
        def p_decaList(p):
            '''
            DeclaList : TkId TkComma DeclaList
                        | TkId
            '''
            if len(p) == 4:
                p[0] = [p[1],*p[3]]
            else:
                p[0] = [p[1]]

        # Secuencia de Declaraciones        
        def p_seqDeclare(p):
            '''
                seqDeclare : declaration TkSemicolon declaration
                           | seqDeclare TkSemicolon declaration
            '''
            #print([*p[1],*p[3]])
            
            for i in p[3]:
                if p[1].get(i)!= None:
                    raise(Exception("error de sintaxis WIP"))
                
                p[1][i] = p[3][i]

            p[0] = p[1] 
            
        
        # Tipos de Datos
        def p_type(p):
            '''
                type : TkInt
                     | TkBool
                     | TkArray TkOBracket TkNum TkSoForth TkNum TkCBracket
                     | TkArray TkOBracket TkMinus TkNum TkSoForth TkMinus TkNum TkCBracket
                     | TkArray TkOBracket TkNum TkSoForth TkMinus TkNum TkCBracket
                     | TkArray TkOBracket TkMinus TkNum TkSoForth TkNum TkCBracket
            '''
            if len(p) == 2:
                p[0] = p[1]
            elif len(p) == 7:
                 p[0] = p[1] + p[2] + "Literal: " + p[3] + p[4] + "Literal: " + p[5] + p[6]
            elif len(p) == 9:
                p[0] =  p[1] + p[2] + "Literal: -" + p[4] + p[5] + "Literal: -" + p[7] + p[8]
            else:
                if p[3] == "-":
                    p[0] =  p[1] + p[2] + "Literal: -" + p[4] + p[5] + "Literal: " + p[6] + p[7]
                else:
                    p[0] =  p[1] + p[2] + "Literal: " + p[3] + p[4] + "Literal: " + p[6] + p[7]

        # Estructura de los bloques de codigo
        def p_code(p):
            '''
                code : instruction
                     | sequencing
            '''
            p[0] = p[1]
        
        # Definicion de secuenciacion de instrucciones
        def p_sequencing(p):
            '''
                sequencing : instruction TkSemicolon instruction
                           | sequencing TkSemicolon instruction
            '''
            #p[0] = ["Sequencing", p[1],p[3]]
            p[0] = nodito("Sequencing",[p[1], p[3]])
            p[0].sons[0].father = p[0]
            p[0].sons[1].father = p[0]
        
        # Instruccion Print
        def p_instPrint(p):
            '''
                instPrint : TkPrint printAble
                          | TkPrint instConcat
            '''
            
            p[0] = ["Print", p[2]]

        # Instruccion Skip
        def p_instSkip(p):
            '''
                instSkip : TkSkip
            '''
            print("entre a skip")
            p[0] = nodito("Skip",[])
        
        # Instruccion Concatenacion
        def p_instConcat(p):
            '''
                instConcat : printAble TkConcat  printAble
                           | instConcat TkConcat printAble
            '''
            p[0] = ["Concat", p[1], p[3]]

        # Sentencia Imprimible de Strings
        def p_printeAble1(p):
            '''
            printAble : TkString
            '''
            p[0] = ["String", {p[1]}]
        
        # Sentencia Imprimible de Expresiones
        def p_printeAble2(p):
            '''
            printAble : exp
            '''
            p[0] = p[1]
            
        # Definicion de los Arrays
        def p_arrayIni(p):
            '''
                arrayIni : exp TkComma exp
                         | arrayIni TkComma exp
            '''
            p[0] = ["Comma", p[1], p[3]]
            
        # Instruccion de Asignacion
        def p_instAsig(p):
            '''
                instAsig : TkId TkAsig exp
                         | TkId TkAsig arrayIni
                         | TkId TkAsig modArray
            '''
            #p[0] = ["Asig",["Ident",p[1]],p[3]]
            #print(symbolTables)
            for i in symbolTables:
                if i.get(p[1]) != None:
                    if i[p[1]] != p[3].type:
                        raise(Exception("Error de tipo WIP"))
                    
                    p[0] = nodito("Asig",[
                        noditoIdentificador("Ident", p[1], i[p[1]])
                        ] )    
                    return
            
            raise(Exception("Error en el ID WIP"))

            
        
        # Generalizacion de instrucciones
        def p_instruction(p):
            '''
                instruction : instPrint
                            | instAsig
                            | instSkip
                            | instBlock
                            | instFor
                            | instIf
                            | instDo
            '''
            p[0] = p[1]
        
        # Caracterizacion de los arrays
        def p_consArray(p):
            '''
                consArray : TkId TkOBracket exp TkCBracket
            '''
            p[0] = ["ReadArray",["Ident", {p[1]}], p[3]]

        def p_consArray1(p):
            '''
                consArray : modArray TkOBracket exp TkCBracket
            '''
            p[0] = ["ReadArray", p[1], p[3]]

        def p_modArray(p):
            '''
                modArray : modArray TkOpenPar exp TkTwoPoints exp TkClosePar
                         | finish
                
            '''
            if len(p) == 2: 
                p[0] = p[1]
            else:         
                p[0] = ["WriteArray",p[1], ["TwoPoints", p[3], p[5]]]
        
        def p_modArray1(p):
            '''
                finish : TkId TkOpenPar exp TkTwoPoints exp TkClosePar
            '''
            p[0] = ["WriteArray",["Ident", {p[1]}],["TwoPoints",p[3],p[5]]]
        
        # Gramatica de los Operadores Binarios
        def p_opBin(p):
            '''
                exp : exp TkPlus exp
                    | exp TkMinus exp
                    | exp TkMult exp
            '''
            if p[1].type != "int" or p[3].type != "int": raise(Exception("Error con las expreciones de enteros"))
            
            if p[2] == "+":
                #p[0] = ["Minus",p[1],p[3]]
                p[0] = noditoExpresion("Plus",[p[1],p[3]],"int")
            elif p[2] == "-":
                #p[0] = ["Minus",p[1],p[3]]
                p[0] = noditoExpresion("Minus",[p[1],p[3]],"int")
            elif p[2] == "*":
                #p[0] = ["Mult",p[1],p[3]]
                p[0] = noditoExpresion("Mult",[p[1],p[3]],"int")
        
        def p_opBin2(p):
            '''
                exp : exp TkAnd exp
                    | exp TkOr exp
            '''
            if p[2] == "/\\":
                p[0] = ["And",p[1],p[3]]
            elif p[2] == "\\/":
                p[0] = ["Or",p[1],p[3]]
        
        def p_opBin3(p):
            '''
                exp : exp TkLess exp
                    | exp TkLeq exp
                    | exp TkGeq exp
                    | exp TkGreater exp
                    | exp TkEqual exp
                    | exp TkNEqual exp
            '''
            if p[2] == "<":
                p[0] = ["Less",p[1],p[3]]
            elif p[2] == "<=":
                p[0] = ["Leq",p[1],p[3]]
            elif p[2] == ">=":
                p[0] = ["Geq",p[1],p[3]]
            elif p[2] == ">":
                p[0] = ["Greater",p[1],p[3]]
            elif p[2] == "==":
                p[0] = ["Equal",p[1],p[3]]
            elif p[2] == "!=":
                p[0] = ["NotEqual",p[1],p[3]]
        
        # Generalizacion de la gramatica de las expresiones
        def p_exp(p):
            '''
                exp : TkNot exp
                    | TkOpenPar exp TkClosePar
                    | consArray
            '''
            if len(p) == 3:
                #p[0] = ["Not",p[2]]
                if p[2].type != "bool":
                    raise(Exception("Error en Not WIP"))
                    
                p[0] = noditoExpresion("Not",[p[2]],"bool")
            elif len(p) == 4:
                p[0] = p[2]
            else: 
                p[0] = p[1]

        # Definicion de las estructuras de los literales
        def p_literales(p):
            '''
                exp : TkMinus exp %prec UMinus
            '''
            #p[0] = ["Minus", p[2]]
            if p[2].type != "int":
                raise(Exception("Error en minus WIP"))

            p[0] = noditoExpresion("Minus",[p[2]],"int")
            
        def p_literales1(p):
            '''
                exp : TkNum
            '''
            #p[0] = ["Literal", p[1]]
            p[0] = noditoExpresion("Literal",[nodito(p[1],[])],"int")

        def p_literales2(p):
            '''
                exp : TkTrue
                    | TkFalse
            '''
            #p[0] = ["Literal", p[1]]
            p[0] = noditoExpresion("Literal",[nodito(p[1],[])],"bool")
        
        # Definicion de las estructuras de las variables (ids)
        def p_id(p):
            '''
                exp : TkId 
            '''        
            #p[0] = ["Ident",p[1]]
            
            for i in symbolTables:
                if i.get(p[1]) != None:
                    p[0] = noditoExpresion("Ident",[nodito(p[1],[])],i[p[1]])
                    return
            
            raise(Exception("Error en el ID WIP"))
        
        # Gramatica del bucle for
        def p_instFor(p):
            '''
                instFor : TkFor TkId TkIn exp TkTo exp TkArrow code TkRof
            '''
            p[0] = ["For",["In",["Ident",p[2]],["To", p[4], p[6]]],p[8]]
        
        # Gramatica de la instruccion de seleccion if
        def p_instIf(p):
            '''
                instIf : TkIf guards TkFi
            '''
            p[0] = ["If", p[2]]

        # Gramatica del bucle do
        def p_instDo(p):
            '''
                instDo : TkDo guards TkOd
            '''
            p[0] = ["Do", p[2]]

        # Estructura de las Guardas de las instrucciones de seleccion y bucle
        def p_guards(p):
            '''
                guards : guards TkGuard then 
                       | then
            '''
            if len(p) != 2: 
                p[0] = ["Guard", p[1], p[3]]
            else:
                p[0] = p[1]

        # Simbolos adicionales
        def p_then(p):
            '''
                then : exp TkArrow code
            '''
            p[0] = ["Then", p[1],p[3]]

        def p_ignorados(p):
            '''
            ignorados : TkComment
                      | TkSpace
                      | TkNewLine
                      | ignorados
            '''
            pass

        # Manejo de los errores
        def p_error(p):
            row = p.lexer.lineno - self.noLineas # Fila del Error
            excedente_col = 0
            with open(self.nombre_archivo, 'r') as f:
                for line in range(row-1):
                    excedente_col += sum( 1 for char in f.readline() )
            col = p.lexpos - excedente_col + 1 # Columna del error
            print(f"Sintaxis error in row {row}, column {col}: unexpected token '{p.value}'.")
            
        parser = yacc.yacc()
        return parser
    
    
    
    
    
    
    # Se imprime el AST
    
    def imprimir_ast(self):
        self.ast.print(0)
    
    # def  imprimir_ast(self):
    #     print("#################### ORIGINAL #######################")
    #     print(self.ast)
    #     print("########################### EXTENDIDO ####################")
    #     astExt = crear_ast_extendido(self.ast)
    #     imprimir_ast_extendido(astExt.sons[0])
        
    # def  imprimir_ast(self):
    #     self.imprimir_ast_rec(self.ast,0)
    
    # # Accion Recursiva de impresion sobre el AST
    # def imprimir_ast_rec(self, ast, lvl):
    #     if type(ast) != list:
    #         print("-"*lvl +str(ast))
    #     elif type(ast) == list:
    #         i = 1
    #         print("-"*lvl + str(ast[0]))
    #         while i < len(ast):
    #             self.imprimir_ast_rec(ast[i],lvl+1)
    #             i += 1
    #     else:
    #         pass
    #         #print("WIP")
    
    # # Retorna el AST asociado
    # def obtener_ast(self):
    #     return self.ast
    
    # # Se convierte el AST en String 
    # def ast_to_string(self):
    #     return self.ast_to_string_rec(self.ast,0)
    
    # # Accion recursiva de conversion a string sobre el AST
    # def ast_to_string_rec(self,ast,lvl):
    #     if type(ast) == str:
    #         return "-"*lvl + ast
    #     elif type(ast) == list:
    #         i = 1
    #         resultado = "-"*lvl + ast[0]
    #         while i < len(ast):
    #             resultado += "\n" + self.ast_to_string_rec(ast[i],lvl+1)
    #             i += 1
    #         return resultado
    #     else:
    #         print("WIP")