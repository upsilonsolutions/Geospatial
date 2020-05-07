import arcpy
import uuid

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "LCCS Toolbox - Overlap Topology"
        self.alias = "LCCS Toolbox - Overlap Topology"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "LCCS Toolbox - Overlap Topology"
        self.description = "This tool finds and resolves the polygon overlapping topological errors. Developed by: Manager, Muhammad Ali | Trg R&D Dte, SAR Wing, SUPARCO HQ."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        param0 = arcpy.Parameter(
            displayName="Input Feature (from gdb)",
            name="in_features",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input")
        param1 = arcpy.Parameter(
        displayName="Output Features",
        name="out_features",
        datatype="GPFeatureLayer",
        parameterType="Required",
        direction="Output")

        param2 = arcpy.Parameter(
        displayName="Column Name which contains mapping Codes (LCCS3 - Bui, NvM)",
        name="lccs_col_name",
        datatype="String",
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
        outFeatureClass = parameters[1].valueAsText
        ClassFeildName = parameters[2].valueAsText
        
        dirName =  os.path.splitdrive(outFeatureClass)[0] + "/LCCSTopology"
        arcpy.AddMessage("directory:" + dirName +  " testing..  ")
        if not os.path.exists(dirName):
            os.mkdir(dirName)
        dirName =  os.path.splitdrive(outFeatureClass)[0]+  "/LCCSTopology/" + str(uuid.uuid1())
        if os.path.exists(dirName):
            shutil.rmtree(dirName)
        arcpy.AddMessage("Old Directory :" + dirName +  " Remove ")
        os.mkdir(dirName)
        arcpy.AddMessage("New Directory :" + dirName +  " Created ")
        
        arcpy.env.workspace = inFeatures.split('.gdb')[0] + ".gdb"
        featureName = inFeatures.split('.gdb')[1].split("\\")[len(inFeatures.split('.gdb')[1].split("\\"))-1]
	arcpy.Intersect_analysis(featureName + " #", dirName + "/Intersect_Analysis.shp","ALL","#","INPUT")
	arcpy.MultipartToSinglepart_management(dirName + "/Intersect_Analysis.shp",dirName + "/multipartSinglePart.shp")
	arcpy.Dissolve_management(dirName + "/multipartSinglePart.shp",dirName + "/dissolved.shp","#","#","SINGLE_PART","DISSOLVE_LINES")
	arcpy.Erase_analysis(featureName,dirName + "/dissolved.shp",dirName + "/erased.shp","#")
        fields = arcpy.ListFields(dirName + "/multipartSinglePart.shp")
        for field in fields:
            if field.name == "FID" or field.name == "Shape" or field.name == "ORIG_FID":
                print('Field not remove : ' + field.name)
            else:
                arcpy.DeleteField_management(dirName + "/multipartSinglePart.shp", [field.name])
        
	arcpy.SpatialJoin_analysis(dirName + "/multipartSinglePart.shp",dirName + "/erased.shp",dirName + "/sj_1.shp","JOIN_ONE_TO_ONE","KEEP_ALL")
	arcpy.Merge_management(dirName + "/sj_1.shp;"+dirName + "/erased.shp",dirName + "/merge_1.shp")
	arcpy.Dissolve_management(dirName + "/merge_1.shp",outFeatureClass,ClassFeildName,"#","SINGLE_PART","DISSOLVE_LINES")
	# get the map document
	mxd = arcpy.mapping.MapDocument("CURRENT")
	# get the data frame
	df = arcpy.mapping.ListDataFrames(mxd,"*")[0]
	# create a new layer
	newlayer = arcpy.mapping.Layer(outFeatureClass)
	# add the layer to the map at the bottom of the TOC in data frame 0
	arcpy.mapping.AddLayer(df, newlayer,"TOP")

	if os.path.exists(dirName):
            shutil.rmtree(dirName)
        arcpy.AddMessage("Temp Directory " + dirName +  " Remove ")

        return
