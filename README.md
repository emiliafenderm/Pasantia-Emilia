# comepa-nlp-screening

Este repositorio contiene scripts y herramientas para el análisis y procesamiento de informes de imagenología.
A continuación se detallan los pasos para configurar el entorno y ejecutar los scripts disponibles.

## Configuración del Entorno

1. Crear un entorno virtual:
   python -m venv mi_entorno

2. En Windows:
   mi_entorno\Scripts\activate
   En macOS y Linux:
   source mi_entorno/bin/activate

3. Instalar los requerimientos necesarios:
   pip install -r requirements.txt

## Ejecución de Scripts

## Instrucciones para la interfaz Gradio
El archivo gradiointerfaz.py proporciona una interfaz gráfica interactiva utilizando la biblioteca Gradio. Para ejecutarla y abrir la interfaz: python gradiointerfaz.py, devuelve un link local de la web.

# Funciones utilizadas
El archivo funciones.py contiene varias funciones personalizadas que son utilizadas en diferentes scripts, especialmente en la interfaz de Gradio. Algunas de estas funciones incluyen el preprocesamiento de texto, la detección de errores ortográficos, y el análisis de datos.
