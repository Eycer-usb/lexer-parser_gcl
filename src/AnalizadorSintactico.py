
import ply.yacc as yacc
import re

class analizadorSintactico: 
    def __init__(self, nombre_archivo,tokens):        
        
        # Informacion del arbol
        # usaremos listas para modelar el arbol cada sub arbol tendra la siguiente 
        # estructura:
        #[a,b,ci]
        # donde a es lo que se imprimira b es el padre/ raiz del subarbol
        # y ci es una lista con todos los hijos de b


        precedence = (
            ("left","TkComma"),
            ("left","TkOr"),
            ("left","TkAnd"),
            ("left","TkEqual","TkNEqual"),
            ("left","TkLess","TkLeq","TkGeq","TkGreater"),
            ("left","TkPlus","TkMinus"),
            ("left","TkMult"),
            ("right","UMinus","TkNot")
        )
        
        start = 'instBlock'
        
        # El programa vacio no es reconocido como valido
        # El apartado declare es opcional, pero si 
        # existe debe tener al menos una declaracion
        def p_instBlock(p):
            '''
            instBlock : TkOBlock declare TkCBlock
                      | TkOBlock declare code TkCBlock
                      | TkOBlock code TkCBlock
            '''
            if len(p) == 5:
                p[0] = ["Block",p[2],p[3]]
            else:
                p[0] = ["Block",p[2]]
        
        def p_declare(p):
            '''
                declare : TkDeclare declaration
                        | TkDeclare seqDeclare
            '''
            p[0] = ["Declare",p[2]]
        
        def p_declaration(p):
            '''
                declaration : DeclaList TkTwoPoints type
            '''
            #p[0] = [p[1] + p[2] + p[3], p[1], p[3]]
            p[0] = p[1] + " : " + p[3]

        def p_decaList(p):
            '''
            DeclaList : TkId TkComma DeclaList
                        | TkId
            '''
            if len(p) == 4:
                p[0] = p[1] + ", " +p[3]
            else:
                p[0] = p[1]
                
        def p_seqDeclare(p):
            '''
                seqDeclare : declaration TkSemicolon declaration
                           | seqDeclare TkSemicolon declaration
            '''
            p[0] = ["Sequencing", p[1], p[3]]
        
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

        def p_code(p):
            '''
                code : instruction
                     | sequencing
            '''
            p[0] = p[1]
        
        def p_sequencing(p):
            '''
                sequencing : instruction TkSemicolon instruction
                           | sequencing TkSemicolon instruction
            '''
            p[0] = ["Sequencing", p[1],p[3]]
        
        def p_instPrint(p):
            '''
                instPrint : TkPrint printAble
                          | TkPrint instConcat
            '''
            
            p[0] = ["Print", p[2]]
            
        def p_instConcat(p):
            '''
                instConcat : printAble TkConcat  printAble
                           | instConcat TkConcat printAble
            '''
            p[0] = ["Concat", p[1], p[3]]

        def p_printeAble1(p):
            '''
            printAble : TkString
            '''
            p[0] = f"String: {p[1]}"
        
        def p_printeAble2(p):
            '''
            printAble : exp
            '''
            p[0] = p[1]
               
        def p_arrayIni(p):
            '''
                arrayIni : exp TkComma exp
                         | arrayIni TkComma exp
            '''
            p[0] = ["Comma", p[1], p[3]]
        
        def p_instAsig(p):
            '''
                instAsig : TkId TkAsig exp
                         | TkId TkAsig arrayIni
                         | TkId TkAsig modArray
            '''
            p[0] = ["Asig",f"Ident: {p[1]}",p[3]]
        
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
        
        def p_consArray(p):
            '''
                consArray : TkId TkOBracket exp TkCBracket
            '''
            p[0] = ["ReadArray",f"Ident: {p[1]}", p[3]]

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
            p[0] = ["WriteArray",f"Ident: {p[1]}",["TwoPoints",p[3],p[5]]]
                
        def p_opBin(p):
            '''
                exp : exp TkPlus exp
                    | exp TkMinus exp
                    | exp TkMult exp
                    | exp TkAnd exp
                    | exp TkOr exp
                    | exp TkLess exp
                    | exp TkLeq exp
                    | exp TkGeq exp
                    | exp TkGreater exp
                    | exp TkEqual exp
                    | exp TkNEqual exp
            '''
            if p[2] == "+":
                p[0] = ["Plus",p[1],p[3]]
            elif p[2] == "-":
                p[0] = ["Minus",p[1],p[3]]
            elif p[2] == "*":
                p[0] = ["Mult",p[1],p[3]]
            elif p[2] == "/\\":
                p[0] = ["And",p[1],p[3]]
            elif p[2] == "\\/":
                p[0] = ["Or",p[1],p[3]]
            elif p[2] == "<":
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
                p[0] = ["Not Equal",p[1],p[3]]
        
        def p_exp(p):
            '''
                exp : TkNot exp
                    | TkOpenPar exp TkClosePar
                    | consArray
            '''
            if len(p) == 3:
                p[0] = ["Not",p[2]]
            elif len(p) == 4:
                p[0] = p[1] + p[2] + p[3]
            else: 
                p[0] = p[1]

        def p_literales(p):
            '''
                exp : TkNum
                    | TkTrue
                    | TkFalse
                    | TkMinus exp %prec UMinus
            '''
            if len(p) == 2:
                p[0] = "Literal: " + p[1]
            else:
                p[0] = ["Minus", p[2]]
        
        def p_id(p):
            '''
                exp : TkId 
            '''        
            p[0] = f"Ident: {p[1]}"
        
        def p_instFor(p):
            '''
                instFor : TkFor TkId TkIn exp TkTo exp TkArrow code TkRof
            '''
            p[0] = ["For",["In",f"Ident: {p[2]}",["To", p[4], p[6]]],p[8]]
        
        def p_instIf(p):
            '''
                instIf : TkIf guards TkFi
            '''
            p[0] = ["If", p[2]]

        def p_instDo(p):
            '''
                instDo : TkDo guards TkOd
            '''
            p[0] = ["Do", p[2]]

        def p_guards(p):
            '''
                guards : guards TkGuard then 
                       | then
            '''
            if len(p) != 2: 
                p[0] = ["Guard", p[1], p[3]]
            else:
                p[0] = p[1]

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
            instSkip : TkSkip
            '''
            pass

        def p_error(p):
            print("error")
        
        parser = yacc.yacc()
        self.archivo = open(nombre_archivo)
        contenido = self.archivo.read()
        self.archivo.close()
        self.ast = parser.parse(contenido)
    
    def  imprimir_ast(self):
        self.imprimir_ast_rec(self.ast,0)
    
    def imprimir_ast_rec(self, ast, lvl):
        if type(ast) == str:
            print("-"*lvl +ast)
        elif type(ast) == list:
            i = 1
            print("-"*lvl +ast[0])
            while i < len(ast):
                self.imprimir_ast_rec(ast[i],lvl+1)
                i += 1
        else:
            print("WIP")
    
    def obtener_ast(self):
        return self.ast
    
    def ast_to_string(self):
        return self.ast_to_string_rec(self.ast,0)
    
    def ast_to_string_rec(self,ast,lvl):
        if type(ast) == str:
            return "-"*lvl + ast
        elif type(ast) == list:
            i = 1
            resultado = "-"*lvl + ast[0]
            while i < len(ast):
                resultado += "\n" + self.ast_to_string_rec(ast[i],lvl+1)
                i += 1
            return resultado
        else:
            print("WIP")