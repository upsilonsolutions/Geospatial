// By Muhammad Ali 77.muhammadali@gmail.com	

import arcpy
import uuid

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "LCCS Toolbox - Gap Topology"
        self.alias = "LCCS Toolbox - Gap Topology"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LCCS Toolbox - Gap Topology"
        self.description = "This tool finds and resolves the gap topological errors. Developed by: Manager, Muhammad Ali | Trg R&D Dte, SAR Wing, SUPARCO HQ."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        param0 = arcpy.Parameter(
            displayName="Input Feature (from gdb)",
            name="in_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param1 = arcpy.Parameter(
           displayName="Mask File(from gdb)",
            name="mask_features",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input")
        
        param2 = arcpy.Parameter(
        displayName="Output Features",
        name="out_features",
        datatype="DEFeatureClass",
        parameterType="Required",
        direction="Output")

        params = [param0,param1,param2]
        
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        import os
        import sys
        import shutil
        inFeatures      = parameters[0].valueAsText
        maskFile = parameters[1].valueAsText
        outFeatureClass = parameters[2].valueAsText
       
        
        
        dirName =  os.path.splitdrive(outFeatureClass)[0] + "/LCCSTopology"
        arcpy.AddMessage("directory:   " + dirName )
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        dirName =  os.path.splitdrive(outFeatureClass)[0]+  "/LCCSTopology/" + str(uuid.uuid1())
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
        arcpy.AddMessage("Old Directory :" + dirName +  " Remove ")
        os.mkdir(dirName)
        arcpy.AddMessage("New Directory :" + dirName +  " Created ")
        
        #   arcpy.Dissolve_management(inFeatures,dirName + "/dissolve.shp","","","SINGLE_PART","DISSOLVE_LINES")
        arcpy.Erase_analysis(maskFile,inFeatures,dirName + "/Erase.shp")
        arcpy.MultipartToSinglepart_management(dirName + "/Erase.shp",dirName + "/multipart.shp")
        arcpy.Union_analysis([inFeatures,dirName + "/multipart.shp"],dirName + "/union.shp","ALL",0.01,"GAPS")
	arcpy.AddMessage("Layer creation for Selection... " )
	arcpy.AddField_management(dirName + "/union.shp","AreaInSqM","DOUBLE")
	expression1 = "{0}".format("!SHAPE.area@SQUAREMETERS!")
	arcpy.CalculateField_management(dirName + "/union.shp","AreaInSqM",expression1,"PYTHON")
        arcpy.MakeFeatureLayer_management(dirName + "/union.shp","tempSelection")
        arcpy.AddMessage("Selection of empty features which are less than 4000 sq KM" )
        arcpy.SelectLayerByAttribute_management("tempSelection","NEW_SELECTION","(LCCS = '' or LCCS IS NULL) AND AreaInSqM <4000")
        arcpy.AddMessage("Eliminate tool Start working... " )
        arcpy.Eliminate_management("tempSelection",outFeatureClass,"LENGTH")
        arcpy.AddMessage("Eliminate tool Finished working... " )
	mxd = arcpy.mapping.MapDocument("CURRENT")
	df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
	newlayer = arcpy.mapping.Layer(outFeatureClass)
	arcpy.mapping.AddLayer(df, newlayer,"TOP")
        arcpy.AddMessage("output layer added... " )
        arcpy.Delete_management('tempSelection', 'Layer')

        
	if os.path.exists(dirName):
            shutil.rmtree(dirName)
        arcpy.AddMessage("Temp Directory " + dirName +  " Remove ")

        return
