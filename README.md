# Generador de Calendarios con formato .ICS en Python

Este repositorio contiene un script automatizado en **Python** diseñado para procesar listas de eventos académicos o personales y generar un archivo `.ics` (iCalendar) listo para importar en Google Calendar, Apple Calendar, Outlook y Microsoft Teams.

El script calcula dinámicamente las fechas reales de los eventos a partir de una **Semana Base** especificada y configura automáticamente múltiples alertas de notificación previas a cada evento.

---

## 📌 Características Principales

* **Cálculo Dinámico de Fechas y/o horas:** Interpreta expresiones como `Semana X | Día(s) | Horario` y calcula automáticamente la fecha calendario exacta basada en el lunes de inicio de la Semana 1.
* **Alertas Automatizadas:** Cada evento incluye alertas predefinidas
* **Sin Dependencias Externas:** Desarrollado utilizando exclusivamente la biblioteca estándar de Python (`datetime`).
* **Reporte en Consola:** Genera una lista de lectura con los días y fechas exactas calculadas.
* **Eventos de Día Completo y con horario de inicio y fin:** Soporta ambos tipo de eventos, pero solo uno a la vez por ejecución (temporal)

---

## ⚙️ Configuración de la Fecha Base

Para que el script interprete correctamente el número de cada semana, es **fundamental** definir la fecha correspondiente al **lunes de la Semana 1** (Semana BASE).

Ejemplo: FECHA_BASE_STR = "2026-08-03"  # Lunes 3 de agosto de 2026 (Inicio de la Semana 1)

---

## ⚙️ Configuración correcta para el Input

**Formato estándar requerido para eventos de todo un día:** <nombre evento> | Semana <numero> | <día de semana>\
Full Day | Semana 1 | Domingo\
Viaje | Semana 6 | Viernes\
**Formato requerido para eventos con horario con y sin repetición:** RepX <# repeticiones> | <nombre evento> | Semana <numero> | <días de semana> | <inicio>-<fin>\
Voluntariado | Semana 3 | Sábado | 07:00-13:00\
RepX 12 | Oratoria | Semana 1 | Martes y Jueves y Sábado | 09:00-11:00\

**En un String, cada línea (separada por un salto \n) representará cada evento.**
