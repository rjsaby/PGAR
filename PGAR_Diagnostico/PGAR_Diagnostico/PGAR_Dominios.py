import arcpy
import pandas as pd
import os

class dominios_bd:   
    """
    La instanciación de la clase requiere, como parámetros:
    bd_limites: base de datos donde se localiza la capa sobre la cual se extraerá el dominio. Se analiza una base de datos 
    sin dataframes. 
    bd_trabajo: Base de datos donde se parametrizará el dominio creado
    nombre_feature: Nombre de la capa donde se extraerá la información para la construcción del dominio
    campo_dominio_1: Campo -codigo- para la construcción del dominio
    campo_dominio_2: Campo -descripción- para la construcción del dominio
    ruta_generacion_csv_dominios: Ruta Windows donde se creará el archivo .csv que será usado para la generación del dominio
    nombre_dominio: Nombre que quiere que se le asigné al dominio a crear
    decripcion_dominio: Descripción que quiere que se parametrice en el domunio a crear
    campo_asignacion: Campo del o los elementos que masivamente se les quiere asignar el dominio
    wildcard: Wilcard para buscar algún dataset en particular
    """     
    def __init__(self, 
                 bd_limites, 
                 bd_trabajo, 
                 nombre_feature, 
                 campo_dominio_1, 
                 campo_dominio_2, 
                 ruta_generacion_csv_dominios, 
                 nombre_dominio, 
                 decripcion_dominio,
                 campo_asignacion,
                 wildcard):
                
            self.bd_limites = bd_limites
            self.bd_trabajo = bd_trabajo
            self.nombre_feature = nombre_feature
            self.campo_dominio_1 = campo_dominio_1
            self.campo_dominio_2 = campo_dominio_2
            self.ruta_generacion_csv_dominios = ruta_generacion_csv_dominios
            self.nombre_dominio = nombre_dominio
            self.decripcion_dominio = decripcion_dominio
            self.campo_asignacion = campo_asignacion
            self.wildcard = wildcard
    def generacion_dominio(self):
        arcpy.env.overwriteOutput = True
        
        arcpy.env.workspace = self.bd_limites        
        # ? Se asigna en una valiable la capa que permitirá construir el dominio
        lista_feature = [feature for feature in arcpy.ListFeatureClasses() if feature == self.nombre_feature]
        
        lcode = []
        ldescription = []        
        # ? Se seleccionan los campos de la capa que se quieren hagan parte del domino como codigo y descriptor
        with arcpy.da.SearchCursor(lista_feature[0], [self.campo_dominio_1, self.campo_dominio_2]) as cursor:
            for row in cursor:
                lcode.append(row[0])
                ldescription.append(row[0])
        print(" *** Se recorre la capa ***")
        
        # ? Se define el dataframe
        df_dominio = pd.DataFrame(list(zip(lcode, ldescription)), columns = ['code','description'])
        # ? Se parametriza la ruta de salida del archivo .csv
        ruta_generacion = str(os.path.join(self.ruta_generacion_csv_dominios, self.nombre_dominio)) +'.csv'
        # ? Exportación de .csv
        df_dominio.to_csv(ruta_generacion)        
        # ? Parametrización de nuevo espacio de trabajo, donde se asignará el dominio (base de datos oficial de trabajo)
        arcpy.env.workspace = self.bd_trabajo
        # ? Asignación de tabla a dominio
        arcpy.management.TableToDomain(ruta_generacion, 'code', 'description', arcpy.env.workspace, self.nombre_dominio, self.decripcion_dominio, update_option = 'REPLACE')
        
        # ? Bucle de actualización masiva de campo con dominios (cuando aplica y cuando no)
        for dataset in arcpy.ListDatasets(wild_card=self.wildcard):
            for feature in arcpy.ListFeatureClasses(feature_dataset=dataset):
                for campo in arcpy.ListFields(dataset=feature):
                    if campo.name == self.campo_asignacion:    
                        arcpy.management.AssignDomainToField(feature, campo.name, self.nombre_dominio)
                        print(f"Se asigna el dominio {self.nombre_dominio} de la capa {feature}")
                    else:
                        print(f"La capa {feature} no tiene el campo requerido")