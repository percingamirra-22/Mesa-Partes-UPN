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

expedientes = cargar()

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

    opcion = input("Elige una opción: ")

    if opcion == "1":
        # registrar devuelve True solo si el expediente se creó de verdad;
        # en ese caso se guarda de inmediato (guardar tras cada cambio).
        if registrar(expedientes):
            guardar(expedientes)
            print("Expedientes guardados.")

    elif opcion == "2":
        buscar(expedientes)

    elif opcion == "3":
        listar(expedientes)

    elif opcion == "4":
        filtrar(expedientes)

    elif opcion == "5":
        ordenar(expedientes, "codigo")

    elif opcion == "6":
        ordenar(expedientes, "fecha_hora_recepcion")

    elif opcion == "7":
        # resolver devuelve True solo si el estado cambió de verdad;
        # en ese caso se guarda de inmediato (guardar tras cada cambio).
        if resolver(expedientes):
            guardar(expedientes)
            print("Expedientes guardados.")

    elif opcion == "8":
        ticket(expedientes)

    elif opcion == "9":
        exportar(expedientes)

    elif opcion == "0":
        print("Programa finalizado.")
        break

    else:
        print("Opción incorrecta.")
