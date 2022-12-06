class nodito:
    def __init__(self, name, sons, father = None) -> None:
        self.name = name
        self.sons = sons
    
    def print(self, indent):
        self._print_rec(self,indent)
    
    def _print_rec(self, ast, ident):
        print("-"*ident + str(ast))
        for i in ast.sons:
            self._print_rec(i,ident+1)
    
    def __str__(self) -> str:
        return f"{self.name}"

class noditoBlock(nodito):
    def __init__(self, name, sons, father=None) -> None:
        super().__init__(name, sons, father)


class noditoDeclare(nodito):
    def __init__(self, name, sons, tabla, father=None) -> None:
        super().__init__(name, sons, father)
        self.symbolTable = tabla.copy()

        # le agregamos al no de declaracion los nodos con los nombres

        for key in self.symbolTable[0].keys():
            type = self.symbolTable[0][key]
            self.sons.append( 
                noditoIdentificador("variable", key, type, [], self)
                )

    def __str__(self) -> str:
        return f"{self.name}"

class noditoIdentificador(nodito):
    def __init__(self, name, key, type, sons=[], father=None):
        super().__init__(name, sons, father)
        self.type = type
        self.key = key
    def __str__(self) ->str:
        return f"{self.name}: {self.key} | type: {self.type}"



class noditoExpresion(nodito):
    def __init__(self, name, sons, type, father=None) -> None:
        super().__init__(name, sons, father)
        self.type = type
    
    def __str__(self) -> str:
        return f"{self.name} | type: {self.type}"
    
class noditoComma(nodito):
    def __init__(self, name, type, length, sons=[], father=None):
        super().__init__(name, sons, father)
        self.type = type
        self.length = length
    def __str__(self) ->str:
        return f"{self.name} | type: {self.type} with length={self.length}"

