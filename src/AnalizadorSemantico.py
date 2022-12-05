class nodito:
    def __init__(self,name, sons, father = None) -> None:
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
    def __init__(self, name, sons, father=None) -> None:
        super().__init__(name, sons, father)
        self.symbolTable = {}

class noditoExpresion(nodito):
    def __init__(self, name, sons, type,father=None) -> None:
        super().__init__(name, sons, father)
        self.type = type
    