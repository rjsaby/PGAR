import arcpy
import os
import sys

class normalizacion_campos():
    try:
        # ? Parametros
        arcpy.env.overwriteOutput=True
        cmt12 = r"C:\PUBLIC\SERESCO\Resultados\_8_Py\ctm12.prj"
        
        def __init__(self,
                    bd_trabajo,
                    wilcard):
            self.bd_trabajo = bd_trabajo
            self.wilcard = wilcard
            arcpy.env.workspace = bd_trabajo
        
        def proceso_normalizacion(self):    
            
            diccionario = {}
            for dataset in arcpy.ListDatasets(wild_card=self.wilcard):
                for feature in arcpy.ListFeatureClasses(feature_dataset=dataset):
                    for campo in arcpy.ListFields(dataset = feature):
                        if campo.type == 'String':
                            if feature not in diccionario:                            
                                diccionario[feature] = [campo.name]
                            else: 
                                diccionario[feature].append(campo.name) 
                        else:
                            pass
                else:
                    pass
                
            resultados = {}       
            for llave, valor in diccionario.items():    
                with arcpy.da.SearchCursor(llave, valor) as cursor:
                    for fila in cursor:
                        for i, nombre_campo in enumerate(valor):
                            valor_campo = fila[i]
                            if valor_campo:
                                longitud = len(valor_campo) 
                                if nombre_campo in resultados:
                                    if longitud > resultados[nombre_campo]:
                                        resultados[nombre_campo] = longitud
                                else:
                                    resultados[nombre_campo] = longitud
                                    
            for dataset in arcpy.ListDatasets(wild_card=self.wilcard):
                for feature in arcpy.ListFeatureClasses(feature_dataset=dataset):
                        for campo in arcpy.ListFields(dataset = feature):
                            try:
                                for llave, valor in resultados.items(): 
                                    if campo.name == llave:
                                        if '_Norm' in campo.name:
                                            palabras = campo.name.split('_')
                                            nuevo_nombre = '_'.join([palabra.capitalize() for palabra in palabras])
                                            arcpy.management.AlterField(feature, field=campo.name, new_field_name=nuevo_nombre[:-5])
                                            print(print(f" *** {campo.name} actualizado ***"))
                                        else:
                                            try:                            
                                                arcpy.management.AddField(feature, str(campo.name)+'_Norm', field_type = 'TEXT', field_length = int(valor))
                                                print(f" 1. Se crea campo {str(campo.name)+'_Norm'} para la capa {feature}")
                                            except arcpy.ExecuteError as e:
                                                print(f"Se produjo un error al actualizar el campo {campo.name} de la capa {feature}: {e}")
                                            try:    
                                                arcpy.management.CalculateField(feature, str(campo.name)+'_Norm', "!"+campo.name+"!", 'PYTHON3')
                                                print(f" 2. Se se migra {campo.name} para la capa {feature}")
                                            except arcpy.ExecuteError as e:
                                                print(f"Se produjo un error al actualizar el campo {campo.name} de la capa {feature}: {e}")
                                            try:
                                                arcpy.management.DeleteField(feature, campo.name)
                                                print(f" 3. Se borra campo {campo.name} de capa {feature}")                                        
                                            except arcpy.ExecuteError as e:
                                                print(f"Se produjo un error al actualizar el campo {campo.name} de la capa {feature}: {e}")
                                            # ? Generar Letra Capital en todas las palabras que conforman el nombre de la capa
                                            palabras = campo.name.split('_')
                                            nuevo_nombre = '_'.join([palabra.capitalize() for palabra in palabras])
                                            try:
                                                arcpy.management.AlterField(feature, field=str(campo.name)+'_Norm', new_field_name=nuevo_nombre, new_field_alias=nuevo_nombre)
                                                print(f" 4. Se actualiza campo {campo.name} de capa {feature}")
                                            except arcpy.ExecuteError as e:
                                                print(f"Se produjo un error al actualizar el campo {campo.name} de la capa {feature}: {e}")
                            except arcpy.ExecuteError as e:
                                print(f"Se produjo un error al actualizar el campo {campo.name} de la capa {feature}: {e}")
                                              
    except Exception:
        e = sys.exc_info()[1]
        print(e.args[0])

        # If using this code within a script tool, AddError can be used to return messages 
        #   back to a script tool. If not, AddError will have no effect.
        arcpy.AddError(e.args[0])