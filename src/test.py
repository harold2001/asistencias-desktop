# semanas = {}
dias = []
current_day = primer_dia
while current_day <= ultimo_dia:
    if current_day.weekday() < 5:  # De lunes a viernes (0 a 4)
        dia_letra = dias_es[current_day.weekday()]
        dias.append((dia_letra, current_day.day))
        # semana_mes = (current_day.day - 1) // 7 + 1
        # if semana_mes not in semanas:
        #     semanas[semana_mes] = []

        # semanas[semana_mes].append((dia_letra, current_day.day))
    current_day += timedelta(days=1)

coldata = [
    {"text": "N°", "stretch": True},
    {"text": "Nombres y apellidos", "stretch": True},
]
# for dias in list(semanas.values()):


records = [row.values for row in table.tablerows]

        if len(headers) == 0 or len(records) == 0:
            self.display_error_box("No hay datos para exportar en esta tabla")
            return