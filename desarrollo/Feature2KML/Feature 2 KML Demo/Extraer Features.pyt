'''FUENTES
Plantilla: https://pro.arcgis.com/en/pro-app/latest/arcpy/geoprocessing_and_python/a-template-for-python-toolboxes.htm'''

import arcpy
import os
import datetime

class Toolbox(object):
    def __init__(self):
        self.label = "Extraer Features"
        self.alias = "ExtraerFeatures"

        # Lista de tools en la toolbox

        self.tools = [FeatureToKML]

class FeatureToKML(object):
    def __init__(self):
        self.version = "1.5"
        # self.name = "FeatureToKML"
        self.label = "Feature To KML"
        self.alias = "Feature2KML"
        self.description = "Extraer entidades de una capa para crear una nueva capa KML por cada entidad, que tendrá por nombre el valor de un campo elegido por el usuario."
        self.canRunInBackground = False #da igual, no sirve de nada

        #-------------------------------------
        # propiedades parametrizables
        #-------------------------------------
        self.nombre_carpeta_resultado = "resultados"
        self.nombre_capa_temporal = "Fextraida_deFC"
        # self.nombre_capa_salida = "Fronteras_"
        self.salto_mensaje_porcentajes = 5

        #-------------------------------------
        # constantes
        #-------------------------------------
        proyecto = arcpy.mp.ArcGISProject("CURRENT")
        self.mapa = proyecto.listMaps()[0]
        ruta_proyecto = proyecto.filePath
        self.carpeta_resultado = os.path.join(os.path.dirname(ruta_proyecto), self.nombre_carpeta_resultado)
         #-------------------------------------
         
        self.mensajes = [""]
        self.mensajesError = [""]

    def getParameterInfo(self):
        """Define the tool parameters."""
        param0 = arcpy.Parameter(
            name="InputFeatureLayer",
            displayName="Capa de entrada",
            direction="Input",
            parameterType="Required",
            datatype="GPFeatureLayer"
        )

        param1 = arcpy.Parameter(
            name="CampoIdentificativo",
            displayName="Campo identificativo",
            direction="Input",
            parameterType="Required",
            datatype="Field"
        )
        param1.parameterDependencies = [param0.name]
        param1.filter.list = ["Text", "GUID", "GlobalID", "Date", "TimeOnly", "DateOnly", "TimestampOffset"]

        param2 = arcpy.Parameter(
            name="EncabezadoNombre",
            displayName="Encabezado del nombre de salida",
            direction="Input",
            parameterType="Optional",
            datatype="GPString"
        )
        param2.value = "ExtraccionesKML_"

        params =[param0, param1, param2]
        return params
    
# region NO USADOS
    def isLicensed(self): # Es opcional
        # La herramienta usada (arcpy.conversion.LayerToKML()) está disponible en Basic, por tanto siempre está licenciado
        return True
    
    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return
# endregion    

# region EXECUTE
    def execute(self, parameters, messages):
        arcpy.AddMessage(f"\n'{self.label}' version '{self.version}'")
        try:
            self.numero_registros = arcpy.management.GetCount(parameters[0].value)
            self.numero_registros_int = int(self.numero_registros.getOutput(0))

            self.ComprobarExistenciaCapaTemporalTOC()
            self.ComprobarExistenciaCarpetaResultados()

            self.ExtraerFeature2KML(parameters)
        except Exception as e:
            arcpy.AddError(f"ERROR En EXECUTE >>> '{e}")
    
    def ComprobarExistenciaCapaTemporalTOC(self):
        for capa in self.mapa.listLayers():
            if capa.name == self.nombre_capa_temporal:
                self.mapa.removeLayer(capa)
                arcpy.AddMessage(f"\nEliminada una capa con nombre '{self.nombre_capa_temporal}'")
        arcpy.AddMessage("\nComprobada la existencia de una capa temporal previa.")

    def ComprobarExistenciaCarpetaResultados(self):
        try:
            if os.path.exists(self.carpeta_resultado):
                if not os.listdir(self.carpeta_resultado):
                    arcpy.AddMessage(f"\nLa carpeta '{self.carpeta_resultado}' existe, está vacía y se va a reutilizar")
                else:
                    fh = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    nuevo_nombre = f"{self.nombre_carpeta_resultado}_{fh}"
                    nueva_ruta = os.path.join(os.path.dirname(self.carpeta_resultado), nuevo_nombre)
                    os.rename(self.carpeta_resultado, nueva_ruta)
                    arcpy.AddWarning(f"\nExiste una carpeta con el nombre '{self.nombre_carpeta_resultado}' con contenido, por lo que se ha renombrado como '{nuevo_nombre}'")
                    self.CrearCarpetaResultados()
            else:
                self.CrearCarpetaResultados()
            
        except Exception as e:
            arcpy.AddError(f"ERROR En COMPROBAR CARPETA >>> '{e}'")

    def CrearCarpetaResultados(self):
        os.makedirs(self.carpeta_resultado)
        arcpy.AddMessage(f"\nSe ha creado la carpeta '{self.nombre_carpeta_resultado}'")

    def ExtraerFeature2KML(self, parameters):
        try:
            capa_entrada = parameters[0].value
            campo_nombre = parameters[1].valueAsText
            prenombre_capa_salida = parameters[2].valueAsText
            arcpy.SetProgressor("step", "Procesando registros...", 0, self.numero_registros_int, 1)

            with arcpy.da.SearchCursor(capa_entrada, ['OID@', campo_nombre]) as cursor:
                arcpy.AddMessage("\nIniciado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")))
                arcpy.AddMessage(f"\nSe van a extraer '{self.numero_registros_int}' registros, creando el mismo número de capas en '{self.nombre_carpeta_resultado}'")
                i = 1
                # fraccion_aux = 0
                for row in cursor:
                    sql = f"OBJECTID = {row[0]}"
                    arcpy.management.MakeFeatureLayer(capa_entrada, self.nombre_capa_temporal, sql)
                    nombre_kml = prenombre_capa_salida + f"{row[1]}" + ".kml"
                    # Comprobar si existe el nombre y renombrar añadiendo un numero si ya existe 
                    count = 1
                    while arcpy.Exists(os.path.join(self.carpeta_resultado, nombre_kml)):
                        nombre_kml = prenombre_capa_salida + f"{row[1]}"+ str(count) + ".kml"
                        count += 1
                    # -----------------------------------------
                    arcpy.conversion.LayerToKML(self.nombre_capa_temporal, self.carpeta_resultado + "\\" + nombre_kml)
                    arcpy.management.Delete(self.nombre_capa_temporal)

                    # Contador
                    arcpy.AddMessage(f"Creada la capa '{i}' de '{self.numero_registros_int}' >>> '{nombre_kml}'")
                    '''fraccion = round((i / self.numero_registros_int) * 100, 1)
                    if fraccion_aux == 1 or fraccion > fraccion_aux + self.salto_mensaje_porcentajes or fraccion >= 100:
                        arcpy.AddMessage("Procesado el " + str(fraccion) + "% de los registros")
                        fraccion_aux = fraccion'''
                    i = i + 1
                    # -----------------------------------------
                    arcpy.SetProgressorPosition()
                arcpy.AddMessage("Finalizado el proceso de creación de capas a partir de registros a las " + str(datetime.datetime.now().strftime("%H:%M:%S %d.%m.%Y")) + "\n")
        except Exception as e:
            arcpy.AddError(f"ERROR EN LA EXTRACCIÓN >>> '{e}")

# endregion

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return