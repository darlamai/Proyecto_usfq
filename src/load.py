import pandas as pd
from pathlib import Path
import numpy as np

ruta = Path(__file__).parent.parent
ruta_data=ruta / "data"
archivos=list(ruta_data.rglob("*.xlsx"))



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
        "MOROSIDAD DE LA CARTERA DE CRÉDITOS INMOBILIARIO",
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



cuentas = [
        "1",
        "14",
        "2101",
        "2103",
        "3",
        "11",
        "13"
    ]



def encontrar_fecha(df, n_columnas=3):
    for col in df.columns[:n_columnas]:

        fechas = pd.to_datetime(
            df[col],
            errors="coerce",
            dayfirst=True,
            format="mixed"
        )

        if fechas.notna().any():
            idx = fechas.first_valid_index()
            return fechas.loc[idx]

    return None



def procesar_indicadores(anio, archivos,meses, columnas_indicadores):

    lista_indicadores = []
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

            indicadores.columns = indicadores.columns.astype(str).str.strip()

            # Eliminar fila utilizada como encabezado
            indicadores = indicadores.iloc[1:].reset_index(drop=True)

            # Cambiar nombre de columna
            indicadores.rename(
                columns={"NOMBRE DEL INDICADOR": "ENTIDAD"},
                inplace=True
            )
            indicadores.columns = indicadores.columns.astype(str).str.strip()

            # Obtener mes y año
            mes = meses[fecha_encontrada.month - 1]
            anio_fecha = fecha_encontrada.year

            # Insertar MES y AÑO
            indicadores.insert(0, "MES", mes)
            indicadores.insert(1, "AÑO", anio_fecha)

            # Seleccionar columnas
            indicadores = indicadores[columnas_indicadores]

            # CAMBIAR NOMBRE DE LA ENTIDAD
            indicadores["ENTIDAD"] = indicadores["ENTIDAD"].replace({
                "BP FINCA S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO AMIBANK S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO ATLÁNTIDA S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP D-MIRO S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP COMERCIAL DE MANABI":"BP BANCO COMERCIAL DE MANABI"
            })

            # FILTRAR SOLO BANCOS PRIVADOS
    
            indicadores = indicadores[
                indicadores["ENTIDAD"].str.startswith(("BP ", "BANCO "), na=False)
            ].copy()

            # Agregar a la lista
            lista_indicadores.append(indicadores)

    return lista_indicadores



def procesar_cartera(anio, archivos, meses):

    lista_cartera = []

    for i in archivos:

        # Procesar únicamente archivos del año solicitado
        if str(anio) in i.name:

            cartera = pd.read_excel(
                i,
                sheet_name="COMPOS CART",
                index_col=0
            )

            cartera = cartera.dropna(how="all")
            cartera = cartera.reset_index(drop=True)
            cartera = cartera.dropna(axis=1, how="all")

            # Obtener fecha del archivo
            fecha_encontrada = encontrar_fecha(cartera)

            # Eliminar filas iniciales
            cartera = cartera.iloc[4:].reset_index(drop=True)

            # Eliminar primera columna
            cartera = cartera.drop(
                columns=[cartera.columns[0]]
            )


            cartera = cartera.T

            # Primera fila como encabezados
            cartera.columns = cartera.iloc[0]

            # Eliminar fila utilizada como encabezado
            cartera = cartera.iloc[1:].reset_index(drop=True)


            cartera = cartera[
                cartera["CUENTA"].str.startswith(
                    ("BP ", "BANCO "),
                    na=False
                )
            ].copy()

            # Cambiar nombre CUENTA por ENTIDAD
            cartera.rename(
                columns={"CUENTA": "ENTIDAD"},
                inplace=True
            )

            # CAMBIAR NOMBRE DE LA ENTIDAD
            cartera["ENTIDAD"] = cartera["ENTIDAD"].replace({
                "BP FINCA S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO AMIBANK S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO ATLÁNTIDA S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP D-MIRO S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP COMERCIAL DE MANABI":"BP BANCO COMERCIAL DE MANABI"
            })


            mes = meses[fecha_encontrada.month - 1]
            anio_fecha = fecha_encontrada.year

            cartera.insert(0, "MES", mes)
            cartera.insert(1, "AÑO", anio_fecha)

            lista_cartera.append(cartera)

    return lista_cartera


def procesar_balances(archivos, meses,cuentas):

    lista_balance = []

    for archivo in archivos:
        balance = pd.read_excel(
            archivo,
            sheet_name="BALANCE",
            index_col=0
        )

        balance = balance.dropna(how="all")
        balance = balance.reset_index(drop=True)
        balance = balance.dropna(axis=1, how="all")

        fecha_encontrada = encontrar_fecha(balance)

        balance = balance.iloc[4:].reset_index(drop=True)
        balance.columns = balance.iloc[0]
        balance["CÓDIGO"] = balance["CÓDIGO"].astype(str).str.strip()

        balance = balance[balance["CÓDIGO"].isin(cuentas)].copy()

        balance = balance.drop(
            columns=[balance.columns[0]]
        )

        balance = balance.T
        balance = balance.reset_index()

        # Primera fila como nombres de columnas
        balance.columns = balance.iloc[0]

        # Eliminar fila usada como encabezado
        balance = balance.iloc[1:].reset_index(drop=True)

        balance = balance[
            balance["CUENTA"].str.startswith(
                ("BP ", "BANCO "),
                na=False
            )
        ].copy()

        balance.rename(
            columns={"CUENTA": "ENTIDAD"},
            inplace=True
        )

        balance["ENTIDAD"] = balance["ENTIDAD"].replace({
                "BP FINCA S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO AMIBANK S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO ATLÁNTIDA S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP D-MIRO S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP COMERCIAL DE MANABI":"BP BANCO COMERCIAL DE MANABI"
            })
        

        mes = meses[fecha_encontrada.month - 1]
        anio = fecha_encontrada.year

        balance.insert(0, "MES", mes)
        balance.insert(1, "AÑO", anio)

        lista_balance.append(balance)

    return lista_balance















































































































































































































































































