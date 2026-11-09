# ------------------------------------------------------------------
# ticket_pdf.py — Boleta PDF imprimible (fpdf2).
#
# Decisiones de diseño (el porqué, no el qué):
# - Tamaño 1/3 de A4: es el formato físico real de la constancia de
#   una mesa de partes (una tira que se entrega al usuario como
#   comprobante), no una hoja completa desperdiciada.
# - fpdf2 usa Helvetica, que SOLO imprime latin-1. Esa limitación es
#   la RAZÓN de toda la cadena de validadores latinos: esta capa
#   confía en que lo que recibe ya es imprimible (defensa en capas:
#   validadores primero, try/except en ticket() como red de
#   seguridad).
# - fecha_legible() convierte ISO a formato peruano y TOLERA datos
#   corruptos: la boleta es para un humano, no para una base de
#   datos; si el dato fue editado a mano y no se puede convertir,
#   mejor mostrar el texto crudo que reventar el ticket.
# - Los valores vacíos se imprimen como texto representativo ("AÚN
#   NO RESUELTO", "(no registrado)"): un campo en blanco en un
#   documento oficial parece un error de impresión; el texto declara
#   explícitamente que el dato aún no existe.
# - auto_page_break: si un asunto larguísimo no cabe en los 99 mm se
#   imprime una segunda boleta, no texto cortado en el borde: la
#   información SIEMPRE queda completa.
# ------------------------------------------------------------------

from datetime import datetime

from fpdf import FPDF

# ------------------------------------------------------------------
# Formato de la boleta: 1/3 de una hoja A4 en vertical.
# A4 = 210 x 297 mm; 297 / 3 = 99 mm de alto.
# ------------------------------------------------------------------
ANCHO_BOLETA = 210
ALTO_BOLETA = 99

ALTO_FILA = 4  # alto de cada fila del detalle, en milímetros

# Etiquetas legibles de cada campo, en el orden en que se imprimen.
# El código no va aquí porque ya se muestra destacado en el encabezado.
ETIQUETAS = [
    ("tipo_persona", "Tipo de persona"),
    ("nombres_apellidos", "Nombres y apellidos"),
    ("tipo_documento_identidad", "Tipo de doc. de identidad"),
    ("numero_documento_identidad", "N° de doc. de identidad"),
    ("domicilio", "Domicilio"),
    ("telefono", "Teléfono"),
    ("correo_electronico", "Correo electrónico"),
    ("tipo_documento", "Tipo de documento"),
    ("tipo_tramite", "Tipo de trámite"),
    ("asunto", "Asunto"),
    ("area_destinatario", "Área destinataria"),
    ("numero_folios", "N° de folios"),
    ("fecha_hora_recepcion", "Fecha/hora de recepción"),
    ("estado", "Estado"),
    ("fecha_hora_resolucion", "Fecha/hora de resolución"),
]


def fecha_legible(texto_iso):
    """Convierte una fecha ISO del expediente ('2026-11-02T14:23:45-05:00')
    a formato legible ('02/11/2026 14:23:45'). Si el texto viene corrupto
    y no se puede convertir, se devuelve tal cual (defensa extra)."""
    try:
        momento = datetime.fromisoformat(texto_iso)
        return momento.strftime("%d/%m/%Y %H:%M:%S")
    except ValueError:
        return texto_iso


def generar_pdf(expediente, ruta):
    """Genera la boleta PDF (1/3 de A4) con los datos del expediente."""
    # Documento en milímetros, con tamaño de página personalizado.
    pdf = FPDF(orientation="P", unit="mm", format=(ANCHO_BOLETA, ALTO_BOLETA))

    # Si el contenido no cabe en los 99 mm, se agrega otra "boleta"
    # (página siguiente) en lugar de cortar el texto en el borde.
    pdf.set_auto_page_break(auto=True, margin=6)

    # Márgenes: 10 mm a izquierda y derecha, 6 mm arriba.
    pdf.set_margins(10, 6, 10)
    pdf.add_page()

    # ---------------- Encabezado ----------------
    # (Reemplaza "MESA DE PARTES DIGITAL" por el nombre de tu institución)
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(
        0,
        6,
        "MESA DE PARTES DIGITAL UPN (Prototipo)",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_font("helvetica", "", 9)
    pdf.cell(
        0,
        6,
        "CONSTANCIA DE RECEPCIÓN DE EXPEDIENTE",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # Línea divisoria justo a la altura donde quedó el cursor
    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(1)

    # Código del expediente, grande y centrado
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(
        0, 6, expediente.get("codigo", ""), align="C", new_x="LMARGIN", new_y="NEXT"
    )

    y = pdf.get_y()
    pdf.line(10, y, 200, y)
    pdf.ln(2)

    # ---------------- Detalle ----------------
    for campo, etiqueta in ETIQUETAS:
        valor = str(expediente.get(campo, ""))

        # Las fechas se muestran legibles, no en formato ISO crudo
        if campo in ("fecha_hora_recepcion", "fecha_hora_resolucion"):
            valor = fecha_legible(valor)

        # Los valores vacíos reciben un texto representativo
        if valor == "":
            if campo == "fecha_hora_resolucion":
                valor = "AÚN NO RESUELTO"
            else:
                valor = "(no registrado)"

        # Etiqueta en negrita, en la columna izquierda
        pdf.set_font("helvetica", "B", 8)
        pdf.cell(52, ALTO_FILA, etiqueta + ":")

        # Valor a su derecha: multi_cell envuelve los textos largos
        # (domicilio, asunto) en varias líneas y baja a la fila siguiente.
        # align="L" evita la justificación por defecto, que deforma
        # el espaciado en las líneas cortadas.
        pdf.set_font("helvetica", "", 8)
        pdf.multi_cell(0, ALTO_FILA, valor, align="L", new_x="LMARGIN", new_y="NEXT")

    pdf.output(ruta)
