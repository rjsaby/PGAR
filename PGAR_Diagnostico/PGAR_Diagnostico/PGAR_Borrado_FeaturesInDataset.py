import arcpy

class borrado_featureindataset:
    def __init__(self, ruta_trabajo):
        self.ruta_trabajo = ruta_trabajo
        
    def borrado(self):
        arcpy.env.workspace = self.ruta_trabajo
        lista_feature = [feature for feature in arcpy.ListFeatureClasses()]
        try:
            for indice, capa in enumerate(lista_feature, start=1):
                arcpy.Delete_management(in_data = capa)
                print(f"{indice}/{len(lista_feature)} - Se elimina la capa: {capa}")
        except Exception as e:
            print(f"Se marca la excepción en la capa {capa} que es {e}")