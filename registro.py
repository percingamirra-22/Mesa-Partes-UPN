from datetime import datetime
from pathlib import Path

from almacenamiento import guardar
from interfaz import CANCELAR, anular_registro, pedir_opcion, pedir_texto
from ticket_pdf import generar_pdf
from validadores import (
    asunto_valido,
    correo_o_vacio,
    correo_valido,
    domicilio_valido,
    folios_valido,
    nombre_juridico_valido,
    nombre_natural_valido,
    solo_digitos,
    telefono_o_vacio,
    validar_numero_documento,
)

# ------------------------------------------------------------------
# Catálogos cerrados: el usuario elige por número, nunca escribe libre.
# ------------------------------------------------------------------
TIPOS_PERSONA = ["NATURAL", "JURÍDICA"]
TIPOS_DOCUMENTO_IDENTIDAD = ["DNI", "CE", "PASAPORTE", "RUC"]
TIPOS_DOCUMENTO = [
    "OFICIO",
    "CARTA",
    "INFORME",
    "RESOLUCIÓN",
    "DECLARACIÓN JURADA",
    "CONSTANCIA",
    "SOLICITUD TUPA",
]
TIPOS_TRAMITE = ["TUPA", "NO TUPA"]
AREAS = [
    "DIRECCIÓN",
    "EMPLEABILIDAD",
    "MARKETING",
    "ACADÉMICA",
    "ADMINISTRACIÓN",
    "TI",
]


# ------------------------------------------------------------------
# Operaciones de la mesa de partes
# ------------------------------------------------------------------
def registrar(lista):
    print("\n--- REGISTRAR EXPEDIENTE ---")
    print("Escribe " + CANCELAR + " en cualquier pregunta para anular el registro.")

    # 1) Tipo de persona (menú)
    tipo_persona = pedir_opcion("Tipo de persona:", TIPOS_PERSONA)
    if tipo_persona is None:
        anular_registro()
        return

    # 2) Nombres según el tipo de persona (la regla depende del paso 1)
    if tipo_persona == "NATURAL":
        nombres_apellidos = pedir_texto(
            "Nombres y apellidos",
            nombre_natural_valido,
            "Solo letras latinas (con ñ y tildes), espacios, guion o apóstrofo. Mínimo 2 caracteres, sin números.",
        )
    else:
        nombres_apellidos = pedir_texto(
            "Nombre de la persona jurídica",
            nombre_juridico_valido,
            "Solo letras latinas, dígitos, puntos y espacios. Mínimo 2 caracteres y al menos una letra.",
        )
    if nombres_apellidos is None:
        anular_registro()
        return

    # 3) Tipo de documento de identidad (menú)
    tipo_documento_identidad = pedir_opcion(
        "Tipo de documento de identidad:", TIPOS_DOCUMENTO_IDENTIDAD
    )
    if tipo_documento_identidad is None:
        anular_registro()
        return

    # 4) Número de documento (validación condicional, con error específico)
    while True:
        numero_documento_identidad = input(
            "Número de documento (" + tipo_documento_identidad + "): "
        ).strip()
        if numero_documento_identidad.upper() == CANCELAR:
            anular_registro()
            return
        error = validar_numero_documento(
            numero_documento_identidad, tipo_documento_identidad
        )
        if error == "":
            break
        print("ERROR:", error)

    # 5) Domicilio
    domicilio = pedir_texto(
        "Domicilio",
        domicilio_valido,
        "No puede estar vacío, máximo 150 caracteres, solo letras latinas, números y signos comunes.",
    )
    if domicilio is None:
        anular_registro()
        return

    # 6) Teléfono (opcional, pero si se escribe debe cumplir el formato)
    telefono = pedir_texto(
        "Teléfono (opcional)",
        telefono_o_vacio,
        "El teléfono debe tener 9 dígitos y empezar con 0 o 9 (ej. 01XXXXXXX o 9XXXXXXXX).",
    )
    if telefono is None:
        anular_registro()
        return

    # 7) Correo: obligatorio si no hay teléfono, opcional si sí hay
    if telefono == "":
        correo_electronico = pedir_texto(
            "Correo electrónico (obligatorio, no hay teléfono)",
            correo_valido,
            "Correo inválido: texto@dominio.algo, sin espacios, exactamente una @ y al menos un punto en el dominio.",
        )
    else:
        correo_electronico = pedir_texto(
            "Correo electrónico (opcional)",
            correo_o_vacio,
            "Correo inválido: texto@dominio.algo, sin espacios, exactamente una @ y al menos un punto en el dominio.",
        )
    if correo_electronico is None:
        anular_registro()
        return

    # 8) Tipo de documento (menú)
    tipo_documento = pedir_opcion("Tipo de documento:", TIPOS_DOCUMENTO)
    if tipo_documento is None:
        anular_registro()
        return

    # 9) Tipo de trámite (menú)
    tipo_tramite = pedir_opcion("Tipo de trámite:", TIPOS_TRAMITE)
    if tipo_tramite is None:
        anular_registro()
        return

    # 10) Asunto
    asunto = pedir_texto(
        "Asunto",
        asunto_valido,
        "Entre 10 y 200 caracteres, solo letras latinas, números y signos comunes.",
    )
    if asunto is None:
        anular_registro()
        return

    # 11) Área destinataria (menú)
    area_destinatario = pedir_opcion("Área destinataria:", AREAS)
    if area_destinatario is None:
        anular_registro()
        return

    # 12) Número de folios
    numero_folios = pedir_texto(
        "Número de folios",
        folios_valido,
        "Los folios deben ser un número entero entre 1 y 1000.",
    )
    if numero_folios is None:
        anular_registro()
        return

    # ---- Generación del código (con protección contra datos corruptos) ----
    anio = datetime.now().year
    mayor = 0
    for expediente in lista:
        codigo = expediente.get("codigo", "")
        sufijo = codigo[-7:]
        if codigo.startswith(f"EXP-{anio}-"):
            if len(sufijo) == 7 and solo_digitos(sufijo):
                mayor = max(mayor, int(sufijo))

    # ---- Construcción del expediente con los campos automáticos ----
    datos = {
        "tipo_persona": tipo_persona,
        "nombres_apellidos": nombres_apellidos,
        "tipo_documento_identidad": tipo_documento_identidad,
        "numero_documento_identidad": numero_documento_identidad,
        "domicilio": domicilio,
        "telefono": telefono,
        "correo_electronico": correo_electronico,
        "tipo_documento": tipo_documento,
        "tipo_tramite": tipo_tramite,
        "asunto": asunto,
        "area_destinatario": area_destinatario,
        "numero_folios": numero_folios,
        "estado": "PENDIENTE",
        "fecha_hora_resolucion": "",
    }
    datos["codigo"] = f"EXP-{anio}-{mayor + 1:07d}"
    datos["fecha_hora_recepcion"] = datetime.now().astimezone().isoformat()

    lista.append(datos)
    print("Registrado:", datos["codigo"], "- estado:", datos["estado"])
    # Devuelve True para que main sepa que SÍ debe guardar el CSV.
    # Las rutas de anulación terminan antes con "return" (devuelven None).
    return True


def buscar(lista):
    codigo = input("Código a buscar: ").strip().upper()

    for expediente in lista:
        if expediente["codigo"] == codigo:
            print("\nExpediente encontrado:")
            for campo, valor in expediente.items():
                print(campo, ":", valor)
            return

    print("No se encontró el expediente.")


def resolver(lista):
    """Marca un expediente como RESUELTO y estampa su fecha de resolución.
    Devuelve True SOLO si el estado cambió, para que main sepa que debe
    guardar el CSV (regla: guardar tras cada cambio real)."""
    if not lista:
        print("No hay expedientes.")
        return False

    print("\n--- MARCAR COMO RESUELTO ---")
    codigo = (
        input("Código del expediente (" + CANCELAR + " para cancelar): ")
        .strip()
        .upper()
    )
    if codigo == CANCELAR:
        print("Operación cancelada.")
        return False

    for expediente in lista:
        if expediente["codigo"] == codigo:
            # Regla de transición: no se puede resolver lo ya resuelto.
            if expediente.get("estado", "PENDIENTE") == "RESUELTO":
                print(
                    "El expediente",
                    codigo,
                    "ya está RESUELTO. No se hizo ningún cambio.",
                )
                return False
            expediente["estado"] = "RESUELTO"
            # Misma estampa ISO que usa fecha_hora_recepcion.
            expediente["fecha_hora_resolucion"] = (
                datetime.now().astimezone().isoformat()
            )
            print("Expediente", codigo, "marcado como RESUELTO.")
            print("Fecha de resolución:", expediente["fecha_hora_resolucion"])
            return True

    print("No se encontró el expediente.")
    return False


def listar(lista):
    if not lista:
        print("No hay expedientes.")
        return

    # Encabezados de la tabla
    print()
    print("CÓDIGO | NOMBRES/APELLIDOS | ASUNTO | FECHA/HORA RECEPCIÓN | ESTADO")
    print("-" * 80)

    for expediente in lista:
        print(
            expediente["codigo"],
            "|",
            expediente["nombres_apellidos"],
            "|",
            expediente["asunto"],
            "|",
            expediente["fecha_hora_recepcion"],
            "|",
            # .get con valor por defecto: blindaje extra si algún
            # expediente viejo llegó sin estado.
            expediente.get("estado", "PENDIENTE"),
        )


def filtrar(lista):
    if not lista:
        print("No hay expedientes.")
        return

    # Menú de áreas con la misma prevención de errores de pedir_opcion:
    # vacío, texto no numérico, fuera de rango y CANCELAR para cancelar.
    area = pedir_opcion("Área a filtrar:", AREAS)
    if area is None:
        print("Operación cancelada.")
        return

    encontrados = []

    # Igualdad exacta: como el área viene del catálogo AREAS,
    # ya no hace falta comparar en minúsculas ni por subcadena.
    for expediente in lista:
        if expediente["area_destinatario"] == area:
            encontrados.append(expediente)

    if not encontrados:
        print("No hay expedientes para el área", area)
        return

    listar(encontrados)


def ordenar(lista, campo):
    if not lista:
        print("No hay expedientes.")
        return

    # Menú de dirección con prevención de errores (vacío, no número,
    # fuera de rango, CANCELAR para cancelar la operación).
    modo = pedir_opcion("Modo de ordenamiento:", ["ASCENDENTE", "DESCENDENTE"])
    if modo is None:
        print("Operación cancelada.")
        return

    copia = lista.copy()
    ascendente = modo == "ASCENDENTE"

    # Algoritmo de ordenamiento burbuja
    # Ascendente: intercambia si el anterior es MAYOR que el siguiente.
    # Descendente: intercambia si el anterior es MENOR que el siguiente
    # (la comparación se invierte, el resto del algoritmo no cambia).
    for i in range(len(copia)):
        for j in range(len(copia) - i - 1):
            if ascendente:
                hay_que_intercambiar = copia[j][campo] > copia[j + 1][campo]
            else:
                hay_que_intercambiar = copia[j][campo] < copia[j + 1][campo]
            if hay_que_intercambiar:
                copia[j], copia[j + 1] = copia[j + 1], copia[j]

    listar(copia)


def ticket(lista):
    codigo = input("Código para generar ticket: ").strip().upper()

    for expediente in lista:
        if expediente["codigo"] == codigo:
            carpeta = Path("tickets")
            carpeta.mkdir(exist_ok=True)

            # Marca de tiempo única para ambos archivos: el TXT y el PDF
            # de la misma generación quedan emparejados con el mismo
            # sufijo dd-mm-aaaa_hh-mm-ss.
            momento = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

            # 1) Ticket TXT: respaldo técnico plano (como siempre)
            ruta_txt = carpeta / f"ticket_{codigo}_{momento}.txt"
            with open(ruta_txt, "w", encoding="utf-8") as archivo:
                archivo.write("CONSTANCIA DE RECEPCIÓN\n\n")
                for campo, valor in expediente.items():
                    archivo.write(f"{campo}: {valor}\n")

            # 2) Boleta PDF 1/3 de A4: documento imprimible
            ruta_pdf = carpeta / f"ticket_{codigo}_{momento}.pdf"
            generar_pdf(expediente, ruta_pdf)

            print("Ticket TXT generado:", ruta_txt)
            print("Ticket PDF generado:", ruta_pdf)
            return

    print("Expediente no encontrado.")


def exportar(lista):
    """Exporta una copia del CSV con nombre automático dentro de la
    carpeta 'expedientes'. Pide confirmación antes de exportar."""
    if not lista:
        print("No hay expedientes para exportar.")
        return

    # Confirmación con menú 1-2 (misma prevención de errores que
    # todos los demás menús: vacío, texto, fuera de rango, CANCELAR).
    confirmacion = pedir_opcion("¿Desea exportar una copia del CSV?", ["SÍ", "NO"])
    if confirmacion is None or confirmacion == "NO":
        print("Operación cancelada.")
        return

    # Nombre automático: expedientes_dd-mm-aaaa_hh-mm-ss.csv
    # %d=día, %m=mes, %Y=año en 4 dígitos, %H=hora 24h, %M=minuto,
    # %S=segundo (los segundos evitan que dos exportaciones del
    # mismo minuto se sobrescriban entre sí).
    ahora = datetime.now()
    nombre = ahora.strftime("expedientes_%d-%m-%Y_%H-%M-%S") + ".csv"

    # Carpeta 'expedientes', igual que la carpeta 'tickets':
    # se crea si no existe y el archivo se guarda adentro.
    carpeta = Path("expedientes")
    carpeta.mkdir(exist_ok=True)
    ruta = carpeta / nombre

    guardar(lista, str(ruta))
    print("Archivo exportado:", ruta)
