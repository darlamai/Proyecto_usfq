from pathlib import Path
import papermill as pm


# --------------------------------------------------------
# Configuración de rutas del proyecto
# --------------------------------------------------------

# Se obtiene la carpeta raíz del proyecto a partir de la ubicación
# del archivo main.py.
RAIZ_PROYECTO = Path(__file__).resolve().parent

NOTEBOOKS_DIR = RAIZ_PROYECTO / "notebooks"
OUTPUT_DIR = NOTEBOOKS_DIR / "output"


def _ejecutar_notebook(nombre_archivo: str):
    """Función auxiliar para ejecutar un notebook individual."""

    # Se crea la carpeta de salida si no existe.
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    input_path = NOTEBOOKS_DIR / nombre_archivo
    output_path = OUTPUT_DIR / f"ejecutado_{nombre_archivo}"

    print(f"Iniciando: {nombre_archivo}...")

    pm.execute_notebook(
        input_path=str(input_path),
        output_path=str(output_path),
        kernel_name="python3",
        parameters={
            "RAIZ_PROYECTO": str(RAIZ_PROYECTO)
        }
    )

    print(f"✓ Finalizado: {nombre_archivo}\n")


def run_preprocessing():
    """Ejecuta el cuaderno de preprocesamiento."""
    _ejecutar_notebook("01.preprocessing.ipynb")


def run_eda():
    """Ejecuta el cuaderno de Análisis Exploratorio de Datos."""
    _ejecutar_notebook("02.EDA.ipynb")


def run_pca():
    """Ejecuta el cuaderno de Análisis de Componentes Principales."""
    _ejecutar_notebook("03.PCA.ipynb")


def main():
    print("PROYECTO USFQ")

    run_preprocessing()
    run_eda()
    run_pca()


if __name__ == "__main__":
    main()