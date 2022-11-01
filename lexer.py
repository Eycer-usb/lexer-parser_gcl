from src.AnalizadorLexicoGCL import AnalizadorLexicoGCL
import sys


def main():
    if(sys.argv[1] != None):
        print ("Abriendo el archivo " + sys.argv[1])
        lexer = AnalizadorLexicoGCL(sys.argv[1])
        lexer.imprimirTokens()
    else:
        print('Introduzca un archivo valido')

if __name__ == '__main__':
    main()