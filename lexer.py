from src.AnalizadorLexicoGCL import AnalizadorLexicoGCL
import sys


def main():
    if(sys.argv[1] != None):
        print ("Abriendo el archivo " + sys.argv[1])
        lexer = AnalizadorLexicoGCL(sys.argv[1])
        if lexer.respuesta["estatus"] == 0:
            lexer.imprimirTokens()
        elif lexer.respuesta["estatus"] ==1:
            lexer.imprimirErrores()
    else:
        print('Introduzca un archivo valido')

if __name__ == '__main__':
    main()