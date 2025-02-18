import arcpy
message = arcpy.GetParameterAsText(0)
arcpy.AddMessage("{0}".format(message))
