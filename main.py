import os
import papermill as pm # librería para parametrizar y ejecutar Jupyter Notebooks 

NOTEBOOKS_DIR = "notebooks"
OUTPUT_DIR = os.path.join(NOTEBOOKS_DIR, "output")

def _ejecutar_notebook(nombre_archivo: str):
    """Función auxiliar para ejecutar un notebook individual."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    input_path = os.path.join(NOTEBOOKS_DIR, nombre_archivo)
    output_path = os.path.join(OUTPUT_DIR, f"ejecutado_{nombre_archivo}")
    
    print(f"Iniciando: {nombre_archivo}...")
    pm.execute_notebook(
        input_path=input_path,
        output_path=output_path,
        kernel_name="python3"
    )
    print(f"✓ Finalizado: {nombre_archivo}\n")

def run_preprocessing():
    """Ejecuta el cuaderno de preprocesamiento."""
    _ejecutar_notebook("01.preprocessing.ipynb")

def run_eda():
    """Ejecuta el cuaderno de Análisis Exploratorio de Datos (EDA)."""
    _ejecutar_notebook("02. EDA.ipynb")

def main():
    print("Hello from proyecto-usfq!")
    
    # Llamada a las funciones en secuencia
    run_preprocessing()
    run_eda()

if __name__ == "__main__":
    main()
