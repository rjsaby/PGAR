import os
import arcpy
import pathlib
import geopandas as gpd
import fiona
import pandas as pd
from arcgis.features import GeoAccessor, GeoSeriesAccessor

# Ruta del directorio donde se localizan los archivos geojson.
ruta_geojson = arcpy.GetParameterAsText(0)
# Espacio de trabajo, asociada a la base de datos donde se almanacenarán los geojson convertidos a feature class
arcpy.env.workspace = arcpy.GetParameterAsText(1)

# Borrado de capas dentro de la base de datos existente
if arcpy.Exists(arcpy.env.workspace):
    for capas in arcpy.ListFeatureClasses():
        arcpy.management.Delete(capas)
        print("Se borra la información registrada en la capa: {0}".format(capas))
else:
    print("No hay capas alojadas en la base de datos")

nombre_geojson = os.listdir(ruta_geojson)
lista_ruta_archivo = []
for rutas in nombre_geojson:
    lista_ruta_archivo.append(os.path.join(ruta_geojson, rutas))
    
# ? Diccionario que se usará en la transformación del geoJSON a Feature Class
geometrias = {'Polygon':'POLYGON',
              'MultiPolygon':'POLYGON',
              'LineString':'POLYLINE',
              'MultiLineString':'POLYLINE',
              'Point':'POINT'}

for generacion_feature in lista_ruta_archivo:
    if pathlib.Path(generacion_feature).suffix == '.geojson':
        nombre_geojson = os.path.split(generacion_feature)
        nombre_geojson_parametrizado = (nombre_geojson[1].split(".")[0]).replace(" ","_")
        nombre_geojson_parametrizado = (nombre_geojson[1].split(".")[0]).replace("-","_")
        nombre_geojson_parametrizado = (nombre_geojson[1].split(".")[0]).replace("%","_")
        if nombre_geojson_parametrizado != os.path.basename(ruta_geojson):
            salida_feature = os.path.join(arcpy.env.workspace, nombre_geojson_parametrizado)
            # ? Se exporta el geoJSON a GeoDataFrame
            df = gpd.read_file(generacion_feature)
            # ? Por medio del atributo .geom_type se extrae el tipo de geometría para cada registro
            tipo_geometria = df.geom_type
            # ? Como las geometrias varías si son simples o multiples, se seleccina la que se almacena en la primera fila
            primer_registro_tipo_geometria = tipo_geometria.loc[0]
            # ? Se recorre el diccionario
            for valor, llave in geometrias.items():
                # ? Se compara la geometría seleccionada con el valor almacenado en el diccionario
                if primer_registro_tipo_geometria == valor:
                    # ? Se genera el feature class, tomando como variable el valor de la geometría
                    arcpy.conversion.JSONToFeatures(generacion_feature, salida_feature, llave)
                    print("geojson {0} convertido al feature {1}".format(nombre_geojson, nombre_geojson_parametrizado))
    elif pathlib.Path(generacion_feature).suffix == '.json':
        nombre_geojson = os.path.split(generacion_feature)
        nombre_geojson_parametrizado = (nombre_geojson[1].split(".")[0]).replace(" ","_")
        nombre_geojson_parametrizado = (nombre_geojson[1].split(".")[0]).replace("-","_")
        nombre_geojson_parametrizado = (nombre_geojson[1].split(".")[0]).replace("%","_")
        if nombre_geojson_parametrizado != os.path.basename(ruta_geojson):
            salida_feature = os.path.join(arcpy.env.workspace, nombre_geojson_parametrizado)
            # ? Se exporta el geoJSON a GeoDataFrame
            df = gpd.read_file(generacion_feature)
            # ? Por medio del atributo .geom_type se extrae el tipo de geometría para cada registro
            tipo_geometria = df.geom_type
            # ? Como las geometrias varías si son simples o multiples, se seleccina la que se almacena en la primera fila
            primer_registro_tipo_geometria = tipo_geometria.loc[0]
            # ? Se recorre el diccionario
            for valor, llave in geometrias.items():
                # ? Se compara la geometría seleccionada con el valor almacenado en el diccionario
                if primer_registro_tipo_geometria == valor:
                    # ? Se genera el feature class, tomando como variable el valor de la geometría
                    arcpy.conversion.JSONToFeatures(generacion_feature, salida_feature, llave)
                    print("json {0} convertido al feature {1}".format(nombre_geojson, nombre_geojson_parametrizado))
    else:
        print("Es la base de datos") 
        
lista_capas_convertidas = arcpy.ListFeatureClasses()
nombre_campo = 'nombre_capa'

for features in lista_capas_convertidas:
    descripcion = arcpy.Describe(features)
    expresion = "'" + descripcion.name +"'"
    arcpy.management.AddField(features, nombre_campo, 'TEXT', field_length = 100, field_alias = 'Nombre Capa Origen')
    arcpy.management.CalculateField(features, nombre_campo, expresion, expression_type = 'PYTHON3')
    print("Se actualiza la capa {0}".format(features))