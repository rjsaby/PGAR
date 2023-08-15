import arcpy
import pandas as pd
import os

"""La función cuenta con dos parámetros:
        rutaBaseDatos: Con la ruta de la base de datos sobre la que se quiere generar el diccionario de datos
        wilkcard = Si quiere tenerse encuenta algún dataset en particular
        rutaSalidaArchivos: La carpeta donde se quiere almacenar los XLSX resultantes con el diccionario de datos
"""
def generacion_diccionario_datos(rutaBaseDatos, wilcard, rutaSalidaArchivos):
    
    arcpy.env.workspace = rutaBaseDatos

    try: 
        lista_dataset = []
        lista_codigos_dataset = []
        lista_nombre_feature_class = []
        lista_codigos_fc = []
        lista_tipogeo_feature = []
            
        for dataset in arcpy.ListDatasets(wild_card=wilcard):
            # ? Se presenta la función enumerate con el objetivo de numerar cada capa dentro de cada dataset y asignarle ese codigo
            # ? Dentro del diccionario de datos
            for i, feature in enumerate(arcpy.ListFeatureClasses(feature_dataset=dataset), start=1):
                # ! Si la base del código de nombre aumenta en dos caracteres, esta operación falla
                # ! dataset[3:] (Se aplicaba el slicing para quitar el _1_ de los dataset)
                tematica_componente = '<<'+str(dataset)+'>>'
                lista_dataset.append(tematica_componente)
                codigo_dataset = dataset.split('_')[1]
                lista_codigos_dataset.append(codigo_dataset)
                lista_nombre_feature_class.append('<<'+str(feature)+'>>')
                featureDescription = arcpy.Describe(feature)
                lista_tipogeo_feature.append(featureDescription.shapeType)
                # ? Nacido de la función enumerate
                lista_codigos_fc.append(i)

        df_disenioGDB = pd.DataFrame(list(zip(lista_dataset, lista_codigos_dataset, lista_nombre_feature_class, lista_codigos_fc, lista_tipogeo_feature)), columns=['tematica_componente', 'codigo_tematica', 'feature_class', 'codigo_fc', 'geometria'])               
        
    except Exception as e:
        print(e)
        
    try:
        lista_feature = []
        lista_nombre_campo = []
        lista_tipo_campo = []
        lista_longitud_campo = []
        lista_nombre_dominio = []
        lista_feature_geometria = []

        for dataset in arcpy.ListDatasets(wild_card=wilcard):
            # ? Se presenta la función enumerate con el objetivo de numerar cada capa dentro de cada dataset y asignarle ese codigo
            # ? Dentro del diccionario de datos
            for feature in arcpy.ListFeatureClasses(feature_dataset=dataset):
                featureDescription = arcpy.Describe(feature)
                for campo in arcpy.ListFields(dataset = feature):
                    if campo.name not in ('SHAPE_Length','SHAPE_Area','OBJECTID','SHAPE', 'Shape', 'Shape_Length', 'Shape_Area', 'OBJECTID_12', 'OBJECTID_1'):                   
                            featureDescription = arcpy.Describe(feature)
                            lista_feature.append('<<'+str(feature)+'>>')
                            lista_feature_geometria.append(featureDescription.shapeType)
                            lista_nombre_campo.append(campo.name)
                            lista_tipo_campo.append(campo.type)
                            lista_longitud_campo.append(campo.length)
                            lista_nombre_dominio.append(campo.domain)                    
        
        df_featureClass = pd.DataFrame(list(zip(lista_feature, lista_feature_geometria, lista_nombre_campo, lista_tipo_campo, lista_longitud_campo, lista_nombre_dominio)), columns=['feature_class', 'lista_feature_geometria', 'nombre_campo', 'tipo_campo', 'longitud_campo', 'dominio'])
                    
    except Exception as e:
        print(e)      

    # ? Reemplazo de valores para estandarizar mejor el diccionario de datos
    
    df_disenioGDB['geometria'] = df_disenioGDB['geometria'].replace('Point','Punto')
    df_disenioGDB['geometria'] = df_disenioGDB['geometria'].replace('Polygon','Poligono')
    df_disenioGDB['geometria'] = df_disenioGDB['geometria'].replace('Polyline','Linea')
    # TODO: Dataframe de Campos
    df_featureClass['lista_feature_geometria'] = df_featureClass['lista_feature_geometria'].replace('Point','Punto')
    df_featureClass['lista_feature_geometria'] = df_featureClass['lista_feature_geometria'].replace('Polygon','Poligono')
    df_featureClass['lista_feature_geometria'] = df_featureClass['lista_feature_geometria'].replace('Polyline','Linea')

    # ? Se crea una columna nueva para registrar el codigo de la geometría y para la relación de metadatos
    df_disenioGDB['codigo_geometria'] = ''
    df_disenioGDB['id_feature'] = None
    df_disenioGDB['feature_diligenciado'] = None
    df_disenioGDB['metadato'] = None

    # ? Insertar una nueva columna en blanco al inicio del DataFrame
    df_disenioGDB.insert(0, 'geodatabase', None)
    df_disenioGDB.insert(1, 'codigo_geodatabase', None)
    # ! Estos dos campos deberán actualizarse cuando se expecifiquen tablas
    df_disenioGDB.insert(2, 'formato', '<<Vectorial>>')
    df_disenioGDB.insert(3, 'codigo_formato', 'V')
    df_disenioGDB.insert(4, 'tema_general_o_medio', None)
    # TODO: Dataframe de Campos
    df_featureClass.insert(5, 'descripcion', None)

    # ? Asignar valores a la nueva columna mediante consultas
    df_disenioGDB.loc[df_disenioGDB['geometria'] == 'Punto', 'codigo_geometria'] = 'PT'
    df_disenioGDB.loc[df_disenioGDB['geometria'] == 'Poligono', 'codigo_geometria'] = 'PG'
    df_disenioGDB.loc[df_disenioGDB['geometria'] == 'Linea', 'codigo_geometria'] = 'LN'

    nombre_archivo_xlsx = 'Diccionario_Datos_PGAR_2023_2035'
    salida_archivo_dd = str(os.path.join(rutaSalidaArchivos,nombre_archivo_xlsx)) + '.xlsx'
    

    with pd.ExcelWriter(salida_archivo_dd, engine='xlsxwriter') as writer:
        # ? Se utiliza el método to_excel para guardar cada DataFrame en una hoja separada.
        # ? Se puede especificar el nombre de la hoja con el argumento 'sheet_name'.
        df_disenioGDB.to_excel(writer, sheet_name='Dis_Geodata_O', index=False)
        df_featureClass.to_excel(writer, sheet_name='FeatureClass_O', index=False)
        
    return salida_archivo_dd
        
# ? Código para ejecutar la función sin necesidad de ser llamada en otro Script. 
if __name__ == "__main__":
    print("La función cuenta con tres parámetros")