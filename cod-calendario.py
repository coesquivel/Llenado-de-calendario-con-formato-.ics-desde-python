
import datetime
import uuid

#FECHA_BASE_STR = "AAAA-MM-DD" 
FECHA_BASE_STR = "2026-08-03" 
#El día base es siempre un lunes

def repetir_o_no(INPUT): # Para clases, no eventos
    lineas = INPUT.strip().split('\n')
    DDlnDD = ""
    for linea in lineas:
        if not linea.strip(): continue
        
        partes = [p.strip() for p in linea.split('|')]

        if "RepX" not in partes[0]: continue

        #Extraemos el número de repeticiones
        str_repeticiones = partes[0].replace("RepX", "").strip()
        try:
            num_repeticiones = int(str_repeticiones)
        except ValueError:
            print(f"Número de semana inválido en: {linea}")
            continue

        #Extraemos el número de semana 
        semana_str = partes[2].lower().replace("semana", "").strip()
        try:
            semana = int(semana_str)
        except ValueError:
            print(f"Número de semana inválido en: {linea}")
            continue
        
        dias = [x.strip() for x in partes[3].split("y")]
        contador_dias_de_semana = 0
        
        for i in range(num_repeticiones):
            contador_dias_de_semana += 1
            if contador_dias_de_semana > len(dias):
                semana += 1 #Dado que avanza la semana
                contador_dias_de_semana = 1
            idx = contador_dias_de_semana - 1
            DDlnDD += f"{partes[1]} | Semana {semana} | {dias[idx]} | {partes[4]}\n"
        
    return DDlnDD

# Formato estándar requerido para eventos de todo un día: <nombre evento> | Semana <numero> | <día de semana>
# Full Day | Semana 1 | Domingo
# Formato requerido para eventos con horario: RepX <# repeticiones> | <nombre evento> | Semana <numero> | <días de semana> | <inicio>-<fin>
# RepX 12 | Oratoria | Semana 1 | Martes y Jueves y Sábado | 09:00-11:00

INPUT_EVENTOS = """
RepX 6 | Mate | Semana 1 | Lunes y Miercoles y Viernes | 11:00-14:00
RepX 7 | Lenguaje | Semana 1 | Martes y Jueves y Sábado | 13:00-16:00
"""

INPUT_EVENTOS = repetir_o_no(INPUT_EVENTOS)

# Mapeo de días de la semana a desplazamientos numéricos (Lunes = 0)
DIAS_SEMANA = {
    "domingo": 6, "lunes": 0, "martes": 1, 
    "miércoles": 2, "miercoles": 2, "jueves": 3, 
    "viernes": 4, "sábado": 5, "sabado": 5
} #Se consideran los dias con tildes y sin ellas para evitar errores

zona_utc_menos_5 = datetime.timezone(datetime.timedelta(hours=-5))
#Tenemos en cuenta una hora UTC-5 para Perú, esto se usará únicamente por un requerimiento de hora de generación del archivo .ics
#Como tal, las horas de nuestros eventos no requerirán cambios de este estilo
#Esto dado que nuestra aplicación de calendario se asume definida al uso horario respectivo y manejará correctamente las horas

def generar_archivos_dinamicos(input_string, fecha_base_str, EVENTO_O_CLASE):
    #Fecha base a objeto datetime
    fecha_base = datetime.datetime.strptime(fecha_base_str, "%Y-%m-%d").date()
    eventos = []
    
    #Recorrido de las lineas del input
    lineas = input_string.strip().split('\n')
    for linea in lineas:
        if not linea.strip(): continue
        
        partes = [p.strip() for p in linea.split('|')]
        if EVENTO_O_CLASE:
            if len(partes) != 3:
                print(f"Error de formato en la línea: {linea}")
                continue
        else:
            if len(partes) != 4:
                print(f"Error de formato en la línea: {linea}")
                continue
            
        nombre = partes[0]
        
        #Extraemos el número de semana 
        semana_str = partes[1].lower().replace("semana", "").strip()
        try:
            num_semana = int(semana_str)
        except ValueError:
            print(f"Número de semana inválido en: {linea}")
            continue
            
        #Identificamos el día de la semana
        dia_str = partes[2].lower()
        if dia_str not in DIAS_SEMANA:
            print(f"Día de la semana inválido en: {linea}")
            continue
            
        offset_dia = DIAS_SEMANA[dia_str]

        #Calculamos la fecha exacta:
        dias_totales = ((num_semana - 1) * 7) + offset_dia
        fecha_evento = fecha_base + datetime.timedelta(days=dias_totales)

        if not EVENTO_O_CLASE:
            try:
                hora_inicio_str, hora_fin_str = partes[3].split('-')
                h_ini, m_ini = map(int, hora_inicio_str.strip().split(':'))
                h_fin, m_fin = map(int, hora_fin_str.strip().split(':'))
            except ValueError:
                print(f"Error en el formato de hora en: {partes[3]}")
                continue

            dt_inicio_local = datetime.datetime.combine(fecha_evento, datetime.time(h_ini, m_ini))
            dt_fin_local = datetime.datetime.combine(fecha_evento, datetime.time(h_fin, m_fin))
            eventos.append({"nombre": nombre, "fecha": fecha_evento, "dt_inicio_local":dt_inicio_local, "dt_fin_local": dt_fin_local})
        
        else: eventos.append({"nombre": nombre, "fecha": fecha_evento})
        
    #GENERAMOS UN REPORTE (no diferencia entre tipo 'evento' o tipo 'clase', no lo vi tan necesario capaz luego lo modifico)

    print("### Lista de Eventos Agendados (Lectura Normal)\n")
    for ev in eventos:
        fecha_formateada = ev["fecha"].strftime("%A, %d de %B de %Y")
        print(f"* {ev['nombre']}")
        print(f"  * Fecha: {fecha_formateada.capitalize()}\n")
        
    #CREAMOS AHORA SÍ EL ARCHIVO .ICS
    ics_lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Agendar Eventos//MX",
        "CALSCALE:GREGORIAN"
    ]
    
    for ev in eventos:
        #Generamos un ID único por seguridad para que el calendario no sobreescriba eventos
        evento_uid = f"{uuid.uuid4()}@generador"

        #Diferenciamos entre evento de día completo (true) o clase (false)
        if EVENTO_O_CLASE: #Además distingue recordatorios de días con True y en False de 1 y 2 horas
            dtstart = ev["fecha"].strftime("%Y%m%d")
            dtend = (ev["fecha"] + datetime.timedelta(days=1)).strftime("%Y%m%d")
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:{evento_uid}",
                f"SUMMARY:{ev['nombre']}",
                f"DTSTART;VALUE=DATE:{dtstart}",
                f"DTEND;VALUE=DATE:{dtend}",
                # --- ALERTAS CONFIGURADAS ---
                "BEGIN:VALARM",
                "TRIGGER:-P1D",
                "ACTION:DISPLAY",
                "DESCRIPTION:Recordatorio: 1 dia antes",
                "END:VALARM",
                "BEGIN:VALARM",
                "TRIGGER:-P5D",
                "ACTION:DISPLAY",
                "DESCRIPTION:Recordatorio: 5 dias antes",
                "END:VALARM",
                "BEGIN:VALARM",
                "TRIGGER:-P7D",
                "ACTION:DISPLAY",
                "DESCRIPTION:Recordatorio: 1 semana antes",
                "END:VALARM",
                "BEGIN:VALARM",
                "TRIGGER:-P10D",
                "ACTION:DISPLAY",
                "DESCRIPTION:Recordatorio: 10 dias antes",
                "END:VALARM",
                "END:VEVENT"
            ])
        else:
            formato_ics = "%Y%m%dT%H%M%S"
            str_inicio = ev["dt_inicio_local"].strftime(formato_ics)
            str_fin = ev["dt_fin_local"].strftime(formato_ics)
            ahora = datetime.datetime.now(zona_utc_menos_5).strftime(formato_ics)
            
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"DTSTAMP:{ahora}",
                f"UID:{evento_uid}",
                f"SUMMARY:{ev['nombre']}",
                f"DTSTART:{str_inicio}",
                f"DTEND:{str_fin}",
                # --- ALERTAS CONFIGURADAS ---
                "BEGIN:VALARM",
                "TRIGGER:-PT1H",
                "ACTION:DISPLAY",
                "DESCRIPTION:Recordatorio: 1 hora antes",
                "END:VALARM",
                "BEGIN:VALARM",
                "TRIGGER:-PT2H",
                "ACTION:DISPLAY",
                "DESCRIPTION:Recordatorio: 2 horas antes",
                "END:VALARM",
                "END:VEVENT"
            ])
        
    ics_lines.append("END:VCALENDAR")
    
    #Guardamos el archivo
    nombre_archivo = "prueba6.ics"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write("\n".join(ics_lines))
        
    print(f"Archivo '{nombre_archivo}' generado")

#Ejecutamos
if __name__ == "__main__":
    generar_archivos_dinamicos(INPUT_EVENTOS, FECHA_BASE_STR, False)




