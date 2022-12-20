from src.GCLtoPreApp import translate
from src.AnalizadorSemantico import *

ast = noditoIdentificador("Literal","1234","int")

print(translate(ast))