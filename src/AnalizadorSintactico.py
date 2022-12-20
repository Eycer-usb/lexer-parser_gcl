import ply.yacc as yacc
import sys
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
        self.ast = parser.parse(contenido,tracking = True)

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
        global symbolTablesFor
        
        symbolTables = []
        symbolTablesFor = []

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
                p[0] = noditoBlock("Block",[p[2],p[3]])
                p[0].sons[0].father = p[0]
                p[0].sons[1].father = p[0]
            else:
                p[0] = noditoBlock("Block",[p[2]])
                p[0].sons[0].father = p[0]
            
            symbolTables.pop(0)

        # Sentencia de Declaracion
        def p_declare(p):
            '''
                declare : TkDeclare declaration
                        | TkDeclare seqDeclare
            '''
            
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
            if p[1] in symbolTablesFor: 
                self.semantic_error( p, f"It is changing the variable \"{p[1]}\", which is a control variable of a 'for' statement")

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
            for i in p[3]:
                if p[1].get(i)!= None:
                    self.semantic_error(p, "Error de sintaxis en la secuencia de declaraciones")
                
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
                 p[0] = p[1] + p[2] + p[3] + p[4] + p[5] + p[6]
            elif len(p) == 9:
                p[0] =  p[1] + p[2] + "-" + p[4] + p[5] + "-" + p[7] + p[8]
            else:
                if p[3] == "-":
                    p[0] =  p[1] + p[2] + "-" + p[4] + p[5] + p[6] + p[7]
                else:
                    p[0] =  p[1] + p[2] + p[3] + p[4] + p[6] + p[7]

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
            p[0] = nodito('Print', [p[2]], [])

        # Instruccion Skip
        def p_instSkip(p):
            '''
                instSkip : TkSkip
            '''
            p[0] = nodito("Skip",[])
        
        # Instruccion Concatenacion
        def p_instConcat(p):
            '''
                instConcat : printAble TkConcat  printAble
                           | instConcat TkConcat printAble
            '''
            p[0] = nodito("Concat", [p[1], p[3]])

        # Sentencia Imprimible de Strings
        def p_printeAble1(p):
            '''
            printAble : TkString
            '''
            p[0] = noditoIdentificador("String", p[1], "String")
        
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
            ''' 

            if p[1].type != p[3].type: self.semantic_error(p, 'Wrong type in array initialization')
            p[0] = noditoComma("Comma", sons= [p[1], p[3]],type = p[1].type, length = 2)

        def p_arrayIni2(p):
            """
                arrayIni : arrayIni TkComma exp 
            """
            if p[1].type != p[3].type: self.semantic_error(p, 'Wrong type in array initialization')
            p[0] = noditoComma("Comma", sons= [p[1], p[3]],type =p[1].type, length = p[1].lenght + 1)
            
        # Instruccion de Asignacion
        def p_instAsig(p):
            '''
                instAsig : TkId TkAsig arrayIni
                         | TkId TkAsig exp 
                         | TkId TkAsig modArray
            '''
            if p[1] in symbolTablesFor: 
               self.semantic_error( p, f"It is changing the variable \"{p[1]}\", which is a control variable of a 'for' statement")

            for i in symbolTables:
                if i.get(p[1]) != None:
                    if "array" in i[p[1]] and p[3].type == 'int':
                        p[0] = nodito("Asig",[noditoIdentificador("Ident", key = p[1], type =i[p[1]]), p[3]] ) 
                    elif i[p[1]] != p[3].type:
                        self.semantic_error(p, f'Try to assign a type {p[3].type} to a type {i[p[1]]}')
                    else:
                        p[0] = nodito("Asig",[noditoIdentificador("Ident", key = p[1], type =i[p[1]]), p[3]] ) 
                    return 
            
            self.semantic_error(p, f'Undefined variable "{p[1]}"')     
        
        # Generalizacion de instrucciones
        def p_instruction(p):
            '''
                instruction : instPrint
                            | instAsig
                            | instSkip
                            | instBlock
                            | instIf
                            | instDo
            '''
            p[0] = p[1]
        
        def p_for(p):
            '''
            instruction : instFor
            '''
            
            p[0] = p[1]
            
            symbolTablesFor.pop(0)
        
        # Caracterizacion de los arrays
        def p_consArray(p):
            '''
                consArray : TkId TkOBracket exp TkCBracket
            '''
            if p[1] in symbolTablesFor: 
                self.semantic_error( p, f"It is changing the variable \"{p[1]}\", which is a control variable of a 'for' statement")
            
            if p[3].type != "int": self.semantic_error(p, (f'Incorrect type in accessor, "{p[3].key}", expected "int" but "' + 
                f'{p[3].type}" given'))

            for i in symbolTables:
                if i.get(p[1]) == None:
                    self.semantic_error( p, f"variable \"{p[1]}\" is undefined")
                else:
                    tipo = i[p[1]]
                    p[0] = noditoExpresion("ReadArray",[
                        noditoIdentificador("Ident", key = p[1] , type= tipo ), p[3]
                        ],"int") 
                return 
            self.semantic_error( p, f"variable \"{p[1]}\" is undefined")
 
        
            #p[0] = ["ReadArray",["Ident", {p[1]}], p[3]]

        def p_consArray1(p):
            '''
                consArray : modArray TkOBracket exp TkCBracket
            '''
            #p[0] = ["ReadArray", p[1], p[3]]
            if  p[3].type != "int" : self.semantic_error( p, f"Wrong type reading array")

            
            p[0] = noditoExpresion("ReadArray",[p[1], p[3]],"int")
        
        def p_modArray(p):
            '''
                modArray : modArray TkOpenPar exp TkTwoPoints exp TkClosePar
                         | finish
                
            '''
            if len(p) == 2: 
                p[0] = p[1]
            else:
                if p[3].type != "int" or p[5].type != "int": self.semantic_error(p, 'Wrong type updating array')         
                #p[0] = ["WriteArray",p[1], ["TwoPoints", p[3], p[5]]]
                p[0] = noditoExpresion("WriteArray",[p[1], nodito("TwoPoints", [p[3], p[5]])],p[1].type)
                
        
        def p_modArray1(p):
            '''
                finish : TkId TkOpenPar exp TkTwoPoints exp TkClosePar
            '''
            if p[1] in symbolTablesFor: 
                self.semantic_error( p, f"It is changing the variable \"{p[1]}\", which is a control variable of a 'for' statement")
            
            if p[3].type != "int" or p[5].type != "int": self.semantic_error(p, 'Wrong type updating array') 
                                   
            if p[1] in symbolTablesFor: 
                self.semantic_error( p, f"It is changing the variable \"{p[1]}\", which is a control variable of a 'for' statement")
                
            for i in symbolTables:
                if i.get(p[1])!= None:
                    if "array" in i[p[1]]:
                        p[0] = noditoExpresion("WriteArray",[noditoIdentificador("Ident",p[1],i[p[1]]), nodito("TwoPoints", [p[3], p[5]])],i[p[1]])
                        return
                    else:
                        self.semantic_error(p, 'Wrong type of id updating array') 
                
                self.semantic_error(p, 'Wrong id updating array') 
        
        # Gramatica de los Operadores Binarios
        def p_opBin(p):
            '''
                exp : exp TkPlus exp
                    | exp TkMinus exp
                    | exp TkMult exp
            '''
            if p[1].type != "int" or p[3].type != "int": self.semantic_error(p, "Wrong integer operation")
            
            if p[2] == "+":
                p[0] = noditoExpresion("Plus",[p[1],p[3]],"int")

            elif p[2] == "-":
                p[0] = noditoExpresion("Minus",[p[1],p[3]],"int")

            elif p[2] == "*":
                p[0] = ["Mult",p[1],p[3]]
                p[0] = noditoExpresion("Mult",[p[1],p[3]],"int")

        
        def p_opBin2(p):
            '''
                exp : exp TkAnd exp
                    | exp TkOr exp
            '''
            if p[1].type != "bool" or p[3].type != "bool": self.semantic_error(p, "Wrong boolean operation")

            if p[2] == "/\\":
                
                p[0] = noditoExpresion("And",[p[1],p[3]],"bool")
            elif p[2] == "\\/":
                
                p[0] = noditoExpresion("Or",[p[1],p[3]],"bool")
        
        def p_opBin3(p):
            '''
                exp : exp TkLess exp
                    | exp TkLeq exp
                    | exp TkGeq exp
                    | exp TkGreater exp
            '''
            if p[1].type != "int" or p[3].type != "int": raise(self.semantic_error(p, f'Integer comparative operations is comparing {p[1].type} and {p[3].type}'))
            
            if p[2] == "<":
                p[0] = noditoExpresion("Less",[p[1],p[3]],"bool")
                
            elif p[2] == "<=":
                p[0] = noditoExpresion("Leq",[p[1],p[3]],"bool")
                
            elif p[2] == ">=":
                p[0] = noditoExpresion("Geq",[p[1],p[3]],"bool")
                
            elif p[2] == ">":
                p[0] = noditoExpresion("Greater",[p[1],p[3]],"bool")
                

        def p_opBin4(p):
            '''
                exp : exp TkEqual exp
                    | exp TkNEqual exp
            '''
            if p[1].type != p[3].type: self.semantic_error(p, f'Comparing {p[1].type} and { p[3].type }')

            if p[2] == "==":
                p[0] = noditoExpresion("Equal",[p[1],p[3]],"bool")
            elif p[2] == "!=":
                p[0] = noditoExpresion("NotEqual",[p[1],p[3]],"bool")

        
        # Generalizacion de la gramatica de las expresiones
        def p_exp(p):
            '''
                exp : TkNot exp
                    | TkOpenPar exp TkClosePar
                    | consArray
            '''
            if len(p) == 3:
    
                if p[2].type != "bool":
                    self.semantic_error(p, 'Not operator work only over boolean expresions') 
                    
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
                self.semantic_error(p, 'Minus operator only accept "int" as argument') 

            p[0] = noditoExpresion("Minus",[p[2]],"int")
            
        def p_literales1(p):
            '''
                exp : TkNum
            '''
            
            p[0] = noditoIdentificador("Literal",p[1],"int")

        def p_literales2(p):
            '''
                exp : TkTrue
                    | TkFalse
            '''
            
            p[0] = noditoIdentificador("Literal", p[1], "bool")
        
        # Definicion de las estructuras de las variables (ids)
        def p_id(p):
            '''
                exp : TkId 
            '''        
            

            for i in symbolTables:
                if i.get(p[1]) != None:
                    p[0] = noditoIdentificador("Ident",p[1],i[p[1]])
                    return
            
            self.semantic_error(p, f'Undefined varible {p[1]}')
        
        # Gramatica del bucle for
        def p_instFor(p):
            '''
                instFor : TkFor range TkArrow code TkRof
            '''
            #p[0] = ["For",["In",["Ident",p[2]],["To", p[4], p[6]]],p[8]]
            p[0] = nodito("For",[p[2],p[4]]) # WIP
        
        def p_instForRange(p):
            '''
                range : TkId TkIn exp TkTo exp 
            '''  
            global symbolTablesFor

            if len(symbolTablesFor) == 0 :
                symbolTablesFor = [p[1]]
            else:
                symbolTablesFor = [p[1],*symbolTablesFor]
            
            if p[3].type != "int" or p[5].type != "int": self.semantic_error(p, 'Incorrect type in "range" of for instruction')
            
            p[0] = nodito("In",[noditoIdentificador("Ident",p[1],"int"), nodito("To",[p[3],p[5]])])

        # Gramatica de la instruccion de seleccion if
        def p_instIf(p):
            '''
                instIf : TkIf guards TkFi
            '''
            
            p[0] = nodito("If", [p[2]])

        # Gramatica del bucle do
        def p_instDo(p):
            '''
                instDo : TkDo guards TkOd
            '''
            
            p[0] = nodito("Do", [p[2]])

        # Estructura de las Guardas de las instrucciones de seleccion y bucle
        def p_guards(p):
            '''
                guards : guards TkGuard then 
                       | then
            '''
            if len(p) != 2: 
                
                p[0] = nodito("Guard", [p[1], p[3]])
            else:
                p[0] = p[1]

        # Simbolos adicionales
        def p_then(p):
            '''
                then : exp TkArrow code
            '''
            #p[0] = ["Then", p[1],p[3]]
            p[0] = nodito("Then", (p[1],p[3]))

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

    def semantic_error(self, p, message):
        row = p.lexer.lineno - self.noLineas-1 # Fila del Error
        excedente_col = 0
        with open(self.nombre_archivo, 'r') as f:
            for line in range(row):
                excedente_col += sum( 1 for char in f.readline() )
        col = p.lexer.lexpos - excedente_col + 3 # Columna del error
        #help(p.lexer)

        print( f'Error in row {row}, column {col}: ' + message)
        sys.exit()
    