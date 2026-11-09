# Mesa-Partes-UPN

Software de consola en Python que simula una **mesa de partes digital** para la UPN: registra expedientes con validación de datos, permite buscarlos, listarlos, filtrarlos por área, ordenarlos, marcarlos como resueltos, generar tickets (TXT y PDF) y exportar la base a CSV.

## Requisitos

| Requisito | Detalle |
| --- | --- |
| Python | 3.9 o superior (probado en 3.13) |
| Dependencias | Las listadas en `requirements.txt` (fpdf2, fonttools, pillow) |
| Sistema operativo | Windows, Linux o macOS |

## Instalación paso a paso

Abre una terminal **dentro de la carpeta del proyecto** y sigue los pasos en orden.

### 1. Clona el repositorio

```
git clone https://github.com/percingamirra-22/Mesa-Partes-UPN.git
cd Mesa-Partes-UPN
```

### 2. Crea y activa un entorno virtual

Windows (CMD o PowerShell):

```
python -m venv .venv
.venv\Scripts\activate
```

Linux / macOS:

```
python3 -m venv .venv
source .venv/bin/activate
```

> **Nota (solo PowerShell):** si al activar aparece el error "running scripts is
> disabled", ejecuta una sola vez
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
> y vuelve a intentar el activate.

Sabes que el entorno quedó activo cuando el prompt muestra `(.venv)` al
inicio de la línea.

### 3. Instala las dependencias

Con el entorno virtual activado:

```
pip install -r requirements.txt
```

Eso instala exactamente fpdf2 2.9.0 y sus dependencias (fonttools y pillow).

## Uso

Con el entorno virtual activado, ejecuta:

```
python main.py
```

Aparecerá este menú:

| Opción | Acción |
| --- | --- |
| 1 | Registrar expediente (captura validada campo por campo) |
| 2 | Buscar expediente por código |
| 3 | Listar todos los expedientes |
| 4 | Filtrar por área |
| 5 | Ordenar por código (ascendente o descendente) |
| 6 | Ordenar por fecha de recepción (ascendente o descendente) |
| 7 | Marcar un expediente como RESUELTO |
| 8 | Generar ticket (TXT + PDF) |
| 9 | Exportar una copia del CSV |
| 0 | Salir |

**Cancelar una captura:** en cualquier pregunta de datos puedes escribir
`CANCELAR` para anular el registro en curso; no se guarda nada.

**Guardado automático:** al registrar o resolver un expediente, el programa
guarda la base `expedientes.csv` de inmediato. El guardado es **atómico**:
primero se escribe todo a un archivo temporal (`.tmp`) y solo si terminó
bien se reemplaza al original, así una interrupción nunca deja la base a
medias.

## Estructura del proyecto

| Módulo | Responsabilidad |
| --- | --- |
| `main.py` | Menú principal y orquestación |
| `registro.py` | Operaciones del negocio: registrar, buscar, resolver, listar, filtrar, ordenar, ticket y exportar |
| `interfaz.py` | Conversación con el usuario: menús numerados, re-pregunta ante errores y cancelación |
| `validadores.py` | Reglas de validación de datos (funciones puras, sin `input` ni `print`) |
| `almacenamiento.py` | Persistencia de expedientes en CSV |
| `ticket_pdf.py` | Boleta PDF de 1/3 de hoja A4 generada con fpdf2 |

Arquitectura en capas, sin ciclos de importación:

```
main.py
  └── registro.py
        ├── interfaz.py ──► validadores.py
        ├── validadores.py
        ├── almacenamiento.py
        └── ticket_pdf.py ──► fpdf (librería externa)
```

## Archivos generados en ejecución

El programa crea estos archivos mientras corre. **No se suben al repositorio**
(están en `.gitignore`) porque son datos de prueba de cada máquina:

- `expedientes.csv` — base de datos local (se crea sola al primer guardado; se escribe en UTF-8 con BOM, por lo que Excel la abre con acentos correctos)
- `tickets/` — boletas TXT y PDF generadas por la opción 8
- `expedientes/` — copias exportadas del CSV generadas por la opción 9

## Historial de cambios

### Versión 1.1 — Endurecimiento tras las pruebas (09/11/2026)

Correcciones derivadas de la campaña de pruebas de datos (127 casos:
éxitos, límites, errores y accidentes no voluntarios):

- **Menú principal unificado**: la opción se limpia con `strip()` y se
  interpreta como número; `" 1"`, `"1 "` y `"01"` valen igual que en los
  menús internos.
- **Salida limpia ante Ctrl+C y Ctrl+Z**: se capturan `KeyboardInterrupt`
  y `EOFError`; el programa despide con un mensaje en vez de un traceback.
- **Correo blindado**: se valida el alfabeto latino (un correo como
  `user@ドメイン.com` pasaba la validación y hacía fallar fpdf2 al generar
  el ticket PDF); se añadió `_` a los símbolos permitidos. El ticket
  además genera el PDF con `try/except`: ante un dato corrupto inyectado
  a mano en el CSV, avisa y el programa sigue vivo.
- **Folios normalizados**: se acepta `"0005"` pero se guarda `"5"`.
- **CSV compatible con Excel**: `expedientes.csv` y las copias exportadas
  se escriben en UTF-8 con BOM (`utf-8-sig`), con acentos correctos al
  abrirlos en Excel.
- **Carga con saneo**: cada expediente se reconstruye con exactamente las
  16 columnas; las de más (una coma extra) se descartan y las de menos se
  completan con su valor por defecto.
- **Guardado atómico**: el CSV se escribe primero a un archivo temporal y
  solo si terminó bien reemplaza al original; una interrupción a media
  escritura ya no puede destruir la base.
- **Todos los modulos**: cabecera con las decisiones de diseno (el porque
  de cada decision, referenciado a los hallazgos de las pruebas)

### Versión 1.0 — Primera versión modular (07/11/2026)

Modularización en 6 módulos (main, registro, interfaz, validadores,
almacenamiento, ticket_pdf): registro validado campo por campo con
`CANCELAR`, marcado RESUELTO con fecha, ticket TXT + PDF (fpdf2) y
exportación CSV.

## Licencia

MIT. Ver el archivo `LICENSE`.