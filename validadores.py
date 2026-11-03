# ------------------------------------------------------------------
# validadores.py — Reglas que definen qué es un dato válido.
#
# Funciones PURAS: no usan input() ni print(). Reciben texto y
# devuelven True/False (validar_numero_documento devuelve "" si el
# dato es válido, o un mensaje de error específico).
# No importa de ningún otro módulo del proyecto: es una "hoja" del
# árbol de dependencias, imposible de crear ciclos de importación.
# ------------------------------------------------------------------

DIGITOS = "0123456789"
# Letras latinas permitidas: A-Z, a-z más las vocales con tilde, ü y ñ
# del español (mayúsculas y minúsculas). Todo lo que NO esté aquí
# (chino, árabe, cirílico, etc.) se rechaza en la validación de nombres,
# garantizando que la boleta PDF nunca falle por caracteres no latinos.
LETRAS_LATINAS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZáéíóúüñÁÉÍÓÚÜÑ"
# Signos de puntuación permitidos en los textos libres (domicilio, asunto).
# Todos son representables en latin-1, el alfabeto de la fuente Helvetica
# de la boleta PDF: garantiza que el PDF nunca falle por codificación.
SIMBOLOS_LIBRES = " .,:;-()¡!¿?'\"#%&$@°"


# ------------------------------------------------------------------
# Verificaciones básicas de caracteres
# ------------------------------------------------------------------
def solo_digitos(texto):
    """True si todos los caracteres son dígitos del 0 al 9 (ASCII).
    Se usa esta verificación en vez de .isdigit() porque .isdigit()
    también acepta dígitos de otros alfabetos (ej. arábigos).
    La cadena vacía NO cuenta como válida (caso borde: si no se
    escribe nada, el bucle nunca se ejecuta y habría que devolver
    True "al vacío", por eso se rechaza explícitamente)."""
    if texto == "":
        return False
    for caracter in texto:
        if caracter not in DIGITOS:
            return False
    return True


def es_letra_latina(caracter):
    """True si el carácter es una letra latina: A-Z, a-z o las
    vocales con tilde, ü y ñ del español."""
    return caracter in LETRAS_LATINAS


def contiene_letra_latina(texto):
    """True si el texto tiene al menos una letra latina."""
    for caracter in texto:
        if es_letra_latina(caracter):
            return True
    return False


def texto_libre_valido(texto):
    """True si todos los caracteres son 'imprimibles' latinos: letras
    latinas, dígitos o signos de puntuación comunes del español.
    Se usa para los campos de texto libre (domicilio, asunto) para
    garantizar que la boleta PDF nunca falle por codificación."""
    for caracter in texto:
        permitido = (
            es_letra_latina(caracter)
            or caracter in DIGITOS
            or caracter in SIMBOLOS_LIBRES
        )
        if not permitido:
            return False
    return True


# ------------------------------------------------------------------
# Validadores de campo: cada uno devuelve True o False
# ------------------------------------------------------------------
def nombre_natural_valido(texto):
    """Letras latinas (con ñ y tildes), espacios, guion y apóstrofo.
    Mínimo 2 caracteres, al menos una letra, sin números ni símbolos."""
    if len(texto) < 2:
        return False
    if not contiene_letra_latina(texto):
        return False
    for caracter in texto:
        if not (es_letra_latina(caracter) or caracter in " -'"):
            return False
    return True


def nombre_juridico_valido(texto):
    """Mínimo 2 caracteres y al menos una letra latina. Puede incluir
    dígitos, puntos y espacios (evita confundirlo con un RUC)."""
    if len(texto) < 2:
        return False
    if not contiene_letra_latina(texto):
        return False
    for caracter in texto:
        if not (es_letra_latina(caracter) or caracter in DIGITOS or caracter in ". "):
            return False
    return True


def domicilio_valido(texto):
    """No vacío, máximo 150 caracteres, solo texto latino."""
    if texto == "" or len(texto) > 150:
        return False
    return texto_libre_valido(texto)


def telefono_valido(texto):
    """9 dígitos, y el primero debe ser 0 (fijo) o 9 (celular)."""
    if len(texto) != 9:
        return False
    if not solo_digitos(texto):
        return False
    return texto[0] == "0" or texto[0] == "9"


def telefono_o_vacio(texto):
    """El teléfono es opcional, pero si se escribe debe ser válido."""
    return texto == "" or telefono_valido(texto)


def correo_valido(texto):
    """Descompuesto con funciones de strings, sin expresiones regulares:
    una sola @, texto antes y después, dominio con al menos un punto,
    sin puntos pegados o en los extremos del dominio, sin espacios."""
    if " " in texto:
        return False

    partes = texto.split("@")
    if len(partes) != 2:  # garantiza exactamente una @
        return False

    local = partes[0]
    dominio = partes[1]

    if local == "" or dominio == "":
        return False
    if "." not in dominio:
        return False
    if dominio.startswith(".") or dominio.endswith("."):
        return False
    if ".." in dominio:
        return False
    return True


def correo_o_vacio(texto):
    return texto == "" or correo_valido(texto)


def asunto_valido(texto):
    """Entre 10 y 200 caracteres, solo texto latino."""
    if not (10 <= len(texto) <= 200):
        return False
    return texto_libre_valido(texto)


def folios_valido(texto):
    """Solo dígitos, entero entre 1 y 1000."""
    if not solo_digitos(texto):
        return False
    cantidad = int(texto)
    return 1 <= cantidad <= 1000


def validar_numero_documento(numero, tipo):
    """Validación condicional según el tipo de documento elegido.
    Devuelve "" si es válido, o un mensaje de error específico."""
    if tipo == "DNI":
        if len(numero) == 8 and solo_digitos(numero):
            return ""
        return "El DNI debe tener exactamente 8 dígitos numéricos."

    if tipo == "CE":
        if len(numero) == 12 and solo_digitos(numero):
            return ""
        return "El CE debe tener exactamente 12 dígitos numéricos."

    if tipo == "PASAPORTE":
        if len(numero) == 12:
            valido = True
            for caracter in numero:
                es_letra_ascii = caracter.isalpha() and caracter.isascii()
                if not (caracter in DIGITOS or es_letra_ascii):
                    valido = False
            if valido:
                return ""
        return "El pasaporte debe tener 12 caracteres alfanuméricos (letras A-Z o dígitos)."

    if tipo == "RUC":
        if len(numero) == 11 and solo_digitos(numero):
            if numero[0:2] == "10" or numero[0:2] == "20":
                return ""
        return "El RUC debe tener 11 dígitos y empezar con 10 o 20."

    return "Tipo de documento desconocido."
