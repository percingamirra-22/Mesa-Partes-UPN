# ------------------------------------------------------------------
# main.py — Punto de entrada: menú principal y ciclo del programa.
#
# Decisiones de arquitectura (el porqué, no el qué):
# - El estado vive en memoria y se persiste tras CADA cambio real,
#   no al salir. Motivo: si el proceso muere, se pierde como máximo
#   la operación en curso, nunca lo registrado antes. En una mesa de
#   partes cada expediente es un documento físico ya recibido:
#   perderlo no es aceptable.
# - El menú se despacha por NÚMERO y no por texto (V5): la entrada se
#   limpia con strip() y se interpreta con int(), así " 1", "1 " y
#   "01" son la misma opción, igual que en los menús internos.
# - Las interrupciones se capturan SOLO aquí, en el borde del
#   programa (V6): cualquier input que explote sube hasta este try y
#   el programa termina con un mensaje limpio. Como el guardado es
#   por operación y atómico, interrumpir a mitad de un input nunca
#   deja el CSV dañado.
# ------------------------------------------------------------------

from almacenamiento import cargar, guardar
from registro import (
    buscar,
    exportar,
    filtrar,
    listar,
    ordenar,
    registrar,
    resolver,
    ticket,
)
from validadores import solo_digitos

expedientes = cargar()

# Ctrl+C (KeyboardInterrupt) y Ctrl+Z+Enter (EOFError) se capturan aquí:
# cualquier interrupción en cualquier input del programa sube hasta este
# bloque y termina con un mensaje limpio, no con un traceback (V6).
# La base no se corrompe: la política de guardar tras cada cambio real
# deja el CSV completo tras la última operación, y guardar() es atómico.
try:
    while True:
        print("\n=== Menu de Mesa de Partes ===")
        print("1. Registrar expediente")
        print("2. Buscar expediente")
        print("3. Listar expedientes")
        print("4. Filtrar por área")
        print("5. Ordenar por código")
        print("6. Ordenar por fecha")
        print("7. Marcar como RESUELTO")
        print("8. Generar ticket")
        print("9. Exportar CSV")
        print("0. Salir")

        opcion = input("Elige una opción: ").strip()

        # Menú unificado con pedir_opcion (V5): se limpia la entrada con
        # strip() y se despacha por NÚMERO, no por texto. Así " 1", "1 "
        # y "01" valen aquí igual que en los menús internos.
        if not solo_digitos(opcion):
            print("Opción incorrecta.")
            continue
        numero = int(opcion)

        if numero == 1:
            # registrar devuelve True solo si el expediente se creó de verdad;
            # en ese caso se guarda de inmediato (guardar tras cada cambio).
            if registrar(expedientes):
                guardar(expedientes)
                print("Expedientes guardados.")

        elif numero == 2:
            buscar(expedientes)

        elif numero == 3:
            listar(expedientes)

        elif numero == 4:
            filtrar(expedientes)

        elif numero == 5:
            ordenar(expedientes, "codigo")

        elif numero == 6:
            ordenar(expedientes, "fecha_hora_recepcion")

        elif numero == 7:
            # resolver devuelve True solo si el estado cambió de verdad;
            # en ese caso se guarda de inmediato (guardar tras cada cambio).
            if resolver(expedientes):
                guardar(expedientes)
                print("Expedientes guardados.")

        elif numero == 8:
            ticket(expedientes)

        elif numero == 9:
            exportar(expedientes)

        elif numero == 0:
            print("Programa finalizado.")
            break

        else:
            print("Opción incorrecta.")

except (KeyboardInterrupt, EOFError):
    print("\nPrograma interrumpido. El último cambio quedó guardado.")
