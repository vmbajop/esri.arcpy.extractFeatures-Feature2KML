import arcpy
import os
import datetime
""" PARAMETROS """
capa_entrada = arcpy.GetParameterAsText(0)
campo_nombre = arcpy.GetParameterAsText(1)
""" CONSTANTES """
nombre_carpeta_resultado = "resultados"
nombre_capa_temporal = "capa_temporal"
nombre_capa_salida = "Fronteras_"
""" ----------------- """
""" OTRAS HIERBAS """
proyecto = arcpy.mp.ArcGISProject("CURRENT")
mapa = proyecto.listMaps()[0]
ruta_proyecto = proyecto.filePath
carpeta_resultado = os.path.join(os.path.dirname(ruta_proyecto), nombre_carpeta_resultado)
numero_registros = arcpy.management.GetCount(capa_entrada)
""" ----------------- """
arcpy.AddMessage("\nRuta de creación de los nuevos KML: "
                 + carpeta_resultado + ".\n"
                 + "Se crearán " + str(numero_registros) + " capas a partir del mismo número de registros de la capa de entrada.")
# Control de la existencia previa de una carpeta con resultados
if os.path.exists(carpeta_resultado):
    contenido = os.listdir(carpeta_resultado)
    if contenido:
        dp = os.path.dirname(carpeta_resultado)
        fh = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        nuevo_nombre = f"{nombre_carpeta_resultado}_{fh}"
        nueva_ruta = os.path.join(dp, nuevo_nombre)
        os.rename(nombre_carpeta_resultado, nueva_ruta)
        arcpy.AddWarning("\nExiste una carpeta con el nombre " + nombre_carpeta_resultado
                         + " que tiene contenido. Para no perder este contenido, se ha renombrada como " + nuevo_nombre)
        os.makedirs(carpeta_resultado)
        arcpy.AddMessage("\nSe ha creado la carpeta " + nombre_carpeta_resultado)
    else:
        arcpy.AddMessage("\nLa carpeta existe, está vacía y se va a reutilizar")
else:
    os.makedirs(carpeta_resultado)
    arcpy.AddMessage("\nSe ha creado la carpeta " + nombre_carpeta_resultado)
# ---------------------------------------------------------------------------
for capa in mapa.listLayers():
    if capa.name == nombre_capa_temporal:
        mapa.removeLayer(capa)
        arcpy.AddMessage("Eliminada una capa con nombre " + nombre_capa_temporal)
arcpy.AddMessage("\nComprobados los nombres de todas las capas del mapa.")    
with arcpy.da.SearchCursor(capa_entrada, ['OID@', campo_nombre]) as cursor:
    arcpy.AddMessage("\nComienza el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now()))
    i = 1
    for row in cursor:
        sql = f"OBJECTID = {row[0]}"
        arcpy.management.MakeFeatureLayer(capa_entrada, nombre_capa_temporal, sql)
        nombre_kml = nombre_capa_salida + f"{row[1]}" + ".kml"
        # Comprobar si existe el nombre y renombrar
        count = 1
        while arcpy.Exists(os.path.join(carpeta_resultado, nombre_kml)):
            nombre_kml = nombre_capa_salida + f"{row[1]}"+ str(count) + ".kml"
            count += 1
        # -----------------------------------------
        arcpy.conversion.LayerToKML(nombre_capa_temporal, carpeta_resultado + "\\" + nombre_kml)
        arcpy.management.Delete(nombre_capa_temporal)
        ''' fraccion = round((i / numero_registros) * 100, 1) '''
        arcpy.AddMessage("Procesado: " + str(i) + " de " + str(numero_registros))
        i = i + 1
    arcpy.AddMessage("Finalizado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now()) + "\n")
  
