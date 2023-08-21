# ? Se importan las librerías
import arcpy
import os
import pandas as pd
#? Geoaccesor para trabajar SEDF
from arcgis import GeoAccessor, GeoSeriesAccessor

class estadisticos_calidad():
    
    def __init__(self,
                 ruta_featureclass,
                 ruta_archivos_salida):
        
        self.ruta_featureclass = ruta_featureclass
        self.ruta_archivos_salida = ruta_archivos_salida
        
    def ejecucion_calidad(self):

        ruta_featureclass = self.ruta_featureclass
        ruta_archivos_salida = self.ruta_archivos_salida
        nombre_archivo_xlsx = os.path.basename(ruta_featureclass)
        salida_archivo_calidad = str(os.path.join(ruta_archivos_salida,nombre_archivo_xlsx)) + '.xlsx'

        df_feature = pd.DataFrame.spatial.from_featureclass(location = ruta_featureclass)        
        lista_estadisticos_generales = [[df_feature.shape[0], df_feature.shape[1]]]
        df_estadisticos_generales = pd.DataFrame(lista_estadisticos_generales, columns = ['numero_registros','numero_columnas'])

        try:
            nombre_columna = [column_name for column_name, column_data in df_feature.items()]
        except Exception as e:
            print(f"Se presenta excepción en la columna {nombre_columna} de la tabla {nombre_archivo_xlsx}: {e}")
        
        try:    
            total_nulos = [df_feature[column_name].isna().sum() for column_name, column_data in df_feature.items()]
        except Exception as e:
            print(f"Se presenta excepción en la columna {nombre_columna} de la tabla {nombre_archivo_xlsx}: {e}")
            
        df_feature_sin_shape = df_feature.loc[:, df_feature.columns != 'SHAPE']
        
        try:
            total_vacios = [((df_feature_sin_shape[column_name]=='').sum()) for column_name, column_data in df_feature_sin_shape.items()]
        except Exception as e:
            print(f"Se presenta excepción en la columna {nombre_columna} de la tabla {nombre_archivo_xlsx}: {e}") 

        lista_resultados = list(zip(nombre_columna,total_nulos,total_vacios))
        df_estadisticos_detallados = pd.DataFrame(lista_resultados, columns = ['nombre_columna','total_nulos','total_vacios'])

        with pd.ExcelWriter(salida_archivo_calidad, engine='xlsxwriter') as writer:
            df_estadisticos_generales.to_excel(writer, sheet_name='Est_Generales', index=False)
            df_estadisticos_detallados.to_excel(writer, sheet_name='Est_Detallados', index=False)
        
        print(f"Se verifican estadisticos de calidad para {nombre_archivo_xlsx}") 