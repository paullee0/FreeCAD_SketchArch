#***************************************************************************	
#*                                                                         *	
#*   Copyright (c) 2018 - 2022                                             *	
#*   Paul Lee <paullee0@gmail.com>                                         *	
#*                                                                         *	
#*   This program is free software; you can redistribute it and/or modify  *	
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *	
#*   as published by the Free Software Foundation; either version 2 of     *	
#*   the License, or (at your option) any later version.                   *	
#*   for detail see the LICENCE text file.                                 *	
#*                                                                         *	
#*   This program is distributed in the hope that it will be useful,       *	
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *	
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *	
#*   GNU Library General Public License for more details.                  *	
#*                                                                         *	
#*   You should have received a copy of the GNU Library General Public     *	
#*   License along with this program; if not, write to the Free Software   *	
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *	
#*   USA                                                                   *	
#*                                                                         *	
#***************************************************************************	
										
import FreeCAD, FreeCADGui, Sketcher, Part, Draft, DraftVecUtils		
import ArchComponent, ArchBuilding, ArchFloor, ArchAxis, ArchWall, ArchWindow	
import ArchSpace, ArchStairs, ArchSectionPlane					
										
import SketchArchIcon								
import SketchArchCommands							
										
# for ArchWindows								
from PySide.QtCore import QT_TRANSLATE_NOOP					
										
import math, time								
from PySide import QtGui, QtCore						
from FreeCAD import Vector							
App = FreeCAD									
Gui = FreeCADGui								
pi = math.pi									
zeroMM = FreeCAD.Units.Quantity('0mm')						
MM = FreeCAD.Units.Quantity('1mm')						
tolerance = 0.000000001								
										
										
										
#--------------------------------------------------------------------------#	
#                           Class Definition                               #	
#--------------------------------------------------------------------------#	
										
										
class ArchSketchObject:								
  def __init__(self, obj):							
      #self.Type = "ArchSketchObject"						
      pass									
										
										
class ArchSketch(ArchSketchObject):						
										
  ''' ArchSketch - Sketcher::SketchObjectPython for Architectural Layout '''	
										
  MasterSketchSubelementTags = [ "MasterSketchSubelementTag", "MasterSketchIntersectingSubelementTag" ]										
  SnapPresetDict = {'AxisStart':0.0, '1/4':0.25, '1/3':1/3, 'MidPoint':0.5, '2/3':2/3, '3/4':3/4, 'AxisEnd':1.0}								
										
  def __init__(self, obj):							
      ArchSketchObject.__init__(self, obj)					
										
      ''' call self.setProperties '''						
										
      self.setProperties(obj)							
      self.setPropertiesLinkCommon(obj)						
      self.initEditorMode(obj)							
      obj.ViewObject.Proxy=0							
      return None								
										
										
  def initEditorMode(self, obj):						
										
      ''' Set DispayMode for Data Properties in Combo View Editor '''		
										
      obj.setEditorMode("MapMode",1)						
      obj.setEditorMode("MapReversed",1)					
      obj.setEditorMode("Constraints",2)					
      obj.setEditorMode("Placement",1)						
										
										
  def setProperties(self, fp):							
										
      ''' Add self.properties '''						
										
      fp.Proxy = self								
      if not hasattr(self,"Type"):						
          self.Type = "ArchSketch"						
										
      if not hasattr(self,"clEdgeSameIndexFlat"):				
          self.clEdgeSameIndexFlat = []						
																	
																	
      ''' Added ArchSketch Properties '''												
																										
      if not hasattr(fp,"DetectRoom"):																						
          fp.addProperty("App::PropertyBool","DetectRoom","Added ArchSketch Properties",QT_TRANSLATE_NOOP("App::Property","Enable to detect rooms enclosed by edges/walls - For CellComplex object to work, the generated shape is not shown in the ArchSketch object, but shown by a CellComplex Object.  This make recompute of this object longer !"))												
      if not hasattr(fp,"CellComplexElements"):																					
          fp.addProperty('Part::PropertyPartShape', 'CellComplexElements', 'Added ArchSketch Properties', QT_TRANSLATE_NOOP("App::Property","The Shape of built CellComplexElements"),8)			
      if not hasattr(fp,"FloorHeight"):																						
          fp.addProperty("App::PropertyLength","FloorHeight","Added ArchSketch Properties","Global ArchSketch Floor to Next Floor Height")									
          fp.FloorHeight = 3000 * MM  # Default																					
																										
																										
  def setPropertiesLinkCommon(self, orgFp, linkFp=None, mode=None):		
      '''									
      Set properties which are :						
          1. common to ArchSketchObject & Arch Objects, and			
          2. required for Link of Arch Objects					
      mode='init', 'ODR' for different settings					
      '''									
										
      if linkFp:								
          fp = linkFp								
      else:									
          fp = orgFp								
										
      prop = fp.PropertiesList							
										
      for i in ArchSketch.MasterSketchSubelementTags:				
          if linkFp:  # no Proxy						
              if i not in prop:							
                  linkFp.addProperty("App::PropertyPythonObject", i)		
                  setattr(linkFp, i, str())					
          else:  # either ArchSketch or ArchObjects, should have Proxy		
              if isinstance(orgFp.Proxy, ArchSketch):				
                  if not hasattr(fp.Proxy, i): 					
                      setattr(orgFp.Proxy, i, str())				
              else:  # i.e. other ArchObjects					
                  if i not in prop:						
                      orgFp.addProperty("App::PropertyPythonObject", i)		
                      setattr(orgFp, i, str())					
      if "MasterSketchSubelementIndex" not in prop:																				
          fp.addProperty("App::PropertyInteger","MasterSketchSubelementIndex","Referenced Object","Index of MasterSketchSubelement to be synced on the fly.  For output only.", 8)				
          fp.setEditorMode("MasterSketchSubelementIndex",1)																			
      if "MasterSketchIntersectingSubelementIndex" not in prop:																			
          fp.addProperty("App::PropertyInteger","MasterSketchIntersectingSubelementIndex","Referenced Object","Index of MasterSketchInteresctingSubelement to be synced on the fly.  For output only.", 8)	
          fp.setEditorMode("MasterSketchIntersectingSubelementIndex",2)																		
										
      ''' Referenced Object '''							
										
      # "Host" for ArchSketch and Arch Equipment (currently all Objects calls except Window which has "Hosts")												
      if not isinstance(fp.getLinkedObject().Proxy, ArchWindow._Window):																
          if "Host" not in prop:																					
              fp.addProperty("App::PropertyLink","Host","Referenced Object","The object that host this object / this object attach to")									
      # "Hosts" for Window																						
      else:  																								
          if "Hosts" not in prop:																					
              fp.addProperty("App::PropertyLinkList","Hosts","Window",QT_TRANSLATE_NOOP("App::Property","The objects that host this window"))  # Arch Window's code					
																									
      if "MasterSketch" not in prop:																					
          fp.addProperty("App::PropertyLink","MasterSketch","Referenced Object","Master Sketch to Attach on")												
      if "MasterSketchSubelement" not in prop:																				
          fp.addProperty("App::PropertyString","MasterSketchSubelement","Referenced Object","Master Sketch Sub-Element to Attach on")									
      if "MasterSketchSubelementOffset" not in prop:																			
          fp.addProperty("App::PropertyDistance","MasterSketchSubelementOffset","Referenced Object","Master Sketch Sub-Element Attached Offset from Startpoint")					
      if "MasterSketchSubelementSnapPreset" not in prop:																		
          fp.addProperty("App::PropertyEnumeration","MasterSketchSubelementSnapPreset","Referenced Object","Preset Snap Offset from Axis Startpoint; will add ms-SubelementOffset Distance (mm)")	
          fp.MasterSketchSubelementSnapPreset = [ "AxisStart", "1/4", "1/3", "MidPoint", "2/3", "3/4", "AxisEnd", "CustomValue" ]									
      if "MasterSketchSubelementSnapCustom" not in prop:																		
          fp.addProperty("App::PropertyFloatConstraint", "MasterSketchSubelementSnapCustom", "Referenced Object", "Custom Value: 0 to 1, Start/EndPoint of Axis (Use formula for fraction e.g 2/11")	
          fp.MasterSketchSubelementSnapCustom = (0.0, 0.0, 1.0, 0.001) # (Default, Start, Finish, Step)												
      if "MasterSketchIntersectingSubelement" not in prop:																		
          fp.addProperty("App::PropertyString","MasterSketchIntersectingSubelement",															
                         "Referenced Object","Master Sketch Subelement Intersecting the Sub-Element Attached on")											
      if "AttachToSubelementOrOffset" not in prop:																			
          fp.addProperty("App::PropertyEnumeration","AttachToSubelementOrOffset","Referenced Object","Select MasterSketch Subelement or Specify Offset to Attach")					
          fp.AttachToSubelementOrOffset = [ "Attach To Edge & Alignment", "Attach to Edge", "Follow Only Offset XYZ & Rotation" ]									
      if "AttachmentOffsetXyzAndRotation" not in prop:																			
          fp.addProperty("App::PropertyPlacement","AttachmentOffsetXyzAndRotation","Referenced Object","Specify XYZ and Rotation Offset")								
      if "AttachmentOffsetExtraRotation" not in prop:																			
          fp.addProperty("App::PropertyEnumeration","AttachmentOffsetExtraRotation","Referenced Object","Extra Rotation about X, Y or Z Axis")								
          fp.AttachmentOffsetExtraRotation = [ "None", "X-Axis CW90", "X-Axis CCW90", "X-Axis CW180", "Y-Axis CW90", "Y-Axis CCW90", "Y-Axis CW180","Z-Axis CW90", "Z-Axis CCW90", "Z-Axis CW180"]	
      if "OriginOffsetXyzAndRotation" not in prop:																			
          fp.addProperty("App::PropertyPlacement","OriginOffsetXyzAndRotation","Referenced Object","Specify Origin's XYZ and Rotation Offset")								
      if "FlipOffsetOriginToOtherEnd" not in prop:																			
          fp.addProperty("App::PropertyBool","FlipOffsetOriginToOtherEnd","Referenced Object","Flip Offset Origin to Other End of Edge / Wall ")							
      if "Flip180Degree" not in prop:																					
          fp.addProperty("App::PropertyBool","Flip180Degree","Referenced Object","Flip Orientation 180 Degree / Inside-Outside / Front-Back")								
      if "OffsetFromIntersectingSubelement" not in prop:																		
          fp.addProperty("App::PropertyBool","OffsetFromIntersectingSubelement",															
                         "Referenced Object","Offset from the Master Sketch Subelement Intersecting the Sub-Element to Attached on")									
      if "AttachmentAlignment" not in prop:																				
          fp.addProperty("App::PropertyEnumeration","AttachmentAlignment","Referenced Object","If AttachToEdge&Alignment, Set (Wall)Left/Right to align to Edge of Wall")				
          fp.AttachmentAlignment = [ "WallLeft", "WallRight", "Left", "Right" ]																
          if isinstance(fp.getLinkedObject().Proxy, ArchWindow._Window):																
              fp.AttachmentAlignment = "WallLeft"  # default for Windows which have normal 0,1,0 so somehow set to ArchWindows (updated from to 'left' after orientation of 'left/right' changed )	
          else:  																							
              fp.AttachmentAlignment = "WallLeft"  # default for cases other than Windows														
      if fp.AttachmentAlignment in [ "Edge", "EdgeGroupWidthLeft", "EdgeGroupWidthRight" ]:														
          curAlign = fp.AttachmentAlignment																				
          fp.AttachmentAlignment = [ "WallLeft", "WallRight", "Left", "Right" ]																
          if curAlign == "Edge":																					
              fp.AttachmentAlignment = "Left"																				
          elif curAlign == "EdgeGroupWidthLeft":																			
              fp.AttachmentAlignment = "WallLeft"																			
          elif curAlign == "EdgeGroupWidthRight":																			
              fp.AttachmentAlignment = "WallRight"																			
          else:  # Should not happen																					
              fp.AttachmentAlignment = "Left"																				
      if "AttachmentAlignmentOffset" not in prop:																			
          fp.addProperty("App::PropertyDistance","AttachmentAlignmentOffset","Referenced Object","Set Offset from Edge / EdgeGroupWidth +ve Right / -ve Left")						
																									
      attachToAxisOrSketchExisting = None																				
      fpLinkedObject = fp.getLinkedObject() 																				
      if "AttachToAxisOrSketch" in prop:																				
          attachToAxisOrSketchExisting = fp.AttachToAxisOrSketch																	
      else:  # elif "AttachToAxisOrSketch" not in prop:																			
          fp.addProperty("App::PropertyEnumeration","AttachToAxisOrSketch","Referenced Object","Select Object Type to Attach on ")									
      if isinstance(fpLinkedObject.Proxy, ArchSketch):																			
          fp.AttachToAxisOrSketch = [ "Host", "Master Sketch", "Placement Axis" ]															
      else:  # i.e. other ArchObjects																					
          fp.AttachToAxisOrSketch = [ "None", "Host", "Master Sketch"]																	
																									
      # has existing selection																						
      if attachToAxisOrSketchExisting is not None:																			
          if attachToAxisOrSketchExisting == "Hosts":																			
              attachToAxisOrSketchExisting = "Host"  # Can attach to only 1 host															
          fp.AttachToAxisOrSketch = attachToAxisOrSketchExisting																	
																									
      # no existing selection, ie. newly added "AttachToAxisOrSketch" attribute																
      elif isinstance(fpLinkedObject.Proxy, ArchSketch):																		
          fp.AttachToAxisOrSketch = "Master Sketch"  # default option for ArchSketch + Link to ArchSketch												
																									
      else:  # other Arch Objects  # elif fpLinkedObject.Proxy.Type != "ArchSketch":															
          # currently only if fp is Window and mode is 'ODR', not to attach to Host or otherwise it would relocate to 1st edge										
          if mode == 'ODR':																						
              #if isinstance(fp.Proxy, ArchWindow._Window):																		
              if isinstance(fpLinkedObject.Proxy, ArchWindow._Window):																	
                  fp.AttachToAxisOrSketch = "None"																			
              else: 																							
                  pass  # currently no other ArchObjects use 'ODR'																	
          else:  # default 'ODR' (or None), i.e. if 																			
              fp.AttachToAxisOrSketch = "Host"  # default option for Arch Objects in general														
																									
																									
  def appLinkExecute(self, fp, linkFp, index, linkElement):			
      self.setPropertiesLinkCommon(fp, linkFp)					
      updateAttachmentOffset(fp, linkFp)					
										
										
  def execute(self, fp):							
										
      ''' Features to Run in Addition to Sketcher.execute() '''			
										
      normal = fp.getGlobalPlacement().Rotation.multVec(FreeCAD.Vector(0,0,1))	
										
      ''' (VII) - Update attachment angle and attachment point coordinate '''	
										
      updateAttachmentOffset(fp)						
										
										
      ''' (IX or XI) - Update the order of edges by getSortedClusters '''	
										
      self.updateSortedClustersEdgesOrder(fp)					
										
										
										
      ''' (X) - Instances fp.resolve / fp.recompute - '''			
										
      fp.solve()								
      fp.recompute()								
										
      if fp.DetectRoom:								
										
          bb = boundBoxShape(fp, 5000)						
          skEdges, skEdgesF = getSketchEdges(fp)				
          cutEdges = selfCutEdges(skEdges)					
          fragmentEdgesL = flattenEdLst(cutEdges)				
          import BOPTools.SplitAPI									
          regions = BOPTools.SplitAPI.slice(bb, fragmentEdgesL, 'Standard', tolerance = 0.0)		
          resultFaces = removeBBFace(bb, regions.SubShapes)  # assume to be faces			
          extv = normal.multiply(fp.FloorHeight)  # WallHeight+fp.SlabThickness				
          resultFacesRebased = []									
          for f in resultFaces:										
              f.Placement = f.Placement.multiply(fp.Placement)						
              resultFacesRebased.append(f)								
          solids = [f.extrude(extv) for f in resultFacesRebased]					
          solidsCmpd =  Part.Compound(solids)								
          fp.CellComplexElements = solidsCmpd								
										
										
  def updateSortedClustersEdgesOrder(self, fp):					
										
      clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex, clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat = getSketchSortedClEdgesOrder(fp)				
										
      self.clEdgePartnerIndex = clEdgePartnerIndex				
      self.clEdgeSameIndex = clEdgeSameIndex					
      self.clEdgeEqualIndex = clEdgeEqualIndex					
										
      self.clEdgePartnerIndexFlat = clEdgePartnerIndexFlat			
      self.clEdgeSameIndexFlat = clEdgeSameIndexFlat				
      self.clEdgeEqualIndexFlat = clEdgeEqualIndexFlat				
										
										
  def onChanged(self, fp, prop):						
      if prop in ["MasterSketch", "PlacementAxis", "AttachToAxisOrSketch"]:	
          changeAttachMode(fp, prop)						
										
										
  def callParentToRebuildMasterSketchTags(self, fp):				
      foundParentArchSketchNames = []						
      foundParentLnkArchSketchesNames = []					
      foundParentLnkArchSketches = []						
      foundParentArchWalls = []						
      foundParentArchObjectNames = []						
      foundParentArchObjects = []						
      for parent in fp.InList:							
          # Find ArchSketch							
          if Draft.getType(parent) == "ArchSketch":				
              if parent.MasterSketch == fp:					
                  # Prevent duplicate and run below multiple times		
                  if parent.Name not in foundParentArchSketchNames:		
                      foundParentArchSketchNames.append(parent.Name)		
          # Find Link of ArchSketch						
          elif Draft.getType(parent.getLinkedObject()) == "ArchSketch":		
              if parent.MasterSketch == fp:					
                  if parent.Name not in foundParentLnkArchSketchesNames:	
                      foundParentLnkArchSketchesNames.append(parent.Name)	
                      foundParentLnkArchSketches.append(parent)		
          # Find ArchWall to further find parents				
          elif hasattr(parent,'Base'):						
              if fp == parent.Base:						
                  if parent not in foundParentArchWalls:			
                      foundParentArchWalls.append(parent)			
      # Find ArchObject parents of ArchWall (Equipment, Window)		
      for wall in foundParentArchWalls:					
          for parent in wall.InList:						
              if hasattr(parent,'Hosts'):  # Windows (and others?)		
                  if wall in parent.Hosts:					
                      if parent.Name not in foundParentArchObjectNames:	
                          foundParentArchObjectNames.append(parent.Name)	
                          foundParentArchObjects.append(parent)		
              elif hasattr(parent,'Host'):  # (Lnk)Eqpt/Win (Lnk)AchrSketch	
                  if wall == parent.Host:					
                      if parent.Name not in foundParentArchObjectNames:	
                          foundParentArchObjectNames.append(parent.Name)	
                          foundParentArchObjects.append(parent)		
										
      # call ArchSketch parent							
      total = len(foundParentArchSketchNames)					
      for key, parentArchSketchName in enumerate(foundParentArchSketchNames):	
          parent = FreeCAD.ActiveDocument.getObject(parentArchSketchName)	
          parent.Proxy.setPropertiesLinkCommon(parent)				
										
          lite = True								
										
          if lite:								
              updatePropertiesLinkCommonODR(parent, None)			
										
      # call Link of ArchSketch parent						
      for lnkArchSketch in foundParentLnkArchSketches:				
          linkedObj = lnkArchSketch.getLinkedObject()				
          linkedObj.Proxy.setPropertiesLinkCommon(linkedObj, lnkArchSketch)	
          updatePropertiesLinkCommonODR(linkedObj, lnkArchSketch)		
										
      # call Arch Objects (& Link) (Equipment, Window)				
      for archObject in foundParentArchObjects:					
          if archObject.isDerivedFrom('App::Link'):				
              linkedObj = archObject.getLinkedObject()				
              linkedObjProxy = linkedObj.Proxy					
              ArchSketch.setPropertiesLinkCommon(linkedObjProxy, linkedObj, archObject, mode='ODR')	
              updatePropertiesLinkCommonODR(linkedObj, archObject)		
          else:									
              archObject.Proxy.onDocumentRestored(archObject)			
              updatePropertiesLinkCommonODR(archObject, None)			
										
										
  def getWidths(self, fp):							
  										
      ''' wrapper function for uniform format '''				
  										
      return self.getSortedClustersEdgesWidth(fp)				
										
										
  def getSortedClustersEdgesWidth(self, fp):					
										
      '''  This method check the SortedClusters-isSame-(flat)List (omitted	
           construction geometry), find the corresponding edgesWidth and make	
           a list of (WidthX, WidthX+1 ...) '''					
										
      '''  Options of data to store width (& other) information conceived	
										
           1st Option - Use self.widths: a Dict of { EdgeX : WidthX, ...}	
                        But when Sketch is edited with some edges deleted, the	
                        edges indexes change, the widths stored become wrong	
										
           2nd Option - Use abdullah's edge geometry				
                        .... bugs found, not working yet			
										
           3rd Option - Use self.EdgeTagDictSync				
                        .... convoluted object sync, restoreOnLoad '''		
      return None								
										
										
  def getAligns(self, fp):							
  										
      ''' wrapper function for uniform format '''				
  										
      return self.getSortedClustersEdgesAlign(fp)				
										
										
  def getSortedClustersEdgesAlign(self, fp):					
      '''  									
           This method check the SortedClusters-isSame-(flat)List		
           find the corresponding edgesAlign ... 				
           and make a list of (AlignX, AlignX+1 ...)				
      '''									
      return None								
										
										
  def getEdgeTagIndex(self, fp, tag=None, index=None, useEdgeTagDictSyncFindIndex=False):		
    ''' Arguments	: fp, tag=None, index=None, useEdgeTagDictSyncFindIndex=False			
        Return		: index, tagSync (not tagInitial nor tagArchive...yet) '''			
													
													
    if tag and index is None:										
										
        if useEdgeTagDictSyncFindIndex == False:				
            i = 0								
            while True:								
                try:								
                    if tag == fp.Geometry[i].Tag:				
                        return i, None						
                except:								
                    print (" Debug - Tag does not (/no longer) exist " + "\n")	
                    return None, None						
                i += 1								
										
    elif not tag and index is not None:						
        try:									
            tagSync = fp.Geometry[index].Tag					
        except:									
            print("DEBUG - Index does not (or no longer?) exist ")		
            return None, None							
										
        return None, tagSync							
										
										
  def getEdgeGeom(self, fp, index):						
    return fp.Geometry[index]							
										
										
  #***************************************************************************#	
										
										
  '''  "ArchStructure"-related  '''						
										
										
  def getStructureBaseShapeWires(self, fp, role='slab', archsketchEdges=None ):									
      ''' Arguments	: fp, role, archsketchEdges (indexes of selected edges (or groups) caller force to use )				
          Return	: dict { 'slabWires' : slabWires, 'slabThickness' : slabThickness } '''							
																		
      slabDict = {}								
      slabEdgesList = []							
										
      # Get ArchSketch edges to construct ArchStructure				
      #										
      # Use inputed archsketchEdges if numeric, if available, as priority	
      if archsketchEdges:							
          for i in archsketchEdges:						
              if isinstance(i, int):						
              # TODO worth to add ? - Just for during onDocumentRestore() cornercase where Structure.ArchSketches is not turn into PropertyStringList from PropertyIntegerList		
                  i = str(i)							
              if i.isnumeric():							
                  slabEdgesList.append(int(i))					
										
										
      if not slabEdgesList:							
          return None								
										
      # Sort Sketch edges consistently with below procedures same as ArchWall	
										
      skGeomEdges = []								
      skPlacement = fp.Placement  # Get Sketch's placement to restore later	
      structureBaseShapeWires = []						
										
      for i in slabEdgesList:							
          skGeomI = self.getEdgeGeom(fp, i)					
										
          # support Line, Arc, Circle for Sketch as Base at the moment				
          if isinstance(skGeomI, (Part.LineSegment, Part.Circle, Part.ArcOfCircle)):		
              skGeomEdgesI = skGeomI.toShape()					
              skGeomEdges.append(skGeomEdgesI)					
										
      clusterTransformed = []							
      for cluster in Part.getSortedClusters(skGeomEdges):			
          edgesTransformed = []							
          for edge in cluster:							
              edge.Placement = edge.Placement.multiply(skPlacement)		
              edgesTransformed.append(edge)					
          clusterTransformed.append(edgesTransformed)				
										
      for clusterT in clusterTransformed:					
          structureBaseShapeWires.append(Part.Wire(clusterT))			
										
      return {'slabWires':structureBaseShapeWires, 'faceMaker':'Bullseye', 'slabThickness' : 250}	
										
										
  #***************************************************************************#	
										
										
  ''' onDocumentRestored '''							
										
										
  def onDocumentRestored(self, fp):						
										
      self.setProperties(fp)							
      self.setPropertiesLinkCommon(fp)						
      self.initEditorMode(fp)							
										
      ''' Rebuilding Tags  '''							
      self.callParentToRebuildMasterSketchTags(fp) # "Master"			
										
										
										
class Voxel:									
										
  def __init__(self, fp):							
      fp.Proxy = self								
      fp.ViewObject.Proxy=0							
										
      ''' call self.setProperties '''						
      self.setProperties(fp)							
										
  def setProperties(self, fp):							
      if not hasattr(fp,"InputShapeObj"):					
          fp.addProperty("App::PropertyLink","InputShapeObj","Voxel Properties","Input Object with Shape to calculate Voxel")					
      if not hasattr(fp,"VoxelObj"):																
          fp.addProperty("App::PropertyLink","VoxelObj","Voxel Properties","Input VoxelObj with Shape to calculate Voxel")					
																				
      if not hasattr(fp,"VoxelX"):																
          fp.addProperty("App::PropertyInteger","VoxelX","Voxel Properties","X Dimension of Voxel")								
          fp.VoxelX = 1000																	
      if not hasattr(fp,"VoxelY"):																
          fp.addProperty("App::PropertyInteger","VoxelY","Voxel Properties","Y Dimension of Voxel")								
          fp.VoxelY = 1000																	
      if not hasattr(fp,"VoxelZ"):																
          fp.addProperty("App::PropertyInteger","VoxelZ","Voxel Properties","Z Dimension of Voxel")								
          fp.VoxelZ = 1000																	
																				
      if not hasattr(fp,"Mode"):																
          fp.addProperty("App::PropertyEnumeration","Mode","Voxel Properties","Algorithm to deduce the disposition of Voxels in an Input Shape Object")		
          fp.Mode = ['Center', 'AnyCorner', 'AllCorners']													
          fp.Mode = 'Center'																	
																				
      if not hasattr(fp,"pList"):																
          fp.addProperty('App::PropertyPlacementList', 'pList', 'Referenced Object', 'Placement List of Voxels as calculated', 8)				
      if not hasattr(fp,"eCount"):																
          fp.addProperty('App::PropertyInteger', 'eCount', 'Referenced Object', 'Element Count of Voxels as calculated', 8)					
																				
  def onDocumentRestored(self, fp):																
      ''' call self.setProperties '''																
      self.setProperties(fp)																	
																				
  def execute(self, fp):																	
      if not fp.InputShapeObj:  # need a shape to calculate, otherwise no action										
          print (" no input shape ! ")																
          return																		
      lx = fp.VoxelX #1000																	
      ly = fp.VoxelY																		
      lz = fp.VoxelZ																		
																				
      pList, eCount = voxelise(fp.InputShapeObj, lx, ly, lz, mode=fp.Mode)											
      fp.pList = pList.copy() #self.pList = pList														
      fp.eCount = eCount																	
      boxList = []																		
																				
      if not fp.VoxelObj:																	
          b = Part.makeBox(lx, ly, lz) #, i.Base)														
          fp.Shape = b																		
      else:  # i.e. if fp.VoxelObj:																
          fp.Shape = fp.VoxelObj.Shape  # no need .copy()													
																				
																				
def voxelise(shapeObj, lx, ly, lz, mode='Center'):														
																				
      if not shapeObj:  # need a shape to calculate, otherwise no action											
          print (" no input shape ! ")																
          return																		
      pList = []  # reset to none																
      objxmin = shapeObj.Shape.BoundBox.XMin															
      objymin = shapeObj.Shape.BoundBox.YMin															
      objzmin = shapeObj.Shape.BoundBox.ZMin															
      objxl = shapeObj.Shape.BoundBox.XLength															
      objyl = shapeObj.Shape.BoundBox.YLength															
      objzl = shapeObj.Shape.BoundBox.ZLength															
																				
      xcount = math.ceil(objxl/lx)																
      ycount = math.ceil(objyl/ly)																
      zcount = math.ceil(objzl/lz)																
																				
      #count = 0																		
      for xx in range (0, xcount):																
          xp = objxmin + xx * lx																
          for yy in range(0, ycount):																
              yp = objymin + yy * ly																
              for zz in range(0, zcount):															
                  zp = objzmin + zz * lz															
                  if testVoxel(shapeObj, xp, yp, zp, lx, ly, lz, mode):												
                      pList.append(FreeCAD.Placement(FreeCAD.Vector(xp,yp,zp),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0)))					
      count = len(pList)																	
      return pList, count																	
																				
def testVoxel(shapeObj, xp, yp, zp, lx, ly, lz, mode='Center'):													
    if mode == 'Center':																	
        xpp = xp + lx/2																		
        ypp = yp + ly/2																		
        zpp = zp + lz/2																		
        if shapeObj.Shape.isInside(FreeCAD.Vector(xpp,ypp,zpp),tolerance,True):											
            return True																		
    elif mode == 'AnyCorner':																	
        for xc in range (0, 2):																	
            xpp = xp + xc * lx																	
            for yc in range (0, 2):																
                ypp = yp + yc * ly																
                for zc in range (0, 2):																
                    zpp = zp + zc * lz																
                    if shapeObj.Shape.isInside(FreeCAD.Vector(xpp,ypp,zpp),tolerance,True):									
                        return True																
    # Test all 8 'corners' of the 'voxel'															
    elif mode == 'AllCorners':																	
        for xc in range (0, 2):																	
            xpp = xp + xc * lx																	
            for yc in range (0, 2):																
                ypp = yp + yc * ly																
                for zc in range (0, 2):																
                    zpp = zp + zc * lz																
                    if not shapeObj.Shape.isInside(FreeCAD.Vector(xpp,ypp,zpp),tolerance,True):									
                        return False																
        else:  # i.e. when it is not returned above														
            return True																		
																				
																				
def makeVoxelPart(InputShapeObj, VoxelObj=None):														
  vp = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","VoxelPart")											
  vi = Voxel(vp)																		
  vp.InputShapeObj = InputShapeObj																
  if VoxelObj:																			
      vp.VoxelObj = VoxelObj																	
  vp.ViewObject.LineWidth = 1.00																
  vp.recompute()  # seems not working																
  return vp																			
					  															
					  															
class CellComplex:								
										
  def __init__(self, fp):							
      fp.Proxy = self								
      fp.ViewObject.Proxy=0							
										
      ''' call self.setProperties '''						
      self.setProperties(fp)							
										
  def setProperties(self, fp):							
      if not hasattr(fp,"InputShapeObj"):					
          fp.addProperty("App::PropertyLink","InputShapeObj","CellComplex Properties","Can select an Input Object with CellComplexElements before initial this command")	
																						
  def onDocumentRestored(self, fp):																		
      ''' call self.setProperties '''																		
      self.setProperties(fp)																			
										
  def execute(self, fp):							
      if fp.InputShapeObj:  #							
        if fp.InputShapeObj.CellComplexElements:				
              sh = Part.Shape(fp.InputShapeObj.CellComplexElements)		
              #pla = fp.InputShapeObj.Placement					
              fp.Shape = sh							
										
										
def makeCellComplex(InputShapeObj=None):					
  cc = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","CellComplex")	
  cci = CellComplex(cc)								
  if InputShapeObj:								
      cc.InputShapeObj = InputShapeObj						
  cc.ViewObject.LineWidth = 1.00						
  cc.ViewObject.Transparency = 60						
  return cc									
										
										
#---------------------------------------------------------------------------#	
#             FreeCAD Commands Classes & Associated Functions               #	
#---------------------------------------------------------------------------#	
										
class _CommandEditWallAlign():							
										
    '''Edit Wall Segment (Underlying [Arch]Sketch) Align Command Definition'''	
										
    def GetResources(self):							
        return {'Pixmap'  : SketchArchIcon.getIconPath()+'/icons/Edit_Align',	
                'Accel'   : "E, A",						
                'MenuText': "Edit Wall Segment Align",				
                'ToolTip' : "Select Wall/ArchSketch to Flip Segment Align ",	
                'CmdType' : "ForEdit"}						
										
    def IsActive(self):								
        return not FreeCAD.ActiveDocument is None				
										
    def Activated(self):							
        try:									
            sel0 = Gui.Selection.getSelection()[0]				
        except:									
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch ) or ArchSketch ")	
            return								
        targetObjectBase = None							
										
        if Draft.getType(sel0) not in ["Wall","ArchSketch"]:			
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch ) or ArchSketch ")	
            return								
        if hasattr(sel0, "Base"): # Wall has Base, ArchSketch does not		
            if sel0.Base:							
                targetObjectBase = sel0.Base					
            else:								
                reply = QtGui.QMessageBox.information(None,"","Arch Wall without Base is not supported - Select an Arch Wall ( with underlying Base ArchSketch or Sketch )")	
                return								
        else:									
            targetObjectBase = sel0						
            if Draft.getType(sel0.InList[0]) in ["Wall"]:			
                sel0 = sel0.InList[0]						
            else:								
                sel0 = None							
        if Draft.getType(targetObjectBase) in ['ArchSketch', 'Sketcher::SketchObject']:	
            if Draft.getType(targetObjectBase) == 'Sketcher::SketchObject':		
                reply = QtGui.QMessageBox.information(None,"","Multi-Align support Sketch with Part Geometry Extension (abdullah's development) / ArchSketch primarily.  Support on Sketch could only be done 'partially' (indexes of edges is disturbed if sketch is edited) until bug in Part Geometry Extension is fixed - currently for demonstration purpose.  Procced now. ")	
            elif Draft.getType(targetObjectBase) == 'ArchSketch':		
                reply = QtGui.QMessageBox.information(None,"","ArchSketch features being added, fallback to treat as Sketch if particular feature not implemented yet - currently for demonstration purpose.  Procced now. ")	
            targetObjectBase.ViewObject.HideDependent = False			
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")		
            Gui.ActiveDocument.setEdit(targetObjectBase)			
            App.Console.PrintMessage("Select target Edge of the ArchSketch / Sketch to Flip the corresponding Wall Segment Align "+ "\n")	
            FreeCADGui.Selection.clearSelection()				
            s=GuiEditWallAlignObserver(sel0, targetObjectBase)			
            self.observer = s							
            FreeCADGui.Selection.addObserver(s)					
        elif Draft.getType(targetObjectBase) == 'Wire':				
            reply = QtGui.QMessageBox.information(None,"","Gui to edit Arch Wall with a DWire Base is not implemented yet - Please directly edit ArchWall OverrideAlign attribute for the purpose.")	
										
										
FreeCADGui.addCommand('EditWallAlign', _CommandEditWallAlign())			
										
										
class GuiEditWallAlignObserver(SketchArchCommands.selectObjectObserver):	
										
    def __init__(self, targetWall, targetBaseSketch):				
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,'Edge')					
        self.targetWall = targetWall  # maybe None				
        self.targetArchSketch = targetBaseSketch  # maybe None			
        if self.targetWall:							
            self.targetWallTransparentcy = targetWall.ViewObject.Transparency	
            targetWall.ViewObject.Transparency = 60				
        if targetBaseSketch:							
            if Draft.getType(self.targetArchSketch) in ['Sketcher::SketchObject','ArchSketch']: 
                if self.targetWall:						
                    tempOverrideAlign = self.targetWall.OverrideAlign		
                    wallAlign = targetWall.Align # use Wall's Align		
                    # filling OverrideAlign if entry is missing for a particular index		
                    while len(tempOverrideAlign) < len(self.targetArchSketch.Geometry):	
                        tempOverrideAlign.append(wallAlign) #('Left')		
                    self.targetWall.OverrideAlign = tempOverrideAlign		
										
    def proceed(self, doc, obj, sub, pnt):					
        self.edge = sub								
        self.pickedEdgePlacement = App.Vector(pnt)				
        subIndex = int( sub.lstrip('Edge'))-1					
										
        if self.targetArchSketch is not None:					
            if Draft.getType(self.targetArchSketch)=='Sketcher::SketchObject':	
                print (" It is a Sketch")					
                curAlign = self.targetWall.OverrideAlign[subIndex]		
										
                if curAlign == 'Left':						
                    curAlign = 'Right'						
                elif curAlign == 'Right':					
                    curAlign = 'Center'						
                elif curAlign == 'Center':					
                    curAlign = 'Left'						
                else:	# 'Center' or else?					
                    curAlign = 'Right'						
										
                # Save information in ArchWall					
                if self.targetWall:						
                    tempOverrideAlign = self.targetWall.OverrideAlign		
                    tempOverrideAlign[subIndex] = curAlign			
                    self.targetWall.OverrideAlign = tempOverrideAlign		
										
            elif Draft.getType(self.targetArchSketch) == 'ArchSketch':		
                print (" It is an ArchSketch")					
                print (" Full Support not added currently yet !")		
                # TODO Test if particular ArchSketch feature has been implemented or not -  Fallback to use 'Sketch workflow' if Not	
                if not hasattr(self.targetArchSketch.Proxy, "getEdgeTagDictSyncAlign"):							
                    curAlign = self.targetWall.OverrideAlign[subIndex]		
                if curAlign == 'Left':						
                    curAlign = 'Right'						
                elif curAlign == 'Right':					
                    curAlign = 'Center'						
                elif curAlign == 'Center':					
                    curAlign = 'Left'						
                # Test if particular ArchSketch feature has been implemented or not -  Fallback to use 'Sketch workflow' if Not		
                # Save information in ArchWall												
                if not hasattr(self.targetArchSketch.Proxy, "getEdgeTagDictSyncAlign"):							
                    if self.targetWall:						
                        tempOverrideAlign = self.targetWall.OverrideAlign	
                        tempOverrideAlign[subIndex] = curAlign			
                if self.targetWall:						
                    self.targetWall.OverrideAlign = tempOverrideAlign		
        else:  									
            # nothing implemented if self.targetArchSketch is None		
            pass								
        if self.targetWall:							
            self.targetWall.recompute()						
										
    def escape(self,info):							
        k=info['Key']								
        if k=="ESCAPE":								
            self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy	
        SketchArchCommands.selectObjectObserver.escape(self,info)		
										
										
class _CommandEditWallWidth():							
										
    '''Edit Wall Segment (Underlying [Arch]Sketch) Width Command Definition'''	
										
    def GetResources(self):							
        return {'Pixmap'  : SketchArchIcon.getIconPath()+'/icons/Edit_Width',	
                'Accel'   : "E, W",						
                'MenuText': "Edit Wall Segment Width",				
                'ToolTip' : "select Wall to Edit Wall Segment Width ",		
                'CmdType' : "ForEdit"}						
										
    def IsActive(self):								
        return not FreeCAD.ActiveDocument is None				
										
    def Activated(self):							
        try:									
            sel0 = Gui.Selection.getSelection()[0]				
        except:									
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch ) or ArchSketch ")	
            return								
        targetObjectBase = None							
										
        if Draft.getType(sel0) not in ["Wall","ArchSketch"]:			
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch ) or ArchSketch ")	
            return								
										
        if hasattr(sel0, "Base"): # Wall has Base, ArchSketch does not		
            if sel0.Base:							
                targetObjectBase = sel0.Base					
            else:								
                reply = QtGui.QMessageBox.information(None,"","Arch Wall without Base is not supported - Select an Arch Wall ( with underlying Base ArchSketch or Sketch ) or ArchSketch")	
                return								
        else:									
            targetObjectBase = sel0						
            if Draft.getType(sel0.InList[0]) in ["Wall"]:			
                sel0 = sel0.InList[0]						
            else:								
                sel0 = None							
        if Draft.getType(targetObjectBase) in ['ArchSketch', 'Sketcher::SketchObject']:		
            if Draft.getType(targetObjectBase) == 'Sketcher::SketchObject':			
                reply = QtGui.QMessageBox.information(None,"","Multi-Width support Sketch with Part Geometry Extension (abdullah's development) / ArchSketch primarily.  Support on Sketch could only be done 'partially' (indexes of edges is disturbed if sketch is edited) until bug in Part Geometry Extension is fixed - currently for demonstration purpose.  Procced now. ")	
            elif Draft.getType(targetObjectBase) == 'ArchSketch':		
                reply = QtGui.QMessageBox.information(None,"","ArchSketch features being added, fallback to treat as Sketch if particular feature not implemented yet - currently for demonstration purpose.  Procced now. ")	
            targetObjectBase.ViewObject.HideDependent = False			
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")		
            Gui.ActiveDocument.setEdit(targetObjectBase)			
            App.Console.PrintMessage("Select target Edge of the ArchSketch / Sketch to Edit the corresponding Wall Segment Width "+ "\n")	
            FreeCADGui.Selection.clearSelection()				
            s=GuiEditWallWidthObserver(sel0, targetObjectBase)			
            self.observer = s							
            FreeCADGui.Selection.addObserver(s)					
										
        elif Draft.getType(targetObjectBase) == 'Wire':				
            reply = QtGui.QMessageBox.information(None,"","Gui to edit Arch Wall with a DWire Base is not implemented yet - Please directly edit ArchWall OverrideAlign attribute for the purpose.")	
										
FreeCADGui.addCommand('EditWallWidth', _CommandEditWallWidth())			
										
										
class GuiEditWallWidthObserver(SketchArchCommands.selectObjectObserver):	
										
    def __init__(self, targetWall, targetBaseSketch):				
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,'Edge')					
        self.targetWall = targetWall						
        self.targetArchSketch = targetBaseSketch				
        self.targetWallTransparentcy = targetWall.ViewObject.Transparency	
        targetWall.ViewObject.Transparency = 60					
        if targetBaseSketch:  # would be none ?					
            tempOverrideWidth = None						
            wallWidth = None							
            if not wallWidth:							
                wallWidth = targetWall.Width.Value  # use Wall's Width		
            if Draft.getType(self.targetArchSketch) == 'ArchSketch':					
                if hasattr(self.targetArchSketch.Proxy, "getUnsortedEdgesWidth"):			
                    tempOverrideWidth = targetBaseSketch.Proxy.getUnsortedEdgesWidth(targetBaseSketch)	
                    tempOverrideWidth = [i if i is not None else wallWidth for i in tempOverrideWidth]	
            if not tempOverrideWidth:						
                tempOverrideWidth = self.targetWall.OverrideWidth		
                # filling OverrideWidth for geometry edges		 	
                while len(tempOverrideWidth) < len(targetBaseSketch.Geometry):	
                    tempOverrideWidth.append(wallWidth)  #(0)			
                tempOverrideWidth = [i if i is not None else wallWidth for i in tempOverrideWidth]	
            self.targetWall.OverrideWidth = tempOverrideWidth						
													
    def proceed(self, doc, obj, sub, pnt):					
        self.edge = sub								
        self.pickedEdgePlacement = App.Vector(pnt)				
        subIndex = int( sub.lstrip('Edge'))-1					
        App.Console.PrintMessage("Input Width"+ "\n")				
        #if Draft.getType(self.targetArchSketch) == 'ArchSketch':		
        curWidth = None								
        if hasattr(self.targetArchSketch, "Proxy"):				
            if hasattr(self.targetArchSketch.Proxy, 'getEdgeTagDictSyncWidth'):					
                curWidth = self.targetArchSketch.Proxy.getEdgeTagDictSyncWidth(self.targetArchSketch, None, subIndex)	
        if not curWidth:												
            curWidth = self.targetWall.OverrideWidth[subIndex]								
        reply = QtGui.QInputDialog.getText(None, "Input Width","Width of Wall Segment", text=str(curWidth))		
        if reply[1]:  # user clicked OK						
            if reply[0]:							
                replyWidth = float(reply[0])					
            else:  # no input							
                return None							
        else:  # user clicked not OK, i.e. Cancel ?				
            return None								
        if self.targetArchSketch is not None:					
            if Draft.getType(self.targetArchSketch) == 'Sketcher::SketchObject':	
                # Save information in ArchWall					
                tempOverrideWidth = self.targetWall.OverrideWidth		
                tempOverrideWidth[subIndex] = replyWidth			
                self.targetWall.OverrideWidth = tempOverrideWidth		
            elif Draft.getType(self.targetArchSketch) == 'ArchSketch':		
                print (" It is an ArchSketch")					
                print (" Full Support not added currently yet !")		
                print (" Fallback to treat as Sketch as 'partial preview' if particular feature Not implemented in ArchSketch yet !")	
                # Save information in ArchWall												
                tempOverrideWidth = self.targetWall.OverrideWidth		
                tempOverrideWidth[subIndex] = replyWidth			
                self.targetWall.OverrideWidth = tempOverrideWidth		
        else:  									
            # nothing implemented if self.targetArchSketch is None		
            pass								
        self.targetWall.recompute()						
										
    def escape(self,info):							
        k=info['Key']								
        if k=="ESCAPE":								
            self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy	
        SketchArchCommands.selectObjectObserver.escape(self,info)		
										
										
class _CommandEditWallAttach():							
										
    '''Edit ArchSketch and ArchObjects Attachment Command Definition		
       edit attachment to Wall Segment (Underlying Arch]Sketch)'''		
										
    def GetResources(self):							
        return {'Pixmap'  : SketchArchIcon.getIconPath()+'/icons/Edit_Attach',	
                'Accel'   : "E, T",						
                'MenuText': "Edit Attachment",					
                'ToolTip' : "Select ArchSketch or Arch Window/Equipment (and optional a target) change attachment edge / to attach to a target ",	
                'CmdType' : "ForEdit"}						
										
    def IsActive(self):								
        return not FreeCAD.ActiveDocument is None				
										
    def Activated(self):							
        try:									
            sel0 = Gui.Selection.getSelection()[0]				
        except:									
            reply = QtGui.QMessageBox.information(None,"","Select an ArchSketch or Arch Window/Equipment, Click this Button, and select the edge to attach ")	
            return								
        try:									
            sel1 = Gui.Selection.getSelection()[1]				
        except:									
            sel1 = None								
										
        # If a Link is newly created and not Recomputed, its Hosts attribute is not added to the Link								
        # Now, if its Hosts[0] is assigned to the Sel1, then it is the Linked Object's Hosts attribute be altered						
        # The result is, instead of the Sel0 object got new Hosts[0] and attach to it,										
        # it is 'wrongly' the Linked Object (the 'Original') attach to new Hosts[0] !										
        # - Check and Recompute if State is Touched														
																				
        if "Touched" in sel0.State: #  == "Touched":  # State is a List												
            sel0.recompute()																	
																				
        targetHostWall = None																	
        targetBaseSketch = None																	
																				
        if Draft.getType(sel0.getLinkedObject()) not in ['ArchSketch','Window','Equipment']:									
            reply = QtGui.QMessageBox.information(None,"","Select an ArchSketch or Arch Window/Equipment, Click this Button, and select the edge to attach ")	
            return																		
        # check if targetHostWall is selected by user : selection take precedence 															
        if sel1:																							
            if Draft.getType(sel1) != 'Wall':																				
                reply = QtGui.QMessageBox.information(None,"","Target Object is Not Wall - Feature not supported 'Yet' ")										
                return																							
            else:																							
                targetHostWall = sel1																					
        # if no sel1: check if it was assigned -																			
        # or use Windows.Hosts / Equiptment.Host, i.e. not changing targetHostWall															
        # Window has Hosts, Equipment Host																				
        elif hasattr(sel0, "Host"):						
            if sel0.Host:							
                targetHostWall = sel0.Host					
        elif hasattr(sel0, "Hosts"):						
            if sel0.Hosts:							
                targetHostWall = sel0.Hosts[0]  # TODO to scan through ?	
        									
        if not targetHostWall:							
            if Draft.getType(sel0.getLinkedObject()) != 'ArchSketch':  # ArchSketch can has no hostWall / attach to (Arch)Sketch directly								
                reply = QtGui.QMessageBox.information(None,"","Select a Window/Equipment with Host which is Arch Wall (or Select a Window/Equipment with an ArchWall as 2nd selection)")		
                return																							
        elif Draft.getType(targetHostWall) != 'Wall':																			
            reply = QtGui.QMessageBox.information(None,"","Window/Equipment's Host needs to be a Wall to function")											
            return																							
															        									
        if targetHostWall:																						
            if targetHostWall.Base:																					
                targetBaseSketch = targetHostWall.Base																			
        elif hasattr(sel0, "MasterSketch"):																				
            if sel0.MasterSketch:																					
                targetBaseSketch = sel0.MasterSketch																			
        if not targetBaseSketch:																					
            reply = QtGui.QMessageBox.information(None,"","Wall needs to have Base which is to be Sketch or ArchSketch to function; ArchSketch needs to have a MasterSketch to function")		
            return																							
        if Draft.getType(targetBaseSketch) in ['ArchSketch', 'Sketcher::SketchObject']:				
            targetBaseSketch.ViewObject.HideDependent = False							
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")						
            Gui.ActiveDocument.setEdit(targetBaseSketch)							
            App.Console.PrintMessage("Select target Edge of the ArchSketch / Sketch to attach to "+ "\n")	
            FreeCADGui.Selection.clearSelection()								
            s=GuiEditWallAttachObserver(sel0, targetHostWall, targetBaseSketch)					
            self.observer = s											
            FreeCADGui.Selection.addObserver(s)									
        elif Draft.getType(targetBaseSketch) == 'Wire':								
            reply = QtGui.QMessageBox.information(None,"","Gui to edit Arch Wall with a DWire Base is not implemented yet - Please directly edit ArchWall OverrideAlign attribute for the purpose.")	
        else:																								
            reply = QtGui.QMessageBox.information(None,"","Wall needs to have Base which is to be Sketch or ArchSketch to function")									
            return																							
										
										
FreeCADGui.addCommand('EditWallAttach', _CommandEditWallAttach())		
										
										
class GuiEditWallAttachObserver(SketchArchCommands.selectObjectObserver):	
										
    def __init__(self, targetObject, targetHostWall, targetBaseSketch):	
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,'Edge')					
        self.targetObject = targetObject										
        self.targetWall = targetHostWall										
        self.targetArchSketch = targetBaseSketch									
        if self.targetWall:												
            self.targetWallTransparentcy=targetHostWall.ViewObject.Transparency						
            targetHostWall.ViewObject.Transparency = 60									
        if hasattr(targetObject, "Host"):										
            if targetObject.Host != targetHostWall:  # Testing For Host first						
                targetObject.Host = targetHostWall  # No recompute, save time						
        else:  # elif hasattr(targetObject, "Hosts"):									
            if targetObject.Hosts:											
                if targetObject.Hosts[0] != targetHostWall:  # Testing Host[0]						
                    targetObjectHosts = targetObject.Hosts								
                    targetObjectHosts[0] = targetHostWall  # replace 1st item						
                    targetObject.Hosts = targetObjectHosts								
            else:													
                targetObject.Hosts = [targetHostWall]									
            # Not recompute atm to save time										
        if targetHostWall:							
            # check if need to assign to attach to 'Host'			
            if targetObject.AttachToAxisOrSketch != 'Host':			
                targetObject.AttachToAxisOrSketch = 'Host'			
															
    def proceed(self, doc, obj, sub, pnt):										
        self.edge = sub								
        self.pickedEdgePlacement = App.Vector(pnt)				
        subElement = sub.lstrip('Edge')						
										
        if self.targetArchSketch is not None:					
            if Draft.getType(self.targetArchSketch)=='Sketcher::SketchObject':	
                print (" It is a Sketch")					
            elif Draft.getType(self.targetArchSketch) == 'ArchSketch':		
                print (" It is an ArchSketch")					
            self.targetObject.MasterSketchSubelement = subElement		
            # The Command/Observer find and assign the MasterSketchSubelementTag (instead of doing this by onChanged(), which does not exist e.g. for Link) 	
            geoindex = int(subElement.lstrip('Edge'))-1														
            none, tag = self.targetArchSketch.Proxy.getEdgeTagIndex(self.targetArchSketch, None, geoindex)							
            if not hasattr(self.targetObject, "Proxy"):  # i.e. Link		
                self.targetObject.MasterSketchSubelementTag = tag		
            elif self.targetObject.Proxy.Type != "ArchSketch":			
                # ArchObjects other than ArchSketchObjects			
                self.targetObject.MasterSketchSubelementTag = tag		
            else:								
                self.targetObject.Proxy.MasterSketchSubelementTag = tag	
        else:  								
            # nothing implemented if self.targetArchSketch is None		
            pass								
        self.targetObject.recompute()						
        if self.targetWall:							
            self.targetWall.recompute()					
										
    def escape(self,info):							
        k=info['Key']								
        if k=="ESCAPE":								
            if self.targetWall:											
                self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy				
        SketchArchCommands.selectObjectObserver.escape(self,info)						
										
										
class _CommandEditStructure():							
										
    '''Edit Structure (Underlying ArchSketch) Command Definition'''		
    '''Not supporting Sketch                                    '''		
    def GetResources(self):							
        return {'Pixmap'  : SketchArchIcon.getIconPath()+'/icons/Edit_Structure_Toggle.svg',	
                'Accel'   : "E, S",						
                'MenuText': "Edit Structure",					
                'ToolTip' : "Select Structure/ArchSketch to edit ",		
                'CmdType' : "ForEdit"}						
										
    def IsActive(self):								
        return not FreeCAD.ActiveDocument is None				
										
    def Activated(self):							
        try:									
            sel0 = Gui.Selection.getSelection()[0]				
        except:									
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Structure ( with underlying Base ArchSketch Sketch ) or ArchSketch ")	
            return								
        targetObjectBase = None							
										
        if Draft.getType(sel0) not in ["Structure"]:				
            if Draft.getType(sel0) in ["ArchSketch"]:				
                reply = QtGui.QMessageBox.information(None,"","Select an Arch Structure (with underlying Base ArchSketch Sketch) to Edit - Editing an ArchSketch directly would be implemented in due course")	
                return																								
            else:																								
                reply = QtGui.QMessageBox.information(None,"","Select an Arch Structure (with underlying Base ArchSketch Sketch) to Edit")									
                return																								
        if hasattr(sel0, "Base"): # Wall has Base, ArchSketch does not		
            if sel0.Base:							
                targetObjectBase = sel0.Base					
            else:								
                reply = QtGui.QMessageBox.information(None,"","Arch Structure without Base is not supported - Select an Arch Structure ( with underlying Base ArchSketch Sketch ) or ArchSketch ")	
                return								
        else:									
            targetObjectBase = sel0						
            if Draft.getType(sel0.InList[0]) in ["Structure"]:			
                sel0 = sel0.InList[0]						
            else:								
                sel0 = None							
        if Draft.getType(targetObjectBase) in ['ArchSketch']:			
            reply = QtGui.QMessageBox.information(None,"","ArchSketch features being added, fallback to treat as Sketch if particular feature not implemented yet - currently for demonstration purpose.  Procced now. ")	
            targetObjectBase.ViewObject.HideDependent = False			
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")		
            Gui.ActiveDocument.setEdit(targetObjectBase)			
            App.Console.PrintMessage("Select target Edge of the ArchSketch to turn it on/off as Structure edges "+ "\n")	
            FreeCADGui.Selection.clearSelection()				
            s=GuiEditStructureObserver(sel0, targetObjectBase)			
            self.observer = s							
            FreeCADGui.Selection.addObserver(s)					
										
										
FreeCADGui.addCommand('EditStructure', _CommandEditStructure())			
										
										
class GuiEditStructureObserver(SketchArchCommands.selectObjectObserver):	
										
    def __init__(self, targetStructure, targetBaseSketch):			
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,'Edge')	
        self.targetStructure = targetStructure  # maybe None				
        self.targetArchSketch = targetBaseSketch					
        if self.targetStructure:							
            self.targetStructureTransparency = targetStructure.ViewObject.Transparency	
            targetStructure.ViewObject.Transparency = 60			
										
    def proceed(self, doc, obj, sub, pnt):					
        self.edge = sub								
        self.pickedEdgePlacement = App.Vector(pnt)				
        subIndex = int( sub.lstrip('Edge'))-1					
        curStructureStatus = None						
        newStructureStatus = None						
										
        if hasattr(self.targetArchSketch.Proxy, 'getEdgeTagDictSyncStructureStatus'):	
            pass								
										
        else:									
            slabEdgesList = self.targetStructure.ArchSketchEdges		
            # 2 status :  True or Disabled (no False)				
            if str(subIndex) in slabEdgesList:					
                slabEdgesList.remove(str(subIndex))				
            else:								
                slabEdgesList.append(str(subIndex))				
            self.targetStructure.ArchSketchEdges = slabEdgesList		
										
        print (" ArchSketchEdge(s) assigned for Structure - ", slabEdgesList)	
        FreeCADGui.Selection.clearSelection()					
        if self.targetStructure:						
            self.targetStructure.recompute()					
										
    def escape(self,info):							
        k=info['Key']								
        if k=="ESCAPE":								
            self.targetStructure.ViewObject.Transparency = self.targetStructureTransparency		
        SketchArchCommands.selectObjectObserver.escape(self,info)					
													
													
class _Command_ArchSketch():							
										
    ''' ArchSketch Command Definition - Gui to make an ArchSketch '''		
										
    def GetResources(self):							
        return {'Pixmap' : SketchArchIcon.getIconPath() + '/icons/SketchArchWorkbench.svg',		
                'Accel' : "Alt+S",						
                'MenuText': "New ArchSketch",					
                'ToolTip' : "create an ArchSketch"}				
										
    def IsActive(self):								
        return not FreeCAD.ActiveDocument is None				
										
    def Activated(self):							
        reply = QtGui.QMessageBox.information(None,"","ArchSketch functionalities being developed :) ")	
        makeArchSketch()							
										
FreeCADGui.addCommand('ArchSketch', _Command_ArchSketch())			
										
										
class _Command_Voxel():								
										
    ''' ArchSketch Command Definition - Gui to make Voxel '''			
										
    def GetResources(self):							
        return {'Pixmap' : SketchArchIcon.getIconPath() + '/icons/Voxel.svg',	
                'Accel' : "Alt+v",						
                'MenuText': "Create Voxel",					
                'ToolTip' : "create Voxel"}					
										
    def IsActive(self):								
        return not FreeCAD.ActiveDocument is None				
										
    def Activated(self):							
        try:									
            sel = Gui.Selection.getSelection()[0]				
        except:									
            reply = QtGui.QMessageBox.information(None,"","Select an object with Shape to 'voxelise' ")								
            return																		
        try:									
            sel1 = Gui.Selection.getSelection()[1]				
        except:									
            sel1 = None								
        vp = makeVoxelPart(sel, sel1)						
        lva = App.ActiveDocument.addObject('App::Link', "Lnk__VoxelArray")	
        lva.ShowElement = False							
        lva.setLink(vp)								
        lva.setExpression('ElementCount', u''+'<<'+vp.Label+'>>'+'.eCount')	
        lva.setExpression('PlacementList', u''+'<<'+vp.Label+'>>'+'.pList')	
        lva.recompute()								
		        							
										
FreeCADGui.addCommand('Voxel', _Command_Voxel())				
										
										
class _Command_CellComplex():							
										
    ''' ArchSketch Command Definition - Gui to make CellComplex '''		
										
    def GetResources(self):							
        return {'Pixmap' : SketchArchIcon.getIconPath() + '/icons/CellComplex.svg',		
                'Accel' : "Alt+c",								
                'MenuText': "Create CelllComplex",						
                'ToolTip' : "create CelllComplex"}						
												
    def IsActive(self):										
        return not FreeCAD.ActiveDocument is None						
    def Activated(self):									
        sel = None										
        try:											
            sel = Gui.Selection.getSelection()[0]						
        except:											
            reply = QtGui.QMessageBox.information(None,"","Select an object with Shape to get CellComplexElement ")								
        cc = makeCellComplex(sel)																		
										
FreeCADGui.addCommand('CellComplex', _Command_CellComplex())			
										
										
#----------------------------------------------------------------------------#	
#                             Functions                                      #	
#----------------------------------------------------------------------------#	
										
										
def attachToMasterSketch(subject, target=None, subelement=None,		
                         attachmentOffset=None, zOffset='0',			
                         intersectingSubelement=None, mapMode='ObjectXY'):	
										
  if Draft.getType(subject) == "ArchSketch":					
      subject.MapReversed = False						
      subject.MapMode = mapMode							
      subject.Support = subject.MasterSketch					
										
										
def detachFromMasterSketch(fp):							
  fp.MapMode = 'Deactivated'							
  fp.Support = None								
										
										
def updatePropertiesLinkCommonODR(fp, linkFp=None, hostSketch=None):		
    updateAttachmentOffset(fp, linkFp, mode='ODR')				
										
										
def updateAttachmentOffset(fp, linkFp=None, mode=None):				
    '''										
        For ArchSketch(Object), Arch Objects (with SketchArch add-on),		
        and Links of the above.							
    '''										
										
    fpSelf = fp.Proxy								
    if linkFp:									
        fp = linkFp								
    if fp.AttachToAxisOrSketch == "None":					
        return									
										
    hostSketch = None								
    hostSkProxy = None								
    hostWall = None								
    hostObject = None								
    if fp.AttachToAxisOrSketch == "Host":			 		
        if hasattr(fp, "Hosts"):  # (Lnk)ArchWindow				
            if fp.Hosts:							
                if isinstance(fp.Hosts[0].getLinkedObject().Proxy, ArchWall._Wall):		
                    hostWall = fp.Hosts[0]  # Can just take 1st Host wall	
                    hostBase = hostWall.Base					
                else:  # i.e. attaching to objects other than Wall		
                    hostObject = fp.Hosts[0]  # Can just take 1st Host Object	
                    hostBase = hostObject.Base					
                if Draft.getType(hostBase.getLinkedObject()) == 'ArchSketch':	
                    hostSketch = hostBase  # HostWall/Object(Stair?) base	
                else:								
                    return							
        elif hasattr(fp, "Host"):  # (Lnk)Eqpt, [ ? (Lnk)ArchSketch ]		
            if fp.Host:								
                if isinstance(fp.Host.getLinkedObject().Proxy, ArchWall._Wall):			
                    hostWall = fp.Host						
                    hostBase = hostWall.Base					
                else:  # i.e. attaching to objects other than Wall		
                    hostObject = fp.Host					
                    hostBase = hostObject.Base					
                if Draft.getType(hostBase.getLinkedObject()) == 'ArchSketch':	
                    hostSketch = hostBase  # HostWall/Object(Stair?) base	
                else:								
                    return							
										
        if (not hostWall) and (not hostObject):					
            return								
										
    elif fp.AttachToAxisOrSketch == "Master Sketch":			 	
        if fp.MasterSketch:							
            hostSketch = fp.MasterSketch					
        else:									
            return								
										
    if hostSketch:								
        hostSkProxy = hostSketch.Proxy						
										
    attachToSubelementOrOffset = fp.AttachToSubelementOrOffset			
										
    msSubelement = fp.MasterSketchSubelement					
    msSubelementOffset = fp.MasterSketchSubelementOffset			
    msIntSubelement = fp.MasterSketchIntersectingSubelement			
										
    attachmentAlignment = fp.AttachmentAlignment				
    attachmentAlignmentOffset = fp.AttachmentAlignmentOffset			
    attachmentOffsetXyzAndRotation = fp.AttachmentOffsetXyzAndRotation		
    flip180Degree = fp.Flip180Degree						
    flipOffsetOriginToOtherEnd = fp.FlipOffsetOriginToOtherEnd			
    msSubelementTag = None							
    msIntSubelementTag = None							
    msSubelementEdge = None							
    msSubelementIndex = None							
    msIntSubelementIndex = None							
    msSubelementSnapPreset = fp.MasterSketchSubelementSnapPreset		
    msSubelementSnapCustom = fp.MasterSketchSubelementSnapCustom		
    offsetFromIntersectingSubelement = fp.OffsetFromIntersectingSubelement	
										
    newIndex = None								
    newTag = None								
										
    if msSubelement and hostSkProxy:						
        newIndex = int(msSubelement.lstrip('Edge'))-1				
        if newIndex > -1:							
            fp.MasterSketchSubelementIndex = newIndex				
            none, newTag = ArchSketch.getEdgeTagIndex(hostSkProxy, hostSketch,	
                                                      None, newIndex)		
										
    newIntIndex = None								
    newIntTag = None								
										
    if msIntSubelement and hostSkProxy:						
        newIntIndex = int(msIntSubelement.lstrip('Edge'))-1			
        if newIntIndex > -1:							
            fp.MasterSketchIntersectingSubelementIndex = newIntIndex		
            none, newIntTag = ArchSketch.getEdgeTagIndex(hostSkProxy,		
                                                         hostSketch, None,	
                                                         newIntIndex)		
    if hasattr(fp, "Proxy"):  # ArchSketch/ ArchObjects (Window/Equipment)	
        if fp.Proxy.Type == "ArchSketch":					
            if newTag:  # i.e. if found new tag					
                fpSelf.MasterSketchSubelementTag = newTag  # update/record	
            elif msSubelement:							
                fp.MasterSketchSubelementIndex = -1				
                fpSelf.MasterSketchSubelementTag = ''  # clear 			
            else:								
                msSubelementTag = fpSelf.MasterSketchSubelementTag		
										
            if newIntTag:  # i.e. if found new tag				
                # update/record							
                fpSelf.MasterSketchIntersectingSubelementTag = newIntTag	
            elif msIntSubelement:						
                fp.MasterSketchIntersectingSubelementIndex = -1			
                fpSelf.MasterSketchIntersectingSubelementTag = ''  # clear	
            else:								
                msIntSubelementTag=fpSelf.MasterSketchIntersectingSubelementTag 
										
        else:  # Other Arch Objects (Equipment / Windows, Doors)		
            if newTag:  # i.e. if found new tag					
                fp.MasterSketchSubelementTag = newTag  # update/record		
            elif msSubelement:							
                fp.MasterSketchSubelementIndex = -1				
                fp.MasterSketchSubelementTag = ''  # clear			
            else:								
                msSubelementTag = fp.MasterSketchSubelementTag			
										
            if newIntTag:  # i.e. if found new tag				
                # update/record							
                fp.MasterSketchIntersectingSubelementTag = newIntTag		
            elif msIntSubelement:						
                fp.MasterSketchIntersectingSubelementIndex = -1			
                fp.MasterSketchIntersectingSubelementTag = ''  # clear		
            else:								
                msIntSubelementTag=fp.MasterSketchIntersectingSubelementTag	
										
    else:  # Link objects (of ArchSketch or Arch Windows / Doors)		
        if newTag:  # i.e. if found new tag					
            fp.MasterSketchSubelementTag = newTag  # update/record 		
        elif msSubelement:							
            fp.MasterSketchSubelementIndex = -1					
            fp.MasterSketchSubelementTag = ''  # clear				
        else:									
            msSubelementTag = fp.MasterSketchSubelementTag			
        if newIntTag:  # i.e. if found new tag					
            # update/record							
            fp.MasterSketchIntersectingSubelementTag = newIntTag		
        elif msIntSubelement:							
            fp.MasterSketchIntersectingSubelementIndex = -1			
            fp.MasterSketchIntersectingSubelementTag = ''  # clear		
        else:									
            msIntSubelementTag=fp.MasterSketchIntersectingSubelementTag		
										
    if msSubelementTag:  # if has previous tag (then should no newTag)		
        if mode == 'ODR':							
            if fp.MasterSketchSubelementIndex > -1:				
                msSubelementIndex = fp.MasterSketchSubelementIndex		
                none, initialTag = ArchSketch.getEdgeTagIndex(hostSkProxy,	
                                   hostSketch, None, msSubelementIndex)	
                if Draft.getType(fp) == "ArchSketch":				
                    fp.Proxy.MasterSketchSubelementTag = initialTag		
                else:								
                    fp.MasterSketchSubelementTag = initialTag			
        else:  # mode != 'ODR'							
            msSubelementIndex, none = ArchSketch.getEdgeTagIndex(hostSkProxy,	
                                      hostSketch, msSubelementTag, None)	
            # sync index in record ('toponaming tolerent' process)		
            if msSubelementIndex != None:					
                fp.MasterSketchSubelementIndex = msSubelementIndex		
            else:  #  previous tag has no corresonding index			
                if hasattr(fp, "Proxy"):  # ArchSketch/ArchObjects (Win/Equip)	
                    if fp.Proxy.Type == "ArchSketch":				
                        fp.Proxy.MasterSketchSubelementTag =  ''		
                    else:  # Other Arch Objects (Equipment / Windows, Doors)	
                        fp.MasterSketchSubelementTag = ''			
                else:  # Link objects (of ArchSketch or Arch Windows / Doors)	
                    fp.MasterSketchSubelementTag = ''				
                fp.MasterSketchSubelementIndex = -1				
										
    if msIntSubelementTag:  # if has previous tag (then should no newTag)	
        if mode == 'ODR':							
            if fp.MasterSketchIntersectingSubelementIndex > -1:			
                msIntSubelementIndex= fp.MasterSketchIntersectingSubelementIndex
                none, initialTag = ArchSketch.getEdgeTagIndex(hostSkProxy,	
                                   hostSketch, None, msIntSubelementIndex)	
                if Draft.getType(fp) == "ArchSketch":				
                    fp.Proxy.MasterSketchIntersectingSubelementTag = initialTag 
                else:								
                    fp.MasterSketchIntersectingSubelementTag = initialTag	
        else:  # mode != 'ODR'							
            msIntSubelementIndex,none = ArchSketch.getEdgeTagIndex(hostSkProxy, 
                                        hostSketch, msIntSubelementTag, None)	
            # sync index in record ('toponaming tolerent' process)		
            if msIntSubelementIndex != None:					
                fp.MasterSketchIntersectingSubelementIndex = (			
                                                          msIntSubelementIndex) 
            else:  #  previous tag has no corresonding index			
                if hasattr(fp, "Proxy"):  # ArchSketch/ArchObjects (Win/Equip)	
                    if fp.Proxy.Type == "ArchSketch":				
                        fp.Proxy.MasterSketchIntersectingSubelementTag =  ''	
                    else:  # Other Arch Objects (Equipment / Windows, Doors)	
                        fp.MasterSketchIntersectingSubelementTag = ''		
                else:  # Link objects (of ArchSketch or Arch Windows / Doors)	
                    fp.MasterSketchIntersectingSubelementTag = ''		
                fp.MasterSketchIntersectingSubelementIndex = -1			
										
    if newTag:  # if found newTag, use it (Then should no msSubelementTag)	
        msSubelementIndex = newIndex						
										
    if newIntTag:  # if newIntTag, use it (Then should no msIntSubelementTag)	
        msIntSubelementIndex = newIntIndex					
										
    # Clear 'input'								
    if msSubelement:								
        fp.MasterSketchSubelement = ''						
    if msIntSubelement:								
        fp.MasterSketchIntersectingSubelement = ''				
										
    tempAttachmentOffset = FreeCAD.Placement()					
    winSketchPl = FreeCAD.Placement()						
																										
    # Calculate the Position & Rotation (of the point of the edge to attach to)																	
    if (attachToSubelementOrOffset in [ "Attach to Edge", "Attach To Edge & Alignment"] ):															
      if msSubelementIndex != None: # Can't proceed if no index is found																	
        if hostSketch:  # only calculate 'offset' if hostSketch, otherwise, still proceed but 'offset' is kept to 'origin'											
            edgeOffsetPointVector = getSketchEdgeOffsetPointVector(fp, hostSketch, msSubelementIndex, msSubelementSnapPreset, msSubelementSnapCustom, msSubelementOffset,					
                                                                   attachmentOffsetXyzAndRotation, flipOffsetOriginToOtherEnd, flip180Degree,									
                                                                   attachToSubelementOrOffset, msIntSubelementIndex, offsetFromIntersectingSubelement) 								
            tempAttachmentOffset.Base= edgeOffsetPointVector																			
																										
            # Calculate the rotation of the edge																				
            if attachToSubelementOrOffset == "Attach To Edge & Alignment":																	
                    edgeAngle = getSketchEdgeAngle(hostSketch, msSubelementIndex)																
                    # switch to new convention - https://forum.freecadweb.org/viewtopic.php?f=23&t=50802&start=80#p463196											
                    #if flip180Degree:																						
                    if (flip180Degree and (attachmentAlignment == "WallLeft")) or (not flip180Degree and (attachmentAlignment == "WallRight")) or (flip180Degree and (attachmentAlignment == "Left")) or (not flip180Degree and (attachmentAlignment == "Right")) :																						
                        edgeAngle = edgeAngle + math.pi																				
                    tempAttachmentOffset.Rotation.Angle = edgeAngle																		
            else:																								
                    tempAttachmentOffset.Rotation.Angle = attachmentOffsetXyzAndRotation.Rotation.Angle														
																										
            # Offset Parallel from Line Alignment																				
            masterSketchSubelementEdgeVec = getSketchEdgeVec(hostSketch, msSubelementIndex)															
            msSubelementWidth = zeroMM																						
            align = None																							
																										
            if attachmentAlignment in ["WallLeft", "WallRight"]:																		
                    if hasattr(hostSketch, "Proxy"):																				
                        if hasattr(hostSkProxy, "getEdgeTagDictSyncWidth") and hasattr(hostSkProxy,"EdgeTagDictSync"):												
                            msSubelementWidth = hostSkProxy.getEdgeTagDictSyncWidth(hostSketch, None, msSubelementIndex)											
                            if msSubelementWidth != None:																			
                                msSubelementWidth = msSubelementWidth * MM																	
                    if msSubelementWidth in [zeroMM, None]:																			
                        if hostWall:																						
                            try:																						
                                msSubelementWidth = hostWall.OverrideWidth[msSubelementIndex]*MM														
                            except:																						
                                msSubelementWidth = hostWall.Width																		
                        elif hostObject:																					
                            pass																						
                        elif hostSketch:																					
                            pass																						
                        else:																							
                            print (" something wrong ?  msSubelementWidth=0 : Case, ArchSketch on MasterSketch so no hostWall")											
																										
                    if hasattr(hostSketch, "Proxy"):																				
                        if hasattr(hostSkProxy, "getEdgeTagDictSyncAlign") and hasattr(hostSkProxy,"EdgeTagDictSync"):												
                            pass																						
                    if align == None:																						
                        if hostWall:  #elif hostWall:																				
                            try:																						
                                align = hostWall.OverrideAlign[msSubelementIndex]																
                            except:																						
                                align = hostWall.Align																				
                        elif hostObject:																					
                            pass																						
                        elif hostSketch:																					
                            pass																						
                        else:																							
                            print (" something wrong ?  align=None : Case, ArchSketch on MasterSketch so no hostWall")												
																										
            offsetValue = 0																							
            if msSubelementWidth != None:					# TODO If None, latter condition will result in exception	#zeroMM is 0 ->							
                if msSubelementWidth.Value != 0:																				
                    offsetValue = msSubelementWidth.Value # + attachmentAlignmentOffset.Value															
            if attachmentAlignment == "WallLeft":																				
                    if align == "Left":																						
                        offsetValue = attachmentAlignmentOffset.Value  # no need offsetValue (msSubelementWidth.Value)												
                    elif align == "Right":																					
                        offsetValue = offsetValue + attachmentAlignmentOffset.Value																
                    elif align == "Center":																					
                        offsetValue = offsetValue/2 + attachmentAlignmentOffset.Value																
            elif attachmentAlignment == "WallRight":																				
                    if align == "Left":																						
                        offsetValue = -offsetValue+attachmentAlignmentOffset.Value																
                    elif align == "Right":																					
                        offsetValue = attachmentAlignmentOffset.Value  # no need offsetValue (msSubelementWidth.Value)												
                    elif align == "Center":																					
                        offsetValue = -offsetValue/2 + attachmentAlignmentOffset.Value																
            else:																								
                        offsetValue = attachmentAlignmentOffset.Value  # no need offsetValue (msSubelementWidth.Value)												
            if offsetValue != 0:																						
                        vOffsetH = DraftVecUtils.scaleTo(masterSketchSubelementEdgeVec.cross(Vector(0,0,1)), -offsetValue)  # -ve										
                        tempAttachmentOffset.Base = tempAttachmentOffset.Base.add(vOffsetH)															
																										
    elif attachToSubelementOrOffset == "Follow Only Offset XYZ & Rotation":																	
                tempAttachmentOffset = attachmentOffsetXyzAndRotation																		
																										
    # Extra Rotation as user input											
															
    extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,0,0)) #, 0)					
    if fp.AttachmentOffsetExtraRotation == "X-Axis CCW90":  # [ "X-Axis CW90", "X-Axis CCW90", "X-Axis CW180", ]	
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,0,90))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "X-Axis CW90":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,0,-90))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "X-Axis CW180":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,0,180))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "Y-Axis CW90":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,90,0))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "Y-Axis CCW90":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,-90,0))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "Y-Axis CW180":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,180,0))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "Z-Axis CCW90":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(90,0,0))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "Z-Axis CW90":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(-90,0,0))  #,winSketchPl.Base)		
    elif fp.AttachmentOffsetExtraRotation == "Z-Axis CW180":								
                extraRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(180,0,0))  #,winSketchPl.Base)		
															
    tempAttachmentOffset = tempAttachmentOffset.multiply(extraRotation)							
															
    # Alternative OriginOffset manually input by user									
															
    originOffset = fp.OriginOffsetXyzAndRotation									
    invOriginOffset = originOffset.inverse()										
    tempAttachmentOffset = tempAttachmentOffset.multiply(invOriginOffset)						
															
    # ArchObjects, link of ArchSketch, link of ArchObjects								
    # i.e. Not ArchSketch												
    if linkFp or not hasattr(fp, "AttachmentOffset"):  ## TODO or if hostWall ...					
                hostSketchPl = FreeCAD.Placement()									
                if hostSketch:												
                    hostSketchPl = hostSketch.Placement									
                if Draft.getType(fp.getLinkedObject()) == 'Window':							
                    winSketchPl = fp.Base.Placement									
                    # Reset Window's placement to factor out base sketch's placement					
                    invWinSketchPl = winSketchPl.inverse()								
                    # make the placement 'upright' again								
                    winSkRotation = FreeCAD.Placement(App.Vector(0,0,0),App.Rotation(0,0,90))				
                    tempAttachmentOffset = tempAttachmentOffset.multiply(winSkRotation).multiply(invWinSketchPl)	
                originBase = App.Vector(0,0,0)						  				
                if hostWall:												
                    hostWallPl = hostWall.Placement									
                    hostWallRotation = FreeCAD.Placement(App.Vector(0,0,0),hostWallPl.Rotation,originBase)		
                    tempBaseOffset = hostWallRotation.multiply(hostSketchPl)						
                    tempBaseOffset.Base = tempBaseOffset.Base.add(hostWallPl.Base)					
                    tempAttachmentOffset = tempBaseOffset.multiply(tempAttachmentOffset)				
                elif hostObject:											
                    hostObjectPl = hostObject.Placement									
                    #tempAttachmentOffset = (hostSketchPl.multiply(hostObjectPl)).multiply(tempAttachmentOffset)	
                    hostObjectRotation = FreeCAD.Placement(App.Vector(0,0,0),hostObjectPl.Rotation,originBase)		
                    tempBaseOffset = hostObjectRotation.multiply(hostSketchPl)						
                    tempBaseOffset.Base = tempBaseOffset.Base.add(hostObjectPl.Base)					
                    tempAttachmentOffset = tempBaseOffset.multiply(tempAttachmentOffset)				
                else:  # Attach to Master Sketch (only)									
                    tempAttachmentOffset = hostSketchPl.multiply(tempAttachmentOffset)					
    if linkFp or not hasattr(fp, "AttachmentOffset"):  ## TODO or if hostWall ...					
                fp.Placement = tempAttachmentOffset									
    else:														
                fp.AttachmentOffset = tempAttachmentOffset								
										
										
										
'''------------------- Creation/Insertion Functions ---------------------'''	
										
										
def makeArchSketch(grp=None, label="ArchSketch__NAME", attachToAxisOrSketch=None, placementAxis_Or_masterSketch=None, copyFlag=None, visibility=None):		
  name = "ArchSketch"								
  if grp:									
      archSketch = grp.newObject("Sketcher::SketchObjectPython",name)		
  else:										
      archSketch=App.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)	
  archSketch.Label = label							
  archSketchInsta=ArchSketch(archSketch)					
  archSketch.AttachToAxisOrSketch = "Master Sketch"				
  return archSketch								
										
										
'''------------------------- Low Level Operation --------------------------'''	
										
def changeAttachMode(fp, fpProp):						
    if fpProp == "AttachToAxisOrSketch":					
        if fp.AttachToAxisOrSketch == "Master Sketch":				
                fp.setEditorMode("AttachToSubelementOrOffset",0)		
                fp.setEditorMode("AttachmentOffsetXyzAndRotation",0)		
                if fp.MasterSketch:						
                      attachToMasterSketch(fp)					
        else:									
                  fp.setEditorMode("AttachToSubelementOrOffset",1)		
                  fp.setEditorMode("AttachmentOffsetXyzAndRotation",1)		
                  if True:  # TODO						
                      if fp.MasterSketch:					
                          detachFromMasterSketch(fp)				
    # change in "target" in attachToMasterSketch()				
    elif fpProp == "MasterSketch":						
              if fp.MasterSketch:						
                  if fp.AttachToAxisOrSketch == "Master Sketch":		
                      attachToMasterSketch(fp, fp.MasterSketch)			
              else:								
                  if fp.AttachToAxisOrSketch == "Master Sketch":		
                      detachFromMasterSketch(fp)				
										
										
def getSketchEdgeAngle(masterSketch, subelementIndex):				
    vec = getSketchEdgeVec(masterSketch, subelementIndex)			
    draftAngle = -DraftVecUtils.angle(vec)					
    return draftAngle								
										
										
def getSketchEdgeVec(sketch, geoindex):						
    #geoindex = int(subelement.lstrip('Edge'))-1				
    lp1=sketch.Geometry[geoindex].EndPoint					
    lp2=sketch.Geometry[geoindex].StartPoint					
    vec = lp1 - lp2								
    return vec									
										
										
def getSketchEdgeIntersection(sketch, line1Index, line2Index):			
    import DraftGeomUtils							
    e1=sketch.Geometry[int(line1Index)].toShape()				
    e2=sketch.Geometry[int(line2Index)].toShape()				
    i=DraftGeomUtils.findIntersection(e1,e2,True,True)				
    if i:									
        return i[0]								
    else:									
        return None								
										
										
def getSketchEdgeOffsetPointVector(subject, masterSketch, subelementIndex, snapPreset=None, snapCustom=None, attachmentOffset=None, zOffset=None, flipOffsetOriginToOtherEnd=False,		
                                   flip180Degree=False, attachToSubelementOrOffset=None, intersectingSubelementIndex=None, offsetFromIntersectingSubelement=False):				
    geoindex = None																						
    geoindex2 = None																						
    #geoindex = int(subelement.lstrip('Edge'))-1																		
    geoindex = subelementIndex																					
    geoindex2 = intersectingSubelementIndex																			
																								
    #if True:																							
    intersectPoint = None																					
    if offsetFromIntersectingSubelement and (geoindex2 is not None):																
        intersectPoint = getSketchEdgeIntersection(masterSketch, geoindex, geoindex2)														
    if snapPreset != 'CustomValue':																				
        snapValue = ArchSketch.SnapPresetDict[snapPreset]  # Class.Dict																
    else:  # elif snapPreset == 'CustomValue':																			
        snapValue = snapCustom																					
    edgeLength = masterSketch.Geometry[geoindex].length()																	
    if snapValue == 0:  # 'AxisStart'																				
        snapPresetCustomLength = 0  # no unit ?																			
    else:  #elif snapValue != 0:																				
        if geoindex2 is None:																					
            snapPresetCustomLength = edgeLength * snapValue																	
        else:  #elif geoindex2 is not None:  # needs to break the edge																
            if not flipOffsetOriginToOtherEnd:																			
                if not offsetFromIntersectingSubelement: # use 1st portion															
                    edgePortionVec = intersectPoint.sub(masterSketch.Geometry[geoindex].StartPoint)												
                else:  # use 2nd portion																			
                    edgePortionVec = intersectPoint.sub(masterSketch.Geometry[geoindex].EndPoint)												
            else:  #elif flipOffsetOriginToOtherEnd:																		
                if not offsetFromIntersectingSubelement: # use 2nd portion															
                    edgePortionVec = intersectPoint.sub(masterSketch.Geometry[geoindex].EndPoint)												
                else:  # use 1st portion																			
                    edgePortionVec = intersectPoint.sub(masterSketch.Geometry[geoindex].StartPoint)												
            snapPresetCustomLength = edgePortionVec.Length * snapValue																
    totalAttachmentOffset = snapPresetCustomLength + attachmentOffset.Value  # float(attachmentOffset)												
    if not flipOffsetOriginToOtherEnd:																				
        edgeOffsetPoint = masterSketch.Geometry[geoindex].value(totalAttachmentOffset)														
    else:  #elif flipOffsetOriginToOtherEnd:																			
        edgeOffsetPoint = masterSketch.Geometry[geoindex].value(edgeLength - totalAttachmentOffset)												
    if intersectPoint:  # i.e. - if offsetFromIntersectingSubelement and (geoindex2 is not None):												
        if not flipOffsetOriginToOtherEnd:																			
            intOffsetVec = intersectPoint.sub(masterSketch.Geometry[geoindex].StartPoint)													
        else:  #elif flipOffsetOriginToOtherEnd:																		
            intOffsetVec = intersectPoint.sub(masterSketch.Geometry[geoindex].EndPoint)														
        edgeOffsetPoint = edgeOffsetPoint.add(intOffsetVec)																	
																								
    edgeOffsetPoint.z = zOffset.Base.z																				
    return edgeOffsetPoint																					
																								
																								
# For All Sketch, Not Only ArchSketch						
										
def getSketchSortedClEdgesOrder(sketch):					
										
      ''' Call getSortedClEdgesOrder() -					
          To do Part.getSortedClusters() on geometry of a Sketch (omit		
          construction geometry), check the order of edges to return lists of	
          indexes in the order of sorted edges	 			 	
										
          return:								
          - clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex, and		
          - clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat	
      '''									
										
      skGeom = sketch.Geometry							
      skGeomEdgesFullSet = []							
      skGeomEdgesSet = []							
      for c, i in enumerate(skGeom):						
          skGeomEdge = i.toShape()						
          skGeomEdgesFullSet.append(skGeomEdge)					
          if hasattr(i, 'Construction'):					
              construction = i.Construction					
          elif hasattr(sketch, 'getConstruction'):				
              construction = sketch.getConstruction(c)				
          if not construction:							
              skGeomEdgesSet.append(skGeomEdge)					
      return getSortedClEdgesOrder(skGeomEdgesSet, skGeomEdgesFullSet)		
										
										
def getSortedClEdgesOrder(skGeomEdgesSet, skGeomEdgesFullSet=None):		
										
      ''' 0) To support getSketchSortedClEdgesOrder() on a Sketch object	
      	     which pass a) edges not construction (skGeomEdgesSet),		
                    and b) all edges (skGeomEdgesFullSet);			
          1) Or, similar usecases with 2 different edges lists :		
      	     - Do Part.getSortedClusters() on the provided skGeomEdgesSet,	
               and check the order of edges to return lists of indexes		
               against skGeomEdgesFullSet in the order of sorted edges	 	
										
      	  2) Or if skGeomEdgesFullSet is not provided;				
      	     - simply Part.getSortedClusters() provided edges,			
             check the order of edges to return lists of indexes		
             against original in the order of sorted edges	 	 	
										
          return:								
          - clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex, and		
          - clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat	
      '''									
										
      skGeomEdgesSorted = Part.getSortedClusters(skGeomEdgesSet)		
      if skGeomEdgesFullSet is None:						
          skGeomEdgesFullSet = skGeomEdgesSet #  .copy()			
      ## a list of lists (not exactly array / matrix) to contain index of found matching geometry			
      clEdgePartnerIndex = []							
      clEdgeSameIndex = []							
      clEdgeEqualIndex = []							
										
      ## a flat list containing above information - but just flat, not a list of lists ..				
      clEdgePartnerIndexFlat = []						
      clEdgeSameIndexFlat = []							
      clEdgeEqualIndexFlat = []							
										
      for h, c in enumerate(skGeomEdgesSorted):					
          clEdgePartnerIndex.append([])						
          clEdgeSameIndex.append([])						
          clEdgeEqualIndex.append([])						
										
          ''' Build the full sub-list '''					
          for a in c:								
              clEdgePartnerIndex[h].append(None)				
              clEdgeSameIndex[h].append(None)					
              clEdgeEqualIndex[h].append(None)					
										
          for i, skGeomEdgesSortedI in enumerate(c):				
              for j, skGeomEdgesI in enumerate(skGeomEdgesFullSet):		
                  if skGeomEdgesI: # is not None / i.e. Construction Geometry	
                      if j not in clEdgePartnerIndexFlat:			
                        if skGeomEdgesSortedI.isPartner(skGeomEdgesI):		
                          clEdgePartnerIndex[h][i] = j				
                          clEdgePartnerIndexFlat.append(j)			
										
                      if j not in clEdgeSameIndexFlat:				
                        if skGeomEdgesSortedI.isSame(skGeomEdgesI):		
                          clEdgeSameIndex[h][i] = j				
                          clEdgeSameIndexFlat.append(j)				
										
                      if j not in clEdgeEqualIndexFlat:				
                        if skGeomEdgesSortedI.isEqual(skGeomEdgesI):		
                          clEdgeEqualIndex[h][i] = j				
                          clEdgeEqualIndexFlat.append(j)			
										
              if clEdgePartnerIndex[h][i] == None:				
                  clEdgePartnerIndexFlat.append(None)				
              if clEdgeSameIndex[h][i] == None:					
                  clEdgeSameIndexFlat.append(None)				
              if clEdgeEqualIndex[h][i] == None:				
                  clEdgeEqualIndexFlat.append(None)				
      return clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex, clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat		
										
										
def sortSketchAlign(sketch,edgeAlignList):					
										
    '''										
        This function is primarily to support Ordinary Sketch + Arch Wall	
        to gain feature that individual edge / wall segment to have		
        individual Align setting with OverrideAlign attribute in Arch Wall	
										
        This function arrange the edgeAlignList 				
        - a list of Align in the order of Edge Indexes -			
        into a list of Align following the order of edges			
        sorted by Part.getSortedClusters()					
    '''										
										
    sortedIndexes = getSketchSortedClEdgesOrder(sketch)				
    alignsList = sortAlign(edgeAlignList, sortedIndexes)			
    return alignsList								
										
										
def sortAlign(edgeAlignList, sortedIndexes):					
    clEdgeSameIndexFlat = sortedIndexes[4]					
    alignsList = []								
    for i in clEdgeSameIndexFlat:						
        try:									
            curAlign = edgeAlignList[i]						
        # if edgeAlignList does not cover the edge				
        except:									
            curAlign = 'Left'  # default					
        alignsList.append(curAlign)						
    return alignsList								
										
										
def sortSketchWidth(sketch,edgeWidthList):					
										
    '''										
        This function is primarily to support Ordinary Sketch + Arch Wall	
        to gain feature that individual edge / wall segment to have		
        individual Width setting with OverrideWidth attribute in Arch Wall	
										
        This function arrange the edgeWidthList 				
        - a list of Width in the order of Edge Indexes -			
        into a list of Width following the order of edges			
        sorted by Part.getSortedClusters()					
    '''										
										
    sortedIndexes = getSketchSortedClEdgesOrder(sketch)				
    widthList = sortWidth(edgeWidthList, sortedIndexes)				
    return widthList								
										
										
def sortWidth(edgeWidthList, sortedIndexes):					
    clEdgeSameIndexFlat = sortedIndexes[4]					
    widthList = []								
    for i in clEdgeSameIndexFlat:						
        try:									
            curWidth = edgeWidthList[i]						
        # if edgeWidthList does not cover the edge				
        except:									
            curWidth = 200  # default						
        widthList.append(curWidth)						
    return widthList								
										
										
def removeBBFace(bbFace, sliceFaces):  						
    for i, sliceF in enumerate(sliceFaces):					
        if len(sliceF.OuterWire.Vertexes) != 4:  # 'default' rectangler bbFace	
            break								
        for bbEd in bbFace.Edges:						
            foundEd = None							
            for sliceFEd in sliceF.Edges:					
                if bbEd.isSame(sliceFEd):					
                    foundEd = True						
                    break							
            if foundEd == None:							
                break								
            else:								
                continue							
        if foundEd == True:							
            del sliceFaces[i]							
            break								
        else:									
            continue								
    return sliceFaces								
										
										
def boundBoxShape(obj, enlarge):										
														
    objPl = obj.Placement 											
    invPl = objPl.inverse()											
    sh=Part.Shape(obj.Shape)											
    sh.Placement=sh.Placement.multiply(invPl)									
    bb=sh.BoundBox  #bb=obj.Shape.BoundBox									
    p=FreeCAD.Placement()											
    p.Base=FreeCAD.Vector(bb.XMin-enlarge, bb.YMin-enlarge, bb.ZMin)						
    rect = Part.makePlane(bb.XLength+2*enlarge,bb.YLength+2*enlarge,p.Base, FreeCAD.Vector(0,0,1))		
    return rect  #, objPl (no need to return as it is the original object's placement)				
														
														
def getSketchEdges(sk):																
																		
    ''' return lists in lists '''														
																		
    skGeom = sk.GeometryFacadeList														
    skGeomEdges = []																
    skGeomEdgesFull = []															
																		
    for i in skGeom:																
        if isinstance(i.Geometry, (Part.LineSegment, Part.Circle, Part.ArcOfCircle)):								
                skGeomEdgesI = i.Geometry.toShape()												
																		
                if not i.Construction:														
                    skGeomEdges.append(skGeomEdgesI)												
                skGeomEdgesFull.append(skGeomEdgesI)												
    return skGeomEdges, skGeomEdgesFull														
																		
																		
def flattenEdLst(edgesLstInLst):							
											
    flattened  = [e for sublist in edgesLstInLst for e in sublist]			
    return flattened									
											
											
def selfCutEdges(edges):								
    '''											
        The provided edges are cut one by one against the rest,				
        the fragments of edges are collected in a list of list,				
        and returned.									
    '''											
											
    cutEdgesList = []									
    l = len(edges)									
    for n in range(l):									
        cutEdgesListI = []								
        edgesC = edges.copy()								
        e = edgesC.pop(n)								
        cut = e.cut(edgesC)								
        for cutE in cut.Edges:								
            cutEdgesListI.append(cutE)							
        cutEdgesList.append(cutEdgesListI)						
    return cutEdgesList									
											
#***************************************************************************	
reply = QtGui.QMessageBox.information(None,"","SketchArch Add-On being loaded.  Click button to Continue ")	
