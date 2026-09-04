import pandas as pd
from pathlib import Path

ruta = Path(__file__).parent.parent
ruta_data=ruta / "data"
archivos=list(ruta_data.rglob("*.xlsx"))


def encontrar_fecha(df, n_columnas=3):
    for col in df.columns[:n_columnas]:

        fechas = pd.to_datetime(
            df[col],
            errors="coerce",
            dayfirst=True
        )

        if fechas.notna().any():
            idx = fechas.first_valid_index()
            return fechas.loc[idx]

    return None



def procesar_indicadores(anio, archivos):

    lista_indicadores = []

    meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    columnas_indicadores = [
        "MES",
        "AÑO",
        "ENTIDAD",
        "( PATRIMONIO + RESULTADOS ) / ACTIVOS INMOVILIZADOS NETOS (3) (6)",
        "INDICE DE CAPITALIZACION NETO: FK / FI",
        "ACTIVOS IMPRODUCTIVOS NETOS / TOTAL ACTIVOS",
        "ACTIVOS PRODUCTIVOS / TOTAL ACTIVOS",
        "ACTIVOS PRODUCTIVOS / PASIVOS CON COSTO",
        "MOROSIDAD DE LA CARTERA DE CREDITOS CONSUMO",
        "MOROSIDAD DE LA CARTERA DE CRÉDITOS INMOBILIARIO\n",
        "MOROSIDAD DE LA CARTERA DE CRÉDITOS MICROCRÉDITO",
        "MOROSIDAD DE LA CARTERA TOTAL",
        "COBERTURA DE LA CARTERA REFINANCIADA",
        "COBERTURA DE LA CARTERA REESTRUCTURADA",
        "COBERTURA DE LA CARTERA PROBLEMÁTICA",
        "GASTOS DE OPERACION ESTIMADOS / TOTAL ACTIVO PROMEDIO (3)",
        "GASTOS DE OPERACION  / MARGEN FINANCIERO",
        "GASTOS DE PERSONAL ESTIMADOS / ACTIVO PROMEDIO (3)",
        "RESULTADOS DEL EJERCICIO / PATRIMONIO PROMEDIO",
        "RESULTADOS DEL EJERCICIO / ACTIVO PROMEDIO",
        "CARTERA BRUTA / (DEPOSITOS A LA VISTA + DEPOSITOS A PLAZO)",
        "FONDOS DISPONIBLES / TOTAL DEPOSITOS A CORTO PLAZO"
    ]

    for i in archivos:

        # Verificar que el archivo corresponde al año
        if str(anio) in i.name:

            indicadores = pd.read_excel(
                i,
                sheet_name="INDICADORES",
                index_col=0
            )

            # Limpieza inicial
            indicadores = indicadores.dropna(how="all")
            indicadores = indicadores.reset_index(drop=True)
            indicadores = indicadores.dropna(axis=1, how="all")

            # Encontrar fecha
            fecha_encontrada = encontrar_fecha(indicadores)

            # Eliminar filas iniciales
            indicadores = indicadores.iloc[4:].reset_index(drop=True)

            # Transponer
            indicadores = indicadores.T

            # Primera fila como nombres de columnas
            indicadores.columns = indicadores.iloc[0]

            # Eliminar fila utilizada como encabezado
            indicadores = indicadores.iloc[1:].reset_index(drop=True)

            # Cambiar nombre de columna
            indicadores.rename(
                columns={"NOMBRE DEL INDICADOR": "ENTIDAD"},
                inplace=True
            )

            # Obtener mes y año
            mes = meses[fecha_encontrada.month - 1]
            anio_fecha = fecha_encontrada.year

            # Insertar MES y AÑO
            indicadores.insert(0, "MES", mes)
            indicadores.insert(1, "AÑO", anio_fecha)

            # Seleccionar columnas
            indicadores = indicadores[columnas_indicadores]

            # FILTRAR SOLO BANCOS PRIVADOS
    
            indicadores = indicadores[
                indicadores["ENTIDAD"].str.startswith("BP ", na=False)
            ].copy()

            # Agregar a la lista
            lista_indicadores.append(indicadores)

    return lista_indicadores


lista_indicadores_2025 = procesar_indicadores(2025, archivos)
lista_indicadores_2026 = procesar_indicadores(2026, archivos)



def procesar_cartera(anio,archivos):

    lista_cartera = []

    for i in archivos:

        # Validar que el archivo corresponda al año solicitado
        if str(anio) in i.name:
            cartera = pd.read_excel(
                i,
                sheet_name="COMPOS CART",
                index_col=0
            )

            # =========================================================
            # 2. LIMPIEZA INICIAL
            # =========================================================
            cartera = cartera.dropna(how="all")
            cartera = cartera.reset_index(drop=True)
            cartera = cartera.dropna(axis=1, how="all")

            # Obtener fecha
            fecha_encontrada = encontrar_fecha(cartera)

            # Eliminar filas iniciales
            cartera = cartera.iloc[4:].reset_index(drop=True)

            # Eliminar primera columna
            cartera = cartera.drop(columns=[cartera.columns[0]])

            # =========================================================
            # 3. TRANSPONER
            # =========================================================
            cartera = cartera.T

            # Primera fila como nombres de columnas
            cartera.columns = cartera.iloc[0]

            # Eliminar la fila utilizada como encabezado
            cartera = cartera.iloc[1:].reset_index(drop=True)

            # =========================================================
            # 4. FILTRAR SOLO BANCOS PRIVADOS
            # =========================================================
            cartera = cartera[
                cartera["CUENTA"].str.startswith("BP ", na=False)
            ].copy()

            # =========================================================
            # 5. FEATURE ENGINEERING
            # =========================================================
            cartera["CARTERA IMPRODUCTIVA / CARTERA BRUTA"] = (
                cartera["TOTAL CARTERA IMPRODUCTIVA  (NO DEVENGA INTERESES + VENCIDA)"]
                / cartera["CARTERA BRUTA"]
            )

            cartera["CARTERA VENCIDA / CARTERA BRUTA"] = (
                cartera["TOTAL CARTERA VENCIDA"]
                / cartera["CARTERA BRUTA"]
            )

            cartera["CARTERA QUE NO DEVENGA INTERESES / CARTERA BRUTA"] = (
                cartera["TOTAL CARTERA QUE NO DEVENGA INTERES"]
                / cartera["CARTERA BRUTA"]
            )

            cartera["CARTERA REFINANCIADA / CARTERA BRUTA"] = (
                cartera["CARTERA REFINANCIADA"]
                / cartera["CARTERA BRUTA"]
            )

            cartera["CARTERA REESTRUCTURADA / CARTERA BRUTA"] = (
                cartera["CARTERA REESTRUCTURADA"]
                / cartera["CARTERA BRUTA"]
            )

            # =========================================================
            # 6. SELECCIONAR VARIABLES FINALES
            # =========================================================
            variables_finales = [
                "CUENTA",
                "CARTERA IMPRODUCTIVA / CARTERA BRUTA",
                "CARTERA VENCIDA / CARTERA BRUTA",
                "CARTERA QUE NO DEVENGA INTERESES / CARTERA BRUTA",
                "CARTERA REFINANCIADA / CARTERA BRUTA",
                "CARTERA REESTRUCTURADA / CARTERA BRUTA"
            ]

            cartera = cartera[variables_finales].copy()

            # Cambiar nombre CUENTA por ENTIDAD
            cartera.rename(
                columns={"CUENTA": "ENTIDAD"},
                inplace=True
            )

            # =========================================================
            # 7. CREAR MES Y AÑO
            # =========================================================
            meses = [
                "Enero", "Febrero", "Marzo", "Abril",
                "Mayo", "Junio", "Julio", "Agosto",
                "Septiembre", "Octubre", "Noviembre", "Diciembre"
            ]

            mes = meses[fecha_encontrada.month - 1]
            anio_fecha = fecha_encontrada.year

            cartera.insert(0, "MES", mes)
            cartera.insert(1, "AÑO", anio_fecha)

            lista_cartera.append(cartera)

    return lista_cartera

lista_cartera_2025=procesar_cartera(2025, archivos)



























































lista_balance=[]
for i in archivos:
    balance=pd.read_excel(i, sheet_name="BALANCE", index_col=0)
    balance = balance.dropna(how="all")
    balance = balance.reset_index(drop=True)
    balance = balance.dropna(axis=1, how="all")
    fecha_encontrada=encontrar_fecha(balance)
    balance = balance.iloc[4:].reset_index(drop=True)
    balance.columns = balance.iloc[0]
    cuentas = ["1","14","2101","2103","3","11","13"]
    balance = balance[balance["CÓDIGO"].isin(cuentas)].copy()
    balance = balance.drop(columns=[balance.columns[0]])
    balance = balance.T
    balance = balance.reset_index()
    balance.columns = balance.iloc[0]
    # Eliminar la primera fila utilizada como encabezado
    balance = balance.iloc[1:].reset_index(drop=True)
    balance = balance[balance["CUENTA"].str.startswith(("BP ", "BANCO "), na=False)].copy()

    # Cambiar nombre CUENTA por ENTIDAD
    #balance.rename(columns={"CUENTA": "ENTIDAD"},inplace=True)
    
    meses = ["Enero", "Febrero", "Marzo", "Abril",
                    "Mayo", "Junio", "Julio", "Agosto",
                    "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    
    mes = meses[fecha_encontrada.month - 1]
    anio_fecha = fecha_encontrada.year
    
    balance.insert(0, "MES", mes)
    balance.insert(1, "AÑO", anio_fecha)

    lista_balance.append(balance)






    balance = balance.dropna(axis=1, how="all")
    fecha_encontrada=encontrar_fecha(balance)
    balance = balance.iloc[4:].reset_index(drop=True)
    balance = balance.drop(columns=[balance.columns[0]])
    # Transponer
    balance = balance.T
    # Primera fila como nombres de columnas
    balance.columns = balance.iloc[0]
    # Eliminar la fila utilizada como encabezado
    balance = balance.iloc[1:].reset_index(drop=True)
    cuentas = [
    "CUENTA",
    "TOTAL ACTIVO",
    "CARTERA DE CRÉDITOS",
    "Depósitos a la vista",
    "Depósitos a plazo",
    "TOTAL PATRIMONIO",
    "FONDOS DISPONIBLES",
    "INVERSIONES"]
    balance = balance[cuentas].copy()
    balance = balance[balance["CUENTA"].str.startswith(("BP ", "BANCO "), na=False)].copy()
    lista_balance.append(balance)
        # Transponer








































































lista_cartera=[]
for i in archivos:
    if "2025" in i.name:
        cartera=pd.read_excel(i, sheet_name="COMPOS CART", index_col=0)
        cartera = cartera.dropna(how="all")
        cartera = cartera.reset_index(drop=True)
        cartera = cartera.dropna(axis=1, how="all")
        fecha_encontrada=encontrar_fecha(cartera)
        cartera = cartera.iloc[4:].reset_index(drop=True)
        cartera = cartera.drop(columns=[cartera.columns[0]])
        # Transponer
        cartera = cartera.T
        # Primera fila como nombres de columnas
        cartera.columns = cartera.iloc[0]
        # Eliminar la fila utilizada como encabezado
        cartera = cartera.iloc[1:].reset_index(drop=True)
        cartera = cartera[cartera["CUENTA"].str.startswith("BP ", na=False)].copy()
        cartera["CARTERA IMPRODUCTIVA / CARTERA BRUTA"]=cartera["TOTAL CARTERA IMPRODUCTIVA  (NO DEVENGA INTERESES + VENCIDA)"] / cartera["CARTERA BRUTA"]
        cartera["CARTERA VENCIDA / CARTERA BRUTA"]=cartera["TOTAL CARTERA VENCIDA"] / cartera["CARTERA BRUTA"]
        cartera["CARTERA QUE NO DEVENGA INTERESES / CARTERA BRUTA"]=cartera["TOTAL CARTERA QUE NO DEVENGA INTERES"] / cartera["CARTERA BRUTA"]
        cartera["CARTERA REFINANCIADA / CARTERA BRUTA"]=cartera["CARTERA REFINANCIADA"] / cartera["CARTERA BRUTA"]
        cartera["CARTERA REESTRUCTURADA / CARTERA BRUTA"]=cartera["CARTERA REESTRUCTURADA"] / cartera["CARTERA BRUTA"]
        # =========================================================
        # SELECCIONAR SOLO CUENTA + VARIABLES CREADAS
        # =========================================================

        variables_finales = [
            "CUENTA",
            "CARTERA IMPRODUCTIVA / CARTERA BRUTA",
            "CARTERA VENCIDA / CARTERA BRUTA",
            "CARTERA QUE NO DEVENGA INTERESES / CARTERA BRUTA",
            "CARTERA REFINANCIADA / CARTERA BRUTA",
            "CARTERA REESTRUCTURADA / CARTERA BRUTA"
        ]

        cartera = cartera[variables_finales].copy()
        cartera.rename(columns={"CUENTA":"ENTIDAD"}, inplace=True)
        meses = [
                    "Enero", "Febrero", "Marzo", "Abril",
                    "Mayo", "Junio", "Julio", "Agosto",
                    "Septiembre", "Octubre", "Noviembre", "Diciembre"
                ]
        
        mes = meses[fecha_encontrada.month - 1]
        anio = fecha_encontrada.year
        
        cartera.insert(0, "MES", mes)
        cartera.insert(1, "AÑO", anio)
        lista_cartera.append(cartera)






        print(f"Fecha encontrada en {i.name}: {fecha_encontrada}")
        cartera = cartera.iloc[4:].reset_index(drop=True)
        # Transponer
        indicadores_2025 = indicadores_2025.T
        # Primera fila como nombres de columnas
        indicadores_2025.columns = indicadores_2025.iloc[0]
        # Eliminar la fila utilizada como encabezado
        indicadores_2025 = indicadores_2025.iloc[1:].reset_index(drop=True)
        indicadores_2025.rename(columns={"NOMBRE DEL INDICADOR":"ENTIDAD"}, inplace=True)
        meses = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        mes = meses[fecha_encontrada.month - 1]
        anio = fecha_encontrada.year

        indicadores_2025.insert(0, "MES", mes)
        indicadores_2025.insert(1, "AÑO", anio)
        indicadores_2025=indicadores_2025[["MES","AÑO","ENTIDAD","( PATRIMONIO + RESULTADOS ) / ACTIVOS INMOVILIZADOS NETOS (3) (6)","INDICE DE CAPITALIZACION NETO: FK / FI",
                                            'ACTIVOS IMPRODUCTIVOS NETOS / TOTAL ACTIVOS','ACTIVOS PRODUCTIVOS / TOTAL ACTIVOS','ACTIVOS PRODUCTIVOS / PASIVOS CON COSTO',
                                             'MOROSIDAD DE LA CARTERA DE CREDITOS CONSUMO','MOROSIDAD DE LA CARTERA DE CRÉDITOS INMOBILIARIO\n',
                                            'MOROSIDAD DE LA CARTERA DE CRÉDITOS MICROCRÉDITO','MOROSIDAD DE LA CARTERA TOTAL','COBERTURA DE LA CARTERA REFINANCIADA',
                                            'COBERTURA DE LA CARTERA REESTRUCTURADA','COBERTURA DE LA CARTERA PROBLEMÁTICA',  'GASTOS DE OPERACION ESTIMADOS / TOTAL ACTIVO PROMEDIO (3)','GASTOS DE OPERACION  / MARGEN FINANCIERO',
                                            'GASTOS DE PERSONAL ESTIMADOS / ACTIVO PROMEDIO (3)',  'RESULTADOS DEL EJERCICIO / PATRIMONIO PROMEDIO','RESULTADOS DEL EJERCICIO / ACTIVO PROMEDIO',
                                             'CARTERA BRUTA / (DEPOSITOS A LA VISTA + DEPOSITOS A PLAZO)',
                                             'FONDOS DISPONIBLES / TOTAL DEPOSITOS A CORTO PLAZO']]
        lista_indicadores.append(indicadores_2025)
        




































lista_indicadores=[]
for i in archivos:
    if "2025" in i.name:
        indicadores_2025=pd.read_excel(i, sheet_name="INDICADORES", index_col=0)
        indicadores_2025 = indicadores_2025.dropna(how="all")
        indicadores_2025 = indicadores_2025.reset_index(drop=True)
        indicadores_2025 = indicadores_2025.dropna(axis=1, how="all")
        fecha_encontrada=encontrar_fecha(indicadores_2025)
        print(f"Fecha encontrada en {i.name}: {fecha_encontrada}")
        indicadores_2025 = indicadores_2025.iloc[4:].reset_index(drop=True)
        # Transponer
        indicadores_2025 = indicadores_2025.T
        # Primera fila como nombres de columnas
        indicadores_2025.columns = indicadores_2025.iloc[0]
        # Eliminar la fila utilizada como encabezado
        indicadores_2025 = indicadores_2025.iloc[1:].reset_index(drop=True)
        indicadores_2025.rename(columns={"NOMBRE DEL INDICADOR":"ENTIDAD"}, inplace=True)
        meses = [
            "Enero", "Febrero", "Marzo", "Abril",
            "Mayo", "Junio", "Julio", "Agosto",
            "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ]

        mes = meses[fecha_encontrada.month - 1]
        anio = fecha_encontrada.year

        indicadores_2025.insert(0, "MES", mes)
        indicadores_2025.insert(1, "AÑO", anio)
        indicadores_2025=indicadores_2025[["MES","AÑO","ENTIDAD","( PATRIMONIO + RESULTADOS ) / ACTIVOS INMOVILIZADOS NETOS (3) (6)","INDICE DE CAPITALIZACION NETO: FK / FI",
                                            'ACTIVOS IMPRODUCTIVOS NETOS / TOTAL ACTIVOS','ACTIVOS PRODUCTIVOS / TOTAL ACTIVOS','ACTIVOS PRODUCTIVOS / PASIVOS CON COSTO',
                                             'MOROSIDAD DE LA CARTERA DE CREDITOS CONSUMO','MOROSIDAD DE LA CARTERA DE CRÉDITOS INMOBILIARIO\n',
                                            'MOROSIDAD DE LA CARTERA DE CRÉDITOS MICROCRÉDITO','MOROSIDAD DE LA CARTERA TOTAL','COBERTURA DE LA CARTERA REFINANCIADA',
                                            'COBERTURA DE LA CARTERA REESTRUCTURADA','COBERTURA DE LA CARTERA PROBLEMÁTICA',  'GASTOS DE OPERACION ESTIMADOS / TOTAL ACTIVO PROMEDIO (3)','GASTOS DE OPERACION  / MARGEN FINANCIERO',
                                            'GASTOS DE PERSONAL ESTIMADOS / ACTIVO PROMEDIO (3)',  'RESULTADOS DEL EJERCICIO / PATRIMONIO PROMEDIO','RESULTADOS DEL EJERCICIO / ACTIVO PROMEDIO',
                                             'CARTERA BRUTA / (DEPOSITOS A LA VISTA + DEPOSITOS A PLAZO)',
                                             'FONDOS DISPONIBLES / TOTAL DEPOSITOS A CORTO PLAZO']]
        lista_indicadores.append(indicadores_2025)
        