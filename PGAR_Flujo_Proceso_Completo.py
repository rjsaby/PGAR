# ? LIBRERIAS

import os
import arcpy
import pandas as pd
import numpy as np
import csv
from arcgis.features import GeoAccessor, GeoSeriesAccessor

arcpy.env.overwriteOutput = True

# ? _2_PGAR_Construccion_Inventario

print("____________________ INICIA _2_PGAR_Construccion_Inventario ____________________")

# ** Ubicación y registro de archivos .gdb dentro de múltiples directorios

ruta_padre = r"D:\PUBLIC\PGAR\Insumos\Capas_Geograficas"
nombre_directorios = os.listdir(ruta_padre)
rutas_workspace = []

for directorio in nombre_directorios:
    ruta_directorio = os.path.join(ruta_padre, directorio)
    if os.path.isdir(ruta_directorio) == True:
        # Búsqueda de bases de datos dentro de segunda raíz de directorios
        nombre_subdirectorios = os.listdir(ruta_directorio)
        for subdirectorio in nombre_subdirectorios:
            if '.gdb' in subdirectorio:
                ruta_bd = os.path.join(ruta_directorio, subdirectorio)
                rutas_workspace.append(ruta_bd)

# ** Parametrización de Código Temática

nombre_campo_tematico = 'codigo_tematica'

# ? Parte del desarrollo, que por lo pronto, si o si se debe modificar manualmente
clasificacion_tematica = {'_1_POMCA': 1,
                          '_2_Cambio_Climatico': 2,
                          '_3_Cuencas_Hidrograficas': 3,
                          '_4_Suelos': 4,
                          '_5_Areas_Protegidas': 5,
                          '_6_Jurisdiccion_CAR': 6,
                          '_7_Rondas': 7,
                          '_8_Agua_Subterranea': 8,
                          '_9_Paramos': 9,
                          '_10_Analisis_Vulnerabilidad_Riesgo_Inundacion': 10,
                          '_11_Analisis_Vulnerabilidad_Riesgo_Incendio': 11,
                          '_12_Analisis_Vulnerabilidad_Riesgo_Avenida_Torrencial': 12,
                          '_13_Analisis_Vulnerabilidad_Riesgo_Remocion_Masa': 13,
                          '_14_Ecosistema':14,
                          '_15_Licencias_Ambientales':15,
                          '_16_Infraestuctura':16,
                          '_17_Desarrollo_Rural': 17,
                          '_18_Incendios':18,
                          '_19_Geologia_Geomorfologia':19,
                          '_20_Biodiversidad':20}

for espacio_trabajo in rutas_workspace:
    arcpy.env.workspace = espacio_trabajo
    for capa in arcpy.ListFeatureClasses():
        if 'nivel' not in capa:
            ruta_temporal = os.path.join(arcpy.env.workspace, capa)
            division_directorios = os.path.split(ruta_temporal)[0]
            carpetas = division_directorios.split("\\")[5]
            categorizacion_tema = carpetas.split("_")[1]
            # !!Crear Dominio!!, !!Revisar obligatoriedad!!
            arcpy.management.AddField(capa, nombre_campo_tematico, 'LONG', field_alias = 'Codigo Temática')
            for registro in clasificacion_tematica:
                if carpetas == registro:
                    arcpy.management.CalculateField(capa, nombre_campo_tematico, clasificacion_tematica[carpetas], 'PYTHON3')
                    print("Se actualiza de la capa {0}, la temática {1}, con el código: {2}".format(capa, carpetas, clasificacion_tematica[carpetas]))
        else:
            print("No se actualiza el código de temática para la capa {0}".format(capa))
            
# ** Creación tabla -tbl_tematica

df_tematica = pd.DataFrame.from_dict(clasificacion_tematica, orient ='index')
df_tematica = df_tematica.reset_index()
df_tematica.rename({'index':'nombre_tematica', 0:'codigo_tematica'}, axis=1, inplace=True)

# ** Exportar capa -tbl_tematica- a FileGDB

ruta_capas_w_municipio = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"
nombre_tabla_capa = 'tbl_tematica'
ruta_salida_tabla_tematica = os.path.join(ruta_capas_w_municipio, nombre_tabla_capa)
df_tematica.spatial.to_table(location = ruta_salida_tabla_tematica)
print("----------------------------- Se crea la tabla: -tbl_tematica- en Base de Datos -----------------------------")

# ** Parametrización de Nombre Final Capa

ruta_bd_local = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"

nombre_campo_capa_final = 'nombre_capa_final'

for espacio_trabajo in rutas_workspace:
    arcpy.env.workspace = espacio_trabajo
    ruta_temporal = os.path.join(arcpy.env.workspace)
    division_directorios = os.path.split(ruta_temporal)[0]
    carpetas = division_directorios.split("\\")[5]
    categorizacion_tema = carpetas.split("_")[1]
    for capa in arcpy.ListFeatureClasses():
        if 'nivel' not in capa:
            arcpy.management.AddField(capa, nombre_campo_capa_final, 'TEXT', field_alias = 'Nombre Capa Final')
            capa_entrada = os.path.join(arcpy.env.workspace, capa)
            # Parametrizacion de temática en nombre de la capa
            ruta_archivos_a_local = os.path.join(ruta_bd_local, "_" + categorizacion_tema + "_" + capa)
            ruta_archivos_a_local = ruta_archivos_a_local.replace('__','_')
            nombre_capa_final = ruta_archivos_a_local.split('\\')[7]
            arcpy.management.CalculateField(capa, nombre_campo_capa_final, "'" + nombre_capa_final + "'", 'PYTHON3')
            print("Se crea y registra el nombre de la capa final sobre la capa: {0}".format(capa))
            
# ** Borrado de capas en el archivo de consolidación local

arcpy.env.workspace = ruta_bd_local
dataframe_interseccion = 'Interseccion_Municipio'

for capas in arcpy.ListFeatureClasses(feature_dataset=dataframe_interseccion):
    arcpy.Delete_management(capas)
    print("Se borra la capa {0}, alojada en el datafra {1}".format(capas, dataframe_interseccion))
    
for capas in arcpy.ListFeatureClasses():
    arcpy.Delete_management(capas)
    print("Se borra la capa {0} de la raiz de la BD".format(capas))
    
# ** Migración de capas a BD Local Temporal

for espacio_trabajo in rutas_workspace:
    arcpy.env.workspace = espacio_trabajo
    ruta_temporal = os.path.join(arcpy.env.workspace)
    division_directorios = os.path.split(ruta_temporal)[0]
    carpetas = division_directorios.split("\\")[5]
    categorizacion_tema = carpetas.split("_")[1]
    for capa in arcpy.ListFeatureClasses():
        if 'nivel' not in capa:
            capa_entrada = os.path.join(arcpy.env.workspace, capa)
            # Parametrizacion de temática en nombre de la capa
            ruta_archivos_a_local = os.path.join(ruta_bd_local, "_" + categorizacion_tema + "_" + capa)
            ruta_archivos_a_local = ruta_archivos_a_local.replace('__','_')
            arcpy.management.CopyFeatures(capa_entrada, ruta_archivos_a_local)
            print("Se migra la capa: {0}".format(capa)) 

# ** Paramtrización del código de departamento (DANE) por registro\capa

arcpy.env.workspace = ruta_bd_local

ruta_interseccion_mpio = os.path.join(arcpy.env.workspace, dataframe_interseccion + '\\')

if arcpy.Exists(ruta_interseccion_mpio):
    for capas in arcpy.ListFeatureClasses(feature_dataset=dataframe_interseccion):
        arcpy.management.Delete(capas)
        
for capa in arcpy.ListFeatureClasses():
    capa_intersect_salida = capa + "_Intersect_Mpio"
    if capa != '_6_1_Jurisdiccion_CAR':
        arcpy.management.RepairGeometry(capa)
        arcpy.analysis.Intersect([capa,"_6_1_Jurisdiccion_CAR"], os.path.join(ruta_bd_local, dataframe_interseccion, capa_intersect_salida))
        print("Se interseca la capa {0}, con -Jurisdiccion_CAR-".format(capa))
        
print("____________________ FINALIZA _2_PGAR_Construccion_Inventario ____________________")

# ? _3_1_Construccion_OtrosMetadatos

print("____________________ INICIA _3_1_Construccion_OtrosMetadatos ____________________")

# ** Carga de .csv con la información complementaria de los metadatos

df_otros_metadatos_insumo = pd.read_csv("otros_metadatos.csv", sep = ";")

# ** Filtro por capa estructurada según proceso de conversion GeoJSON - Feature Class

# El proceso de conversión a geojson ejecutado incorpora datos dentro del dataframe
df_otros_metadatos_insumo_filtro = df_otros_metadatos_insumo[df_otros_metadatos_insumo['nombre_capa'].str.slice(0, 1) == '_']

# ** Construcción de la Tabla Fuente

# Se parametrizan solo los campos necesarios
df_fuente_insumo = df_otros_metadatos_insumo_filtro.loc[:,'fuente']
df_fuente_insumo = pd.DataFrame(df_fuente_insumo)

# Se agrupan todas las fuentes registradas en el DF
df_grupo_fuentes = df_fuente_insumo.groupby(['fuente']).agg({'fuente':'count'})

# Se cambia el nombre de la columna -fuente-
df_grupo_fuentes.rename({'fuente': 'conteo_fuente'}, axis = 1, inplace = True)

# Reseteo índices
df_grupo_fuentes = df_grupo_fuentes.reset_index()

# Se cambia el nombre de la columna -fuente-
df_grupo_fuentes.rename({'fuente': 'nombre_fuente'}, axis = 1, inplace = True)

# Generación del campo incremental de acuerdo al número de capas
RID = []

# Se suma uno por el header dentro del data frame
for id_rid in range(1, df_grupo_fuentes.shape[0]+1):
    RID.append(id_rid)
 
# Se utiliza el método .loc para incorporar la columna, que en este caso fue la lista que se creo previamente   
df_grupo_fuentes.loc[:,'codigo_fuente'] = RID

# Parametrizo columnas finales del DF
df_fuentes = df_grupo_fuentes[['codigo_fuente','nombre_fuente']]

# Cambio del tipo de dato
df_fuentes['codigo_fuente'].astype('double')

# Ingreso registro para capas sin fuente
df_fuentes = df_fuentes.append({'codigo_fuente': 0, 'nombre_fuente':'Sin informacion'}, ignore_index=True)

# ** Esportada de DF a Feature Table

nombre_tabla_fuentes = 'tbl_fuentes'
ruta_bd = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"
ruta_tabla_fuentes = os.path.join(ruta_bd, nombre_tabla_fuentes)
df_fuentes.spatial.to_table(location=ruta_tabla_fuentes)
print("------------------------------ Se crea la tabla -tbl_fuentes- ------------------------------")

print("____________________ FINALIZA _3_1_Construccion_OtrosMetadatos ____________________")

# ? _3_2_PGAR_Construccion_Tabla_Capa

print("____________________ INICIA _3_2_PGAR_Construccion_Tabla_Capa ____________________")

# ** Creación de DataFrame para la unificación de la tabla -Capa-

df_unificacion_tabla_capa = pd.DataFrame(columns=['nombre_capa_final', 'codigo_tematica','CODDANE'])
print("---------------------------------------- Data frame creado ----------------------------------------")

# ** Generación de DataFrame Global Total con la unificación de las tres columnas principales

ruta_capas_w_municipio = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"

arcpy.env.workspace = ruta_capas_w_municipio

dataset_intersect = 'Interseccion_Municipio'

for capas_w_mpio in arcpy.ListFeatureClasses(feature_dataset = dataset_intersect):
    ruta_capas_w_mpio = os.path.join(ruta_capas_w_municipio,capas_w_mpio)
    capas_w_mpio = pd.DataFrame.spatial.from_featureclass(ruta_capas_w_mpio)
    capas_w_mpio_columnas_reducidas = capas_w_mpio.loc[:, ['nombre_capa_final','codigo_tematica','CODDANE']]
    df_unificacion_tabla_capa = df_unificacion_tabla_capa.append(capas_w_mpio_columnas_reducidas)
    
 # ** Generación del campo -Código Capa-
 
 # Agrupamiento, lo que en SQL es Group by
df_tabla_capa = df_unificacion_tabla_capa.groupby(['nombre_capa_final','codigo_tematica']).agg({'nombre_capa_final':'count', 'codigo_tematica':'count'})

# Generación del campo incremental de acuerdo al número de capas
codigo_capa = []

# Se suma uno por el header dentro del data frame
for numero_capas in range(1, df_tabla_capa.shape[0]+1):
    codigo_capa.append(numero_capas)
 
# Se utiliza el método .loc para incorporar la columna, que en este caso fue la lista que se creo previamente   
df_tabla_capa.loc[:,'codigo_capa'] = codigo_capa

# Se cambia el nombre de las columnas asociadas a los conteos (funcion -rename-)
df_tabla_capa.rename({'codigo_tematica':'conteo_tematica', 'nombre_capa_final': 'conteo_nombre_capa_final'}, axis = 1, inplace = True)

# Se resetan los índices
df_tabla_capa_completa = df_tabla_capa.reset_index()

# Se estandariza la tabla final
df_capa = df_tabla_capa_completa[['codigo_capa','nombre_capa_final','codigo_tematica']]

# ** Generación de Diccionario para parametrizar el -codigo_capa-

# Parametrización del diccionario de las capas
df_capa_parametrizacion_previa_diccionario = df_capa[['codigo_capa','nombre_capa_final']]

# Selección de nuevo índice
df_capa_parametrizacion_previa_diccionario = df_capa_parametrizacion_previa_diccionario.set_index('codigo_capa')

# Migración de Data Frame a Diccionario -función to_dict()-
diccionario_capas = df_capa_parametrizacion_previa_diccionario.to_dict()

# Modelado del diccionario tradicional
diccionario_capas_definitivo = diccionario_capas['nombre_capa_final']

# ** Actualización de cada capa intersecada con Municipio con su respectivo -codigo_capa-

nombre_campo_id_capa = 'codigo_capa'

for capas_w_mpio in arcpy.ListFeatureClasses(feature_dataset = dataset_intersect):
    if arcpy.ListFields(capas_w_mpio,nombre_campo_id_capa):
        print("El campo existe en la capa: {0}".format(capas_w_mpio))
    else:
        arcpy.management.AddField(capas_w_mpio, nombre_campo_id_capa, 'DOUBLE', field_alias = 'Codigo Capa')
        for llave, valor in diccionario_capas_definitivo.items():
            if capas_w_mpio == valor + '_Intersect_Mpio':
                arcpy.management.CalculateField(capas_w_mpio, nombre_campo_id_capa, llave, 'PYTHON3')
                print("Se actualiza el -Codigo de la Capa-, en el feature class: {0}".format(capas_w_mpio))

# ** Incorporación de columnas -codigo_fuente- y -fecha_ultima_actualizacion- a la tabla -tbl_capa-

# --- Carga Feature Table -tbl_fuentes- --
nombre_tabla_fuente = 'tbl_fuentes'
ruta_tabla_fuente = os.path.join(arcpy.env.workspace,nombre_tabla_fuente)
df_fuente = pd.DataFrame.spatial.from_table(ruta_tabla_fuente)

# --- Carga .csv con METADATOS --
df_otros_metadatos_insumo = pd.read_csv("otros_metadatos.csv", sep = ";")
df_otros_metadatos_insumo_filtro = df_otros_metadatos_insumo[df_otros_metadatos_insumo['nombre_capa'].str.slice(0, 1) == '_']

# Estrucuracion
df_fuente_insumo_estructurada = df_otros_metadatos_insumo_filtro.loc[:,['nombre_capa','ultima_actualizacion_reportada','fuente','descripcion_capa']]

# Primer JOIN: Busca acceder a la fecha de actualización y al nombre de la fuente
join_capa_metadato = pd.merge(df_capa, df_fuente_insumo_estructurada, how = 'left', left_on = 'nombre_capa_final', right_on = 'nombre_capa')

# Parametrización del DF
join_capa_metadato = join_capa_metadato.loc[:,['codigo_capa','nombre_capa_final','ultima_actualizacion_reportada','fuente','descripcion_capa','codigo_tematica']]

# Segundo JOIN: Busca acceder al código de la fuente
join_capa_fuente = pd.merge(join_capa_metadato, df_fuente, how = 'left', left_on = 'fuente', right_on = 'nombre_fuente')

# Parametrización del DF
join_capa_fuente = join_capa_fuente.loc[:, ['codigo_capa','nombre_capa_final','ultima_actualizacion_reportada','codigo_fuente','descripcion_capa','codigo_tematica']]

# Se cambian nombres de columnas
join_capa_fuente.rename({'nombre_capa_final': 'nombre_capa', 'ultima_actualizacion_reportada':'fecha_actualizacion_capa'}, axis = 1, inplace = True)

# Reemplazar por 0 todo NaN. Se usa la función fillna
join_capa_fuente['codigo_fuente'].fillna(0, inplace=True)

# Cambio código a entero
join_capa_fuente['codigo_fuente'] = join_capa_fuente['codigo_fuente'].astype('double')

# ** Exportar capa -tbl_capa- a FileGDB

nombre_tabla_capa = 'tbl_capa'
ruta_salida_tabla_capa = os.path.join(arcpy.env.workspace, nombre_tabla_capa)
join_capa_fuente.spatial.to_table(location = ruta_salida_tabla_capa)

print("____________________ FINALIZA _3_2_PGAR_Construccion_Tabla_Capa ____________________")

# ? _4_PGAR_Construccion_Direccion_Municipio

print("____________________ INICIA _4_PGAR_Construccion_Direccion_Municipio ____________________")

# ** Modificación de la capa -Jurisdicción- a Municipio

ruta_capa_jurisdiccion = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\_6_1_Jurisdiccion_CAR"
ruta_capa_geocodificacion = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\_6_2_Geocodificacion_Regionales"

# ? --- PREPARACIÓN DIRECCIÓN ---
df_direccion = pd.DataFrame.spatial.from_featureclass(ruta_capa_jurisdiccion)
# Se implementa .loc para evitar alertas en la modificación del dataframe
df_direccion_columnas_estandarizadas = df_direccion.loc[:,['Direccion']]
df_direccion_columnas_estandarizadas.rename({'Direccion':'nombre_direccion'}, axis = 1, inplace = True)
# Transformación de registros de mayúsculas a letra capital, esto por medio de la función capitalize del método str.
df_direccion_columnas_estandarizadas['nombre_direccion'] = df_direccion_columnas_estandarizadas['nombre_direccion'].str.capitalize()

# ** Generacion de DF, geocodificacion de regionales
df_geocodificacion = pd.DataFrame.spatial.from_featureclass(ruta_capa_geocodificacion)

# ? --- PREPARACIÓN MUNICIPIO ---
df_jurisdiccion = pd.DataFrame.spatial.from_featureclass(ruta_capa_jurisdiccion)
# Se implementa .loc para evitar alertas en la modificación del dataframe
df_jurisdiccion_columnas_estandarizadas = df_jurisdiccion.loc[:,['OBJECTID','Municipio','CODDANE','Departamen','Direccion','SHAPE']]
df_jurisdiccion_columnas_estandarizadas.rename({'OBJECTID':'codigo_municipio', 'Municipio':'nombre_municipio','CODDANE':'codigo_municipio_dane','Departamen':'nombre_departamento'}, axis = 1, inplace = True)
# Transformación de registros de mayúsculas a letra capital, esto por medio de la función capitalize del método str.
df_jurisdiccion_columnas_estandarizadas['nombre_municipio'] = df_jurisdiccion_columnas_estandarizadas['nombre_municipio'].str.capitalize()
df_jurisdiccion_columnas_estandarizadas['nombre_departamento'] = df_jurisdiccion_columnas_estandarizadas['nombre_departamento'].str.capitalize()
df_jurisdiccion_columnas_estandarizadas['Direccion'] = df_jurisdiccion_columnas_estandarizadas['Direccion'].str.capitalize()

# ** Preparación tabla -Direccion-

df_direccion_columnas_agrupadas = df_direccion_columnas_estandarizadas.groupby(['nombre_direccion']).agg({'nombre_direccion':'count'})

# Generación del campo incremental de acuerdo al número de capas
codigo_direccion = []

# Se suma uno por el header dentro del data frame
for numero_direcciones in range(1, df_direccion_columnas_agrupadas.shape[0]+1):
    codigo_direccion.append(numero_direcciones)
 
# Se utiliza el método .loc para incorporar la columna, que en este caso fue la lista que se creo previamente   
df_direccion_columnas_agrupadas.loc[:,'codigo_direccion'] = codigo_direccion

# Se cambia el nombre de las columnas asociadas a los conteos (funcion -rename-)
df_direccion_columnas_agrupadas.rename({'nombre_direccion':'conteo_nombres_direcciones'}, axis = 1, inplace = True)

# Se resetan los índices
df_tabla_direccion_completa = df_direccion_columnas_agrupadas.reset_index()

# Se estandariza la tabla final
df_direccion = df_tabla_direccion_completa[['codigo_direccion','nombre_direccion']]

# Merge de tabla dirección alfanumérica con su respectiva coordenada
df_unificado_geo = pd.merge(df_geocodificacion, df_direccion, how='inner',left_on='nombre_direccion', right_on='nombre_direccion')

# ** Preparación para salida final
df_direccion_final = df_unificado_geo.loc[:,['codigo_direccion','nombre_direccion','direccion','latlong','SHAPE']]

# ** Creación y registro del campo -codigo_departamento-

# Se utiliza el método .loc para incorporar la columna, que en este caso fue la lista que se creo previamente
# La columna creada se le registran los datos haciendo un substring a la columna -codigo_municipio-  
df_jurisdiccion_columnas_estandarizadas.loc[:,'codigo_departamento'] = df_jurisdiccion_columnas_estandarizadas['codigo_municipio_dane'].str.slice(0, 2)

# ** Incorporación del campo -codigo_direccion- en la capa -Municipio-

# Ejecución de un inner join sin where en ningún campo
df_tabla_municipio = pd.merge(df_jurisdiccion_columnas_estandarizadas, df_direccion, how='inner',left_on='Direccion', right_on='nombre_direccion')
df_tabla_municipio_estandarizado = df_tabla_municipio.loc[:,['codigo_municipio','codigo_municipio_dane','nombre_municipio','codigo_departamento', 'codigo_direccion','SHAPE']]

# ** Exportar DF a Feature Class

ruta_bd = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"

# --- PREPARACIÓN DIRECCION ---
nombre_tabla_direccion = 'direccion'
ruta_capa_direccion = os.path.join(ruta_bd, nombre_tabla_direccion)
df_direccion_final.spatial.to_featureclass(location=ruta_capa_direccion)
print("------------------------------ Se crea la capa -direccion- ------------------------------")

# --- PREPARACIÓN MUNICIPIO ---
nombre_capa_municipio = 'municipio_dissolve'
ruta_capa_municipio = os.path.join(ruta_bd, nombre_capa_municipio)
df_tabla_municipio_estandarizado.spatial.to_featureclass(location=ruta_capa_municipio)
print("------------------------------ Se crea la capa -municipio dissolve- ------------------------------")

# ** Dissolve Municipio

capa_municipio_dissolve = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\municipio_dissolve"
nombre_capa_salida_municipio = 'municipio'
ruta_capa_salida = os.path.join(ruta_bd,nombre_capa_salida_municipio)

arcpy.management.Dissolve(capa_municipio_dissolve, ruta_capa_salida, ['codigo_municipio', 'codigo_municipio_dane', 'nombre_municipio', 'codigo_departamento','codigo_direccion'], multi_part = 'MULTI_PART')
print("--------------- Capa Municipio Disuelta ----------------")

print("____________________ FINALIZA _4_PGAR_Construccion_Direccion_Municipio ____________________")

# ? _5_PGAR_Construccion_Tabla_r_Capa_Municipio

print("____________________ INICIA _5_PGAR_Construccion_Tabla_r_Capa_Municipio ____________________")

# ** Corrección capas asociadas al temario Código 12: Avenida Torrencial

ruta_capas_w_municipio = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"

arcpy.env.workspace = ruta_capas_w_municipio

dataset_intersect = 'Interseccion_Municipio'
columna_remover = 'Municipio_1'

for capas_w_mpio in arcpy.ListFeatureClasses(feature_dataset = dataset_intersect):
    if arcpy.ListFields(capas_w_mpio,columna_remover):
        arcpy.management.DeleteField(capas_w_mpio, 'Municipio')
        arcpy.management.AlterField(capas_w_mpio, 'Municipio_1', 'Municipio')
        print("Se borra y actualiza el campo -Municipio- en la capa: {0}".format(capas_w_mpio))        
    else:       
        print("La capa {0} no cuenta con una columna -Municipio_1-".format(capas_w_mpio))  
        
# ** Creación de DataFrame para la unificación de la tabla -Relacion_Capa_Municipio-

df_unificacion_tabla_capa_municipio = pd.DataFrame(columns=['codigo_capa','CODDANE','Municipio'])
print("---------------------------------------- Data frame creado ----------------------------------------")

# ** Generación de DataFrame Global Total con la unificación de dos columnas principales

columna_analisis = 'Municipio'

for capas_w_mpio in arcpy.ListFeatureClasses(feature_dataset = dataset_intersect):
    if arcpy.ListFields(capas_w_mpio,columna_analisis):
        ruta_capas_w_mpio = os.path.join(ruta_capas_w_municipio, dataset_intersect, capas_w_mpio)
        df_capas_w_mpio = pd.DataFrame.spatial.from_featureclass(ruta_capas_w_mpio)
        capas_w_mpio_columnas_reducidas = df_capas_w_mpio.loc[:, ['codigo_capa','CODDANE','Municipio']]
        df_unificacion_tabla_capa_municipio = df_unificacion_tabla_capa_municipio.append(capas_w_mpio_columnas_reducidas)
        print("Se migra a DF: {0}".format(capas_w_mpio))
    else:
        print("La capa {0} no cuenta con la columna {1}, por lo cual no se adiciona al DF".format(capas_w_mpio,columna_analisis))
        
# ** Lectura de la tabla previa -municipio-

capa_municipio = r'D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\municipio'
df_municipio = pd.DataFrame.spatial.from_featureclass(capa_municipio)

# ** Unificación Tabla -relación_capa_municipio-

# Agrupamiento, lo que en SQL es Group by
df_tabla_capa = df_unificacion_tabla_capa_municipio.groupby(['codigo_capa','CODDANE','Municipio']).agg({'codigo_capa':'count', 'CODDANE':'count', 'Municipio':'count'})

# Se cambia el nombre de las columnas asociadas a los conteos (funcion -rename-)
df_tabla_capa.rename({'codigo_capa':'conteo_capa', 'CODDANE': 'conteo_CODDANE', 'Municipio':'conteo_municipio'}, axis = 1, inplace = True)

# Se resetan los índices
df_tabla_capa = df_tabla_capa.reset_index()

# Se cambia el nombre de la columna -CODDANE-
df_tabla_capa.rename({'CODDANE': 'codigo_municipio'}, axis = 1, inplace = True)

# Cambio de tipo de letra a -capitalize-
df_tabla_capa['Municipio'] = df_tabla_capa['Municipio'].str.capitalize()

# Se realiza la unión con la tabla -Municipio-
join_municipio = pd.merge(df_tabla_capa, df_municipio, how = 'inner', left_on = ['Municipio','codigo_municipio'], right_on = ['nombre_municipio','codigo_municipio_dane'])

# Estandarización de tabla
join_municipio = join_municipio[['codigo_municipio_y','codigo_capa']]

# Cambio de nombre al código de municipio
join_municipio.rename({'codigo_municipio_y': 'codigo_municipio'}, axis = 1, inplace = True)

# Generación del campo incremental de acuerdo al número de capas
RID = []

# Se suma uno por el header dentro del data frame
for id_rid in range(1, join_municipio.shape[0]+1):
    RID.append(id_rid)
 
# Se utiliza el método .loc para incorporar la columna, que en este caso fue la lista que se creo previamente   
join_municipio.loc[:,'RID'] = RID

# Se estandariza la tabla final
df_r_capa_municipio = join_municipio[['codigo_capa','codigo_municipio','RID']]
df_r_capa_municipio['codigo_capa'] = df_r_capa_municipio.loc[:,['codigo_capa']].astype('int')
df_r_capa_municipio['codigo_municipio'] = df_r_capa_municipio.loc[:,['codigo_municipio']].astype('int')

# ** Exportado a .csv de la capa que relaciona -tbl_capa- con -municipio-

nombre_csv_capa_municipio = 'r_municipio_capa.csv'
df_r_capa_municipio.to_csv(nombre_csv_capa_municipio, index = False, encoding = 'UTF-8')

print("____________________ FINALIZA _5_PGAR_Construccion_Tabla_r_Capa_Municipio ____________________")

# ? _6_PGAR_Construccion_Capa_Cuenca

print("____________________ INICIA _6_PGAR_Construccion_Capa_Cuenca ____________________")

# ** Modificación de la capa -Cuenca Escala 1:25.000- a cuenca

ruta_capa_cuenca = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\_3_2_Cuencas_escala_1_25000_CAR"

df_cuenca = pd.DataFrame.spatial.from_featureclass(ruta_capa_cuenca)
# Se implementa .loc para evitar alertas en la modificación del dataframe
df_cuenca_columnas_estandarizadas = df_cuenca.loc[:,['Codigo','AreaHidrografica','ZonaHidrografica','SubZonaHidrografica','NombreCuenca','POMCA','SHAPE']]

df_cuenca_columnas_estandarizadas.rename({'Codigo':'codigo_cuenca',
                                          'AreaHidrografica':'area_hidrografica',
                                          'ZonaHidrografica':'zona_hidrografica',
                                          'SubZonaHidrografica':'subzona_hidrografica',
                                          'NombreCuenca':'nombre_cuenca',
                                          'POMCA':'POMCA'}, axis = 1, inplace = True)

# Se reemplaza el caracter - por _ en los códigos de las cuencas
df_cuenca_columnas_estandarizadas.loc[:, 'codigo_cuenca'] = df_cuenca_columnas_estandarizadas.loc[:,'codigo_cuenca'].str.replace('-', '_')

# ** Exportar DF a Feature Class

nombre_capa_cuenca = 'cuenca'
ruta_bd = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"
ruta_capa_cuenca = os.path.join(ruta_bd, nombre_capa_cuenca)
df_cuenca_columnas_estandarizadas.spatial.to_featureclass(location=ruta_capa_cuenca)
print("------------------------------ Se crea la capa -cuenca- ------------------------------")

print("____________________ FINALIZA _6_PGAR_Construccion_Capa_Cuenca ____________________")

# ? _7_PGAR_Construccion_r_Municipio_Cuenca

print("____________________ INICIA _7_PGAR_Construccion_r_Municipio_Cuenca ____________________")

# ** Generación del DF

ruta_capa_municipio_cuenca = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\Interseccion_Municipio\_3_2_Cuencas_escala_1_25000_CAR_Intersect_Mpio"

df_municipio_cuenca = pd.DataFrame.spatial.from_featureclass(ruta_capa_municipio_cuenca)

# ** Preparación de nueva llave principal para la capa Municipio (dificultad 11001, Bogotá Urbana-Rural)

capa_municipio = r'D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\municipio'
df_municipio = pd.DataFrame.spatial.from_featureclass(capa_municipio)

tabla_direccion = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\tbl_direccion"
df_direccion = pd.DataFrame.spatial.from_table(tabla_direccion)

join_municipio_direccion = pd.merge(df_municipio, df_direccion, how='inner',left_on='codigo_direccion', right_on='codigo_direccion')

# ** Unificación Tabla -relación_capa_municipio-

# Agrupamiento, lo que en SQL es Group by
df_tabla_cuenca = df_municipio_cuenca.groupby(['Codigo','CODDANE','Direccion']).agg({'Codigo':'count', 'CODDANE':'count','Direccion':'count'})

# Se cambia el nombre de las columnas asociadas a los conteos (funcion -rename-)
df_tabla_cuenca.rename({'Codigo':'conteo_codigo', 'CODDANE': 'conteo_CODDANE','Direccion':'conteo_Direccion'}, axis = 1, inplace = True)

# # Se resetan los índices
df_tabla_cuenca = df_tabla_cuenca.reset_index()

# Se cambia el nombre de la columna -CODDANE-
df_tabla_cuenca.rename({'CODDANE': 'codigo_municipio_dane', 'Codigo':'codigo_cuenca'}, axis = 1, inplace = True)

#Cambio de tipo de letra a la columna -Direccion-
df_tabla_cuenca['Direccion'] = df_tabla_cuenca['Direccion'].str.capitalize()

df_tabla_cuenca = df_tabla_cuenca[['codigo_cuenca', 'codigo_municipio_dane', 'Direccion']]

# Join para traer OBJECTID de la capa Municipio como llave principal para la relación
# Join comparando dos campos
df_nuevo_codigo = pd.merge(df_tabla_cuenca, join_municipio_direccion, how='inner',left_on=['Direccion','codigo_municipio_dane'], right_on=['nombre_direccion','codigo_municipio_dane'])

# Generación del campo incremental de acuerdo al número de capas
RID = []

# Se suma uno por el header dentro del data frame
for id_rid in range(1, df_nuevo_codigo.shape[0]+1):
    RID.append(id_rid)
 
# Se utiliza el método .loc para incorporar la columna, que en este caso fue la lista que se creo previamente   
df_nuevo_codigo.loc[:,'RID'] = RID

# Reselección de campos
df_tabla_cuenca_estandarizada = df_nuevo_codigo.loc[:, ['codigo_cuenca','codigo_municipio','RID']]

# Se estandariza la tabla final
df_r_municipio_cuenca = df_tabla_cuenca_estandarizada[['codigo_cuenca','codigo_municipio','RID']]

# Se reemplaza el caracter - por _ en los códigos de las cuencas
df_r_municipio_cuenca.loc[:, 'codigo_cuenca'] = df_r_municipio_cuenca.loc[:,'codigo_cuenca'].str.replace('-', '_')
df_r_municipio_cuenca['codigo_municipio'] = df_r_municipio_cuenca.loc[:,['codigo_municipio']].astype('int')

# ** Exportado a .csv de la capa que relaciona -cuenca- con -municipio-

nombre_csv_municipio_cuenca = 'r_municipio_cuenca.csv'
df_r_municipio_cuenca.to_csv(nombre_csv_municipio_cuenca, index = False, encoding = 'UTF-8')
print("------------------------------- Se exporta el .csv: -r_municipio_cuenca- -------------------------------")

print("____________________ FINALIZA _7_PGAR_Construccion_r_Municipio_Cuenca ____________________")

# ? _8_PGAR_Construccion_Tabla_Departamento

print("____________________ INICIA _8_PGAR_Construccion_Tabla_Departamento ____________________")

ruta_capa_jurisdiccion = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\_6_1_Jurisdiccion_CAR"

df_jurisdiccion = pd.DataFrame.spatial.from_featureclass(ruta_capa_jurisdiccion)
# Se implementa .loc para evitar alertas en la modificación del dataframe
df_jurisdiccion_columnas_estandarizadas = df_jurisdiccion.loc[:,['CODDANE','Departamen']]
df_jurisdiccion_columnas_estandarizadas.rename({'CODDANE':'codigo_municipio','Departamen':'nombre_departamento'}, axis = 1, inplace = True)
# Transformación de registros de mayúsculas a letra capital, esto por medio de la función capitalize del método str.
df_jurisdiccion_columnas_estandarizadas['nombre_departamento'] = df_jurisdiccion_columnas_estandarizadas['nombre_departamento'].str.capitalize()

# Se utiliza el método .loc para incorporar la columna, que en este caso fue la lista que se creo previamente
# La columna creada se le registran los datos haciendo un substring a la columna -codigo_municipio-  
df_jurisdiccion_columnas_estandarizadas.loc[:,'codigo_departamento'] = df_jurisdiccion_columnas_estandarizadas['codigo_municipio'].str.slice(0, 2)
df_jurisdiccion_columnas_estandarizadas = df_jurisdiccion_columnas_estandarizadas.loc[:,['codigo_departamento','nombre_departamento']]

df_departamentos_unificados = df_jurisdiccion_columnas_estandarizadas.groupby(['codigo_departamento','nombre_departamento']).agg({'codigo_departamento':'count', 'nombre_departamento':'count'})

# Se cambia el nombre de las columnas asociadas a los conteos (funcion -rename-)
df_departamentos_unificados.rename({'codigo_departamento':'conteo_codigo_departamento', 'nombre_departamento':'conteo_nombre_departamento'}, axis = 1, inplace = True)

# Se resetan los índices
df_departamentos_unificados_completa = df_departamentos_unificados.reset_index()

# Se estandariza la tabla final
df_departamentos = df_departamentos_unificados_completa[['codigo_departamento','nombre_departamento']]

ruta_bd = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"

# --- PREPARACIÓN DEPARTAMENTO ---
nombre_capa_departamento = 'tbl_departamento'
ruta_capa_departamento = os.path.join(ruta_bd, nombre_capa_departamento)
df_departamentos.spatial.to_table(location=ruta_capa_departamento)
print("------------------------------ Se crea la capa -tbl_departamento- ------------------------------")

print("____________________ FINALIZA _8_PGAR_Construccion_Tabla_Departamento ____________________")

# ? _9_PGAR_Estandarizacion_Capas_Registros

print("____________________ INICIA _9_PGAR_Estandarizacion_Capas_Registros ____________________")

# ** Generación de DF

ruta_bd = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"
ruta_capa = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\tbl_capa"

# Construcción del diccionario a partir de la tabla: Capa
df_capa = pd.DataFrame.spatial.from_table(ruta_capa)
df_capa_to_dict = df_capa.loc[:,['codigo_capa','nombre_capa']]
df_capa_to_dict = df_capa_to_dict.set_index('codigo_capa')
diccionario_capa = df_capa_to_dict.to_dict()

# Modelado del diccionario tradicional
diccionario_capas_definitivo = diccionario_capa['nombre_capa']

# ** Actualización de cada capa -registros- con el -codigo_capa-

arcpy.env.workspace = ruta_bd
nombre_campo_codigo_capa = 'codigo_capa'

capas_modelo = ['tbl_capa', 'tbl_departamento', 'tbl_tematica', 'tbl_direccion', 'municipio', 'cuenca']

for elemento in arcpy.ListFeatureClasses():
    for capa_a_no_actualizar in capas_modelo:
        if elemento != capa_a_no_actualizar:
            # Aquí se puede modificar el tipo de campo para el -codigo_capa-
            arcpy.management.AddField(elemento, nombre_campo_codigo_capa, 'LONG', field_alias = 'Codigo Capa')
            for llave, valor in diccionario_capas_definitivo.items():
                if elemento == valor:
                    arcpy.management.CalculateField(elemento, nombre_campo_codigo_capa, int(llave), 'PYTHON3')
                    print("Se actualiza el campo -codigo_capa-, para la capa {0}".format(valor))
        else:
            print("La capa no se actualiza al ser {0}".format(capa_a_no_actualizar))
            
# ** Borrado de campos innecesarios, capas de registros

campos_eliminar = ['nombre_capa','codigo_tematica','nombre_capa']
codigo_capa = "codigo_capa"

for elemento in arcpy.ListFeatureClasses():
    for columnas in arcpy.ListFields(elemento):
        for i in campos_eliminar:
            if i == columnas.name:
                arcpy.management.DeleteField(elemento, i)
                print("Se elimina la columna {0}, de la capa {1}".format(elemento, columnas.name))
                
for elemento in arcpy.ListFeatureClasses():
    if elemento == 'cuenca':
        if arcpy.ListFields(elemento, codigo_capa):
            arcpy.management.DeleteField(elemento, codigo_capa)
            print("Se elimina la columna {0}, de la capa {1}".format(codigo_capa, elemento))

print("____________________ FINALIZA _9_PGAR_Estandarizacion_Capas_Registros ____________________")

# # ? _10_PGAR_Modelo_Inventario

print("____________________ INICIA _10_PGAR_Modelo_Inventario ____________________")

# ** Gestión de BD

arcpy.env.workspace = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR"
ruta_gdb_inventario = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb"

if arcpy.Exists(ruta_gdb_inventario):
    print("------ La BD SDE PGAR_Inventario Existe ------")
else:
    print("------ Pendiente por definir gestión ------")
    
# ** Gestión de Datasets

ruta_tbl_tematica = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\tbl_tematica"
sistema_referencia_inventario = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb\municipio"
arcpy.env.workspace = ruta_gdb_inventario

lista_tematica = []

# Se usa la función SearchCursor para navegar por la tabla alojada en BD
# En este caso no se utiliza un filtro where sql
with arcpy.da.SearchCursor(ruta_tbl_tematica,"nombre_tematica") as cursor:
    for i in cursor:
        if i[0] != '_6_1_Jurisdiccion_CAR':
            lista_tematica.append(i[0])

for nuevos_dataset in arcpy.ListDatasets():
    arcpy.Delete_management(nuevos_dataset)
    print("Se borran los nuevos datasets, entre ellos {0}".format(nuevos_dataset))
 
for dataset in lista_tematica:
    ruta_dataset = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb" + "\\" + dataset
    if arcpy.Exists(ruta_dataset):
        print("El Feature DataFrame {0}, existe".format(dataset))
        for capa in arcpy.ListFeatureClasses(feature_dataset=dataset):
            arcpy.Delete_management(capa)
            print(" - Capa {0} borrada".format(capa))
    else:
        arcpy.management.CreateFeatureDataset(ruta_gdb_inventario, dataset, sistema_referencia_inventario)
        print("Se crea el Feature DataFrame {0}".format(dataset))
        
for capa in arcpy.ListFeatureClasses():
    arcpy.Delete_management(capa)
    print(" - Capa {0} borrada".format(capa))
    
for tabla in arcpy.ListTables():
    arcpy.Delete_management(tabla)
    print(" - Tabla {0} borrada".format(tabla))
    
# ** Migración de registros .gdb - .sde

ruta_origen = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\Local_BD_PGAR.gdb"
arcpy.env.workspace = ruta_origen
lista_capas_no_exentas = []
lista_capas_exentas = []

# Listar capas NO excluidas de la copia a FDF
for capas_no_exentas in arcpy.ListFeatureClasses():
    if "_" in capas_no_exentas and '_6_1_Jurisdiccion_CAR' not in capas_no_exentas:
        lista_capas_no_exentas.append(capas_no_exentas)
        # print("La capa o tabla {0} NO se migra".format(capas_exentas))
    else: 
        print("La capa {0} se migra".format(capas_no_exentas))

# Listar capas NO excluidas de la copia a FDF
for capas_exentas in arcpy.ListFeatureClasses():
    if "_" not in capas_exentas:
        lista_capas_exentas.append(capas_exentas)
        print("La capa o tabla {0} NO se migra".format(capas_exentas))
    # else: 
    #     print("La capa {0} se migra".format(capas_exentas))          

# Lista de rutas con todas las capas a migrar
ruta_capas = []
for capas in arcpy.ListFeatureClasses():
    ruta_capa = os.path.join(arcpy.env.workspace,capas)
    ruta_capas.append(ruta_capa)
    
# Migración de capas al Feature DataFrame correspondiente
for i in arcpy.ListFeatureClasses():
    for r in lista_capas_no_exentas:
        if (i == r):
            for j in lista_tematica:
                if (i.split("_")[1] == j.split("_")[1]):
                    capa_origen = os.path.join(arcpy.env.workspace, i)
                    capa_destino = os.path.join(ruta_gdb_inventario, j, i)
                    arcpy.management.CopyFeatures(capa_origen, capa_destino)
                    print("La capa {0}, se ha migrado al FDF {1} de la BD GDB".format(i,j))
    for y in lista_capas_exentas:
        if (i == y):
            capa_origen = os.path.join(arcpy.env.workspace, i)
            capa_destino = os.path.join(ruta_gdb_inventario, i)
            arcpy.management.CopyFeatures(capa_origen, capa_destino)
            print("La capa {0} se ha migrado BD GDB".format(i))

# Migración de tablas con prefijo -tbl-
for tablas in arcpy.ListTables():
    if "tbl" in tablas:
        capa_origen = os.path.join(arcpy.env.workspace, tablas)
        capa_destino = os.path.join(ruta_gdb_inventario, tablas)
        arcpy.management.Copy(capa_origen, capa_destino)
        print("La tabla {0} se ha migrado BD GDB".format(tablas))
        
# ** Paramtrización capas que tienen el mismo nombre

arcpy.env.workspace = ruta_gdb_inventario

nombre_dataset = ['_10_Analisis_Vulnerabilidad_Riesgo_Inundacion',
           '_11_Analisis_Vulnerabilidad_Riesgo_Incendio',
           '_12_Analisis_Vulnerabilidad_Riesgo_Avenida_Torrencial',
           '_13_Analisis_Vulnerabilidad_Riesgo_Remocion_Masa']

for dataset in arcpy.ListDatasets():
    for seleccion_dataset in nombre_dataset:
        if dataset == seleccion_dataset:
            for capa in arcpy.ListFeatureClasses(feature_dataset=dataset):
                if '_10_' in capa:
                    arcpy.management.Rename(capa, capa + '_Inundacion')
                elif '_11_' in capa:
                    arcpy.management.Rename(capa, capa + '_Incendio')
                elif '_12_' in capa:
                    arcpy.management.Rename(capa, capa + '_Avenida_Torrencial')
                elif '_13_' in capa:
                    arcpy.management.Rename(capa, capa + '_Remocion_Masa')
                else:
                    print("No se localiza la capa dentro del listado disponible")   

# ** Renombrado de capas
for dataset in lista_tematica:
    for capas in arcpy.ListFeatureClasses(feature_dataset=dataset):      
        if ("_" in capas[0]) and ("_" in capas[2]) and ("_" in capas[4]): # !! _1_4_
            arcpy.management.Rename(capas, capas[5:])
            print("Segunda modificación exitosa: {0}".format(capas))
            print(capas[5:])
        elif ("_" in capas[0]) and ("_" in capas[2]) and ("_" in capas[5]): # !! _1_15_
            arcpy.management.Rename(capas, capas[6:])
            print("Tercera modificación exitosa: {0}".format(capas))
        elif ("_" in capas[0]) and ("_" in capas[3]) and ("_" in capas[5]): # !! _12_1_
            arcpy.management.Rename(capas, capas[6:])
            print("Cuarta modificación exitosa: {0}".format(capas))
        elif ("_" in capas[0]) and ("_" in capas[3]) and ("_" in capas[6]): # !! _10_12_
            arcpy.management.Rename(capas, capas[7:])
            print("Quinta modificación exitosa: {0}".format(capas))
        else:
            print("No se renomabra la capa {0}".format(capas))
            
for dataset in lista_tematica:
    for capas in arcpy.ListFeatureClasses(feature_dataset=dataset):
        if ("_" in capas[0]) and ("_" in capas[3]): # !! _10_
            arcpy.management.Rename(capas, capas[4:])
            print("Primera modificación exitosa: {0}".format(capas)) 
            
print("--------------- Finaliza cambio de nombres de las capas ----------------")

# ** Renombrado de datasets

for dataset in arcpy.ListDatasets():
    if ("_" in dataset[0]) and ("_" in dataset[2]): # !! _1_
            arcpy.management.Rename(dataset, dataset[3:])
            print("Primera modificación exitosa: {0}".format(dataset))
    elif ("_" in dataset[0]) and ("_" in dataset[3]): # !! _10_
            arcpy.management.Rename(dataset, dataset[4:])
            print("Segunda modificación exitosa: {0}".format(dataset))
    else:
        print("No se renomabra Feature Dataset {0}".format(dataset))

print("--------------- Finaliza cambio de nombres de Features Datasets ----------------")
print("____________________ FINALIZA _10_PGAR_Modelo_Inventario ____________________")

# ? _11_1_PGAR_AnalisisCapasAVR

print("____________________ INICIA _11_1_PGAR_AnalisisCapasAVR ____________________")

ruta_bd = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb"
arcpy.env.workspace = ruta_bd

capa_riego_rural = ['Riesgo_Urbano_Inundacion','Riesgo_Rural_Incendio','Riesgo_Rural_Remocion_Masa']
campos_actualizar = ['Riesgo']
nombre_dataset = ['Analisis_Vulnerabilidad_Riesgo_Inundacion',
           'Analisis_Vulnerabilidad_Riesgo_Incendio',
           'Analisis_Vulnerabilidad_Riesgo_Remocion_Masa']

for dataset in arcpy.ListDatasets():
    for seleccion_dataset in nombre_dataset:
        if dataset == seleccion_dataset:
            for capa in arcpy.ListFeatureClasses(feature_dataset=dataset):
                for seleccion_capa in capa_riego_rural:
                    if capa == seleccion_capa:
                        with arcpy.da.UpdateCursor(capa, campos_actualizar) as cursor:
                            for fila in cursor:
                                if fila[0] == 'Muy Alto':
                                    fila[0] = 'Muy alto'
                                elif fila[0] == 'Muy Bajo':
                                    fila[0] = 'Muy bajo'
                                elif fila[0] == 'Alta':
                                    fila[0] = 'Alto'
                                elif fila[0] == 'Baja':
                                    fila[0] = 'Bajo'
                                elif fila[0] == 'Media':
                                    fila[0] = 'Medio'
                                elif fila[0] == 'Riesgo Alto':
                                    fila[0] = 'Alto'
                                elif fila[0] == 'Riesgo Medio':
                                    fila[0] = 'Medio'
                                elif fila[0] == 'Riesgo Bajo':
                                    fila[0] = 'Bajo'
                                elif fila[0] == None:
                                    fila[0] = 'Sin información'
                                else:
                                    print("No se ejecuta cambio")                            
                                # ? Se actualiza el cursor con la actualización de la lista anterior
                                cursor.updateRow(fila)

# Generación de DF
df_variables_economicas_cundinamarca = pd.read_csv("Variables_Economicas_Cundinamarca_DANE.csv", sep=";")

# !! Primer Tratamiento
df_variables_economicas_cundinamarca['codigo_municipio_dane'] = df_variables_economicas_cundinamarca.loc[:,['codigo_municipio_dane']].astype('str')

# Migración a Feature Table
nombre_tabla_variables_economicas = "tbl_variables_economicas_dane"
ruta_salida_variables_economicas = os.path.join(arcpy.env.workspace, nombre_tabla_variables_economicas)
df_variables_economicas_cundinamarca.spatial.to_table(location = ruta_salida_variables_economicas)

# Creación de la relación entre Municipio Vs Variables Económicas
r_municipio_variables = "r_municipio_variables"
capa_municipio = "municipio"

# ********************** Relación Capa - Temática **********************
ruta_municipio = os.path.join(arcpy.env.workspace, capa_municipio)

arcpy.management.CreateRelationshipClass(ruta_municipio, ruta_salida_variables_economicas, r_municipio_variables, 'SIMPLE', 'variable', 'municipio', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_municipio_dane', 'codigo_municipio_dane')
print("Creada relación: {0}".format(r_municipio_variables))

# ** CREACIÓN POBLACION

df_poblacion_car = pd.read_csv("poblacion_car.csv", sep=";")

# !! Tratamiento
df_poblacion_car['codigo_municipio'] = df_poblacion_car.loc[:,['codigo_municipio']].astype('str')

# Migración a Feature Table
nombre_poblacion_car = "tbl_poblacion_car"
ruta_salida_poblacion_car = os.path.join(arcpy.env.workspace, nombre_poblacion_car)
df_poblacion_car.spatial.to_table(location = ruta_salida_poblacion_car)

# Creación de la relación entre Municipio Vs Variables Económicas
r_municipio_poblacion = "r_municipio_poblacion"

# ********************** Relación Capa - Temática **********************
ruta_municipio = os.path.join(arcpy.env.workspace, capa_municipio)

arcpy.management.CreateRelationshipClass(ruta_municipio, ruta_salida_poblacion_car, r_municipio_poblacion, 'SIMPLE', 'poblacion', 'municipio', 
                                         "NONE", 'ONE_TO_ONE', "NONE", 'codigo_municipio_dane', 'codigo_municipio')
print("Creada relación: {0}".format(r_municipio_poblacion))

print("____________________ FINALIZA _11_1_PGAR_AnalisisCapasAVR ____________________")

# ? _12_PGAR_Migracion_A_SDE

print("____________________ INICIA _12_PGAR_Migracion_A_SDE ____________________")

# ** Borrado de capas, tablas y relaciones en la SDE

ruta_sde = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde"
arcpy.env.workspace = ruta_sde
# Listas
dataframes = arcpy.ListDatasets()
capas = arcpy.ListFeatureClasses()
tablas = arcpy.ListTables()

for dataframe in dataframes:
    arcpy.Delete_management(dataframe)
    print("Se borra dataframe {0}".format(dataframe))
    
for capas in capas:
    arcpy.Delete_management(capas)
    print("Se borra tabla {0}".format(capas))
    
for tabla in tablas:
    arcpy.Delete_management(tabla)
    print("Se borra capa {0}".format(tabla))
    
ruta_filegdb = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb"
arcpy.env.workspace = ruta_filegdb

# ? Listado de datasets
lista_datasets = []
for dataset in arcpy.ListDatasets():
    lista_datasets.append(dataset)
    
# ? Almacenamiento de rutas de cada una de las capas que se copiaran a base de datos .sde
# # ** Features into Dataset
listado_rutas_capas_into_dataset = []
for dataset in arcpy.ListDatasets():
    for capas in arcpy.ListFeatureClasses(feature_dataset=dataset):
        ruta_capas_i_ds = os.path.join(ruta_filegdb,dataset,capas)
        listado_rutas_capas_into_dataset.append(ruta_capas_i_ds)

# # ** Features out Dataset
listado_rutas_capas_out_dataset = []
for capas in arcpy.ListFeatureClasses():
    ruta_capas_o_ds = os.path.join(ruta_filegdb,capas)
    listado_rutas_capas_out_dataset.append(ruta_capas_o_ds)
    
# ** Tables out Dataset
listado_rutas_tablas = []
for tablas in arcpy.ListTables():
    ruta_tablas_o_ds = os.path.join(ruta_filegdb,tablas)
    listado_rutas_tablas.append(ruta_tablas_o_ds)
    
# ** Toma el sistema de referencia de una capa en específico de la base de datos
ruta_capa_src = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\municipio"

for dataset_a_crear in lista_datasets:
    arcpy.management.CreateFeatureDataset(ruta_sde, dataset_a_crear, spatial_reference = ruta_capa_src)

# ? Copiado de capas y tablas

arcpy.env.workspace = ruta_sde

# ** Copiado de capas dentro de dataset
for dataset in arcpy.ListDatasets():
        for rutas in listado_rutas_capas_into_dataset:
            if dataset.split(".")[1] == rutas.split("\\")[7]:
                ruta_salida = os.path.join(arcpy.env.workspace,dataset,rutas.split("\\")[8])
                arcpy.management.Copy(rutas, ruta_salida)
                print("Se migra la capa {0} dentro del dataset {1}".format(rutas.split("\\")[8],dataset))
                
# ** Copiado de capas dentro de .sde
for rutas in listado_rutas_capas_out_dataset:
    nombre_salida = rutas.split("\\")[7]
    ruta_salida = os.path.join(arcpy.env.workspace,nombre_salida)
    arcpy.management.Copy(rutas, ruta_salida)
    print("Se migra la capa {0}".format(rutas.split("\\")[7]))
    
# ** Copiado de tablas dentro de .sde
for rutas in listado_rutas_tablas:
    arcpy.management.Copy(rutas, rutas.split("\\")[7])
    print("Se migra la tabla {0}".format(rutas.split("\\")[7]))

print("____________________ FINALIZA _12_PGAR_Migracion_A_SDE ____________________")

# ? _13_PGAR_Construccion_Relaciones

print("____________________ INICIA _13_PGAR_Construccion_Relaciones ____________________")

# !! RELACIONES SOBRE LA LOCAL

arcpy.env.workspace = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb"

feature_municipio = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\municipio"
tabla_capa = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\tbl_capa"
tabla_cuenca = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\cuenca"

# ********************** Relación Municipio - Capa **********************
# - Creación de la estrucutura de la relación
r_municipio_capa = "r_municipio_capa"
arcpy.management.CreateRelationshipClass(tabla_capa, feature_municipio, r_municipio_capa, 'SIMPLE', 'capa', 'municipio', 
                                         "NONE", 'MANY_TO_MANY', "NONE", 'codigo_capa', 'codigo_capa', 'codigo_municipio', 'codigo_municipio')
print("Creada relación: {0}".format(r_municipio_capa))

# - Creación de la vista de tabla
ruta_csv_relacion_municipio_capa = r"D:\PUBLIC\PGAR\Resultados\2.Py\r_municipio_capa.csv"

# - Unificación de registros
arcpy.Append_management(ruta_csv_relacion_municipio_capa, r_municipio_capa, "NO_TEST")
print(" - Se incorporan los registros de la relación: {0}".format(r_municipio_capa))

# ********************** Relación Municipio - Cuenca **********************
# - Creación de la estrucutura de la relación
r_municipio_cuenca = "r_municipio_cuenca"
arcpy.management.CreateRelationshipClass(tabla_cuenca, feature_municipio, r_municipio_cuenca, 'SIMPLE', 'cuenca', 'municipio', 
                                         "NONE", 'MANY_TO_MANY', "NONE", 'codigo_cuenca', 'codigo_cuenca', 'codigo_municipio', 'codigo_municipio')
print("Creada relación: {0}".format(r_municipio_cuenca))

# - Creación de la vista de tabla
ruta_csv_relacion_municipio_cuenca = r"D:\PUBLIC\PGAR\Resultados\2.Py\r_municipio_cuenca.csv"

# - Unificación de registros
arcpy.Append_management(ruta_csv_relacion_municipio_cuenca, r_municipio_cuenca, "NO_TEST")
print(" - Se incorporan los registros de la relación: {0}".format(r_municipio_cuenca))

tabla_tematica = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\tbl_tematica"
tabla_direccion = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\direccion"
tabla_departamento = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\tbl_departamento"
tabla_fuente = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\tbl_fuentes"
r_capa_tematica = "r_capa_tematica"
r_direccion_municipio = "r_direccion_municipio"
r_municipio_departamento = "r_municipio_departamento"
r_capa_fuentes = "r_capa_fuentes"

# ********************** Relación Capa - Temática **********************
arcpy.management.CreateRelationshipClass(tabla_tematica, tabla_capa, r_capa_tematica, 'SIMPLE', 'capa', 'tematica', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_tematica', 'codigo_tematica')
print("Creada relación: {0}".format(r_capa_tematica))

# ********************** Relación Dirección - Municipio **********************
arcpy.management.CreateRelationshipClass(tabla_direccion, feature_municipio, r_direccion_municipio, 'SIMPLE', 'municipio', 'direccion', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_direccion', 'codigo_direccion')
print("Creada relación: {0}".format(r_direccion_municipio))

# ********************** Relación Municipio - Departamento **********************
arcpy.management.CreateRelationshipClass(tabla_departamento, feature_municipio, r_municipio_departamento, 'SIMPLE', 'municipio', 'departamento', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_departamento', 'codigo_departamento')
print("Creada relación: {0}".format(r_municipio_departamento))

# ********************** Relación Capa - Fuentes **********************
arcpy.management.CreateRelationshipClass(tabla_fuente, tabla_capa, r_capa_fuentes, 'SIMPLE', 'capa', 'fuente', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_fuente', 'codigo_fuente')
print("Creada relación: {0}".format(r_capa_fuentes))

arcpy.env.workspace = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb"
tabla_capa = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.gdb\tbl_capa"

# Proceso realizado en el archivo _9_...
for datasets in arcpy.ListDatasets():
    for capas in arcpy.ListFeatureClasses(feature_dataset=datasets):
            arcpy.management.AlterField(capas, 'codigo_capa', 'codigo_capa_borrar')
            arcpy.management.AddField(capas, 'codigo_capa', 'DOUBLE', field_alias = 'Código Capa')
            arcpy.management.CalculateField(capas, 'codigo_capa', '!codigo_capa_borrar!')
            print("-Código Capa- actualizado para: {0}".format(capas))
            
for datasets in arcpy.ListDatasets():
    for capas in arcpy.ListFeatureClasses(feature_dataset=datasets):        
        ruta_capa = os.path.join(arcpy.env.workspace,datasets,capas)
        if capas != 'municipio' or capas != 'cuenca':
            nombre_relacion = "r_capa_" + capas
            arcpy.management.CreateRelationshipClass(tabla_capa, ruta_capa, nombre_relacion, 'SIMPLE', 'registros', 'capa', 
                                                "NONE", 'ONE_TO_MANY', "NONE", 'codigo_capa', 'codigo_capa')
            print("Creada relación: {0}".format(nombre_relacion))
            
# !! RELACIONES SOBRE LA EMPRESARIAL

arcpy.env.workspace = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde"

feature_municipio = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\municipio"
tabla_capa = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\tbl_capa"
tabla_cuenca = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\cuenca"

# ********************** Relación Municipio - Capa **********************
# - Creación de la estrucutura de la relación
r_municipio_capa = "r_municipio_capa"
arcpy.management.CreateRelationshipClass(tabla_capa, feature_municipio, r_municipio_capa, 'SIMPLE', 'capa', 'municipio', 
                                         "NONE", 'MANY_TO_MANY', "NONE", 'codigo_capa', 'codigo_capa', 'codigo_municipio', 'codigo_municipio')
print("Creada relación: {0}".format(r_municipio_capa))

# - Creación de la vista de tabla
ruta_csv_relacion_municipio_capa = r"D:\PUBLIC\PGAR\Resultados\2.Py\r_municipio_capa.csv"

# - Unificación de registros
arcpy.Append_management(ruta_csv_relacion_municipio_capa, r_municipio_capa, "NO_TEST")
print(" - Se incorporan los registros de la relación: {0}".format(r_municipio_capa))

# ********************** Relación Municipio - Cuenca **********************
# - Creación de la estrucutura de la relación
r_municipio_cuenca = "r_municipio_cuenca"
arcpy.management.CreateRelationshipClass(tabla_cuenca, feature_municipio, r_municipio_cuenca, 'SIMPLE', 'cuenca', 'municipio', 
                                         "NONE", 'MANY_TO_MANY', "NONE", 'codigo_cuenca', 'codigo_cuenca', 'codigo_municipio', 'codigo_municipio')
print("Creada relación: {0}".format(r_municipio_cuenca))

# - Creación de la vista de tabla
ruta_csv_relacion_municipio_cuenca = r"D:\PUBLIC\PGAR\Resultados\2.Py\r_municipio_cuenca.csv"

# - Unificación de registros
arcpy.Append_management(ruta_csv_relacion_municipio_cuenca, r_municipio_cuenca, "NO_TEST")
print(" - Se incorporan los registros de la relación: {0}".format(r_municipio_cuenca))

tabla_tematica = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\tbl_tematica"
tabla_direccion = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\direccion"
tabla_departamento = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\tbl_departamento"
tabla_fuente = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\tbl_fuentes"
r_capa_tematica = "r_capa_tematica"
r_direccion_municipio = "r_direccion_municipio"
r_municipio_departamento = "r_municipio_departamento"
r_capa_fuentes = "r_capa_fuentes"

# ********************** Relación Capa - Temática **********************
arcpy.management.CreateRelationshipClass(tabla_tematica, tabla_capa, r_capa_tematica, 'SIMPLE', 'capa', 'tematica', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_tematica', 'codigo_tematica')
print("Creada relación: {0}".format(r_capa_tematica))

# ********************** Relación Dirección - Municipio **********************
arcpy.management.CreateRelationshipClass(tabla_direccion, feature_municipio, r_direccion_municipio, 'SIMPLE', 'municipio', 'direccion', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_direccion', 'codigo_direccion')
print("Creada relación: {0}".format(r_direccion_municipio))

# ********************** Relación Municipio - Departamento **********************
arcpy.management.CreateRelationshipClass(tabla_departamento, feature_municipio, r_municipio_departamento, 'SIMPLE', 'municipio', 'departamento', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_departamento', 'codigo_departamento')
print("Creada relación: {0}".format(r_municipio_departamento))

# ********************** Relación Capa - Fuentes **********************
arcpy.management.CreateRelationshipClass(tabla_fuente, tabla_capa, r_capa_fuentes, 'SIMPLE', 'capa', 'fuente', 
                                         "NONE", 'ONE_TO_MANY', "NONE", 'codigo_fuente', 'codigo_fuente')
print("Creada relación: {0}".format(r_capa_fuentes))

arcpy.env.workspace = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde"
tabla_capa = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\PGAR_Inventario.sde\tbl_capa"

# Proceso realizado en el archivo _9_...
for datasets in arcpy.ListDatasets():
    for capas in arcpy.ListFeatureClasses(feature_dataset=datasets):
            arcpy.management.AlterField(capas, 'codigo_capa', 'codigo_capa_borrar')
            arcpy.management.AddField(capas, 'codigo_capa', 'DOUBLE', field_alias = 'Código Capa')
            arcpy.management.CalculateField(capas, 'codigo_capa', '!codigo_capa_borrar!')
            print("-Código Capa- actualizado para: {0}".format(capas))
            
for datasets in arcpy.ListDatasets():
    for capas in arcpy.ListFeatureClasses(feature_dataset=datasets):        
        ruta_capa = os.path.join(arcpy.env.workspace,datasets,capas)
        if capas != 'municipio' or capas != 'cuenca':
            nombre_relacion = "r_capa_" + capas
            arcpy.management.CreateRelationshipClass(tabla_capa, ruta_capa, nombre_relacion, 'SIMPLE', 'registros', 'capa', 
                                                "NONE", 'ONE_TO_MANY', "NONE", 'codigo_capa', 'codigo_capa')
            print("Creada relación: {0}".format(nombre_relacion))

print("____________________ FINALIZA _13_PGAR_Construccion_Relaciones ____________________")