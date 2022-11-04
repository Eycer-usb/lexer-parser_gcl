"""
El presente es el cliente del analizador lexico de GCL

Al ejecutarse es necesario pasarle como argumento el nombre
del archivo a leer. Es condicion necesaria que la extension
del archivo sea .gcl y que tenga permisos de lectura.

Al ejecutarse el cliente, este instancia la clase AnalizadorLexicoGCL
e imprime el resultado del analisis
"""

from src.AnalizadorLexicoGCL import AnalizadorLexicoGCL
import sys


def main():
    
    # Si no se ingresa el nombre de un archivo por 
    # los argumentos de ejecucion entonces se indicara el error
    # Por otro lado si se indica correctamente el archivo
    # entonces se instancia el analizador
    if(sys.argv[1] != None):
        lexer = AnalizadorLexicoGCL(sys.argv[1])

        # El lexer guarda en su diccionario llamado
        # respuesta el estatus del analisis. Si el resultado 
        # fue exitoso (estatus igual a 1)
        # entonces se imprimen los tokens, si por otro lado el analisis
        # falla (estatus == 1) se imprimen los errores del analisis
        if lexer.respuesta["estatus"] == 0:
            lexer.imprimirTokens()
        elif lexer.respuesta["estatus"] ==1:
            lexer.imprimirErrores()
    else:
        print('Introduzca un archivo valido')

# En caso de utilizar este cliente desde otro archivo
# este no ejecutara la funcion main automaticamente.
if __name__ == '__main__':
    main()