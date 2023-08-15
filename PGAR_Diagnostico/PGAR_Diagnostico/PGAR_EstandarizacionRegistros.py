import arcpy
# ? Librería encargada de realizar la limpieza de registros con tildes
from unidecode import unidecode
class estandarizacion_campos:
    def __init__(self, nombreCapa):
        self.nombreCapa = nombreCapa
    
    def estandarizacionCampos(self):
        # ? Se definie, con la capa ingresada como variable, un listado con sus campos
        lista_campos = arcpy.ListFields(dataset=self.nombreCapa)
              
        # ? Se crea buble para recorrer los campos de la capa:
        for campo in lista_campos:
            # ? Se restringe el análisis para los campos de tipo texto o cadena de caracteres
            if campo.type == 'String':
                # ? Se Crea una consulta de actualización para cambiar a minúsculas todos los valores del campo actual.
                # ? Ademas, se aprovecha este proceso para dejar todos los registros en minúsculas.                
                with arcpy.da.UpdateCursor(self.nombreCapa, [campo.name]) as cursor:                        
                    for fila in cursor:
                        try:
                            # ? Se Cambia el valor del campo a minúsculas y quita tildes
                            fila[0] = unidecode(fila[0].lower()) if fila[0] else None
                            # ? Se actualizan los registros
                            cursor.updateRow(fila)
                        except RuntimeError as e:
                            print(f"Se produjo un error al actualizar el campo {campo.name} de la capa {self.nombreCapa}: {e}")