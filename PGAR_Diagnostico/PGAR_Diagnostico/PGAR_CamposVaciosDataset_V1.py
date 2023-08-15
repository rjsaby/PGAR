import arcpy
import pandas as pd
import os

def identificar_campos_vacios(feature_class, ruta):
    try:
        # ** Listar los campos de la variable que entra como parámetro dentro de la función       
        lista_campos = [campo.name for campo in arcpy.ListFields(dataset=feature_class)]           

        # ** Diccionario para almacenar los resultados
        campos_vacios = {}

        # ** Inicializar el diccionario con todos los campos y establecer su valor en True
        for campo in lista_campos:
            # ? Con esta forma de expresar la sentencia, al diccionario previamente iniciado se le asigna
            # ? el valor del key como campo, y el true como valor
            campos_vacios[campo] = True
            
        # ** Recorrer cada registro del feature class y verificar si los campos están vacíos
        with arcpy.da.SearchCursor(feature_class, lista_campos) as cursor:
            for fila in cursor:
                # ? La función enumerate enumera el número de elementos dentro de una lista. Como resultado,
                # ? solo usando la función genera una tupla de elementos. La tupla se puede desempaquetar en 
                # ? cada uno de los elementos de la tupla, por eso a continuación se usa i (contador), valor, 
                # ? elemento de la lista.
                # TODO: Aquí, valor representa cada registro de cada columna.
                for i, valor in enumerate(fila):
                    if valor is not None and valor != "":
                        # ? Se actualiza el diccionario, teniendo en cuenta su posición, marcada por el contador
                        # ? dentro del diccionario creado anteriormente. Recordar que lo localizado entre [] es 
                        # ? el key del diccionario.
                        # TODO: Si alguno de los registros cumple con el condicional, es decir, no está vacío
                        # TODO: dentro del diccionario se marca como false (falso).
                        campos_vacios[lista_campos[i]] = False
                        
        # ** Filtrar los campos que están completamente vacíos (valor = True) y mostrar los resultados
        # ! Por notación, al parecer 'if vacio' significa [valor = True]
        # ? Se identifican, dentro del diccionario y se extran a una lista los campos totalmente vacíos.
        campos_completamente_vacios = [campo for campo, vacio in campos_vacios.items() if vacio]

        # ** Construcción del diccionario para la eliminación de campos vacíos
        diccionario = {}
        for valor in campos_completamente_vacios:
            if feature_class not in diccionario:
                diccionario[feature_class] = [valor]
            else: 
                diccionario[feature_class].append(valor)            
        
        # ** Convertir el diccionario a DataFrame y exportar a csv
        # ? Se crea dataframe a partir del diccionario previamente creado.
        df = pd.DataFrame.from_dict(diccionario)
        # ? Se resetean índices antes de generar archivo de texto plano.
        df.reset_index()
        # ? Se verifican y filtran solo los dataframes con columnas vacias (dataframes vacíos)
        if df.empty:            
            pass
        else:
            ruta_texto = str(os.path.join(ruta, feature_class)) + '.csv'    
            df.to_csv(ruta_texto)
                
        return diccionario
    
    except Exception as e:
        print(e)

# ? Código para ejecutar la función sin necesidad de ser llamada en otro Script. 
if __name__ == "__main__":
    # ! Prueba
    # feature_class = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\_7_GDBs\Producto_Cartografico.gdb\Insumos_Diagnostico\Zonas_Identificadas_Inventariadas_Restaurar_Cuenca_del_Rio_Bogota"
    # ruta = r"D:\PUBLIC\PGAR\Resultados\4.PRO\PGAR\_10_Geoprocesos\Insumos_Diagnostico_Campos_Vacios"
    # identificar_campos_vacios(feature_class, ruta)
    print("Este script requiere ingresar algunos parámetros")