# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 08:05:50 2024

@author: emili
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import unicodedata
from unidecode import unidecode
import re


palabrasycategorias = pd.read_excel('Palabrasycategorias.xlsx')
glosario = pd.read_excel('glosario.xlsx')
glosario_words = {unidecode(word.lower()) for word in glosario['Termino'] if isinstance(word, str)}
dicmed = palabrasycategorias['Palabra']
dicmed_words = {unidecode(word.lower()) for word in dicmed if isinstance(word, str)}
with open('Diccionarioespañol1.txt', 'r', encoding='utf-8') as file:
    content = file.read().lower()
    content_words = set(re.findall(r'\b\w+\b', content))
    

columnas_requeridas = ['Fecha_Ing', 'Tipo_OS', 'Nro_OS','Nro_Acto', 'Acto', 'Edad', 'Sexo','Nro_Medico', 'Dato_Clinico', 'Informe']

def verificar_y_cargar_archivo(file):
    global data
    try:
        todas_filas = pd.read_excel(file, header=None)
        comienzo = todas_filas[todas_filas.apply(lambda row: row.astype(str).str.contains('Fecha_Ing').any(), axis=1)].index[0]
        data= pd.read_excel(file, skiprows=comienzo)
    except Exception as e:
        return None, f"Error al leer el archivo: {e}", "error"

    columnas_faltantes = [col for col in columnas_requeridas if col not in data.columns]
    
    if columnas_faltantes:
        return None, f"El archivo no tiene los siguientes campos: {', '.join(columnas_faltantes)}", "error"

    data['Fecha_Ing'] = pd.to_datetime(data['Fecha_Ing'])
    data['Edad'] = pd.to_numeric(data['Edad'], errors='coerce')
    data = data[(data['Edad'].notnull()) & (data['Edad'] > 0) & (data['Edad'] < 150)]
    
    tipos_a_eliminar = ['COMBO CON CONTRASTE VIA Y BOMBA']
    data = data[~data['Acto'].isin(tipos_a_eliminar)]
    return data, "El archivo se cargó correctamente.", "success"

def normalizar(texto):
    if isinstance(texto, str):
        texto = texto.lower().strip()  # Convertir a minúsculas y eliminar espacios adicionales
        texto = unicodedata.normalize('NFKD', texto)  # Normalizar texto a NFKD para separar caracteres especiales
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])  # Eliminar caracteres diacríticos (tildes)
        texto = re.sub(r'\s+', ' ', texto)  # Reemplazar múltiples espacios por uno solo
    return texto

#ESTADISTICAS

def periodo_tiempo():
    fecha_minima = pd.to_datetime(data['Fecha_Ing']).min()
    fecha_maxima = pd.to_datetime(data['Fecha_Ing']).max()
    
    periodo_tiempo = fecha_maxima - fecha_minima

    def format_periodo_tiempo(periodo):
        dias = periodo.days
        años = dias // 365
        meses = (dias % 365) // 30
        dias_restantes = (dias % 365) % 30
        return f"{años} años, {meses} meses, {dias_restantes} días"

    return f"Desde {fecha_minima.date()} hasta {fecha_maxima.date()} ({format_periodo_tiempo(periodo_tiempo)})"


def distribucion_genero():
    conteo_sexo = data['Sexo'].value_counts()
    femenino = conteo_sexo.get('F', 0)
    masculino = conteo_sexo.get('M', 0)
    total_registros = len(data)

    porcentaje_femenino = round((femenino / total_registros) * 100, 1)
    porcentaje_masculino = round((masculino / total_registros) * 100, 1)

    return pd.DataFrame({
        "Género": ["Femenino", "Masculino"],
        "Cantidad": [femenino, masculino],
        "Porcentaje": [porcentaje_femenino, porcentaje_masculino]
    })

def histograma_edad_genero():
    plt.figure()
    data[data['Sexo'] == 'F']['Edad'].hist(bins=20, alpha=0.7, label='Mujeres', color='#ffa3a5')
    data[data['Sexo'] == 'M']['Edad'].hist(bins=20, alpha=0.7, label='Hombres', color= '#61a5c2')
    plt.title('Distribución de Edad por Género')
    plt.xlabel('Edad')
    plt.ylabel('Cantidad')
    plt.legend()
    plt.grid(False)
    plt.savefig('histograma_edad_genero.png')
    return 'histograma_edad_genero.png'

def genero_por_tipo_de_acto():
    genero_tipoacto = data.groupby(['Acto', 'Sexo']).size().unstack(fill_value=0)
    genero_tipoacto['Total'] = genero_tipoacto.sum(axis=1)
    genero_tipoacto['Porcentaje_F'] = round((genero_tipoacto['F'] / genero_tipoacto['Total']) * 100, 1)
    genero_tipoacto['Porcentaje_M'] = round((genero_tipoacto['M'] / genero_tipoacto['Total']) * 100, 1)
    genero_tipoacto = genero_tipoacto.reset_index()
    return genero_tipoacto.sort_values(by='Total', ascending=False)

def grafico_genero_por_tipo_de_acto():
    genero_tipoacto = data.groupby(['Acto', 'Sexo']).size().unstack(fill_value=0)
    genero_tipoacto['Total'] = genero_tipoacto.sum(axis=1)
    top10_estudios = genero_tipoacto.sort_values(by='Total', ascending=False).head(10).index

    genero_top10 = genero_tipoacto.loc[top10_estudios]

    genero_top10['Porcentaje_F'] = round((genero_top10['F'] / genero_top10['Total']) * 100, 1)
    genero_top10['Porcentaje_M'] = round((genero_top10['M'] / genero_top10['Total']) * 100, 1)

    genero_top10 = genero_top10[['Porcentaje_F', 'Porcentaje_M']]

    ax = genero_top10.plot(kind='bar', stacked=True, figsize=(12, 8), color=['#ffa3a5', '#61a5c2'])

    plt.title('Distribución de Género por los 10 Tipos de Estudios más Frecuentes')
    plt.xlabel('Tipo de Estudio')
    plt.ylabel('Porcentaje')
    plt.legend(['Femenino', 'Masculino'])
    plt.xticks(rotation=45, ha='right')
    
    for i in ax.containers:
        ax.bar_label(i, label_type='center')

    plt.tight_layout()  # Ajusta el layout para evitar que se corten los textos
    plt.subplots_adjust(bottom=0.2)  # Ajusta el margen inferior si es necesario
    plt.savefig('grafico_genero_top10_estudios.png')
    plt.close()
    return 'grafico_genero_top10_estudios.png'

def plot_genero_distribucion():
    genero_tipoacto = data.groupby(['Acto', 'Sexo']).size().unstack(fill_value=0)
    genero_tipoacto['Total'] = genero_tipoacto.sum(axis=1)
    top10_estudios = genero_tipoacto.nlargest(10, 'Total').index
    genero_top10 = genero_tipoacto.loc[top10_estudios]
    plt.figure(figsize=(12, 8))
    genero_top10 = genero_top10.rename(columns={'F': 'Femenino', 'M': 'Masculino'})
    genero_top10[['Femenino', 'Masculino']].plot(kind='bar', stacked=True, ax=plt.gca(), color=['#ffa3a5','#61a5c2'])

    plt.xlabel('Tipo de Estudio')
    plt.ylabel('Cantidad')
    plt.title('Distribución por Género de los 10 Tipos de Estudios más Frecuentes')

    for i, (index, row) in enumerate(genero_top10.iterrows()):
        plt.text(i, row['Total'] + 5, str(row['Total']), ha='center')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('grafico_genero2_top10_estudios.png')
    return 'grafico_genero2_top10_estudios.png'

    
def estadisticas_edad_tipo_de_acto():
    estadisticas = data.groupby('Acto')['Edad'].agg(
        Promedio_Edad=lambda x: round(x.mean(), 1),
        Cantidad='count',
        Desviacion_Estandar=lambda x: round(x.std(), 1),
    ).sort_values(by='Cantidad', ascending=False)
    estadisticas = estadisticas.reset_index()
    return estadisticas

def grafico_top5_estudios():
    genero_tipoacto = data.groupby(['Acto', 'Sexo']).size().unstack(fill_value=0)
    genero_tipoacto['Total'] = genero_tipoacto.sum(axis=1)
    top5_estudios = genero_tipoacto.sort_values(by='Total', ascending=False).head(5).index
    
    plt.rcParams.update({'font.size': 16})
    plt.figure()
    for acto in top5_estudios:
        plt.hist(data[data['Acto'] == acto]['Edad'], bins=20, alpha=0.5, label=acto)
    plt.title('Distribución de Edad por los 5 Tipos de Estudios más Frecuentes')
    plt.xlabel('Edad')
    plt.ylabel('Frecuencia')
    plt.legend(loc='upper center')
    plt.savefig('grafico_top5_estudios.png')
    return 'grafico_top5_estudios.png'

#BUSQUEDA

def buscar_por_palabras(palabras):
    if data is None:
        return "No hay datos cargados."
    
    palabras = [normalizar(palabra) for palabra in palabras.split()]
    columnas_req = ['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Acto', 'Dato_Clinico']
    data['Informe_Normalizado'] = data['Informe'].apply(normalizar)
    filtrado = data
    for palabra in palabras:
        filtrado = filtrado[filtrado['Informe_Normalizado'].str.contains(palabra, case=False, na=False)]
    data_unique = filtrado.drop_duplicates(subset=['Nro_OS'])
    return data_unique[columnas_req]

def buscar_por_palabrasdc(palabras):
    if data is None:
        return "No hay datos cargados."
    
    palabras = [normalizar(palabra) for palabra in palabras.split()]
    columnas_req = ['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Acto', 'Dato_Clinico']
    data['dc_Normalizado'] = data['Dato_Clinico'].apply(normalizar)
    filtrado = data
    for palabra in palabras:
        filtrado = filtrado[filtrado['dc_Normalizado'].str.contains(palabra, case=False, na=False)]
    data_unique = filtrado.drop_duplicates(subset=['Nro_OS'])
    return data_unique[columnas_req]
    

def buscar_por_frase(frase):
    if data is None:
        return "No hay datos cargados."
    columnas_req = ['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Acto', 'Dato_Clinico']
    data['Informe_Normalizado'] = data['Informe'].apply(normalizar)
    frase_normalizada = normalizar(frase)
    filtrado = data[data['Informe_Normalizado'].str.contains(frase_normalizada, case=False, na=False)]
    data_unique = filtrado.drop_duplicates(subset=['Nro_OS'])
    return data_unique[columnas_req]
    

def buscar_por_frasedc(frase):
    if data is None:
        return "No hay datos cargados."
    columnas_req = ['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Acto', 'Dato_Clinico']
    data['dc_Normalizado'] = data['Dato_Clinico'].apply(normalizar)
    frase_normalizada = normalizar(frase)
    filtrado = data[data['dc_Normalizado'].str.contains(frase_normalizada, case=False, na=False)]
    data_unique = filtrado.drop_duplicates(subset=['Nro_OS'])
    return data_unique[columnas_req]

def resaltar_palabras(informe, palabras):
    # Normaliza las palabras
    palabras_normalizadas = [normalizar(palabra) for palabra in palabras]
    
    # Resalta las palabras en el informe usando etiquetas HTML
    for palabra in palabras_normalizadas:
        informe = re.sub(f"({palabra})", r'<mark>\1</mark>', informe, flags=re.IGNORECASE)
    
    return informe

palabras_busqueda = []

df_resultados_busqueda = pd.DataFrame()  # Inicializa el DataFrame vacío


def buscar_y_resaltar(palabras, tipo):
    global df_resultados_busqueda  # Asumiendo que este DataFrame global se utiliza
    global palabras_busqueda
    
    # Normaliza y guarda las palabras de búsqueda
    palabras_busqueda = [normalizar(palabra) for palabra in palabras.split()] 
    
    # Ejecutar búsqueda según el tipo
    if tipo == "Búsqueda por palabras":
        df_resultados_busqueda = buscar_por_palabras(" ".join(palabras_busqueda))
    elif tipo == "Búsqueda por frase":
        df_resultados_busqueda = buscar_por_frase(palabras)

    # Guardar el DataFrame como archivo Excel
    archivo_path = "resultados_busqueda.xlsx"
    df_resultados_busqueda.to_excel(archivo_path, index=False)

    # Retornar el DataFrame y la ruta del archivo
    return df_resultados_busqueda, archivo_path

def obtener_palabras_busqueda():
    return palabras_busqueda


def normalizar2(texto):
    # Normaliza el texto: conviértelo a minúsculas y elimina tildes y caracteres no deseados.
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)  # Normaliza el texto para separar acentos
    texto = texto.encode('ascii', 'ignore').decode('utf-8')  # Elimina los caracteres no ASCII
    return texto


ultima_busqueda = []

def mostrar_informe_resaltado2(nro_os):
    global ultima_busqueda 

    if data is None:
        return "No hay datos cargados."

    nro_os = int(nro_os)
    if nro_os in data['Nro_OS'].values:
        informe = data[data['Nro_OS'] == nro_os]['Informe'].values[0]
    else:
        return "No se encontró el informe para este número de OS."

    informe_normalizado = normalizar2(informe)
    palabras_resaltadas = obtener_palabras_busqueda()
    ultima_busqueda = palabras_resaltadas

    for palabra in palabras_resaltadas:
        palabra_normalizada = normalizar2(palabra)

        if palabra_normalizada in informe_normalizado:
            informe_normalizado = re.sub(
                rf"({re.escape(palabra)})",  
                r'<span style="background-color: pink ;">\1</span>',
                informe_normalizado,
                flags=re.IGNORECASE  
            )
        else:
            print(f"La palabra '{palabra}' no se encuentra en el informe.")

    informe_html = informe_normalizado.replace("\n", "<br>")
    return informe_html


#POSIBLES ANOMALIAS PANCREAS

def posibles_anomalias_pancreas():
    if data is None:
        return "No hay datos cargados."

    palabras = palabrasycategorias['Palabra']
    categorias = palabrasycategorias['Categoria']
    palabras_patologias = palabras[categorias == 'Patologia']

    palabras_relacionadas_pancreas = [
        "adenocarcinoma pancreatico",
        "pancreatitis",
        "tumor neuroendocrino pancreatico",
        "cancer de pancreas",
        "pancreatoblastoma",
        "neoplasia quistica mucinosa",
        "neoplasia quistica serosa",
        "insulinoma",
        "glucagonoma",
        "gastrinoma",
        "somatostatinoma",
        "carcinoma de celulas acinares",
        "metastasis pancreaticas",
        "cistadenoma seroso",
        "cistadenocarcinoma mucinoso",
        "pancreatoduodenectomia (procedimiento de whipple)",
        "icpn (intracystic papillary mucinous neoplasm)",
        "ductal adenocarcinoma",
        "pseudocisto pancreatico",
        "sindrome de von hippel-lindau",
        "sindrome de zollinger-ellison",
        "cirugia de whipple",
        "cpre (colangiopancreatografia retrograda endoscopica)",
        "eus (endoscopic ultrasound)",
        "ca 19-9 (marcador tumoral)",
        "mutacion kras",
        "bilirrubina elevada",
        "obstruccion biliar",
        "ictericia",
        "dolor abdominal",
        "perdida de peso",
        "diabetes",
        "conducto de wirsung",
        "retropancreatico",
        "periduodenopancreatica",
        "pancreatectomia",
        "peripancreatico",
        "intrapancreatica",
        "peripancreaticas",
        "paripancreaticos",
        "cefalopancreatico","pancreatica",
        "lesion tumoral pancreatica", "cabeza de pancreas", "pancreas atrófico", "cuerpo y cola de pancreas", "lesion pancreatica"
    ]
    
    palabras_relacionadas_pancreas_escaped = [re.escape(palabra) for palabra in palabras_relacionadas_pancreas]
    
    frases_exclusion = [
    "pancreas de forma y tamaño normal",
    "pancreas de forma y tamaño habitual",
    "pancreas de forma, tamaño y densidad habitual",
    "pancreas de morfologia, tamaño y densidad habitual",
    "pancreas y glandulas suprarrenales sin alteraciones",
    "pancreas, bazo y glandulas suprarrenales sin alteraciones",
    "pancreas sin lesiones",
    "Pancreas de morfologia y tamaño habitual",
    "bazo, pancreas y suprarrenales sin alteraciones",
    "pancreas y glandulas suprarrenales sin alteraciones"
]


    data['Informe_Normalizado'] = data['Informe'].apply(normalizar)
    columnas_req = ['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Acto', 'Dato_Clinico']
    informes_patologias_pancreas = data[data['Informe_Normalizado'].str.contains('|'.join(palabras_patologias), case=False, na=False) & data['Informe_Normalizado'].str.contains('|'.join(palabras_relacionadas_pancreas_escaped), case=False, na=False)]
    informes_patologias_pancreas = informes_patologias_pancreas[~informes_patologias_pancreas['Informe_Normalizado'].str.contains('|'.join(frases_exclusion), case=False, na=False)]
    data_unique2 = informes_patologias_pancreas.drop_duplicates(subset=['Nro_OS'])

    # resultado = data_unique2[columnas_req]
    # data['Informe_Normalizado'] = data['Informe'].apply(normalizar)
    # columnas_req = ['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Acto', 'Dato_Clinico']
    # informes_patologias_pancreas = data[data['Informe_Normalizado'].str.contains('|'.join(palabras_patologias), case=False, na=False) & data['Informe_Normalizado'].str.contains('|'.join(palabras_relacionadas_pancreas_escaped), case=False, na=False)]
    # informes_patologias_pancreas = informes_patologias_pancreas[~informes_patologias_pancreas['Informe_Normalizado'].str.contains('|'.join(frases_exclusion), case=False, na=False)]
    # data_unique2 = informes_patologias_pancreas.drop_duplicates(subset=['Nro_OS'])
    return data_unique2[columnas_req]

def mostrar_informe_resaltado3(nro_os):
    if data is None:
        return "No hay datos cargados."

    nro_os = int(nro_os)
    if nro_os in data['Nro_OS'].values:
        informe = data[data['Nro_OS'] == nro_os]['Informe'].values[0]
    else:
        return "No se encontró el informe para este número de OS."

    informe_normalizado = normalizar2(informe)
    

    palabras_relacionadas_pancreas = [
        "adenocarcinoma pancreatico",
        "pancreatitis",
        "tumor neuroendocrino pancreatico",
        "cancer de pancreas",
        "pancreatoblastoma",
        "neoplasia quistica mucinosa",
        "neoplasia quistica serosa",
        "insulinoma",
        "glucagonoma",
        "gastrinoma",
        "somatostatinoma",
        "carcinoma de celulas acinares",
        "metastasis pancreaticas",
        "cistadenoma seroso",
        "cistadenocarcinoma mucinoso",
        "pancreatoduodenectomia (procedimiento de whipple)",
        "icpn (intracystic papillary mucinous neoplasm)",
        "ductal adenocarcinoma",
        "pseudocisto pancreatico",
        "sindrome de von hippel-lindau",
        "sindrome de zollinger-ellison",
        "cirugia de whipple",
        "cpre (colangiopancreatografia retrograda endoscopica)",
        "eus (endoscopic ultrasound)",
        "ca 19-9 (marcador tumoral)",
        "mutacion kras",
        "bilirrubina elevada",
        "obstruccion biliar",
        "ictericia",
        "dolor abdominal",
        "perdida de peso",
        "diabetes",
        "conducto de wirsung",
        "retropancreatico",
        "periduodenopancreatica",
        "pancreatectomia",
        "peripancreatico",
        "intrapancreatica",
        "peripancreaticas",
        "paripancreaticos",
        "cefalopancreatico",
        "pancreatica",
        "lesion tumoral pancreatica",
        "cabeza de pancreas",
        "pancreas atrófico",
        "cuerpo y cola de pancreas",
        "lesion pancreatica"
    ]
    
    palabras_clave = palabrasycategorias['Palabra'][palabrasycategorias['Categoria'] == 'Patologia'].tolist() + palabras_relacionadas_pancreas
    patrones = '|'.join(re.escape(palabra) for palabra in palabras_clave)

    informe_resaltado = re.sub(f"({patrones})", r"<span style='background-color: pink;'>\1</span>", informe_normalizado, flags=re.IGNORECASE)
    informe_html2 = informe_resaltado.replace("\n", "<br>")
    return informe_html2

def cant_posibles_anomalias_pancreas():
    return len(posibles_anomalias_pancreas())


#CALIDAD
def busco_faltantes(text):
    if isinstance(text, str):
        text_normalized = unidecode(text.lower())
        
        text_normalized = re.sub(r'[,:.\d;]+', ' ', text_normalized)
        
        words = []
        for segment in text_normalized.split():
            parts = segment.split('-')
            for part in parts:
                cleaned_part = re.sub(r'^[^\w]+|[^\w]+$', '', part)
                
                if cleaned_part and cleaned_part != 'i/v' and not cleaned_part.isdigit() and not re.search(r'\d', cleaned_part):
                    if '/' in cleaned_part:
                        continue
                    words.append(cleaned_part)
        
        words = {unidecode(word) for word in words}
        
        faltantes = [word for word in words if word not in content_words and word not in dicmed_words and word not in glosario_words]
        return faltantes
    
    return []

def cantidad_completos():
    nan_fecha = data['Fecha_Ing'].isna().sum()
    nan_tipo_os = data['Tipo_OS'].isna().sum()
    nan_nro_os = data['Nro_OS'].isna().sum()
    nan_Nacto = data['Nro_Acto'].isna().sum()
    nan_Acto = data['Acto'].isna().sum()
    nan_edad = data['Edad'].isna().sum()
    nan_sexo = data['Sexo'].isna().sum()
    nan_dato_clinico = data['Dato_Clinico'].isna().sum()
    nan_informe = data['Informe'].isna().sum()
    nan_nromedico = data['Nro_Medico'].isna().sum()

    total_filas = len(data)

    completos_fecha = total_filas - nan_fecha
    completos_tipo_os = total_filas - nan_tipo_os
    completos_nro_os = total_filas - nan_nro_os
    completos_Nacto = total_filas - nan_Nacto
    completos_acto = total_filas - nan_Acto
    completos_edad = total_filas - nan_edad
    completos_sexo = total_filas - nan_sexo
    completos_dato_clinico = total_filas - nan_dato_clinico
    completos_informe = total_filas - nan_informe
    completos_numed = total_filas - nan_nromedico

    completos = [completos_fecha, completos_tipo_os, completos_nro_os, completos_Nacto, completos_acto, completos_edad, completos_sexo, completos_numed, completos_dato_clinico, completos_informe]
    columnas = ['Fecha_Ing', 'Tipo_OS', 'Nro_Os', 'Nro_Acto', 'Tipo_Acto', 'Edad', 'Sexo','Nro_Medico', 'Dato_Clinico', 'Informe']

    plt.figure()
    plt.bar(columnas, completos, color='blue', alpha=0.5, label='Completos')
    plt.xlabel('Columnas')
    plt.ylabel('Cantidad')
    plt.legend()
    for i, valor in enumerate(completos):
        plt.text(i, valor + 0.5, str(valor), ha='center', va='bottom')

    plt.xticks(rotation=45)
    plt.ylim(0, max(completos) * 1.1)  # Ajusta el límite superior del eje y
    plt.tight_layout()
    plt.subplots_adjust(top=0.9)  # Ajusta el margen superior
    plt.savefig('Cantidad de columnas completas.png')
    plt.close()
    return 'Cantidad de columnas completas.png'

def deteccion_errores():
    data_unique = data.drop_duplicates(subset=['Nro_OS'])
    data_informe = data_unique.apply(normalizar, axis=1)
    data_informe['Palabras mal escritas'] = data_informe['Informe'].apply(busco_faltantes)
    data_informe['Cant. palabras mal escritas'] = data_informe['Palabras mal escritas'].apply(len)
    data_informe_ordenado = data_informe[['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Medico', 'Cant. palabras mal escritas', 'Palabras mal escritas']]
    data_informe_ordenado = data_informe_ordenado.sort_values(by='Cant. palabras mal escritas', ascending=False)
    data_informe_ordenado['Informe resaltado'] = data_informe.apply(lambda row: resaltar_errores(row['Informe'], row['Palabras mal escritas']), axis=1)
    return data_informe_ordenado

def mostrar_informe_resaltado(nro_os):
    df = deteccion_errores()
    try:
        nro_os = int(nro_os)  
        if nro_os in df['Nro_OS'].values:
            informe = df[df['Nro_OS'] == nro_os]['Informe resaltado'].values[0]
            informe = informe.replace('\n', '<br>')
            leyendas = """
            <div style="background-color: #f2f2f2; border: 1px solid #ccc; padding: 10px; margin-bottom: 10px; max-width: 400px; border-radius: 10px;">
    <h4>Errores:</h4>
    <div style="display: flex; align-items: center;">
        <div style="background-color: lightcoral; width: 20px; height: 20px; margin-right: 5px; border-radius: 5px;"></div>
        <span style="margin-right: 10px;">Palabras mal escritas</span>
        <div style="background-color: #fdfd96; width: 20px; height: 20px; margin-right: 5px; border-radius: 5px;"></div>
        <span>Errores codificación</span>
    </div>
</div>
            """

            return informe, leyendas
        else:
            return "Número de OS no encontrado."
    except ValueError:
        return "El número de OS debe ser un número entero."

def clasificar_errores(faltantes):
    # Clasificar palabras que contienen caracteres especiales
    caracteres_especiales = re.compile(r'[^\w\s]')  # Expresión regular para detectar caracteres especiales
    codificacion = [word for word in faltantes if caracteres_especiales.search(word)]
    
    # Clasificar el resto
    resto = [word for word in faltantes if not caracteres_especiales.search(word)]
    
    return codificacion, resto

def resaltar_errores(text, faltantes):
    codificacion, resto = clasificar_errores(faltantes)
    for word in codificacion:
        text = re.sub(f"({re.escape(word)})", r'<span style="background-color: yellow;">\1</span>', text, flags=re.IGNORECASE)
    for word in resto:
        text = re.sub(f"({re.escape(word)})", r'<span style="background-color: lightcoral;">\1</span>', text, flags=re.IGNORECASE)
    return text

def calcular_errores_por_medico():
    data_informe = deteccion_errores()
    
    data_informe['Errores codificación'], data_informe['Errores'] = zip(*data_informe['Palabras mal escritas'].apply(clasificar_errores))
    
    errores_por_medico = data_informe.groupby('Nro_Medico').apply(lambda df: {
       'Cant. de informes': df.shape[0],
       'Promedio errores por informe': round(df['Cant. palabras mal escritas'].mean(), 1),
       'Desviacion errores por informe': round(df['Cant. palabras mal escritas'].std(), 1),
       'Cantidad informes con errores': len(df[df['Cant. palabras mal escritas'] > 0]),
       'Cant. de errores total': df['Cant. palabras mal escritas'].sum(),
       'Errores codificación': sum(len(e) for e in df['Errores codificación']),
       'Errores palabras': sum(len(e) for e in df['Errores']),
       'Errores': ', '.join(set(word for faltantes in df['Palabras mal escritas'] for word in faltantes))
   }).apply(pd.Series).reset_index()
    
    errores_por_medico = errores_por_medico[errores_por_medico['Cantidad informes con errores'] > 0]
    errores_por_medico['Porcentaje informes con errores'] = (errores_por_medico['Cantidad informes con errores'] / errores_por_medico['Cant. de informes']) * 100
    errores_por_medico['Porcentaje informes con errores'] = errores_por_medico['Porcentaje informes con errores'].apply(lambda x: round(x, 1))
    
    errores_por_medico = errores_por_medico.sort_values(by='Errores palabras', ascending=False)
    
    return errores_por_medico

def filtrar_por_medico(medicos):
    data_informe_ordenado = deteccion_errores()
    data_medico = data_informe_ordenado[data_informe_ordenado['Nro_Medico'] == int(medicos)]
    errores_por_medico = calcular_errores_por_medico()
    df_filtrado = errores_por_medico[errores_por_medico['Nro_Medico'] == int(medicos)]
    columnas_requeridas= ['Fecha_Ing', 'Tipo_OS', 'Nro_OS', 'Nro_Medico', 'Cant. palabras mal escritas', 'Palabras mal escritas']
    columnas_requeridas2= ['Nro_Medico', 'Cant. de informes', 'Promedio errores por informe', 'Desviacion errores por informe', 'Cantidad informes con errores', 'Porcentaje informes con errores' ,'Cant. de errores total', 'Errores codificación',
'Errores palabras', 'Errores'
]
    return df_filtrado[columnas_requeridas2], data_medico[columnas_requeridas]

def plot_errores_por_medico():
    data5 = calcular_errores_por_medico()
    data5 = data5[data5['Errores palabras'] > 0]  
    
    data5= data5.sort_values(by='Cantidad informes con errores', ascending=False)
    
    plt.figure(figsize=(12, 8))

    bars = plt.bar(data5['Nro_Medico'].astype(str), data5['Cantidad informes con errores'], color='#d9594c')
    plt.xlabel('Nro_Medico')
    plt.ylabel('Cantidad de informes con errores')
    plt.title('Cantidad de informes con errores por médico')
    plt.xticks(rotation=90)
      
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height + 0.5, f"{int(height)}/{data5.iloc[bars.index(bar)]['Cant. de informes']}", ha='center')

    plt.tight_layout()
    plt.savefig('informes_con_errores_x_medico.png')
    return 'informes_con_errores_x_medico.png'

def graficar_errores_por_medico():
    df_errores = calcular_errores_por_medico()
    
    df_errores_sorted = df_errores.sort_values(by='Porcentaje informes con errores', ascending=False)
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df_errores_sorted['Nro_Medico'].astype(str), df_errores_sorted['Porcentaje informes con errores'], color='#d9594c')
    plt.xlabel('Número de Médico')
    plt.ylabel('Porcentaje de Informes con Errores')
    plt.title('Porcentaje de Informes con Errores por Médico')
    plt.xticks(rotation=90)
    
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, f'{yval:.2f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('porcentaje_informes_con_errores.png')
    return 'porcentaje_informes_con_errores.png'


def crear_histograma_errores():
    errores_por_medico = calcular_errores_por_medico()
    errores_por_medico = errores_por_medico[errores_por_medico['Errores palabras'] > 0]
    
    plt.figure(figsize=(14, 7))
    
    # Datos de errores de codificación
    errores_con_vocal = errores_por_medico[['Nro_Medico', 'Errores codificación']].copy()
    errores_con_vocal = errores_con_vocal.fillna(0)  # Asegúrate de que no haya valores NaN
    
    plt.subplot(1, 2, 2)
    width = 0.6  
    x = range(len(errores_con_vocal))  
    bars = plt.bar(x, errores_con_vocal['Errores codificación'], color='#f9df74', width=width, align='center')
    plt.xlabel('Nro_Medico')
    plt.ylabel('Cantidad')
    plt.title('Errores codificación')
    plt.xticks(x, errores_con_vocal['Nro_Medico'].astype(str), rotation=90)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, str(int(yval)), ha='center', va='bottom')

    # Datos de errores de palabras
    plt.subplot(1, 2, 1)
    x = range(len(errores_por_medico))  # Genera posiciones para las barras
    bars = plt.bar(x, errores_por_medico['Errores palabras'], color='#d9594c', align='center')  # Ancho de barra para el primer gráfico
    plt.xlabel('Nro_Medico')
    plt.ylabel('Cantidad')
    plt.title('Errores palabras')
    plt.xticks(x, errores_por_medico['Nro_Medico'].astype(str), rotation=90)
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2.0, yval, str(int(yval)), ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('errores_por_medico.png')
    return 'errores_por_medico.png'

def errores_general():
    data_informe_ordenado = deteccion_errores()
    errores_por_medico = calcular_errores_por_medico()
    
    # Contar valores NaN en los informes
    nan_informe = data['Informe'].isna().sum()
    total_filas = len(data)
    total_informes_informe = total_filas - nan_informe
    
    # Contar errores
    mas_de_5_errores_informe = len(data_informe_ordenado[data_informe_ordenado['Cant. palabras mal escritas'] > 5])
    menos_o_igual_5_errores_informe = total_informes_informe - mas_de_5_errores_informe
    informes_con_0_errores = len(data_informe_ordenado[data_informe_ordenado['Cant. palabras mal escritas'] == 0])
    
    # Cálculo de porcentajes
    porcentaje_mas_de_5_informe = (mas_de_5_errores_informe / total_informes_informe) * 100
    porcentaje_menos_o_igual_5_informe = (menos_o_igual_5_errores_informe / total_informes_informe) * 100
    
    # Cálculo de la cantidad total de errores
    cantidad_total_errores_informe = data_informe_ordenado['Cant. palabras mal escritas'].sum()
    cantidad_total_errores_codificacion = errores_por_medico['Errores codificación'].sum()
    cantidad_total_errores_palabras = errores_por_medico['Errores palabras'].sum()

    # Calcular promedio de errores por informe
    promedio_errores_por_informe = cantidad_total_errores_informe / total_informes_informe if total_informes_informe > 0 else 0

    # Resumen de errores
    resumen_errores_informe = (
        f"Total de informes: {total_informes_informe}\n"
        f"Informes con 0 errores:\n"
        f"  - Cantidad: {informes_con_0_errores}\n"
        f"Informes con más de 5 errores:\n"
        f"  - Cantidad: {mas_de_5_errores_informe}\n"
        f"  - Porcentaje: {porcentaje_mas_de_5_informe:.2f}%\n"
        f"Informes con 5 o menos errores:\n"
        f"  - Cantidad: {menos_o_igual_5_errores_informe}\n"
        f"  - Porcentaje: {porcentaje_menos_o_igual_5_informe:.2f}%\n"
        f"Promedio de errores por informe: {promedio_errores_por_informe:.2f}\n"
        f"Cantidad total de errores: {cantidad_total_errores_informe}\n"
        f"  - Errores de codificación: {cantidad_total_errores_codificacion}\n"
        f"  - Errores de palabras: {cantidad_total_errores_palabras}"
    )

    return resumen_errores_informe




