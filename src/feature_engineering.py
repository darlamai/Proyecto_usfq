import pandas as pd 


def feature_engineering_cartera(lista_cartera):

    lista_cartera_fe = []

    for cartera in lista_cartera:

        # Trabajar sobre copia para no modificar la lista original
        cartera = cartera.copy()

        # =====================================================
        # 1. FEATURE ENGINEERING
        # =====================================================

        cartera["CARTERA IMPRODUCTIVA / CARTERA BRUTA"] = (
            cartera[
                "TOTAL CARTERA IMPRODUCTIVA  (NO DEVENGA INTERESES + VENCIDA)"
            ]
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

        # =====================================================
        # 2. SELECCIONAR VARIABLES FINALES
        # =====================================================
        variables_finales = [
            "MES",
            "AÑO",
            "CUENTA",
            "CARTERA IMPRODUCTIVA / CARTERA BRUTA",
            "CARTERA VENCIDA / CARTERA BRUTA",
            "CARTERA QUE NO DEVENGA INTERESES / CARTERA BRUTA",
            "CARTERA REFINANCIADA / CARTERA BRUTA",
            "CARTERA REESTRUCTURADA / CARTERA BRUTA"
        ]

        cartera = cartera[
            variables_finales
        ].copy()

        # =====================================================
        # 3. RENOMBRAR ENTIDAD
        # =====================================================
        cartera.rename(
            columns={"CUENTA": "ENTIDAD"},
            inplace=True
        )

        lista_cartera_fe.append(cartera)

    return lista_cartera_fe



def calcular_variaciones_balance(lista_balance):

    # =========================================================
    # 1. UNIR TODOS LOS DATAFRAMES MENSUALES
    # =========================================================
    balance = pd.concat(
        lista_balance,
        ignore_index=True
    )

    # =========================================================
    # 2. IDENTIFICAR VARIABLES FINANCIERAS
    # =========================================================
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
        (2025, 2024),
        (2026, 2025)
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

    return variaciones




