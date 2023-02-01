import os
import arcpy

analisis_vulnerabilidad_riesgo = ['_10_Analisis_Vulnerabilidad_Riesgo_Inundacion',
                                  '_11_Analisis_Vulnerabilidad_Riesgo_Incendio',
                                  '_12_Analisis_Vulnerabilidad_Riesgo_Avenida_Torrencial',
                                  '_13_Analisis_Vulnerabilidad_Riesgo_Remocion_Masa']

for avr in analisis_vulnerabilidad_riesgo:

    ruta_geojson = 'D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/' + avr
    arcpy.env.workspace = r"D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/" + avr + "/" + avr + ".gdb"

    ruta_vulnerabilidad_urbana = r"D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/" + avr + "\\" + avr + ".gdb" + "\\Vulnerabilidad_Urbana"
    ruta_vulnerabilidad_rural = r"D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/" + avr + "\\" + avr + ".gdb" + "\\Vulnerabilidad_Rural"

    ruta_amenaza_urbano = r"D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/" + avr + "\\" + avr + ".gdb" + "\\Amenaza_Urbano"
    ruta_amenaza_rural = r"D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/" + avr + "\\" + avr + ".gdb" + "\\Amenaza_Rural"

    ruta_riesgo_urbano = r"D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/" + avr + "\\" + avr + ".gdb" + "\\Riesgo_Urbano"
    ruta_riesgo_rural = r"D:/PUBLIC/PGAR/Insumos/Capas_Geograficas/" + avr + "\\" + avr + ".gdb" + "\\Riesgo_Rural"

    # Creación de Base de Datos
    if arcpy.Exists(arcpy.env.workspace):
        for capas in arcpy.ListFeatureClasses():
            arcpy.management.Delete(capas)
            print("Se borra la información registrada en la capa: {0}".format(capas))
    else:
        arcpy.management.CreateFileGDB(ruta_geojson, str(avr) + ".gdb")

    nombre_geojson = os.listdir(ruta_geojson)
    lista_ruta_archivo = []
    for rutas in nombre_geojson:
        lista_ruta_archivo.append(os.path.join(ruta_geojson, rutas))
        
    for generacion_feature in lista_ruta_archivo:
        nombre_geojson = os.path.split(generacion_feature)
        nombre_geojson_parametrizado = (nombre_geojson[1].split(".")[0]).replace(" ","_")
        if nombre_geojson_parametrizado != avr:
            salida_feature = os.path.join(arcpy.env.workspace, nombre_geojson_parametrizado)
            arcpy.conversion.JSONToFeatures(generacion_feature, salida_feature)
            print("geojson {0} convertido al feature {1}".format(nombre_geojson, nombre_geojson_parametrizado))
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
    
    capa_vulnerabilidad_urbana = 'Vulnerabilidad_Urbana'
    capa_vulnerabilidad_rural = 'Vulnerabilidad_Rural'
    capa_amenaza_urbano = 'Amenaza_Urbano'
    capa_amenaza_rural = 'Amenaza_Rural'
    capa_riesgo_urbano = 'Riesgo_Urbano'
    capa_riesgo_rural = 'Riesgo_Rural'

    lista_capas_vulnerabilidad_urbana = []
    lista_capas_vulnerabilidad_rural = []
    lista_capas_amenaza_urbano = []
    lista_capas_amenaza_rural = []
    lista_capas_riesgo_urbano = []
    lista_capas_riesgo_rural = []

    for features in lista_capas_convertidas:    
        if 'Vulnerabilidad_Urbano' in features:
            lista_capas_vulnerabilidad_urbana.append(features)
        elif 'Vulnerabilidad_Rural' in features:
            lista_capas_vulnerabilidad_rural.append(features)
        elif 'Amenaza_Urbano' in features:
            lista_capas_amenaza_urbano.append(features)
        elif 'Amenaza_Rural' in features:
            lista_capas_amenaza_rural.append(features)
        elif 'Riesgo_Urbano' in features:
            lista_capas_riesgo_urbano.append(features)
        elif 'Riesgo_Rural' in features:
            lista_capas_riesgo_rural.append(features)
        else:
            print("La capa {0}, no se unifico".format(features))
    
    print("----- INICIA PROCESO DEL MERGE -----")
    
    if len(lista_capas_vulnerabilidad_urbana) != 0:
        arcpy.management.Merge(lista_capas_vulnerabilidad_urbana, capa_vulnerabilidad_urbana)
        print("Capa unificada en {0}".format(capa_vulnerabilidad_urbana))
    else:
        print("No existe la capa")

    if len(lista_capas_vulnerabilidad_rural) != 0:
        arcpy.management.Merge(lista_capas_vulnerabilidad_rural, capa_vulnerabilidad_rural)
        print("Capa unificada en {0}".format(capa_vulnerabilidad_rural))
    else:
        print("No existe la capa")
        
    if len(lista_capas_amenaza_urbano) != 0:        
        arcpy.management.Merge(lista_capas_amenaza_urbano, capa_amenaza_urbano)
        print("Capa unificada en {0}".format(capa_amenaza_urbano))
    else:
        print("No existe la capa")
        
    if len(lista_capas_amenaza_rural) != 0:          
        arcpy.management.Merge(lista_capas_amenaza_rural, capa_amenaza_rural)
        print("Capa unificada en {0}".format(capa_amenaza_rural))
    else:
        print("No existe la capa")
        
    if len(lista_capas_riesgo_urbano) != 0:         
        arcpy.management.Merge(lista_capas_riesgo_urbano, capa_riesgo_urbano)
        print("Capa unificada en {0}".format(capa_riesgo_urbano))
    else:
        print("No existe la capa")

    if len(lista_capas_riesgo_rural) != 0:        
        arcpy.management.Merge(lista_capas_riesgo_rural, capa_riesgo_rural)
        print("Capa unificada en {0}".format(capa_riesgo_rural))
    else:
        print("No existe la capa")
           
    print(" -------------------------------------------------- FINALIZA {0} --------------------------------------------------".format(avr))