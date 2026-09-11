###-------------------------------------SCRIPT DE FEATURE ENGINEERING----------------------------------·##
### Nombre: Darlyn Ludeña
### Fecha: 11/09/2026

import pandas as pd 
import numpy as np

def feature_engineering_cartera(lista_cartera):

    """ Genera indicadores relativos de cartera mediante feature engineering. 
    Parámetros-> -lista_cartera : lista de dataframes con información de cartera, cada dataframe es un mes. 
    Salida-> lista_cartera_fe-> lista de dataFrames con los indicadores de cartera calculados."""

    lista_cartera_fe = []

    for cartera in lista_cartera:

        cartera = cartera.copy()

        ## Se seleccionan las variables de COMPOS CART seleccionadas para el feature engineering.
        columnas_numericas = [
            "TOTAL CARTERA IMPRODUCTIVA  (NO DEVENGA INTERESES + VENCIDA)",
            "TOTAL CARTERA VENCIDA",
            "TOTAL CARTERA QUE NO DEVENGA INTERES",
            "CARTERA REFINANCIADA",
            "CARTERA REESTRUCTURADA",
            "CARTERA BRUTA"
        ]


        # Se transforman las columnas de los indicadores a numéricas
        for columna in columnas_numericas:
            cartera[columna] = pd.to_numeric(
                cartera[columna],
                errors="coerce"
            )
        # Se pasan los valores nulos de la Cartera Bruta en 0, puesto que corresponde
        # al denominador de todas 
        denominador = cartera["CARTERA BRUTA"].replace(0, np.nan)

        ## Feature Engineering

        cartera["CARTERA IMPRODUCTIVA / CARTERA BRUTA"] = (
            cartera[
                "TOTAL CARTERA IMPRODUCTIVA  (NO DEVENGA INTERESES + VENCIDA)"
            ].div(denominador)
        )

        cartera["CARTERA VENCIDA / CARTERA BRUTA"] = (
            cartera["TOTAL CARTERA VENCIDA"].div(denominador)
        )

        cartera["CARTERA QUE NO DEVENGA INTERESES / CARTERA BRUTA"] = (
            cartera["TOTAL CARTERA QUE NO DEVENGA INTERES"].div(denominador)
        )

        cartera["CARTERA REFINANCIADA / CARTERA BRUTA"] = (
            cartera["CARTERA REFINANCIADA"].div(denominador)
        )

        cartera["CARTERA REESTRUCTURADA / CARTERA BRUTA"] = (
            cartera["CARTERA REESTRUCTURADA"].div(denominador)
        )

  
        # Se seleccionan las variables finales producto del feature engineering
  
        variables_finales = [
            "MES",
            "AÑO",
            "ENTIDAD",
            "CARTERA IMPRODUCTIVA / CARTERA BRUTA",
            "CARTERA VENCIDA / CARTERA BRUTA",
            "CARTERA QUE NO DEVENGA INTERESES / CARTERA BRUTA",
            "CARTERA REFINANCIADA / CARTERA BRUTA",
            "CARTERA REESTRUCTURADA / CARTERA BRUTA"
        ]

        cartera = cartera[variables_finales].copy()

        lista_cartera_fe.append(cartera)

    return lista_cartera_fe



def calcular_variaciones_balance(lista_balance):

    """ Calcula las variaciones interanuales de las cuentas seleccionadas del balance por entidad y mes mediante feature engineering. 
    Parámetros-> lista_balance : lista de DataFrames con información financiera del balance de cada mes. 
   Salida->variaciones: dataframe consolidado con las variaciones interanuales calculadas de las principales cuentas seleccionadas. """


    balance = pd.concat(
        lista_balance,
        ignore_index=True
    )


    columnas_id = ["MES", "AÑO", "ENTIDAD"]

    variables = [
        col for col in balance.columns
        if col not in columnas_id
    ]

    # Convertir variables financieras a numéricas
    for col in variables:
        balance[col] = pd.to_numeric(
            balance[col],
            errors="coerce"
        )
   # Se crea una lista de tuplas con los años sobre los cuales se va a calcular las variaciones interanuales 
    comparaciones = [
        (2022,2021),
        (2023,2022),
        (2024,2023),
        (2025,2024),
        (2026,2025)
    ]

    lista_variaciones = []

    for anio_actual, anio_anterior in comparaciones:

        # Datos del año actual
        actual = balance[
            balance["AÑO"] == anio_actual
        ].copy()

        # Datos del año anterior
        anterior = balance[
            balance["AÑO"] == anio_anterior
        ].copy()

        # Cruzar por el mismo MES y la misma ENTIDAD
        # Las cuentas contables del primer mes pasan con el sufijo ACTUAL, y las del segundo mes con el sufijo ANTERIOR
        comparacion = actual.merge(
            anterior,
            on=["MES", "ENTIDAD"],
            how="inner",
            suffixes=("_ACTUAL", "_ANTERIOR")
        )

        resultado = comparacion[
            ["MES", "ENTIDAD"]
        ].copy()

        resultado["AÑO_ACTUAL"] = anio_actual
        resultado["AÑO_ANTERIOR"] = anio_anterior


        #Se recorre cada cuenta contable que se va a comparar
        for variable in variables:
            #Se toma el valor del primer año con el sufijo ACTUAL 
            valor_actual = comparacion[
                f"{variable}_ACTUAL"
            ]
            #Se toma el valor del segundo año con el sufijo ANTERIOR
            valor_anterior = comparacion[
                f"{variable}_ANTERIOR"
            ]

           #Se crea una nueva variable con el prefijo VAR_ para almacenar las variaciones interanuales de cuenta del balance
            resultado[f"VAR_{variable}"] = np.where(
                # Primer caso: si el valor actual y el anterior son 0 o nulos se considera sin variaciòn y se asigna 0
                ((valor_actual.fillna(0) == 0) & (valor_anterior.fillna(0) == 0)),
                0,
                # Segundo caso: si el valor actual es diferente de 0 y el anterior es 0,
                # la variación porcentual no está definida por división para 0.
                # Se asigna 1 para representar el paso de ausencia de valor a presencia de valor.
                np.where(
                    (valor_actual != 0) & (valor_anterior == 0),
                    1,
                    # Tercer caso: si el valor anterior es diferente de 0, se puede calcular la variación interanual y se expresa su fórmula,
                    # caso contrario le pone NAN.
                    np.where(
                        valor_anterior != 0,
                        (valor_actual - valor_anterior) / valor_anterior,
                        np.nan
                    )
                )
            )

        lista_variaciones.append(resultado)

    variaciones = pd.concat(
        lista_variaciones,
        ignore_index=True
    )


    #Se seleccionan las columnas  finales con las variaciones construidas.
    columnas_finales = [
        "MES",
        "AÑO_ACTUAL",
        "ENTIDAD",
        "VAR_FONDOS DISPONIBLES",
        "VAR_INVERSIONES",
        "VAR_CARTERA DE CRÉDITOS",
        "VAR_TOTAL ACTIVO",
        "VAR_Depósitos a la vista",
        "VAR_Depósitos a plazo",
        "VAR_TOTAL PATRIMONIO"
    ]

    variaciones = variaciones[columnas_finales].copy()

    variaciones = variaciones.rename(
        columns={"AÑO_ACTUAL": "AÑO"}
    )

    return variaciones


def unir_todos_indicadores(indicadores, indicadores_cartera):

    """ Une cada dataframe de la lista de indicadores financieros con cada elemento de la lista de indicadores de cartera. 
    Parámetros->indicadores : lista de DataFrames con indicadores financieros generales, indicadores_cartera : lista de DataFrames con indicadores de cartera. 
    Salida-> lista_unida: lista de dataframes, donde cada uno representa un mes y con todos los indicadores integrados."""


    lista_unida = []

    # Se recorren simultáneamente las dos listas utilizando zip(), 
    # emparejando el DataFrame de indicadores generales con el DataFrame 
    # de indicadores de cartera que corresponde al mismo período.

    for df_indicadores, df_cartera in zip(
        indicadores,
        indicadores_cartera):


        # Se unen ambos DataFrames utilizando AÑO, MES y ENTIDAD como claves de identificación. 
        # El left join conserva todas las  observaciones del DataFrame de indicadores generales 
        # y agrega los indicadores de cartera cuando existe una coincidencia.
        df_unido = df_indicadores.merge(
            df_cartera,
            on=["AÑO", "MES", "ENTIDAD"],
            how="left"
        )

        lista_unida.append(df_unido)

    return lista_unida

def detectar_duplicados(df):
    """
    Cuenta las observaciones duplicadas utilizando AÑO, MES y ENTIDAD
    como llave lógica de identificación.
    Parámetros-> df: dataframe a validar.
    Salida-> número que indica la cantidad de observaciones según la 
    llave definida"""
    return df.duplicated(
        subset=["AÑO", "MES", "ENTIDAD"]
    ).sum()

def detectar_infinitos(df):
    """Cuenta los valores infinitos presentes en las variables numéricas.
    Parámetros->df : dataframe que se desea validar.
    Salida-> serie que indica el número de valores infinitos por variable numérica."""

    # Se seleccionan únicamente las columnas numéricas, ya que
    # los valores infinitos pueden afectar los análisis posteriores.
    columnas_numericas = df.select_dtypes(
        include="number"
    ).columns

    # Se cuentan los valores positivos y negativos infinitos
    # presentes en cada variable.
    return np.isinf(
        df[columnas_numericas]
    ).sum()