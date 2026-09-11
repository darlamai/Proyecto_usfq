###-------------------------------------SCRIPT DE CLUSTERING--------------------------------------------------------
### Nombre: Darlyn Ludeña
### Fecha: 11/09/2026


from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import importlib

from sklearn.cluster import KMeans
from sklearn.metrics import (
    silhouette_score,
    davies_bouldin_score,
    calinski_harabasz_score,
    adjusted_rand_score
)
import sys


def evaluar_kmeans(X, rango_k=range(2, 11), random_state=42, n_init=10):
    """
    Evalúa diferentes valores de K para el algoritmo K-Means.

    Para cada valor de K calcula:
    - Silhouette Score.
    - Davies-Bouldin Index.
    - Calinski-Harabasz Index.

    Parámetros-> X: dataframe o numpy, matriz de características utilizada para clustering,
    rango_k: valores de K que serán evaluados, random_state: int, semilla utilizada para reproducibilidad,
    n_init: Número de inicializaciones independientes de K-Means.
    Salida-> dataframe de resultados con las métricas obtenidas para cada K.
    """

    resultados = []

    for k in rango_k:

        modelo = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=n_init
        )

        etiquetas = modelo.fit_predict(X)

        resultados.append({
            "K": k,
            "Silhouette": silhouette_score(X, etiquetas),
            "Davies-Bouldin": davies_bouldin_score(X, etiquetas),
            "Calinski-Harabasz": calinski_harabasz_score(X, etiquetas)
        })

    return pd.DataFrame(resultados)




def evaluar_tamano_clusters(X, k_min=2, k_max=10, random_state=42, n_init=10):
    """
    Calcula el tamaño y porcentaje de observaciones de cada cluster
    para diferentes valores de K utilizando K-Means.

    Parámetros-> X : dataframe, matriz de datos utilizada para el clustering.
    k_min : int, default=2, es el número mínimo de clusters a evaluar.
    k_max : int, default=10, es el número máximo de clusters a evaluar.
    random_state : int, default=42, es la semilla para garantizar reproducibilidad.
    n_init : int, default=10, número de inicializaciones del algoritmo K-Means.

    Retorna-> dataframe con el número de clusters (K), identificador del cluster,
        número de observaciones y porcentaje de observaciones.
    """

    resultados = []

    for k in range(k_min, k_max + 1):

        modelo = KMeans(
            n_clusters=k,
            random_state=random_state,
            n_init=n_init
        )

        etiquetas = modelo.fit_predict(X)

        conteos = pd.Series(etiquetas).value_counts().sort_index()

        for cluster, cantidad in conteos.items():

            resultados.append({
                "K": k,
                "Cluster": cluster,
                "Observaciones": cantidad,
                "Porcentaje": cantidad / len(X) * 100
            })

    return pd.DataFrame(resultados)



def evaluar_estabilidad_ari(X, semillas, k_min=2, k_max=10, n_init=10):
    """
    Evalúa la estabilidad de K-Means mediante el Adjusted Rand Index (ARI)
    para diferentes valores de K y múltiples inicializaciones aleatorias.

    Para cada valor de K, se ejecuta K-Means utilizando las semillas
    especificadas y se compara cada par de particiones mediante el ARI.

    Parámetros-> X : pandas.DataFrame o numpy.ndarray
        Matriz de datos utilizada para realizar el clustering,  semillas: Lista de semillas aleatorias utilizadas para generar diferentes
        inicializaciones del algoritmo K-Means, k_min : int, default=2, número mínimo de clusters que se desea evaluar, k_max : int, default=10
        número máximo de clusters que se desea evaluar, n_init : int, default=10, número de inicializaciones que utiliza K-Means para cada semilla.
    Salida-> dataframe con K filas y los estadísticos de estabilidad - ARI_media: similitud promedio entre las particiones.
        - ARI_std: desviación estándar de los valores ARI.- ARI_min: menor similitud observada.- ARI_max: mayor similitud observada.
    """

    resultados = []

    for k in range(k_min, k_max + 1):

        etiquetas_modelos = []

        # Generar una partición para cada semilla
        for semilla in semillas:

            modelo = KMeans(
                n_clusters=k,
                random_state=semilla,
                n_init=n_init
            )

            etiquetas = modelo.fit_predict(X)

            etiquetas_modelos.append(etiquetas)

        ari_pares = []

        # Comparar todas las particiones entre sí
        for i in range(len(etiquetas_modelos)):

            for j in range(i + 1, len(etiquetas_modelos)):

                ari = adjusted_rand_score(
                    etiquetas_modelos[i],
                    etiquetas_modelos[j]
                )

                ari_pares.append(ari)

        # Resumen de estabilidad para el K evaluado
        resultados.append({
            "K": k,
            "ARI_media": np.mean(ari_pares),
            "ARI_std": np.std(ari_pares),
            "ARI_min": np.min(ari_pares),
            "ARI_max": np.max(ari_pares)
        })

    return pd.DataFrame(resultados)