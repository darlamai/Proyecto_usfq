import pandas as pd 
import numpy as np

def feature_engineering_cartera(lista_cartera):

    lista_cartera_fe = []

    for cartera in lista_cartera:

        cartera = cartera.copy()

        # =====================================================
        # 1. CONVERTIR VARIABLES A NUMÉRICAS
        # =====================================================

        columnas_numericas = [
            "TOTAL CARTERA IMPRODUCTIVA  (NO DEVENGA INTERESES + VENCIDA)",
            "TOTAL CARTERA VENCIDA",
            "TOTAL CARTERA QUE NO DEVENGA INTERES",
            "CARTERA REFINANCIADA",
            "CARTERA REESTRUCTURADA",
            "CARTERA BRUTA"
        ]

        for columna in columnas_numericas:
            cartera[columna] = pd.to_numeric(
                cartera[columna],
                errors="coerce"
            )

        denominador = cartera["CARTERA BRUTA"].replace(0, np.nan)

        # =====================================================
        # 2. FEATURE ENGINEERING
        # =====================================================

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

        # =====================================================
        # 3. SELECCIONAR VARIABLES FINALES
        # =====================================================

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

        # Cruzar por el mismo MES y la misma CUENTA
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

        for variable in variables:

            valor_actual = comparacion[
                f"{variable}_ACTUAL"
            ]

            valor_anterior = comparacion[
                f"{variable}_ANTERIOR"
            ]

            resultado[f"VAR_{variable}"] = np.where(
                valor_actual != 0,
                (valor_actual - valor_anterior) / valor_actual,
                np.nan
            )

        lista_variaciones.append(resultado)

    variaciones = pd.concat(
        lista_variaciones,
        ignore_index=True
    )

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

    lista_unida = []

    for df_indicadores, df_cartera in zip(
        indicadores,
        indicadores_cartera
    ):

        df_unido = df_indicadores.merge(
            df_cartera,
            on=["AÑO", "MES", "ENTIDAD"],
            how="left"
        )

        lista_unida.append(df_unido)

    return lista_unida

