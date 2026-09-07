import os
import matplotlib
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import re





def obtener_columnas_numericas(df, columnas_excluir=None):

    if columnas_excluir is None:
        columnas_excluir = ["MES", "AÑO", "ENTIDAD"]

    columnas_numericas = [
        columna
        for columna in df.select_dtypes(include="number").columns
        if columna not in columnas_excluir
    ]

    return columnas_numericas



def estadistica_descriptiva(df, columnas=None):

    if columnas is None:
        columnas = obtener_columnas_numericas(df)

    estadisticas = df[columnas].describe().T

    return estadisticas


#########DIAGRAMA DE LÍNEAS########################################################3

# PALETA DE COLORES PARA LAS ENTIDADES
# ============================================================



def graficar_indicadores(
    df,
    indicadores,
    carpeta="graficas_EDA_indicadores_financieros",
    indicadores_notebook=None
):
    
    # Crear carpeta si no existe
    os.makedirs(carpeta, exist_ok=True)
    
    # Lista vacía si no se especifican indicadores para mostrar
    if indicadores_notebook is None:
        indicadores_notebook = []


    entidades = df["ENTIDAD"].dropna().unique()

    # Combinar tab10 y tab20 para tener más colores diferenciables
    colores = (
        list(sns.color_palette("tab10")) +
        list(sns.color_palette("tab20"))
    )

    # Crear un color para cada entidad
    paleta_entidades = dict(
        zip(
            entidades,
            colores[:len(entidades)]
        )
    )
        
    # Recorrer indicadores
    for indicador in indicadores:
        
        # Verificar que el indicador exista
        if indicador not in df.columns:
            print(f"No se encontró la variable: {indicador}")
            continue
        
        # Crear figura
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Gráfico
        sns.lineplot(
            data=df,
            x="FECHA",
            y=indicador,
            hue="ENTIDAD",
            palette=paleta_entidades,
            ax=ax
        )
        
        # Título y etiquetas
        ax.set_title(
            f"Evolución temporal de {indicador} (en porcentaje)",
            fontsize=14
        )
        
        ax.set_xlabel("Fecha")
        ax.set_ylabel(indicador)
        
        # Leyenda fuera del gráfico
        ax.legend(
            title="Entidad",
            bbox_to_anchor=(1.02, 1),
            loc="upper left"
        )
        
        # Ajustar distribución
        plt.tight_layout()
        
        # Si está en la lista → mostrar en notebook
        if indicador in indicadores_notebook:
            
            plt.show()
            
        # Si no → guardar en carpeta
        else:
            
            # Limpiar nombre para usarlo como archivo
            nombre_archivo = re.sub(
                r'[\\/*?:"<>|()]',
                "",
                indicador
            )
            
            nombre_archivo = nombre_archivo.replace("/", "_")
            nombre_archivo = nombre_archivo.replace(" ", "_")
            
            ruta = os.path.join(
                carpeta,
                f"{nombre_archivo}.png"
            )
            
            plt.savefig(
                ruta,
                dpi=300,
                bbox_inches="tight"
            )
            
            plt.close()
            
            print(f"Guardado: {ruta}")


###############HEATMAPS##################################################################33

def generar_heatmaps(
    df,
    indicadores,
    indicadores_notebook=None,
    carpeta="graficas_EDA"
):

    os.makedirs(carpeta, exist_ok=True)

    if indicadores_notebook is None:
        indicadores_notebook = []

    for indicador in indicadores:

        # Verificar que el indicador exista
        if indicador not in df.columns:
            print(f"No se encontró la variable: {indicador}")
            continue

        # Crear estructura Entidad x Fecha
        heatmap_data = df.pivot_table(
            index="ENTIDAD",
            columns="FECHA",
            values=indicador,
            aggfunc="mean"
        )

        # Crear figura
        fig, ax = plt.subplots(figsize=(18, 10))

        # --------------------------------------------------
        # Excepción: SUFICIENCIA PATRIMONIAL
        # --------------------------------------------------
        if indicador == "SUFICIENCIA PATRIMONIAL":

            # Intervalos cada 9 puntos porcentuales
            limites = [
                0, 9, 18, 27, 36, 45,
                54, 63, 72, 81, 90, 100
            ]

            # Colores
            colores = [
                "#B30000",  # 0-9   → rojo intenso
                "pink",    # 9-18  → rosa
                "#FC8D59",  # 18-27 → salmón
                "#FDBB84",  # 27-36 → durazno
                "#FDD49E",  # 36-45 → beige
                "#FEE8C8",  # 45-54 → piel claro
                "#F7F7D5",  # 54-63 → crema
                "#D9E8C8",  # 63-72 → verde suave
                "#9ECAE1",  # 72-81 → azul claro
                "#4292C6",  # 81-90 → azul
                "#08519C"   # 90-100 → azul intenso
            ]

            cmap = ListedColormap(colores)

            norm = BoundaryNorm(
                limites,
                cmap.N
            )

            sns.heatmap(
                heatmap_data,
                cmap=cmap,
                norm=norm,
                linewidths=0.2,
                cbar_kws={
                    "label": indicador,
                    "ticks": limites
                },
                ax=ax
            )

        # --------------------------------------------------
        # Excepción: COBERTURA DE LA CARTERA PROBLEMÁTICA
        # --------------------------------------------------
        elif indicador == "COBERTURA DE LA CARTERA PROBLEMÁTICA":

            # Intervalos cada 100 puntos porcentuales
            # hasta 1000%, y un último grupo para valores mayores
            limites = [
                0, 100, 200, 300, 400, 500,
                600, 700, 800, 900, 1000
            ]

            # Colores: rojo → tonos piel → azul
            colores = [
                "#B30000",  # 0-100   → rojo intenso
                "#E34A33",  # 100-200 → rojo
                "#FC8D59",  # 200-300 → salmón
                "#FDBB84",  # 300-400 → durazno
                "#FDD49E",  # 400-500 → beige
                "#FEE8C8",  # 500-600 → piel claro
                "#F7F7D5",  # 600-700 → crema
                "#D9E8C8",  # 700-800 → verde suave
                "#9ECAE1",  # 800-900 → azul claro
                "#4292C6"   # 900-1000 → azul
            ]

            cmap = ListedColormap(colores)

            norm = BoundaryNorm(
                limites,
                cmap.N
            )

            sns.heatmap(
                heatmap_data,
                cmap=cmap,
                norm=norm,
                linewidths=0.2,
                cbar_kws={
                    "label": indicador,
                    "ticks": limites
                },
                ax=ax
            )

        # --------------------------------------------------
        # Resto de indicadores: escala automática
        # --------------------------------------------------
        else:

            sns.heatmap(
                heatmap_data,
                cmap="YlGnBu",
                linewidths=0.2,
                cbar_kws={
                    "label": indicador
                },
                ax=ax
            )

        # --------------------------------------------------
        # Configuración del gráfico
        # --------------------------------------------------

        ax.set_title(
            f"Heatmap de {indicador}",
            fontsize=14
        )

        ax.set_xlabel("Fecha")
        ax.set_ylabel("Entidad")

        # Mostrar solamente Año-Mes
        ax.set_xticks(
            [i + 0.5 for i in range(len(heatmap_data.columns))]
        )

        ax.set_xticklabels(
            heatmap_data.columns.strftime("%Y-%m"),
            rotation=90
        )

        plt.tight_layout()

        # -----------------------------------------
        # Mostrar en notebook
        # -----------------------------------------
        if indicador in indicadores_notebook:

            plt.show()

        # -----------------------------------------
        # Guardar en carpeta
        # -----------------------------------------
        else:

            nombre_archivo = re.sub(
                r'[\\/*?:"<>|()]',
                "",
                indicador
            )

            nombre_archivo = (
                nombre_archivo
                .replace("/", "_")
                .replace(" ", "_")
            )

            ruta = os.path.join(
                carpeta,
                f"heatmap_{nombre_archivo}.png"
            )

            plt.savefig(
                ruta,
                dpi=300,
                bbox_inches="tight"
            )

            plt.close()

            print(f"Guardado: {ruta}")


#######################BOXPLOTS#################################################################33

def generar_boxplots(
    df,
    indicadores,
    indicadores_notebook=None,
    carpeta="graficas_EDA"
):

    os.makedirs(carpeta, exist_ok=True)

    if indicadores_notebook is None:
        indicadores_notebook = []

    for indicador in indicadores:

        # Verificar que el indicador exista
        if indicador not in df.columns:
            print(f"No se encontró la variable: {indicador}")
            continue

        # Crear figura
        fig, ax = plt.subplots(figsize=(10, 7))

        # Boxplot
        sns.boxplot(
            y=df[indicador],
            ax=ax
        )

        ax.set_title(
            f"Diagrama de caja de {indicador}",
            fontsize=14
        )

        ax.set_xlabel("")
        ax.set_ylabel(indicador)

        plt.tight_layout()

        # -----------------------------------------
        # Mostrar en notebook
        # -----------------------------------------
        if indicador in indicadores_notebook:

            plt.show()

        # -----------------------------------------
        # Guardar en carpeta
        # -----------------------------------------
        else:

            # Limpiar nombre para crear archivo
            nombre_archivo = re.sub(
                r'[\\/*?:"<>|()]',
                "",
                indicador
            )

            nombre_archivo = (
                nombre_archivo
                .replace("/", "_")
                .replace(" ", "_")
            )

            ruta = os.path.join(
                carpeta,
                f"boxplot_{nombre_archivo}.png"
            )

            plt.savefig(
                ruta,
                dpi=300,
                bbox_inches="tight"
            )

            plt.close()

            print(f"Guardado: {ruta}")



##############DETECTAR ATÍPICOS###########################################################

def detectar_atipicos_iqr(df, indicadores):

    resultados = []

    for indicador in indicadores:

        # Verificar que exista la variable
        if indicador not in df.columns:
            print(f"No se encontró la variable: {indicador}")
            continue

        # Serie numérica sin nulos
        serie = pd.to_numeric(
            df[indicador],
            errors="coerce"
        ).dropna()

        # Si no hay datos suficientes
        if len(serie) < 4:
            continue

        # Cuartiles
        Q1 = serie.quantile(0.25)
        Q3 = serie.quantile(0.75)

        # Rango intercuartílico
        IQR = Q3 - Q1

        # Límites
        limite_inferior = Q1 - 1.5 * IQR
        limite_superior = Q3 + 1.5 * IQR

        # Identificar atípicos
        mascara_atipico = (
            (df[indicador] < limite_inferior) |
            (df[indicador] > limite_superior)
        )

        datos_atipicos = df.loc[
            mascara_atipico,
            ["ENTIDAD", "FECHA", indicador]
        ].copy()

        # Agregar información del indicador
        datos_atipicos["INDICADOR"] = indicador
        datos_atipicos["Q1"] = Q1
        datos_atipicos["Q3"] = Q3
        datos_atipicos["IQR"] = IQR
        datos_atipicos["LIMITE_INFERIOR"] = limite_inferior
        datos_atipicos["LIMITE_SUPERIOR"] = limite_superior

        # Clasificar según dirección del atípico
        datos_atipicos["TIPO_ATIPICO"] = np.where(
            datos_atipicos[indicador] < limite_inferior,
            "Inferior",
            "Superior"
        )

        resultados.append(datos_atipicos)

    # Unir resultados
    if resultados:

        tabla_atipicos = pd.concat(
            resultados,
            ignore_index=True
        )

    else:

        tabla_atipicos = pd.DataFrame()

    return tabla_atipicos