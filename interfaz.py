# ------------------------------------------------------------------
# interfaz.py — Capa de conversación con el usuario: menús numerados,
# re-pregunta ante errores y cancelación con CANCELAR.
#
# Depende solo de validadores.py (para verificar que la opción elegida
# del menú es un número válido). Es la única capa que habla con el
# usuario en la captura de datos: registro y main la usan, nunca al revés.
# ------------------------------------------------------------------

from validadores import solo_digitos

CANCELAR = "CANCELAR"


def pedir_texto(mensaje, validar, mensaje_error):
    """Pide un texto y repite hasta que la función validar devuelva True.
    Muestra el mensaje de error específico de cada campo.
    Devuelve None si el usuario escribe CANCELAR (se anula el registro)."""
    while True:
        valor = input(mensaje + " (" + CANCELAR + " para anular): ").strip()
        if valor.upper() == CANCELAR:
            return None
        if validar(valor):
            return valor
        print("ERROR:", mensaje_error)


def pedir_opcion(mensaje, opciones):
    """Muestra las opciones numeradas del 1 al N y devuelve el valor elegido
    (internamente resta 1 para obtener el índice de la lista).
    Devuelve None si el usuario escribe CANCELAR (se anula el registro)."""
    print()
    print(mensaje)
    for i in range(len(opciones)):
        print("  " + str(i + 1) + ". " + opciones[i])
    while True:
        respuesta = input("Elige una opción (" + CANCELAR + " para anular): ").strip()
        if respuesta.upper() == CANCELAR:
            return None
        if solo_digitos(respuesta) and 1 <= int(respuesta) <= len(opciones):
            return opciones[int(respuesta) - 1]
        print("ERROR: escribe un número entre 1 y", len(opciones))


def anular_registro():
    """Mensaje estándar cuando el usuario cancela el registro en curso."""
    print("Registro anulado. No se guardó nada.")
