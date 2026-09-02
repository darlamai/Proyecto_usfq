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








lista_indicadores=[]
for i in archivos:
    if "2025" in i.name:
        indicadores_2025=pd.read_excel(i, sheet_name="INDICADORES", index_col=0)
        indicadores_2025 = indicadores_2025.dropna(how="all")
        indicadores_2025 = indicadores_2025.reset_index(drop=True)
        indicadores_2025 = indicadores_2025.dropna(axis=1, how="all")
        fecha_encontrada=encontrar_fecha(indicadores_2025)
        indicadores_2025 = indicadores_2025.iloc[4:].reset_index(drop=True)
        indicadores_2025.columns = indicadores_2025.iloc[0]

        # Tomar la primera columna como índice
        df = indicadores_2025.set_index("NOMBRE DEL INDICADOR")

        # Transponer
        df = df.T.reset_index()

        # Renombrar la columna con el nombre del banco
        df = df.rename(columns={"index": "BANCO"})


        lista_indicadores.append(indicadores_2025)
        