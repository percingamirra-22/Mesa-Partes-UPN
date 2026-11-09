# ------------------------------------------------------------------
# almacenamiento.py — Única capa que toca el disco.
#
# Decisiones de persistencia (el porqué, no el qué):
# - Formato CSV y no JSON/SQLite: es el formato del curso, se lee a
#   simple vista y Excel lo abre sin importar nada. Su costo (texto,
#   comillas, encabezado) se concentra AQUÍ: el resto del programa
#   trabaja con listas/dicts y no sabe cómo se guarda nada.
# - CAMPOS es la única fuente de verdad del "contrato" del expediente:
#   guardar() lo usa para el encabezado y cargar() para reconstruir
#   cada fila. Agregar un campo = tocar UNA lista; las dos funciones
#   se adaptan solas.
# - Defensa en profundidad: las validaciones de entrada NO bastan,
#   porque el CSV es un archivo editable a mano (CP-005 lo demostró:
#   una coma extra en el encabezado corrompía la base). Por eso
#   guardar() es atómico y cargar() sanea: el programa nunca asume
#   que el disco contiene exactamente lo que él escribió.
# ------------------------------------------------------------------

import csv
import os
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
    """Guardado ATÓMICO y con BOM (V3 y V9):
    - Primero se escribe TODO en un archivo temporal .tmp y solo cuando
      la escritura termina bien se reemplaza al original con os.replace.
      Si el proceso muere a media escritura, el original queda intacto:
      nunca más un expedientes.csv destruido (lo que pasó en CP-005).
    - utf-8-sig agrega el BOM al inicio: Excel abre el CSV con los
      acentos correctos. Vale para expedientes.csv Y para las copias
      exportadas, porque ambas salen de esta función."""
    temporal = nombre + ".tmp"
    with open(temporal, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(lista)
    os.replace(temporal, nombre)


def cargar():
    ruta = Path("expedientes.csv")

    if not ruta.exists():
        return []

    # utf-8-sig para leer: si el archivo tiene BOM se lo salta, y si no
    # lo tiene (CSVs viejos escritos con encoding="utf-8") también lo
    # lee bien. Un solo encoding para escribir y leer.
    with open(ruta, "r", newline="", encoding="utf-8-sig") as archivo:
        lector = csv.DictReader(archivo)
        lista = list(lector)

    # Saneo y migración (V2): cada expediente se RECONSTRUYE con
    # exactamente las 16 claves de CAMPOS. Esto corrige a la vez:
    # - claves de MÁS: una coma extra en el encabezado del CSV crea la
    #   clave '' que hacía fallar guardar() con ValueError (CP-005);
    #   como solo se copian las claves de CAMPOS, la basura se descarta;
    # - claves de MENOS: un CSV viejo sin "estado" ni
    #   "fecha_hora_resolucion" (migración original), o una fila corta
    #   que DictReader rellena con None, se completan con su valor por
    #   defecto ("PENDIENTE" para estado, "" para el resto).
    saneada = []
    for expediente in lista:
        limpio = {}
        for campo in CAMPOS:
            valor = expediente.get(campo)
            if valor is None:  # campo ausente o fila corta
                if campo == "estado":
                    valor = "PENDIENTE"
                else:
                    valor = ""
            limpio[campo] = valor
        saneada.append(limpio)

    return saneada
