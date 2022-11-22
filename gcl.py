"""
El presente es el cliente del analizador de GCL

Al ejecutarse es necesario pasarle como argumento el nombre
del archivo a leer. Es condicion necesaria que la extension
del archivo sea .gcl y que tenga permisos de lectura.

"""

from src.AnalizadorLexicoGCL import AnalizadorLexicoGCL
from src.AnalizadorSintactico import analizadorSintactico
import sys

def main():
    
    # Si no se ingresa el nombre de un archivo por 
    # los argumentos de ejecucion entonces se indicara el error
    # Por otro lado si se indica correctamente el archivo
    # entonces se instancia el analizador
    if(len(sys.argv) > 1):
        lexer = AnalizadorLexicoGCL(sys.argv[1])
        if lexer.estatus == 0: 
            a = analizadorSintactico(sys.argv[1],lexer.tokens)
            a.imprimir_ast()
            # archivo = open("salida.out","w")
            # archivo.write(a.ast_to_string())
            # archivo.close()
        elif lexer.estatus == 1:
            lexer.imprimirErrores()
    else:
        print('Introduzca un archivo valido')

# En caso de utilizar este cliente desde otro archivo
# este no ejecutara la funcion main automaticamente.
if __name__ == '__main__':
    main()


"""
        'Los grandes hombres no nacen siendo grandes, crecen grandiosamente'
        
        - El Padrino
        
"""