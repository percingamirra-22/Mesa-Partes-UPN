import csv
from pathlib import Path

CAMPOS = [
    "codigo",
    "tipo_persona",
    "nombres_apellidos",
    "tipo_documento_identidad",
    "numero_documento_identidad",
    "domicilio",
    "telefono",
    "correo_electronico",
    "tipo_documento",
    "tipo_tramite",
    "asunto",
    "area_destinatario",
    "numero_folios",
    "fecha_hora_recepcion",
    "estado",
    "fecha_hora_resolucion",
]


def guardar(lista, nombre="expedientes.csv"):
    with open(nombre, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(lista)


def cargar():
    ruta = Path("expedientes.csv")

    if not ruta.exists():
        return []

    with open(ruta, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)
        lista = list(lector)

    # Migración: expedientes guardados con la versión anterior del programa
    # no tienen los campos "estado" ni "fecha_hora_resolucion".
    # Se completan con sus valores por defecto para evitar KeyError.
    for expediente in lista:
        if "estado" not in expediente:
            expediente["estado"] = "PENDIENTE"
        if "fecha_hora_resolucion" not in expediente:
            expediente["fecha_hora_resolucion"] = ""

    return lista
