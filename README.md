# Identificación de perfiles financieros de las entidades bancarias privadas ecuatorianas

## Descripción del proyecto

Este proyecto tiene como objetivo **identificar y caracterizar perfiles financieros de las entidades bancarias privadas ecuatorianas**, utilizando técnicas de análisis exploratorio de datos, reducción de dimensionalidad y aprendizaje automático no supervisado.

El análisis se desarrolla sobre información financiera mensual de las entidades bancarias privadas proporcianadas en los boletines públicos de la Superintendencia de Bancos y busca identificar patrones de comportamiento financiero, considerando tanto el nivel de los indicadores como su evolución temporal.

La metodología se estructura en cuatro etapas principales:

1. **Preprocesamiento y Feature Engineering**
2. **Análisis Exploratorio de Datos (EDA)**
3. **Análisis de Componentes Principales (PCA)**
4. **Clustering mediante K-Means**

El flujo completo se encuentra automatizado mediante `main.py`, que ejecuta los cuatro notebooks utilizando **Papermill**.

En caso de no poder ejecutar el proyecto desde `main.py`  por falta de datos, por favor clonar el repositorio público del siguiente link:
https://github.com/darlamai/Proyecto_usfq.git

Tiempo estimado de corrida desde `main.py`: 4 min aprox.
Los resultados de cada fase se presentan en la carpeta results.

---

## Objetivo

Identificar grupos homogéneos de observaciones entidad–período a partir de sus características financieras y posteriormente caracterizar los perfiles obtenidos mediante los indicadores financieros originales.

De esta manera, el proyecto busca pasar de un conjunto amplio de indicadores financieros a una representación reducida y posteriormente a perfiles financieros interpretables.

---

## Datos

La base de datos se construye a partir de información financiera de entidades bancarias privadas ecuatorianas.

El período analizado corresponde a observaciones mensuales de las entidades disponibles en la información procesada.

La unidad de análisis corresponde a:

**Entidad financiera – Año – Mes** 

Los datos utilizados incluyen indicadores financieros, información de cartera, cuentas de balance y variables derivadas mediante ingeniería de características.

### Variables derivadas

Entre las variables construidas se encuentran:

- Indicadores relativos de cartera:
  - Cartera improductiva / cartera bruta
  - Cartera vencida / cartera bruta
  - Cartera que no devenga intereses / cartera bruta
  - Cartera refinanciada / cartera bruta
  - Cartera reestructurada / cartera bruta

- Variaciones interanuales de:
  - Fondos disponibles
  - Inversiones
  - Cartera de créditos
  - Total activo
  - Depósitos a la vista
  - Depósitos a plazo
  - Total patrimonio

Las variaciones interanuales se calculan comparando el mismo mes entre períodos consecutivos, permitiendo incorporar la dinámica financiera además del nivel observado.

---

# Metodología

## 1. Preprocesamiento y Feature Engineering

En esta etapa se procesan los boletines financieros y se homologan las entidades a través del tiempo.

El proceso incluye:

- Lectura automatizada de archivos Excel.
- Extracción de información de las hojas financieras.
- Limpieza y transformación de los datos.
- Homologación de nombres de entidades.
- Incorporación de año y mes.
- Construcción de indicadores relativos de cartera.
- Cálculo de variaciones interanuales.
- Integración de los diferentes conjuntos de indicadores.
- Conversión de variables numéricas.
- Validación de duplicados.
- Identificación de valores infinitos.
- Control de valores nulos.

El resultado de esta etapa constituye la base utilizada posteriormente para el EDA.

---

## 2. Análisis Exploratorio de Datos (EDA)

El análisis exploratorio se realizó separando los indicadores de acuerdo con la dirección deseable de su comportamiento financiero:

- Indicadores donde **valores mayores representan un mejor desempeño**.
- Indicadores donde **valores menores representan un mejor desempeño**.

Para cada grupo se analizaron:

- Series temporales.
- Heatmaps entidad–tiempo.
- Boxplots.
- Valores atípicos mediante el criterio del rango intercuartílico (IQR).

La identificación de valores atípicos se utilizó como mecanismo de diagnóstico y no como criterio automático de eliminación.

También se realizó un análisis de correlación para identificar relaciones elevadas y posibles redundancias entre indicadores antes de aplicar PCA.

---

## 3. Análisis de Componentes Principales (PCA)

Después del EDA se seleccionaron los indicadores utilizados para la reducción de dimensionalidad.

El conjunto utilizado para PCA contiene **24 indicadores financieros**.

Las variables fueron estandarizadas mediante Z-score:

$$
z_{ij} =
\frac{x_{ij}-\bar{x}_j}{s_j}
$$

La estandarización permite trabajar con indicadores expresados en diferentes escalas y evita que una variable domine el análisis por su magnitud.

Posteriormente se aplicó la **descomposición en valores singulares (SVD)**:

$$
Z = U\Sigma V^T
$$

y se obtuvieron los scores de las componentes principales mediante:

$$
T = ZV
$$

Se evaluó la varianza acumulada explicada por las componentes.

Se consideraron dos representaciones alternativas para la etapa de clustering:

- **PC1–PC11:** aproximadamente 80 % de varianza acumulada.
- **PC1–PC15:** aproximadamente 91 % de varianza acumulada.

---

## 4. Clustering

Para identificar perfiles financieros se utilizó el algoritmo **K-Means** sobre las componentes principales obtenidas mediante PCA.

El algoritmo busca minimizar la suma de las distancias cuadráticas entre las observaciones y los centroides de sus respectivos grupos:

$$
J =
\sum_{k=1}^{K}
\sum_{x_i\in C_k}
\|x_i-\mu_k\|^2
$$

Se evaluaron diferentes valores de:

$$
K=2,\ldots,10
$$

y se compararon las soluciones utilizando:

- **Silhouette Score**
- **Davies-Bouldin Index**
- **Calinski-Harabasz Index**
- **Adjusted Rand Index (ARI)**
- Tamaño de los clusters
- Estabilidad de las soluciones
- Interpretabilidad financiera

El análisis llevó a seleccionar:

**PC11 + K = 4**

La caracterización final de los grupos se realizó utilizando nuevamente los indicadores financieros originales, permitiendo interpretar económicamente los clusters obtenidos.

---

# Perfiles financieros identificados

La solución final de cuatro clusters permitió identificar perfiles diferenciados de comportamiento financiero.

Los perfiles se caracterizaron utilizando los indicadores originales y sus desviaciones respecto al promedio de la muestra.

Los grupos fueron interpretados considerando dimensiones como:

- Capitalización.
- Morosidad.
- Rentabilidad.
- Eficiencia operativa.
- Liquidez.
- Calidad de cartera.
- Cobertura.
- Crecimiento de activos y cartera.
- Dinámica de depósitos y patrimonio.

La clasificación también permitió analizar la **evolución temporal de los perfiles** y detectar entidades que presentan cambios de cluster durante el período analizado.

