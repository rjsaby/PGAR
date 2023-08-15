import arcpy
import os

class copiado_dataset:
    def __init__(self, ruta_dataset_inicio, ruta_dataset_final):
        self.ruta_dataset_inicio = ruta_dataset_inicio
        self.ruta_dataset_final = ruta_dataset_final    
    def proceso_copiado_dataset(self):
        
        descripcion_dataset_inicial = arcpy.Describe(self.ruta_dataset_inicio)
        descripcion_dataset_final = arcpy.Describe(self.ruta_dataset_final)

        lista_feature_inicio = []
        lista_feature_final = []
        
        # ? Verificación Sistemas de Referencia
        if descripcion_dataset_inicial.spatialReference.name == descripcion_dataset_final.spatialReference.name:
            # ? Se recorre el dataset inicio
            arcpy.env.workspace = self.ruta_dataset_inicio
            try:
                for feature in arcpy.ListFeatureClasses():
                    # ? Para usar la función copy almaneno las rutas de inicio y fin de cada una de las capas que se quieren copiar
                    inicio = os.path.join(arcpy.env.workspace,feature)
                    lista_feature_inicio.append(inicio)
                    fin = os.path.join(self.ruta_dataset_final,feature)
                    lista_feature_final.append(fin)
            except Exception as e:
                print(f"Se presenta la Excepción: {e}")        
        else:
            print("Los dataset no tienen el mismo SRC, por ende, no se pueden copiar")
            
        print("*** Finaliza Enlace de Rutas ***")

        # ? Se unifican las listas de rutas de inicio y fin 
        lista_unificada = list(zip(lista_feature_inicio, lista_feature_final))
        # ? Se recorre la lista con un bucle
        try:
            for indice, i in enumerate(lista_unificada, start=1):
                # ? Se verifica que la capa no haya sido copiada, esto para evitar reprocesos si el proceso se corta  por alguna razón.
                # ? Para ello se usa la función .Exist() del paquete arcpy
                if arcpy.Exists(i[1]):
                    print(f"{indice}/{len(lista_unificada)} Capa {os.path.basename(i[0])} existe en el dataset")
                else:
                    try:
                        arcpy.Copy_management(in_data=i[0], out_data=i[1])
                        print(f"{indice}/{len(lista_unificada)} Capa {os.path.basename(i[0])} copiada")
                    except (Exception) as e:
                        print(f"Se presenta el error: {e}, sobre la capa {os.path.basename(i[0])}")
        
        # ? Con esta forma de manejar el except, podemos vincular varios tipos de errores
        # ? en una sola línea de código e.j -except (ZeroDivisionError, ValueError) as e:-    
        except (Exception, ValueError) as e:
            print(f"Se presenta el error: {e}, sobre la capa {os.path.basename(i[0])}")
            
        print("*** Finaliza el copiado de dataset de Rutas ***")   