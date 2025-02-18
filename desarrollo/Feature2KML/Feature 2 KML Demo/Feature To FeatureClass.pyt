import arcpy
import os
import datetime

class Toolbox(object):
    def __init__(self):
        self.name = "Extraer Features"
        self.label = "Extraer Features"
        self.alias = "ExtraerFeatures"

        self.description = "Extraer entidades de una capa a una nueva capa por cada entidad."

        # Lista de tools en la toolbox

        self.tools = [FeatureToKML]

class FeatureToKML(object):
    def __init__(self):
        self.name = "Feature To KML"
        self.label = "Feature To KML"
        self.alias = "Feature2KML"
        self.description = "Extraer entidades de una capa para crear una nueva capa KML por cada entidad, que tendrá por nombre el valor de un campo elegido por el usuario."
        # self.description = "A partir de una capa, toma cada feature una por una y crea una capa de tipo KML para cada una"
        self.canRunInBackground = False

        #-------------------------------------
        # propiedades parametrizables
        #-------------------------------------
        self.nombre_carpeta_resultado = "resultados"
        self.nombre_capa_temporal = "capa_temporal"
        # self.nombre_capa_salida = "Fronteras_"
        self.salto_mensaje_porcentajes = 5

        #-------------------------------------
        # constantes
        #-------------------------------------
        self.proyecto = arcpy.mp.ArcGISProject("CURRENT")
        self.mapa = self.proyecto.listMaps()[0]
        self.ruta_proyecto = self.proyecto.filePath
        self.carpeta_resultado = os.path.join(os.path.dirname(self.ruta_proyecto), self.nombre_carpeta_resultado)        
         #-------------------------------------

    def getParameterInfo(self):
        """Define the tool parameters."""
        capa_entrada = arcpy.Parameter(
            name="InputFeatureLayer",
            displayName="Capa de entrada",
            direction="Input",
            parameterType="Required",
            datatype="GPFeatureLayer"
        )

        campo_nombre = arcpy.Parameter(
            name="CampoIdentificativo",
            displayName="Campo identificativo",
            direction="Input",
            parameterType="Required",
            datatype="Field"
        )
        campo_nombre.parameterDependencies = [capa_entrada.name]
        campo_nombre.filter.list = ["Text", "OID", "GUID", "GlobalID", "Date", "TimeOnly", "DateOnly", "TimestampOffset"]

        nombre_capa_salida = arcpy.Parameter(
            name="EncabezadoNombre",
            displayName="Encabezado del nombre de salida",
            direction="Input",
            parameterType="Optional",
            datatype="GPString"
        )
        nombre_capa_salida.value = "ExtraccionesKML_"

        params =[capa_entrada, campo_nombre, nombre_capa_salida]
        return params

    def execute(self, parameters, messages):
        try:
            self.numero_registros = arcpy.management.GetCount(parameters[0].value)
            self.numero_registros_int = int(self.numero_registros.getOutput(0))

            self.ComprobarExistenciaCapaTemporalTOC()
            self.ComprobarExistenciaCarpetaPrevia()

            self.ExtraerFeature2KML(parameters)
        except:
            arcpy.AddError("ERROR En EXECUTE")
    
    def ComprobarExistenciaCapaTemporalTOC(self):
        for capa in self.mapa.listLayers():
            if capa.name == self.nombre_capa_temporal:
                self.mapa.removeLayer(capa)
                arcpy.AddMessage("Eliminada una capa con nombre " + self.nombre_capa_temporal)
        arcpy.AddMessage("\nComprobada la existencia de una capa temporal previa.")

    def ComprobarExistenciaCarpetaPrevia(self):
        try:
            if os.path.exists(self.carpeta_resultado):
                contenido = os.listdir(self.carpeta_resultado)
                if contenido:
                    dp = os.path.dirname(self.carpeta_resultado)
                    fh = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    nuevo_nombre = f"{self.nombre_carpeta_resultado}_{fh}"
                    nueva_ruta = os.path.join(dp, nuevo_nombre)
                    os.rename(self.nombre_carpeta_resultado, nueva_ruta)
                    arcpy.AddWarning("\nExiste una carpeta con el nombre " + self.nombre_carpeta_resultado
                                    + " que tiene contenido. Para no perder este contenido, se ha renombrada como " + nuevo_nombre)
                    os.makedirs(self.carpeta_resultado)
                    arcpy.AddMessage("\nSe ha creado la carpeta " + self.nombre_carpeta_resultado)
                else:
                    arcpy.AddMessage("\nLa carpeta existe, está vacía y se va a reutilizar")
            else:
                os.makedirs(self.carpeta_resultado)
                arcpy.AddMessage("\nSe ha creado la carpeta " + self.nombre_carpeta_resultado)
        except:
            arcpy.AddError("ERROR En COMPROBAR CARPETA")

    def ExtraerFeature2KML(self, parameters):
        try:
            with arcpy.da.SearchCursor(parameters[0].value, ['OID@', parameters[1].valueAsText]) as cursor:
                arcpy.AddMessage("\nIniciado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
                i = 1
                fraccion_aux = 0
                for row in cursor:
                    sql = f"OBJECTID = {row[0]}"
                    arcpy.management.MakeFeatureLayer(parameters[0].value, self.nombre_capa_temporal, sql)
                    nombre_kml = parameters[2].valueAsText + f"{row[1]}" + ".kml"
                    # Comprobar si existe el nombre y renombrar
                    count = 1
                    while arcpy.Exists(os.path.join(self.carpeta_resultado, nombre_kml)):
                        nombre_kml = parameters[2].valueAsText + f"{row[1]}"+ str(count) + ".kml"
                        count += 1
                    # -----------------------------------------
                    arcpy.conversion.LayerToKML(self.nombre_capa_temporal, self.carpeta_resultado + "\\" + nombre_kml)
                    arcpy.management.Delete(self.nombre_capa_temporal)
                    
                    # arcpy.AddMessage("Procesado: " + str(i) + " de " + str(numero_registros))
                    fraccion = round((i / self.numero_registros_int) * 100, 1)
                    if fraccion_aux == 0 or fraccion > fraccion_aux + self.salto_mensaje_porcentajes or fraccion >= 100:
                        arcpy.AddMessage("Procesado el " + str(fraccion) + "% de los registros")
                        fraccion_aux = fraccion
                    i = i + 1
                arcpy.AddMessage("Finalizado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
        except:
            arcpy.AddError("ERROR En la extraccion de entidad a capa")