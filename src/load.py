###-------------------------------------SCRIPT DE CARGA Y PROCESAMIENTO DE LOS INDICADORES----------------------------------
### Nombre: Darlyn Ludeña
### Fecha: 11/09/2026

import pandas as pd 
from pathlib import Path # Librería que permite trabajar con rutas y directorios
import numpy as np

ruta = Path(__file__).parent.parent #Se obtiene la ruta raíz del proyecto
ruta_data=ruta / "data" #Se construye la ruta hacia la carpeta data
archivos=list(ruta_data.rglob("*.xlsx")) # Permite buscar todos los archivos de excel dentro de data y sus subcarpetas # El resultado es una lista de objetos Path

# =========================
# CONSTANTES
# =========================

### Se enlistan los meses del año para ser añadidos en la columna Mes del dataset
meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

## Listado de los nombres de los indicadores financieros más mes, año y entidad.
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


# Código Contable de las variables extraídas de balance, entre ellas:
# 1-> Activos, 3-> Patrimonio, 14-> Catera de Créditos, 11-> Fondos disponibles
# 13-> Inversiones, 2101-> Depósitos a la vista , 2103-> Depósitos a plazo
cuentas = [
        "1",
        "14",
        "2101",
        "2103",
        "3",
        "11",
        "13"
    ]


# =========================
# FUNCIONES
# =========================


def encontrar_fecha(df, n_columnas=3):

    """Recorre la primeras `n_columnas` de df buscando la primera fecha válida.
    Cuando la encuentra devuelve la primera fecha encontrada según el orden de las filas en 
    formato datetime, caso contrario devuelve None
    Parámetros-> df: dataframe a analizar, n_columnas: número de columnas sobre la cual se realiza la búsqueda.
    Salida-> None o la fecha encontrada dependiendo el caso."""

    for col in df.columns[:n_columnas]:

        fechas = pd.to_datetime(
            df[col],
            errors="coerce", # Si algún valor no puede convertirse a fecha, se reempla por NaT.
            dayfirst=True, #interpreta primero el día, luego el mes
            format="mixed"  # reconoce cualquier formato de fecha
        )
        if fechas.notna().any():
            idx = fechas.first_valid_index()
            return fechas.loc[idx]

    return None



def procesar_indicadores(anio, archivos,meses, columnas_indicadores):

    """Procesa los archivos de la hoja INDICADORES para un año específico, estandariza su estructura, incorpora las variables MES Y AÑO,
       homologa nombres de entidades y filtra únicamente a las entidades.
       Parámetros-> anio, archivos (path de excels), meses (nombres de meses en letras)
       y columnas_indicadores(lista de indicadores financieros).
       Salida-> lista_indicadores: una lista de 12 dataframes, cada uno representa un mes del anio especifico llamado en el input de la función."""

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

            # Insertar MES y AÑO como las columnas iniciales de cada dataframe
            indicadores.insert(0, "MES", mes)
            indicadores.insert(1, "AÑO", anio_fecha)

            # Seleccionar columnas
            indicadores = indicadores[columnas_indicadores]

            # Se realiza una homologación de nombres para garantizar la continuidad de las series históricas. 
            # Por ejemplo, Banco FINCA pasó a denominarse Banco Amibank en 2023, 
            # mientras que Banco D-MIRO fue adquirido por el Grupo Financiero Atlántida en 2024. 
            # Sin esta homologación, una misma entidad podría aparecer bajo distintos nombres en diferentes boletines, 
            # afectando los análisis de evolución y comparabilidad
            indicadores["ENTIDAD"] = indicadores["ENTIDAD"].replace({
                "BP FINCA S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO AMIBANK S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO ATLÁNTIDA S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP D-MIRO S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP COMERCIAL DE MANABI":"BP BANCO COMERCIAL DE MANABI"
            })

 
            indicadores = indicadores[
                indicadores["ENTIDAD"].str.startswith(("BP ", "BANCO "), na=False)
            ].copy()

            # Agregar a la lista
            lista_indicadores.append(indicadores)

    return lista_indicadores



def procesar_cartera(anio, archivos, meses):

    """Procesa los archivos de la hoja COMPOS CART para un año específico, estandariza su estructura, incorpora las variables MES Y AÑO,
    homologa nombres y filtra a las de entidades.
    Parámetros-> anio, archivos (path de excels), meses (nombres de meses en letras)
    Salida-> lista_cartera: lista de 12 dataframes, donde cada uno representa un mes del año especifico llamado en el input de la función."""

    lista_cartera = []

    for i in archivos:

        # Procesar únicamente archivos del año solicitado
        if str(anio) in i.name:

            cartera = pd.read_excel(
                i,
                sheet_name="COMPOS CART",
                index_col=0
            )
            # Limpieza inicial
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
            # Se transpone el dataframe
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

            # Se realiza una homologación de nombres para garantizar la continuidad de las series históricas. 
            # Por ejemplo, Banco FINCA pasó a denominarse Banco Amibank en 2023, 
            # mientras que Banco D-MIRO fue adquirido por el Grupo Financiero Atlántida en 2024. 
            # Sin esta homologación, una misma entidad podría aparecer bajo distintos nombres en diferentes boletines, 
            # afectando los análisis de evolución y comparabilidad
            cartera["ENTIDAD"] = cartera["ENTIDAD"].replace({
                "BP FINCA S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO AMIBANK S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO ATLÁNTIDA S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP D-MIRO S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP COMERCIAL DE MANABI":"BP BANCO COMERCIAL DE MANABI"
            })

            mes = meses[fecha_encontrada.month - 1]
            anio_fecha = fecha_encontrada.year

            # Insertar MES y AÑO como las columnas iniciales de cada dataframe
            cartera.insert(0, "MES", mes)
            cartera.insert(1, "AÑO", anio_fecha)

            # Se filtra solamente las columnas empleadas para el feature de los indicadores de cartera
            cartera=cartera[["MES","AÑO","ENTIDAD",
            "TOTAL CARTERA IMPRODUCTIVA  (NO DEVENGA INTERESES + VENCIDA)",
            "TOTAL CARTERA VENCIDA",
            "TOTAL CARTERA QUE NO DEVENGA INTERES",
            "CARTERA REFINANCIADA",
            "CARTERA REESTRUCTURADA",
            "CARTERA BRUTA"]]

            columnas_id = ["MES", "AÑO", "ENTIDAD"]

            for columna in cartera.columns:
                if columna not in columnas_id:
                    cartera[columna] = pd.to_numeric(
                        cartera[columna],
                        errors="coerce"  # Si algún valor no puede convertirse, lo reemplaza por NaN en lugar de generar un error.
                    )

            lista_cartera.append(cartera)

    return lista_cartera





def procesar_balances(archivos, meses,cuentas):

    """Procesa los archivos de balance general BALANCE, extrae las cuentas de interés, estandariza la estructura de los datos, 
    incorpora las variables MES y AÑO, homologa nombres de entidades y devuelve una lista de DataFrames.
    Parámetros-> archivos (path de excels), meses (nombre de meses en letras)
     cuentas (códigos contables de los boletines). 
    Salida-> lista_balance:devuelve una lista de 12 dataframes con los balances  
     procesadoss, donde cada uno representa un mes del año especifico llamado en el input de la función."""

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

        # Se realiza una homologación de nombres para garantizar la continuidad de las series históricas. 
        # Por ejemplo, Banco FINCA pasó a denominarse Banco Amibank en 2023, 
        # mientras que Banco D-MIRO fue adquirido por el Grupo Financiero Atlántida en 2024. 
        # Sin esta homologación, una misma entidad podría aparecer bajo distintos nombres en diferentes boletines, 
        # afectando los análisis de evolución y comparabilidad

        balance["ENTIDAD"] = balance["ENTIDAD"].replace({
                "BP FINCA S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO AMIBANK S.A.": "BP FINCA S.A./BANCO AMIBANK S.A.",
                "BANCO ATLÁNTIDA S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP D-MIRO S.A.": "BP D-MIRO S.A./BANCO ATLÁNTIDA S.A.",
                "BP COMERCIAL DE MANABI":"BP BANCO COMERCIAL DE MANABI"
            })
        

        mes = meses[fecha_encontrada.month - 1]
        anio = fecha_encontrada.year

        # Insertar MES y AÑO como las columnas iniciales de cada dataframe
        balance.insert(0, "MES", mes)
        balance.insert(1, "AÑO", anio)


        columnas_id = ["MES", "AÑO", "ENTIDAD"]


        for columna in balance.columns:
            if columna not in columnas_id:
                balance[columna] = pd.to_numeric(
                    balance[columna],
                    errors="coerce"
                )

        lista_balance.append(balance)

    return lista_balance















































































































































































































































































