#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2018-25 Paul Lee <paullee0@gmail.com>                   *
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
import ArchWindow
import Arch, ArchWall, ArchCurtainWall
from FreeCAD import Vector

import SketchArchIcon
import SketchArchCommands

# for ArchWindows
from PySide.QtCore import QT_TRANSLATE_NOOP
from PySide import QtGui, QtCore

import uuid, math, time
pi = math.pi

App = FreeCAD
Gui = FreeCADGui
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

  MasterSketchSubelementTags = ['MasterSketchSubelementTag',
                                'MasterSketchIntersectingSubelementTag' ]
  SnapPresetDict = {'AxisStart':0.0, '1/4':0.25, '1/3':1/3, 'MidPoint':0.5,
                    '2/3':2/3, '3/4':3/4, 'AxisEnd':1.0}
  EdgeTagDicts=['EdgeTagDictArchive', 'EdgeTagDictInitial', 'EdgeTagDictSync']
  GeomSupported = (Part.LineSegment, Part.Circle, Part.ArcOfCircle,
                   Part.Ellipse)


  def __init__(self, obj):
      pass
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
      obj.setEditorMode("Placement",1)


  def setProperties(self, fp):

      ''' Add self.properties '''

      fp.Proxy = self
      if not hasattr(self,"Type"):
          self.Type = "ArchSketch"
      for i in ArchSketch.EdgeTagDicts:
        if not hasattr(self,i):
          setattr(self, i, {})

      if not hasattr(self,'PropertySetDict'):
          self.PropertySetDict = {}
      if not hasattr(self,"clEdgeDict"):
          self.clEdgeDict = {}
      if not hasattr(self,"clEdgePartnerIndexFlat"):
          self.clEdgePartnerIndexFlat = []
      if not hasattr(self,"clEdgeSameIndexFlat"):
          self.clEdgeSameIndexFlat = []
      if not hasattr(self,"clEdgeEqualIndexFlat"):
          self.clEdgeEqualIndexFlat = []

      ''' Added ArchSketch Properties '''

      ArchSkPropStr = 'Added ArchSketch Properties'
      if not hasattr(fp,"Align"):
          fp.addProperty("App::PropertyEnumeration","Align",ArchSkPropStr,"The default alignment for the wall with this ArchSketch as its base object")
          fp.Align = ['Left','Right','Center']
          fp.Align = 'Center'
      if not hasattr(fp,"Offset"):
          fp.addProperty("App::PropertyDistance","Offset",ArchSkPropStr,QT_TRANSLATE_NOOP("App::Property","The offset between the wall (segment) and its baseline (only for left and right alignments)"))
      if not hasattr(fp,"ArchSketchWidth"):
          fp.addProperty("App::PropertyLength","ArchSketchWidth",
                         ArchSkPropStr,"ArchSketchWidth returned ")
          fp.ArchSketchWidth = 200 * MM  # Default

      if not hasattr(fp,"DetectRoom"):
          fp.addProperty("App::PropertyBool","DetectRoom",ArchSkPropStr,QT_TRANSLATE_NOOP("App::Property","Enable to detect rooms enclosed by edges/walls - For CellComplex object to work, the generated shape is not shown in the ArchSketch object, but shown by a CellComplex Object.  This make recompute of this object longer !"))
      if not hasattr(fp,"CellComplexElements"):
          fp.addProperty('Part::PropertyPartShape', 'CellComplexElements', ArchSkPropStr, QT_TRANSLATE_NOOP("App::Property","The Shape of built CellComplexElements"),8)
      if not hasattr(fp,"FloorHeight"):
          fp.addProperty("App::PropertyLength","FloorHeight",ArchSkPropStr,"Global ArchSketch Floor to Next Floor Height")
          fp.FloorHeight = 3000 * MM  # Default
      if not hasattr(fp,"PropertySet"):
          fp.addProperty("App::PropertyEnumeration","PropertySet",ArchSkPropStr
                         ,QT_TRANSLATE_NOOP("App::Property"
                         ,"List User Defined Property Sets"))
          fp.PropertySet = ['Default']
      if not hasattr(self,"PropSetListPrev"):
          self.PropSetListPrev = []
      if not hasattr(self,"PropSetPickedUuid"):
          self.PropSetPickedUuid = None
      if not hasattr(fp,"ShapeList"):
          sstr="The returned Shape of the ArchSkech with supported geometries"
          fp.addProperty('Part::PropertyTopoShapeList', 'ShapeList',
                         ArchSkPropStr, QT_TRANSLATE_NOOP("App::Property",
                         sstr),8)


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
          fp.addProperty("App::PropertyInteger","MasterSketchIntersectingSubelementIndex","Referenced Object","Index of MasterSketchInteresctingSubelement to be synced on the fly. For output only.", 8)
          fp.setEditorMode("MasterSketchIntersectingSubelementIndex",2)

      ''' Referenced Object '''

      # "Host" for ArchSketch and Arch Equipment
      # (currently all Objects calls except Window which has "Hosts")
      if not isinstance(fp.getLinkedObject().Proxy, ArchWindow._Window):
          pass
          if "Host" not in prop:
              fp.addProperty("App::PropertyLink","Host","Referenced Object",
                  "The object that host this object / this object attach to")
      # "Hosts" for Window
      else:
          if "Hosts" not in prop:
              fp.addProperty("App::PropertyLinkList","Hosts","Window",
                             QT_TRANSLATE_NOOP("App::Property",
                             "The objects that host this window"))
                             # Arch Window's code

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

      # No existing selection, ie. newly added "AttachToAxisOrSketch" attribute
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


      if True:
          propSetPickedUuidPrev = self.PropSetPickedUuid
          propSetListPrev = self.PropSetListPrev
          propSetSelectedNamePrev = fp.PropertySet
          propSetSelectedNameCur = None

          # get full list of PropertySet
          propSetListCur = self.getPropertySet(fp)
          # get updated name (if any) of the selected PropertySet
          propSetSelectedNameCur = self.getPropertySet(fp,
                                        propSetUuid=propSetPickedUuidPrev)
          if propSetSelectedNameCur:  # True if selection is not deleted
              if propSetListPrev != propSetListCur:
                  fp.PropertySet = propSetListCur
                  fp.PropertySet = propSetSelectedNameCur
                  self.propSetListPrev = propSetListCur
              elif propSetSelectedNamePrev != propSetSelectedNameCur:
                  fp.PropertySet = propSetSelectedNameCur
          else:  # True if selection is deleted
              if propSetListPrev != propSetListCur:
                  fp.PropertySet = propSetListCur
                  fp.PropertySet = 'Default'


      ''' (-I) - Sync EdgeTagDictSync: ArchSketch Edge Indexes against Tags '''

      self.syncEdgeTagDictSync(fp)


      ''' (VII) - Update attachment angle and attachment point coordinate '''

      updateAttachmentOffset(fp)


      ''' (IX or XI) - Update the order of edges by getSortedClusters '''

      self.updateShapeList(fp)
      self.updateSortedClustersEdgesOrder(fp)


      ''' (X) - Instances fp.resolve / fp.recompute - '''

      fp.solve()
      fp.recompute()

      if fp.DetectRoom and not fp.Shape.isNull():

          bb = boundBoxShape(fp, 5000)
          skEdges, skEdgesF = getSketchEdges(fp)
          cutEdges = selfCutEdges(skEdges)
          fragmentEdgesL = flattenEdLst(cutEdges)
          import BOPTools.SplitAPI
          regions = BOPTools.SplitAPI.slice(bb, fragmentEdgesL, 'Standard',
                                            tolerance = 0.0)
          resultFaces = removeBBFace(bb, regions.SubShapes)  # assume to be faces
          extv = normal.multiply(fp.FloorHeight)  # WallHeight+fp.SlabThickness
          resultFacesRebased = []
          for f in resultFaces:
              f.Placement = f.Placement.multiply(fp.Placement)
              resultFacesRebased.append(f)
          solids = [f.extrude(extv) for f in resultFacesRebased]
          solidsCmpd =  Part.Compound(solids)
          fp.CellComplexElements = solidsCmpd


  def updateShapeList(self, fp):
      skGeom = fp.Geometry
      skGeomEdgesFullSet = []
      for c, i in enumerate(skGeom):
          skGeomEdge = i.toShape()
          skGeomEdgesFullSet.append(skGeomEdge)
      fp.ShapeList = skGeomEdgesFullSet


  def getMinDistInfo(self, fp, pointShape=None):
      shapeListCmpd = Part.Compound(fp.ShapeList)
      shapeListCmpd.Placement = fp.Placement
      info = shapeListCmpd.distToShape(pointShape)
      if info[2][0][0] == 'Edge':
          geo = info[2][0][1]
          edge = geo + 1
          off = round(info[2][0][2],-1)
      else:
          edge, off = None
      skPl = fp.Placement
      skLoc = skPl.Base
      normal = fp.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1))
      planeShape = Part.Plane(skLoc,normal).toShape()
      infoPlane = planeShape.distToShape(pointShape)
      ht = round(infoPlane[0],-1)
      edgeLocAngle = getSketchEdgeAngle(fp, geo)
      edgeLocRotation = App.Placement()  # default Axis.z = 1
      edgeLocRotation.Rotation.Angle = edgeLocAngle
      # edge 'local placement' ignored
      edgeGlobalPl = skPl.multiply(edgeLocRotation)
      eGlAxis = edgeGlobalPl.Rotation.Axis
      eGlAxisZ = eGlAxis.z
      eGlAng = edgeGlobalPl.Rotation.Angle
      if round((eGlAxisZ - 1),6) == 0:  # +1
          pass
      elif round((eGlAxisZ + 1),6) == 0:  # -1
          eGlAng = -eGlAng
      dict = {'edge':edge, 'offset':off, 'height':ht, 'edgeAngle':eGlAng}
      return dict  # return info


  def updateSortedClustersEdgesOrder(self, fp):

      tup = getSketchSortedClEdgesOrder(fp)
      (clEdgePartnerIndex,clEdgeSameIndex,clEdgeEqualIndex,
       clEdgePartnerIndexFlat,clEdgeSameIndexFlat,clEdgeEqualIndexFlat) = tup

      self.clEdgeDict['clEdgeSameIndexFlat'] = clEdgeSameIndexFlat
      self.clEdgePartnerIndex = clEdgePartnerIndex
      self.clEdgeSameIndex = clEdgeSameIndex
      self.clEdgeEqualIndex = clEdgeEqualIndex
      self.clEdgePartnerIndexFlat = clEdgePartnerIndexFlat
      self.clEdgeSameIndexFlat = clEdgeSameIndexFlat
      self.clEdgeEqualIndexFlat = clEdgeEqualIndexFlat

      for key, value in iter(fp.Proxy.PropertySetDict.items()):
          tupUuid = getSketchSortedClEdgesOrder(fp, propSetUuid=key)
          (partnerIndex,sameIndex,equalIndex,
           partnerIndexFlat,sameIndexFlat,equalIndexFlat) = tupUuid
          if not self.clEdgeDict.get(key,None):
              self.clEdgeDict[key] = {}
          self.clEdgeDict[key]['clEdgeSameIndexFlat'] = sameIndexFlat


  def onChanged(self, fp, prop):
      if prop in ["MasterSketch", "PlacementAxis", "AttachToAxisOrSketch"]:
          changeAttachMode(fp, prop)

      if prop == "PropertySet":
          uuid = self.getPropertySet(fp, propSetName=fp.PropertySet)
          self.PropSetPickedUuid = uuid

  def rebuildEdgeTagDicts(self, fp):  # To be called by Local

      self.EdgeTagDictArchive = dict(self.EdgeTagDictSync)
      self.EdgeTagDictInitial = {}
      self.EdgeTagDictSync = {}

      i = 0
      while True:
          try:
              tagI = fp.Geometry[i].Tag
          except:
              break
          edgeTagDictArchiveTagDict = None
          if self.EdgeTagDictArchive.values():
            if isinstance (list(self.EdgeTagDictArchive.values())[0], dict):
              none, tagArchive = self.getEdgeTagDictArchiveTagIndex(fp,
                                      tag=None, index=i)
              if tagArchive is not None:
                  edgeTagDictArchiveTagDict=self.EdgeTagDictArchive[tagArchive]
                  self.EdgeTagDictInitial[tagI] = edgeTagDictArchiveTagDict
              else:
                  edgeTagDictArchiveTagDict = None
          if not edgeTagDictArchiveTagDict:
                  self.EdgeTagDictInitial[tagI]={}
                  self.EdgeTagDictInitial[tagI]['index']=i
          i += 1

      self.EdgeTagDictSync = self.EdgeTagDictInitial.copy()


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
          parent.Proxy.setProperties(parent)
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


  #**************************************************************************#


  ''' Property Set Dict (self.PropertySetDict) related method()  '''


  def getPropertySet(self, fp, propSetUuid=None, propSetName=None):

      if not propSetUuid and not propSetName:
          setDicts = list(self.PropertySetDict.values())
          setNames = [ d.get('name',None) for d in setDicts ]
          propertySetList = ['Default'] + setNames
          return propertySetList
      elif propSetUuid:
          setDict = self.PropertySetDict.get(propSetUuid, None)
          if setDict:
              setName = setDict.get('name',None)
              return setName
          else:
              return None
      elif propSetName:
          if propSetName == 'Default' : return None
          for k, v in self.PropertySetDict.items():
              if v.get('name') == propSetName:
                  uuid = k
                  break
          return uuid


  #**************************************************************************#


  ''' edge Tag Dict (self.syncEdgeTagDictSync) related method()  '''


  def getWidths(self, fp, propSetUuid=None):

      ''' wrapper function for uniform format '''

      return self.getSortedClustersEdgesWidth(fp, propSetUuid)


  def getWidth(self,fp,tag=None,index=None,propSetUuid=None):

      curWidth = self.getEdgeTagDictSyncWidth(fp, tag, index, propSetUuid)
      if not curWidth:
          if fp.ArchSketchWidth:
              curWidth = fp.ArchSketchWidth.Value
          else:
              curWidth = 0  # 0 follow Wall's Width
      return curWidth


  def getAligns(self, fp, propSetUuid=None):

      ''' wrapper function for uniform format '''

      return self.getSortedClustersEdgesAlign(fp, propSetUuid)


  def getOffsets(self, fp , propSetUuid=None):

      ''' wrapper function for uniform format '''

      return self.getSortedClustersEdgesOffset(fp, propSetUuid)


  def getUnsortedEdgesWidth(self, fp, propSetUuid=None):

      widthsList = []
      for j in range(0, len(fp.Geometry)):
          curWidthEdgeTagDictSync = self.getEdgeTagDictSyncWidth(fp, None, j,
                                         propSetUuid)
          widthsList.append(curWidthEdgeTagDictSync)
      return widthsList


  def getUnsortedEdgesAlign(self, fp, propSetUuid=None):

      alignsList = []
      for j in range(0, len(fp.Geometry)):
          curAlignEdgeTagDictSync = self.getEdgeTagDictSyncAlign(fp, None, j,
                                         propSetUuid)
          alignsList.append(curAlignEdgeTagDictSync)
      return alignsList


  def getSortedClustersEdgesWidth(self, fp, propSetUuid=None):

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

      widthsList = []

      if not propSetUuid:
          clEdgeSameIndexFlat = self.clEdgeDict.get('clEdgeSameIndexFlat',None)
      else:
          clEdgeSameIndexFlat = None
          dictUuid = self.clEdgeDict.get(propSetUuid,None)
          if dictUuid:
              clEdgeSameIndexFlat = dictUuid.get('clEdgeSameIndexFlat',None)
          if not clEdgeSameIndexFlat:
              return []

      for i in clEdgeSameIndexFlat:
          curWidth = self.getEdgeTagDictSyncWidth(fp, None, i, propSetUuid)
          if not curWidth:
              if fp.ArchSketchWidth:
                  curWidth = fp.ArchSketchWidth.Value
              else:
                  curWidth = 0  # 0 follow Wall's Width
          widthsList.append(curWidth)
      return widthsList


  def getEdgeTagDictSyncWidth(self,fp,tag=None,index=None,propSetUuid=None):

      if tag is not None:
          tagI = tag
      elif index is not None:
          try:  # Cases where self.EdgeTagDictSync not updated yet ?
              tagI = fp.Geometry[index].Tag
          except:
              self.syncEdgeTagDictSync(fp)
              try: # again
                  tagI = fp.Geometry[index].Tag
              except:
                  return None
      else:
          return None  #pass
      if propSetUuid:
          dictI = self.EdgeTagDictSync[tagI].get(propSetUuid, None)
      else:
          dictI = self.EdgeTagDictSync[tagI]
      if not dictI:
          return None
      widthI = dictI.get('width', None)
      return widthI


  def getSortedClustersEdgesAlign(self, fp, propSetUuid):
      '''
           This method check the SortedClusters-isSame-(flat)List
           find the corresponding edgesAlign ...
           and make a list of (AlignX, AlignX+1 ...)
      '''

      alignsList = []

      if not propSetUuid:
          clEdgeSameIndexFlat = self.clEdgeDict.get('clEdgeSameIndexFlat',None)
      else:
          clEdgeSameIndexFlat = None
          dictUuid = self.clEdgeDict.get(propSetUuid,None)
          if dictUuid:
              clEdgeSameIndexFlat = dictUuid.get('clEdgeSameIndexFlat',None)
          if not clEdgeSameIndexFlat:
              return []

      for i in clEdgeSameIndexFlat:
          curAlign = self.getEdgeTagDictSyncAlign(fp, None, i, propSetUuid)
          if not curAlign:
              curAlign = fp.Align # default Align (set up to 'Center')
          alignsList.append(curAlign)
      return alignsList


  def getEdgeTagDictSyncAlign(self,fp,tag=None,index=None,propSetUuid=None):
      if tag is not None:
          tagI = tag
      elif index is not None:
          try:
              tagI = fp.Geometry[index].Tag
              #return self.EdgeTagDictSync[tagI].get('align', None)
          except:
              self.syncEdgeTagDictSync(fp)
              try:  # again
                  tagI = fp.Geometry[index].Tag
                  #return self.EdgeTagDictSync[tagI].get('align', None)
              except:
                  return None
      if propSetUuid:
          dictI = self.EdgeTagDictSync[tagI].get(propSetUuid, None)
      else:
          dictI = self.EdgeTagDictSync[tagI]
      if not dictI:
          return None
      alignI = dictI.get('align', None)
      return alignI


  def getSortedClustersEdgesOffset(self, fp, propSetUuid=None):
      offsetsList = []
      if not propSetUuid:
          clEdgeSameIndexFlat = self.clEdgeDict.get('clEdgeSameIndexFlat',None)
      else:
          clEdgeSameIndexFlat = None
          dictUuid = self.clEdgeDict.get(propSetUuid,None)
          if dictUuid:
              clEdgeSameIndexFlat = dictUuid.get('clEdgeSameIndexFlat',None)
          if not clEdgeSameIndexFlat:
              return []

      for i in clEdgeSameIndexFlat:
          curOffset = self.getEdgeTagDictSyncOffset(fp, None, i, propSetUuid)
          if not curOffset:
              curOffset = fp.Offset
          offsetsList.append(curOffset)
      return offsetsList


  def getEdgeTagDictSyncOffset(self,fp,tag=None,index=None,propSetUuid=None):
      if tag is not None:
          tagI = tag
      elif index is not None:
          try:
              tagI = fp.Geometry[index].Tag
          except:
              self.syncEdgeTagDictSync(fp)
              try:  # again
                  tagI = fp.Geometry[index].Tag
              except:
                  return None
      else:
          return None  #pass
      if propSetUuid:
          dictI = self.EdgeTagDictSync[tagI].get(propSetUuid, None)
      else:
          dictI = self.EdgeTagDictSync[tagI]
      if not dictI:
          return None
      OffsetI = dictI.get('offset', None)
      return OffsetI


  def getEdgeTagDictSyncRoleStatus(self, fp, tag=None, index=None,
                                   role='wallAxis', propSetUuid=None):

      if tag is not None:
          pass
      elif index is not None:
          tag = fp.Geometry[index].Tag
      if not propSetUuid:
          return self.EdgeTagDictSync[tag].get(role, 'Not Set')
      else:
          dictPropSet = self.EdgeTagDictSync[tag].get(propSetUuid, None)
          if dictPropSet:
               return dictPropSet.get(role, 'Not Set')
          else:
              return None


  def getEdgeTagDictSyncWallStatus(self,fp,tag=None,index=None,role='wallAxis',
                                   propSetUuid=None):

      roleStatus = self.getEdgeTagDictSyncRoleStatus(fp, tag, index, role,
                                                     propSetUuid)
      if roleStatus == True:
          wallAxisStatus = True
      elif roleStatus == 'Disabled':
          wallAxisStatus = False
      # 'Not Set' (default)
      else:
          if tag != None:  #elif
              index, none = self.getEdgeTagIndex(fp,tag, None)
          construction = fp.getConstruction(index)
          if not construction:  # for Wall, True if not construction
              wallAxisStatus = True
          else:
              wallAxisStatus = False
      return wallAxisStatus


  def getEdgeTagDictSyncStructureStatus(self, fp, tag=None, index=None,
                                        role='slab', propSetUuid=None):
      roleStatus = self.getEdgeTagDictSyncRoleStatus(fp, tag, index, role,
                                                     propSetUuid)
      if roleStatus == True:
          slabStatus = True
      elif roleStatus == 'Disabled':
          slabStatus = False
      # 'Not Set' (default) / False
      else:
          slabStatus = False
      return slabStatus


  def getEdgeTagDictSyncCurtainWallStatus(self, fp, tag=None, index=None,
                                role='curtainWallAxis', propSetUuid=None):

      roleStatus = self.getEdgeTagDictSyncRoleStatus(fp, tag, index, role,
                                                     propSetUuid)
      if roleStatus == True:
          cwAxisStatus = True
      elif roleStatus == 'Disabled':
          cwAxisStatus = False
      # 'Not Set' (default)
      else:
          cwAxisStatus = False
      return cwAxisStatus


  def getEdgeTagDictSyncStairsStatus(self, fp, tag=None, index=None,
                                role='flightAxis', propSetUuid=None):

      roleStatus = self.getEdgeTagDictSyncRoleStatus(fp, tag, index, role,
                                                     propSetUuid)
      if roleStatus == True:
          stairsStatus = True
      elif roleStatus == 'Disabled':
          stairsStatus = False
      # 'Not Set' (default)
      else:
          stairsStatus = False
      return stairsStatus


  def syncEdgeTagDictSync(self, fp):
      edgeTagDictTemp = {}

      i = 0
      while True:
          try:
              tagI = fp.Geometry[i].Tag
          except:
              break
          try:
              edgeTagDictSyncTagDict = self.EdgeTagDictSync[tagI]
          except:
              edgeTagDictSyncTagDict = {}
          edgeTagDictTemp[tagI] = edgeTagDictSyncTagDict
          edgeTagDictTemp[tagI]['index']=i
          i += 1
      self.EdgeTagDictSync = edgeTagDictTemp.copy()
      return


  def getEdgeTagDictArchiveTagIndex(self, fp, tag=None, index=None):
    if tag and index is None:
        try:
            return fp.Proxy.EdgeTagDictArchive[tag]['index'], None
        except:
            return None, None
    elif not tag and index is not None:
        try:
            for key, value in iter(fp.Proxy.EdgeTagDictArchive.items()):
                if value['index'] == index:
                    return None, key  # i.e. tagArchive
            return None, None
        except:
            return None, None


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


  '''  ArchWall-related          '''
  '''  ArchStructure-related     '''
  '''  ArchCurtainWall-related   '''


  def getWallBaseShapeEdgesInfo(self,fp,role='wallAxis',propSetUuid=None):

      edgesSortedClusters = []
      skGeom = fp.GeometryFacadeList
      skGeomEdges = []
      skPlacement = fp.Placement  # Get Sketch's placement to restore later

      for i in skGeom:
          if isinstance(i.Geometry, ArchSketch.GeomSupported):
              wallAxisStatus = self.getEdgeTagDictSyncWallStatus(fp, tag=i.Tag,
                                    role='wallAxis', propSetUuid=propSetUuid)
              if wallAxisStatus:
                  skGeomEdgesI = i.Geometry.toShape()
                  skGeomEdges.append(skGeomEdgesI)
      for cluster in Part.getSortedClusters(skGeomEdges):
          clusterTransformed = []
          for edge in cluster:
              edge.Placement = skPlacement.multiply(edge.Placement)
              clusterTransformed.append(edge)
          edgesSortedClusters.append(clusterTransformed)
      return {'wallAxis' : edgesSortedClusters}


  def getStructureBaseShapeWires(self, fp, role='slab', propSetUuid=None):

      skGeom = fp.GeometryFacadeList
      skGeomEdges = []
      skPlacement = fp.Placement  # Get Sketch's placement to restore later
      structureBaseShapeWires = []
      for i in skGeom:
          if isinstance(i.Geometry, ArchSketch.GeomSupported):
              slabStatus = self.getEdgeTagDictSyncStructureStatus(fp,
                           tag=i.Tag, role='slab', propSetUuid=propSetUuid)
              if slabStatus:
                  skGeomEdgesI = i.Geometry.toShape()
                  skGeomEdges.append(skGeomEdgesI)
      # Sort Sketch edges consistently with below procedures same as ArchWall
      clusterTransformed = []
      for cluster in Part.getSortedClusters(skGeomEdges):
          edgesTransformed = []
          for edge in cluster:
              edge.Placement = skPlacement.multiply(edge.Placement)
              edgesTransformed.append(edge)
          clusterTransformed.append(edgesTransformed)
      for clusterT in clusterTransformed:
          structureBaseShapeWires.append(Part.Wire(clusterT))

      return {'slabWires':structureBaseShapeWires, 'faceMaker':'Bullseye',
              'slabThickness' : 250}


  def getCurtainWallBaseShapeEdgesInfo(self, fp, role='curtainWallAxis',
                                       propSetUuid=None):

      skGeom = fp.GeometryFacadeList
      skGeomEdges = []
      skPlacement = fp.Placement  # Get Sketch's placement to restore later
      curtainWallBaseShapeEdges = []
      for i in skGeom:
          # support Line, Arc, Circle for Sketch as Base at the moment
          if isinstance(i.Geometry, (Part.LineSegment, Part.Circle,
                                     Part.ArcOfCircle)):
              cwAxisStatus = self.getEdgeTagDictSyncCurtainWallStatus(fp,
                                        tag=i.Tag,role='curtainWallAxis',
                                        propSetUuid=propSetUuid)
              if cwAxisStatus:
                  skGeomEdgesI = i.Geometry.toShape()
                  skGeomEdges.append(skGeomEdgesI)
      for edge in skGeomEdges:
          edge.Placement = edge.Placement.multiply(skPlacement)
          curtainWallBaseShapeEdges.append(edge)

      return {'curtainWallEdges':curtainWallBaseShapeEdges}


  def getStairsBaseShapeEdgesInfo(self,fp,role='wallAxis',propSetUuid=None):

      edgesSortedClusters = []
      skGeom = fp.GeometryFacadeList
      skGeomEdges = []
      skPlacement = fp.Placement  # Get Sketch's placement to restore later

      for i in skGeom:
          if isinstance(i.Geometry, ArchSketch.GeomSupported):
              flightAxisStatus = self.getEdgeTagDictSyncStairsStatus(fp,
                                 tag=i.Tag, role='flightAxis',
                                 propSetUuid=propSetUuid)
              if flightAxisStatus:
                  skGeomEdgesI = i.Geometry.toShape()
                  skGeomEdges.append(skGeomEdgesI)
      edgesTransformed = []
      for edge in skGeomEdges:
          edge.Placement = skPlacement.multiply(edge.Placement)
          edgesTransformed.append(edge)
      return {'flightAxis' : edgesTransformed}


  #*************************************************************************#


  ''' onDocumentRestored '''


  def onDocumentRestored(self, fp):

      self.setProperties(fp)
      self.setPropertiesLinkCommon(fp)
      self.initEditorMode(fp)

      ''' Rebuilding Tags  '''
      self.rebuildEdgeTagDicts(fp)
      self.callParentToRebuildMasterSketchTags(fp) # "Master"
      ''' Update to self.clEdgeDict Dict - For Backward Compatibility '''
      if not fp.ShapeList:
          self.updateShapeList(fp)
      self.updateSortedClustersEdgesOrder(fp)


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


class _CommandArchSketchLock():

    """GuiCommand for the ArchSketch Lock tool."""

    def __init__(self):
        FreeCAD.ArchSketchLock = True  #Assumed default checkable status

    def GetResources(self):
        return {'Pixmap' :   SketchArchIcon.getIconPath() +
                                          '/icons/ArchSketchLock.svg',
                "Accel":     "Shift+S",
                "MenuText":  QT_TRANSLATE_NOOP("ArchSketchLock",
                                               "ArchSketch Lock"),
                "ToolTip":   QT_TRANSLATE_NOOP("ArchSketchLock",
                             "Enable / Disable ArchSketch creation by " +
                             "ArchWall and ArchObjects"),
                "CmdType":   "NoTransaction",
                "Checkable": self.isChecked()}

    def IsActive(self):
        return True

    def Activated(self, status=0):
        if not status:  #if FreeCAD.ArchSketchLock:
            FreeCAD.ArchSketchLock = False
        else:
            FreeCAD.ArchSketchLock = True

    def isChecked(self):
        return FreeCAD.ArchSketchLock

FreeCADGui.addCommand('ArchSketchLock', _CommandArchSketchLock())


class _CommandEditWallAlign():

    '''Edit Align of Wall Segment (Underlying ArchSketch) Command Definition'''

    def GetResources(self):
        return {'Pixmap':SketchArchIcon.getIconPath()+'/icons/Edit_Align.svg',
                'Accel'   : "E, A",
                'MenuText': "Edit Wall Segment Align",
                'ToolTip' : "Select Wall/ArchSketch to Flip Segment Align ",
                'CmdType' : "ForEdit"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = "Select an Arch Wall (with Base ArchSketch) or ArchSketch"
        msg2 = "Arch Wall without Base is not supported - "
        msg3 = ("ArchSketchData is set False :  " +
                "This tool would update ArchWall's ArchSketchEdges " +
                "but Not data in the underlying ArchSketch")
        msg4 = ("Select target Edge of the ArchSketch " +
                "to Flip the corresponding Wall Segment Align")
        msg5 = ("Gui to edit Arch Wall with a DWire Base is not " +
                "implemented yet - Please directly edit ArchWall " +
                "OverrideAlign attribute for the purpose.")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        if Draft.getType(sel0) not in ["Wall","ArchSketch"]:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        if hasattr(sel0, "Base"): # Wall has Base, ArchSketch does not
            if sel0.Base:
                targetObjectBase = sel0.Base
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2 + msg1)
                return
        else:
            targetObjectBase = sel0
            if Draft.getType(sel0.InList[0]) in ["Wall"]:
                sel0 = sel0.InList[0]
            else:
                sel0 = None
        if Draft.getType(targetObjectBase) in ['ArchSketch']:
            targetObjectBase.ViewObject.HideDependent = False
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
            if not sel0.ArchSketchData:
                reply = QtGui.QMessageBox.information(None,"",msg3)
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            s=GuiEditWallAlignObserver(sel0, targetObjectBase)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)

        elif Draft.getType(targetObjectBase) == 'Wire':
            reply = QtGui.QMessageBox.information(None,"",msg5)

FreeCADGui.addCommand('EditWallAlign', _CommandEditWallAlign())


class GuiEditWallAlignObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self, targetWall, targetBaseSketch):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)
        self.targetWall = targetWall  # maybe None
        self.targetArchSketch = targetBaseSketch  # maybe None

        if targetWall and hasattr(targetWall.Proxy,'ArchSkPropSetPickedUuid')
            self.propSetUuid = targetWall.Proxy.ArchSkPropSetPickedUuid
        else:
            self.propSetUuid = None

        self.targetWallTransparentcy = targetWall.ViewObject.Transparency
        targetWall.ViewObject.Transparency = 60
        targetWall.recompute()
        if True:  # if not targetWall.ArchSketchData:
            wallAlign = targetWall.Align  # use Wall's Align
            tempOverrideAlign = self.targetWall.OverrideAlign
            # filling OverrideAlign for geometry edges
            while len(tempOverrideAlign) < len(targetBaseSketch.Geometry):
                tempOverrideAlign.append(wallAlign)
            tempOverrideAlign = [i if i is not None else wallAlign
                                 for i in tempOverrideAlign]
            self.targetWall.OverrideAlign = tempOverrideAlign

    def tasksSketchClose(self):
        self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy
        self.targetWall.recompute()
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subIndex = int( sub.lstrip('Edge'))-1
        App.Console.PrintMessage("Click Edge to change its Align"+ "\n")

        targetArchSk = self.targetArchSketch
        if (self.targetWall.ArchSketchData and hasattr(targetArchSk.Proxy,
                                               "getEdgeTagDictSyncAlign")):
            curAlign = targetArchSk.Proxy.getEdgeTagDictSyncAlign(self.
                                          targetArchSketch, None, subIndex,
                                          propSetUuid=self.propSetUuid)
            if curAlign == 'Left':
                curAlign = 'Right'
            elif curAlign == 'Right':
                curAlign = 'Center'
            elif curAlign == 'Center':
                curAlign = 'Left'
            else:  # 'Center' or else?
                curAlign = 'Right'
            tempDict = targetArchSk.Proxy.EdgeTagDictSync
            tempDictI = tempDict[targetArchSk.Geometry[subIndex].Tag]
            if self.propSetUuid:
                if not tempDictI.get(self.propSetUuid, None):
                    tempDictI[self.propSetUuid] = {}
                tempDictI[self.propSetUuid]['align'] = curAlign
            else:
                tempDictI['align'] = curAlign
            targetArchSk.Proxy.EdgeTagDictSync = tempDict
            targetArchSk.recompute()
        else:
            if (self.targetWall.ArchSketchData and not
                     hasattr(targetArchSk.Proxy, "getEdgeTagDictSyncAlign")):
                msg1 = ("ArchSketchData set but SketchArch Not installed : " +
                        "This tool would update ArchWall's ArchSketchEdges " +
                        "but Not data in the underlying ArchSketch")
                reply = QtGui.QMessageBox.information(None,"",msg1)
            curAlign = self.targetWall.OverrideAlign[subIndex]
            if curAlign == 'Left':
                curAlign = 'Right'
            elif curAlign == 'Right':
                curAlign = 'Center'
            elif curAlign == 'Center':
                curAlign = 'Left'
            else:  # 'Center' or else?
                curAlign = 'Right'

            # Save information in ArchWall
            if self.targetWall:
                tempOverrideAlign = self.targetWall.OverrideAlign
                tempOverrideAlign[subIndex] = curAlign
                self.targetWall.OverrideAlign = tempOverrideAlign
        FreeCADGui.Selection.clearSelection()
        if self.targetWall:
            self.targetWall.recompute()

    def escape(self,info):
        k=info['Key']
        if k=="ESCAPE":
            self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy
            SketchArchCommands.selectObjectObserver.escape(self,info)


class _CommandEditWallWidth():

    '''Edit Width of Wall Segment (Underlying ArchSketch) Command Definition'''

    def GetResources(self):
        return {'Pixmap':SketchArchIcon.getIconPath()+'/icons/Edit_Width.svg',
                'Accel'   : "E, D",
                'MenuText': "Edit Wall Segment Width",
                'ToolTip' : "select Wall to Edit Wall Segment Width ",
                'CmdType' : "ForEdit"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = "Select an Arch Wall (with Base ArchSketch) or ArchSketch"
        msg2 = "Arch Wall without Base is not supported - "
        msg3 = ("ArchSketchData is set False :  " +
                "This tool would update ArchWall's ArchSketchEdges " +
                "but Not data in the underlying ArchSketch")
        msg4 = ("Select target Edge of the ArchSketch " +
                "to Edit the corresponding Wall Segment Width")
        msg5 = ("Gui to edit Arch Wall with a DWire Base is not " +
                "implemented yet - Please directly edit ArchWall " +
                "OverrideWidth attribute for the purpose.")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        if Draft.getType(sel0) not in ["Wall","ArchSketch"]:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        if hasattr(sel0, "Base"):  # Wall has Base, ArchSketch does not
            if sel0.Base:
                targetObjectBase = sel0.Base
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2 + msg1)
                return
        else:
            targetObjectBase = sel0
            if Draft.getType(sel0.InList[0]) in ["Wall"]:
                sel0 = sel0.InList[0]
            else:
                sel0 = None
        if Draft.getType(targetObjectBase) in ['ArchSketch']:
            targetObjectBase.ViewObject.HideDependent = False
            if not sel0.ArchSketchData:
                reply = QtGui.QMessageBox.information(None,"",msg3)
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            s=GuiEditWallWidthObserver(sel0, targetObjectBase)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)

        elif Draft.getType(targetObjectBase) == 'Wire':
            reply = QtGui.QMessageBox.information(None,"",msg5)

FreeCADGui.addCommand('EditWallWidth', _CommandEditWallWidth())


class GuiEditWallWidthObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self, targetWall, targetBaseSketch):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)

        self.targetWall = targetWall
        self.targetArchSketch = targetBaseSketch

        if targetWall and hasattr(targetWall.Proxy,'ArchSkPropSetPickedUuid')
            self.propSetUuid = targetWall.Proxy.ArchSkPropSetPickedUuid
        else:
            self.propSetUuid = None

        self.targetWallTransparentcy = targetWall.ViewObject.Transparency
        targetWall.ViewObject.Transparency = 60
        targetWall.recompute()
        if not targetWall.ArchSketchData:
            wallWidth = targetWall.Width.Value  # use Wall's Width
            tempOverrideWidth = self.targetWall.OverrideWidth
            # filling OverrideWidth for geometry edges
            while len(tempOverrideWidth) < len(targetBaseSketch.Geometry):
                tempOverrideWidth.append(wallWidth)
            tempOverrideWidth = [i if i is not None else wallWidth
                                 for i in tempOverrideWidth]
            self.targetWall.OverrideWidth = tempOverrideWidth

    def tasksSketchClose(self):
        self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy
        self.targetWall.recompute()
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subIndex = int( sub.lstrip('Edge'))-1
        App.Console.PrintMessage("Input Width"+ "\n")
        curWidth = None
        targetArchSk = self.targetArchSketch
        if self.targetWall.ArchSketchData:
            curWidth = targetArchSk.Proxy.getEdgeTagDictSyncWidth(
                                          targetArchSk, None, subIndex,
                                          propSetUuid=self.propSetUuid)
            if not curWidth:
                curWidth = targetArchSk.ArchSketchWidth.Value
            if not curWidth:  # if above is 0
                curWidth = self.targetWall.OverrideWidth[subIndex]
        else:  # if not self.targetWall.ArchSketchData
            curWidth = self.targetWall.OverrideWidth[subIndex]

        reply = QtGui.QInputDialog.getText(None, "Input Width",
                                           "Width of Wall Segment",
                                           text=str(curWidth))
        if reply[1]:  # user clicked OK
            if reply[0]:
                replyWidth = float(reply[0])
            else:  # no input
                return None
        else:  # user clicked not OK, i.e. Cancel ?
            return None

        if self.targetWall.ArchSketchData:
            tempDict = targetArchSk.Proxy.EdgeTagDictSync
            tempDictI = tempDict[targetArchSk.Geometry[subIndex].Tag]
            if self.propSetUuid:
                if not tempDictI.get(self.propSetUuid, None):
                    tempDictI[self.propSetUuid] = {}
                tempDictI[self.propSetUuid]['width'] = replyWidth
            else:
                tempDictI['width'] = replyWidth
            targetArchSk.Proxy.EdgeTagDictSync = tempDict
        else:  # if not self.targetWall.ArchSketchData
            # Save information in ArchWall
            tempOverrideWidth = self.targetWall.OverrideWidth
            tempOverrideWidth[subIndex] = replyWidth
            self.targetWall.OverrideWidth = tempOverrideWidth
        FreeCADGui.Selection.clearSelection()
        targetArchSk.recompute()
        self.targetWall.recompute()

    def escape(self,info):
        k=info['Key']
        if k=="ESCAPE":
            targetWall = self.targetWall
            targetWall.ViewObject.Transparency = self.targetWallTransparentcy
            SketchArchCommands.selectObjectObserver.escape(self,info)


class _CommandEditWallOffset():

    '''Edit Offset of Wall Segment (Underlying ArchSketch) Command Definition'''

    def GetResources(self):
        return {'Pixmap':SketchArchIcon.getIconPath()+'/icons/Edit_Offset.svg',
                'Accel'   : "E, F",
                'MenuText': "Edit Wall Segment Offset",
                'ToolTip' : "select Wall to Edit Wall Segment Offset ",
                'CmdType' : "ForEdit"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = "Select an Arch Wall (with Base ArchSketch) or ArchSketch"
        msg2 = "Arch Wall without Base is not supported - "
        msg3 = ("ArchSketchData is set False :  " +
                "This tool would update ArchWall's ArchSketchEdges " +
                "but Not data in the underlying ArchSketch")
        msg4 = ("Select target Edge of the ArchSketch " +
                "to Edit the corresponding Wall Segment Offset")
        msg5 = ("Gui to edit Arch Wall with a DWire Base is not " +
                "implemented yet - Please directly edit ArchWall " +
                "OverrideOffset attribute for the purpose.")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        if Draft.getType(sel0) not in ["Wall","ArchSketch"]:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        if hasattr(sel0, "Base"):  # Wall has Base, ArchSketch does not
            if sel0.Base:  # ArchSketch or Sketch
                targetObjectBase = sel0.Base
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2 + msg1)
                return
        else:
            targetObjectBase = sel0
            if Draft.getType(sel0.InList[0]) in ["Wall"]:
                sel0 = sel0.InList[0]
            else:
                sel0 = None
        if Draft.getType(targetObjectBase) in ['ArchSketch']:
            targetObjectBase.ViewObject.HideDependent = False
            if not sel0.ArchSketchData:
                reply = QtGui.QMessageBox.information(None,"",msg3)
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            s=GuiEditWallOffsetObserver(sel0, targetObjectBase)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)
        elif Draft.getType(targetObjectBase) == 'Wire':
            reply = QtGui.QMessageBox.information(None,"",msg5)

FreeCADGui.addCommand('EditWallOffset', _CommandEditWallOffset())


class GuiEditWallOffsetObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self, targetWall, targetBaseSketch):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)

        self.targetWall = targetWall
        self.targetArchSketch = targetBaseSketch

        if targetWall and hasattr(targetWall.Proxy,'ArchSkPropSetPickedUuid')
            self.propSetUuid = targetWall.Proxy.ArchSkPropSetPickedUuid
        else:
            self.propSetUuid = None

        self.targetWallTransparentcy = targetWall.ViewObject.Transparency
        targetWall.ViewObject.Transparency = 60
        targetWall.recompute()
        if not targetWall.ArchSketchData:
            wallWidth = targetWall.Offset.Value  # use Wall's Offset
            tempOverrideOffset = self.targetWall.OverrideOffset
            # filling OverrideOffset for geometry edges
            while len(tempOverrideOffset) < len(targetBaseSketch.Geometry):
                tempOverrideOffset.append(wallOffset)
            tempOverrideOffset = [i if i is not None else wallOffset
                                  for i in tempOverrideOffset]
            self.targetWall.OverrideOffset = tempOverrideOffset

    def tasksSketchClose(self):
        self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy
        self.targetWall.recompute()
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subIndex = int( sub.lstrip('Edge'))-1
        App.Console.PrintMessage("Input Width"+ "\n")
        curOffset = None
        targetArchSk = self.targetArchSketch
        if self.targetWall.ArchSketchData:
            curOffset = targetArchSk.Proxy.getEdgeTagDictSyncOffset(
                                           targetArchSk, None, subIndex,
                                           propSetUuid=self.propSetUuid)
            if not curOffset:
                curOffset = targetArchSk.Offset
        else:  # if not self.targetWall.ArchSketchData
            curOffset = self.targetWall.OverrideOffset[subIndex]

        reply = QtGui.QInputDialog.getText(None, "Input Offset",
                                           "Offset of Wall Segment",
                                           text=str(curOffset))
        if reply[1]:  # user clicked OK
            if reply[0]:
                replyOffset = float(reply[0])
            else:  # no input
                return None
        else:  # user clicked not OK, i.e. Cancel ?
            return None
        if self.targetWall.ArchSketchData:
            tempDict = targetArchSk.Proxy.EdgeTagDictSync
            tempDictI = tempDict[targetArchSk.Geometry[subIndex].Tag]
            if self.propSetUuid:
                if not tempDictI.get(self.propSetUuid, None):
                    tempDictI[self.propSetUuid] = {}
                tempDictI[self.propSetUuid]['offset'] = replyOffset
            else:
                tempDictI['offset'] = replyOffset
            targetArchSk.Proxy.EdgeTagDictSync = tempDict
        #elif targetArchSk is not None:
        else:  # if not self.targetWall.ArchSketchData
            # Save information in ArchWall
            tempOverrideOffset = self.targetWall.OverrideOffset
            tempOverrideOffset[subIndex] = replyOffset
            self.targetWall.OverrideOffset = tempOverrideOffset
        FreeCADGui.Selection.clearSelection()
        targetArchSk.recompute()
        self.targetWall.recompute()

    def escape(self,info):
        k=info['Key']
        if k=="ESCAPE":
            targetWall = self.targetWall
            targetWall.ViewObject.Transparency = self.targetWallTransparentcy
            SketchArchCommands.selectObjectObserver.escape(self,info)


class _CommandEditWallAttach():

    '''Edit ArchObjects and ArchSketch Attachment Command Definition
       edit attachment to Wall Segment (Underlying Arch]Sketch)'''

    def GetResources(self):
        return {'Pixmap':SketchArchIcon.getIconPath()+'/icons/Edit_Attach.svg',
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

        # If a Link is newly created and not Recomputed, its Hosts attribute
        # is not added to the Link.  Now, if its Hosts[0] is assigned to the
        # Sel1, then it is the Linked Object's Hosts attribute be altered
        # The result is, instead of the Sel0 object got new Hosts[0] and
        # attach to it, it is 'wrongly' the Linked Object (the 'Original')
        # attach to new Hosts[0] ! - Check and Recompute if State is Touched

        if "Touched" in sel0.State: #  == "Touched":  # State is a List
            sel0.recompute()

        msg1 = ("Select an ArchSketch or Arch Window/Equipment, Click " +
                "this Button, and select the edge to attach ")
        msg2 =  "Target Object is Not Wall - Feature not supported 'Yet'"
        msg3 = ("Select a Window/Equipment with Host which is Arch Wall " +
                "(or a Window/Equipment with an ArchWall as 2nd selection)")
        msg4 =  "Window/Equipment's Host needs to be a Wall to function"
        msg5 = ("Wall needs to have Base which is to be Sketch or " +
                "ArchSketch to function (needs a MasterSketch to function)")
        msg6 = ("Select target Edge of the ArchSketch / Sketch to attach to" +
                "\n")
        msg7 = ("Gui to edit Arch Wall with a DWire Base is not " +
                "implemented yet - Please directly edit ArchWall " +
                "OverrideAlign attribute for the purpose.")
        targetHostWall = None
        targetBaseSketch = None

        if Draft.getType(sel0.getLinkedObject()) not in ['ArchSketch',
                                                         'Window','Equipment']:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        # check if targetHostWall is selected by user : which take precedence
        if sel1:
            if Draft.getType(sel1) != 'Wall':
                reply = QtGui.QMessageBox.information(None,"", msg2)
                return
            else:
                targetHostWall = sel1
        # if no sel1: check if it was assigned - or use Windows.Hosts /
        # Equipment.Host, i.e. not changing targetHostWall
        # Window has Hosts, Equipment Host
        elif hasattr(sel0, "Host"):
            if sel0.Host:
                targetHostWall = sel0.Host
        elif hasattr(sel0, "Hosts"):
            if sel0.Hosts:
                targetHostWall = sel0.Hosts[0]  # TODO to scan through ?
        if not targetHostWall:
            # ArchSketch can has no hostWall / attach to (Arch)Sketch directly
            if Draft.getType(sel0.getLinkedObject()) != 'ArchSketch':
                reply = QtGui.QMessageBox.information(None,"",msg3)
                return
        elif Draft.getType(targetHostWall) != 'Wall':
            reply = QtGui.QMessageBox.information(None,"",msg4)
            return
        if targetHostWall:
            if targetHostWall.Base:
                targetBaseSketch = targetHostWall.Base
        elif hasattr(sel0, "MasterSketch"):
            if sel0.MasterSketch:
                targetBaseSketch = sel0.MasterSketch
        if not targetBaseSketch:
            reply = QtGui.QMessageBox.information(None,"",msg5)
            return
        if Draft.getType(targetBaseSketch) in ['ArchSketch',
                                               'Sketcher::SketchObject']:
            targetBaseSketch.ViewObject.HideDependent = False
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
            Gui.ActiveDocument.setEdit(targetBaseSketch)
            App.Console.PrintMessage(msg6)
            FreeCADGui.Selection.clearSelection()
            s=GuiEditWallAttachObserver(sel0, targetHostWall, targetBaseSketch)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)
        elif Draft.getType(targetBaseSketch) == 'Wire':
            reply = QtGui.QMessageBox.information(None,"",msg7)
        else:
            reply = QtGui.QMessageBox.information(None,"",msg5)
            return


FreeCADGui.addCommand('EditWallAttach', _CommandEditWallAttach())


class GuiEditWallAttachObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self, targetObject, targetHostWall, targetBaseSketch):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)
        self.targetObject = targetObject
        self.targetWall = targetHostWall
        self.targetArchSketch = targetBaseSketch
        if self.targetWall:
            self.targetWallTransparentcy=targetHostWall.ViewObject.Transparency
            targetHostWall.ViewObject.Transparency = 60
            targetHostWall.recompute()
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

    def tasksSketchClose(self):
        if self.targetWall:
            self.targetWall.ViewObject.Transparency = (
                self.targetWallTransparentcy )
            self.targetWall.recompute()
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subElement = sub.lstrip('Edge')

        if self.targetArchSketch is not None:
            self.targetObject.MasterSketchSubelement = subElement
            geoindex = int(subElement.lstrip('Edge'))-1
            none, tag = self.targetArchSketch.Proxy.getEdgeTagIndex(
                                      self.targetArchSketch, None, geoindex)
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
        FreeCADGui.Selection.clearSelection()
        self.targetObject.recompute()
        if self.targetWall:
            self.targetWall.recompute()

    def escape(self,info):
        k=info['Key']
        if k=="ESCAPE":
            if self.targetWall:
                self.targetWall.ViewObject.Transparency = (
                                               self.targetWallTransparentcy)
            SketchArchCommands.selectObjectObserver.escape(self,info)


class _CommandEditStructure():

    '''Edit Structure (Underlying ArchSketch) Command Definition'''
    '''Not supporting Sketch                                    '''
    def GetResources(self):
        return {'Pixmap'  : SketchArchIcon.getIconPath() +
                                      '/icons/Edit_Structure_Toggle.svg',
                'Accel'   : "E, S",
                'MenuText': "Edit Structure",
                'ToolTip' : "Select Structure/ArchSketch to edit ",
                'CmdType' : "ForEdit"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = "Select an Arch Structure (with Base ArchSketch) or ArchSketch"
        msg2 = "Arch Structure without Base is not supported - "
        msg3 = ("ArchSketchData is set False :  " +
                "This tool would update Arch Structure's ArchSketchEdges " +
                "but Not data in the underlying ArchSketch")
        msg4 = ("Select target Edge of the ArchSketch " +
                "to turn it on/off as Structure (Slab) edges")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        if Draft.getType(sel0) not in ["Structure","ArchSketch"]:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        if hasattr(sel0, "Base"): # Wall has Base, ArchSketch does not
            if sel0.Base:  # ArchSketch or Sketch
                targetObjectBase = sel0.Base
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2 + msg1)
                return
        else:
            targetObjectBase = sel0
            if Draft.getType(sel0.InList[0]) in ["Structure"]:
                sel0 = sel0.InList[0]
            else:
                sel0 = None
        if Draft.getType(targetObjectBase) in ['ArchSketch']:
            targetObjectBase.ViewObject.HideDependent = False
            #Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
            if not sel0.ArchSketchData:
                reply = QtGui.QMessageBox.information(None,"",msg3)
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            s=GuiEditStructureObserver(sel0, targetObjectBase)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)


FreeCADGui.addCommand('EditStructure', _CommandEditStructure())


class GuiEditStructureObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self, targetStruc, targetBaseSketch, propSetUuid=None):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)
        self.targetStruc = targetStruc  # maybe None
        self.targetArchSketch = targetBaseSketch
        if propSetUuid:
            self.propSetUuid = propSetUuid
        else:
            if targetStruc and hasattr(targetStruc.Proxy,
                                       'ArchSkPropSetPickedUuid')
                self.propSetUuid = targetStruc.Proxy.ArchSkPropSetPickedUuid
            else:
                self.propSetUuid = None
        if self.targetStruc:
            self.targetStrucTransparency = targetStruc.ViewObject.Transparency
            targetStruc.ViewObject.Transparency = 60
            targetStruc.recompute()

    def tasksSketchClose(self):
        targetStrucVobj = self.targetStruc.ViewObject
        targetStrucVobj.Transparency = self.targetStrucTransparency
        #self.targetStruc.recompute()
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subIndex = int( sub.lstrip('Edge'))-1
        curStrucStatus = None
        newStrucStatus = None
        targetArchSk = self.targetArchSketch
        targetArchSkPx = targetArchSk.Proxy
        if self.targetStruc.ArchSketchData:
            curStrucStatus = targetArchSkPx.getEdgeTagDictSyncStructureStatus(
                             targetArchSk, None, subIndex, role='slab',
                             propSetUuid=self.propSetUuid)
            if curStrucStatus == False:  # not curStrucStatus:
                newStrucStatus = True  # 'Enabled'
            elif curStrucStatus == True:  # curStrucStatus:
                newStrucStatus = 'Disabled'
            elif curStrucStatus == 'Disabled':
                newStrucStatus = True  # 'Enabled'
            else:  #'Not Used' / False
                newStrucStatus = True  # 'Enabled'
            tempDict = targetArchSkPx.EdgeTagDictSync
            tempDictI = tempDict[targetArchSk.Geometry[subIndex].Tag]
            if self.propSetUuid:
                if not tempDictI.get(self.propSetUuid, None):
                    tempDictI[self.propSetUuid] = {}
                tempDictI[self.propSetUuid]['slab'] = newStrucStatus
            else:
                tempDictI['slab'] = newStrucStatus
            targetArchSkPx.EdgeTagDictSync = tempDict
            self.targetArchSketch.recompute()
        else:
            slabEdgesList = self.targetStruc.ArchSketchEdges
            if str(subIndex) in slabEdgesList:
                slabEdgesList.remove(str(subIndex))
            else:
                slabEdgesList.append(str(subIndex))
            self.targetStruc.ArchSketchEdges = slabEdgesList
        FreeCADGui.Selection.clearSelection()
        if self.targetStruc:
            self.targetStruc.recompute()

    def escape(self,info):
        k=info['Key']
        if k=="ESCAPE":
            SketchArchCommands.selectObjectObserver.escape(self,info)


class _CommandEditCurtainWall():

    '''Edit CurtainWall (Underlying ArchSketch) Command Definition'''
    '''Not supporting Sketch                                    '''
    def GetResources(self):
        return {'Pixmap'  : SketchArchIcon.getIconPath() +
                                      '/icons/Edit_CurtainWall_Toggle.svg',
                'Accel'   : "E, C",
                'MenuText': "Edit Curtain Wall",
                'ToolTip' : "Select Curtain Wall/ArchSketch to edit ",
                'CmdType' : "ForEdit"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = "Select an Arch CurtainWall (with Base ArchSketch) / ArchSketch"
        msg2 = "Arch CurtainWall without Base is not supported - "
        msg3 = ("ArchSketchData is set False :  " +
                "This tool would update CurtainWall's ArchSketchEdges " +
                "but Not data in the underlying ArchSketch")
        msg4 = ("Select target Edge of the ArchSketch " +
                "to turn it on/off as CurtainWall Segment")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        if Draft.getType(sel0) in ["ArchSketch"]:
            inListCW = Draft.getObjectsOfType(sel0.InList, "CurtainWall")
            targetObjectBase = sel0
            if not inListCW:
                sel0 = [ArchCurtainWall.makeCurtainWall(sel0)]
                App.ActiveDocument.recompute()
            else:
                sel0 = inListCW
        elif Draft.getType(sel0) in ["CurtainWall"]:
            if sel0.Base and Draft.getType(sel0.Base) in ["ArchSketch"]:
                targetObjectBase = sel0.Base
                sel0 = [sel0]
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2 + msg1)
                return
        else:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        if True:
            targetObjectBase.ViewObject.HideDependent = False
            Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            s=GuiEditCurtainWallObserver(sel0, targetObjectBase)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)


FreeCADGui.addCommand('EditCurtainWall', _CommandEditCurtainWall())


class GuiEditCurtainWallObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self,targetCwList,targetBaseSketch,propSetUuid=None):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)

        self.targetCwList = targetCwList
        self.targetArchSketch = targetBaseSketch
        targetCw0 = targetCwList[0]  # all should be same as it is screened
        if propSetUuid:
            self.propSetUuid = propSetUuid
        else:
            if targetCw0 and hasattr(targetCw0.Proxy,'ArchSkPropSetPickedUuid')
                self.propSetUuid = targetCw0.Proxy.ArchSkPropSetPickedUuid
            else:
                self.propSetUuid = None
        if self.targetCwList:
            self.targetCwListTransparency = []
            for c in self.targetCwList:
                t = c.ViewObject.Transparency
                c.ViewObject.Transparency = 60
                c.recompute()
                self.targetCwListTransparency.append(t)

    def tasksSketchClose(self):
        if self.targetCwList:
            for c in self.targetCwList:
                t = self.targetCwListTransparency.pop(0)
                c.ViewObject.Transparency = t
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subIndex = int( sub.lstrip('Edge'))-1
        curCwStatus = None
        newCwStatus = None
        targetArchSk = self.targetArchSketch
        targetCw0 = self.targetCwList[0]
        if targetCw0.ArchSketchData:
            curCwStatus=targetArchSk.Proxy.getEdgeTagDictSyncCurtainWallStatus(
                        targetArchSk, None, subIndex, role='curtainWallAxis',
                        propSetUuid=self.propSetUuid)
            if curCwStatus == False or curCwStatus == 'Not Set':
                newCwStatus = True  # 'Enabled'
            elif curCwStatus == True:
                newCwStatus = 'Disabled'
            elif curCwStatus == 'Disabled':
                newCwStatus = True  # 'Enabled'
            tempDict = targetArchSk.Proxy.EdgeTagDictSync
            tempDictI = tempDict[targetArchSk.Geometry[subIndex].Tag]
            if self.propSetUuid:
                if not tempDictI.get(self.propSetUuid, None):
                    tempDictI[self.propSetUuid] = {}
                tempDictI[self.propSetUuid]['curtainWallAxis'] = newCwStatus
            else:
                tempDictI['curtainWallAxis'] = newCwStatus
            targetArchSk.Proxy.EdgeTagDictSync = tempDict
            targetArchSk.recompute()
        else:
            for c in self.targetCwList:
                curtainWallEdgesList = c.OverrideEdges
                # 2 status :  True or Disabled (no False)
                if str(subIndex) in curtainWallEdgesList:
                    curtainWallEdgesList.remove(str(subIndex))
                else:
                    curtainWallEdgesList.append(str(subIndex))
                c.OverrideEdges = curtainWallEdgesList
        FreeCADGui.Selection.clearSelection()
        for c in self.targetCwList:
            c.recompute()

    def escape(self,info):
        k=info['Key']
        if k=="ESCAPE":
            SketchArchCommands.selectObjectObserver.escape(self,info)


class _CommandEditWall():

    '''Edit ArchWall (Underlying ArchSketch) Command Definition '''

    def GetResources(self):
        return {'Pixmap'  : SketchArchIcon.getIconPath() +
                                           '/icons/Edit_Wall_Toggle.svg',
                'Accel'   : "E, W",
                'MenuText': "Edit Wall",
                'ToolTip' : "Select Wall / ArchSketch to edit ",
                'CmdType' : "ForEdit"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = "Select an Arch Wall (with Base ArchSketch) or ArchSketch"
        msg2 = "Arch Wall without Base is not supported - "
        msg3 = ("ArchSketchData is set False :  " +
                "This tool would update ArchWall's ArchSketchEdges " +
                "but Not data in the underlying ArchSketch")
        msg4 = ("Select target Edge of the ArchSketch " +
                "to turn it on/off as Wall Segment")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        if Draft.getType(sel0) not in ['Wall', 'ArchSketch']:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        if hasattr(sel0, "Base"):  # Wall has Base, ArchSketch does not
            if sel0.Base:  # ArchSketch or Sketch
                targetObjectBase = sel0.Base
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2 + msg1)
                return
        else:
            targetObjectBase = sel0
            if Draft.getType(sel0.InList[0]) in ["Wall"]:
                sel0 = sel0.InList[0]
            else:
                sel0 = None
        if Draft.getType(targetObjectBase) in ['ArchSketch']:
            targetObjectBase.ViewObject.HideDependent = False
            #Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
            if not sel0.ArchSketchData:
                reply = QtGui.QMessageBox.information(None,"",msg3)
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            s=GuiEditWallObserver(sel0, targetObjectBase)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)


FreeCADGui.addCommand('EditWall', _CommandEditWall())


class GuiEditWallObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self, targetWall, targetBaseSketch, propSetUuid=None):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)
        self.targetWall = targetWall
        self.targetArchSketch = targetBaseSketch
        if propSetUuid:
            self.propSetUuid = propSetUuid
        else:
            if targetWall and hasattr(targetWall.Proxy,
                                      'ArchSkPropSetPickedUuid')
                self.propSetUuid = targetWall.Proxy.ArchSkPropSetPickedUuid
            else:
                self.propSetUuid = None
        if self.targetWall:
            self.targetWallTransparency = targetWall.ViewObject.Transparency
            targetWall.ViewObject.Transparency = 60
            targetWall.recompute()

    def tasksSketchClose(self):
        self.targetWall.ViewObject.Transparency = self.targetWallTransparency
        self.targetWall.recompute()
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subIndex = int( sub.lstrip('Edge'))-1
        curWallStatus = None
        newWallStatus = None
        targetArchSk = self.targetArchSketch
        if self.targetWall.ArchSketchData:
            curWallStatus = targetArchSk.Proxy.getEdgeTagDictSyncRoleStatus(
                            targetArchSk, None, subIndex, role='wallAxis',
                            propSetUuid=self.propSetUuid)
            if curWallStatus == True:
                newWallStatus = 'Disabled'
            elif curWallStatus == 'Disabled':
                newWallStatus = True
            else:
                construction = targetArchSk.getConstruction(subIndex)
                if not construction:  # for Wall, True if not construction
                    newWallStatus = 'Disabled'
                else:
                    newWallStatus = True
            tempDict = targetArchSk.Proxy.EdgeTagDictSync
            tempDictI = tempDict[targetArchSk.Geometry[subIndex].Tag]
            if self.propSetUuid:
                if not tempDictI.get(self.propSetUuid, None):
                    tempDictI[self.propSetUuid] = {}
                tempDictI[self.propSetUuid]['wallAxis'] = newWallStatus
            else:
                tempDictI['wallAxis'] = newWallStatus
            targetArchSk.Proxy.EdgeTagDictSync = tempDict
            self.targetArchSketch.recompute()
            wallEdgesList = self.targetWall.ArchSketchEdges
            if str(subIndex) in wallEdgesList:
                wallEdgesList.remove(str(subIndex))
            else:
                wallEdgesList.append(str(subIndex))
            self.targetWall.ArchSketchEdges = wallEdgesList
        FreeCADGui.Selection.clearSelection()
        if self.targetWall:
            self.targetWall.recompute()

    def escape(self,info):
        k=info['Key']
        if k=="ESCAPE":
            SketchArchCommands.selectObjectObserver.escape(self,info)


class _CommandEditStairs():

    '''Edit Stairs (Underlying ArchSketch) Command Definition'''
    '''Not supporting Sketch                                 '''
    def GetResources(self):
        return {'Pixmap'  : SketchArchIcon.getIconPath() +
                                      '/icons/Edit_Stairs_Toggle.svg',
                'Accel'   : "E, R",
                'MenuText': "Edit Stairs",
                'ToolTip' : "Select Stairs/ArchSketch to edit ",
                'CmdType' : "ForEdit"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = "Select an Arch Stairs (with Base ArchSketch) or ArchSketch"
        msg2 = "Arch Stairs without Base is not supported - "
        msg3 = ("ArchSketchData is set False :  " +
                "This tool would update Arch Stairs's ArchSketchEdges " +
                "but Not data in the underlying ArchSketch")
        msg4 = ("Select target Edge of the ArchSketch " +
                "to turn it on/off as Stairs (Flight) axis")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        if Draft.getType(sel0) not in ["Stairs","ArchSketch"]:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        if hasattr(sel0, "Base"): # Wall has Base, ArchSketch does not
            if sel0.Base:  # ArchSketch or Sketch
                targetObjectBase = sel0.Base
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2 + msg1)
                return
        else:
            targetObjectBase = sel0
            if Draft.getType(sel0.InList[0]) in ["Stairs"]:
                sel0 = sel0.InList[0]
            else:
                sel0 = None
        if Draft.getType(targetObjectBase) in ['ArchSketch']:
            targetObjectBase.ViewObject.HideDependent = False
            #Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
            if not sel0.ArchSketchData:
                reply = QtGui.QMessageBox.information(None,"",msg3)
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            s=GuiEditStairsObserver(sel0, targetObjectBase)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)


FreeCADGui.addCommand('EditStairs', _CommandEditStairs())


class GuiEditStairsObserver(SketchArchCommands.selectObjectObserver):

    def __init__(self, targetStairs, targetBaseSketch, propSetUuid=None):
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,
                                                         'Edge')
        mw = FreeCADGui.getMainWindow()
        self.taskspanel = mw.findChild(QtGui.QDockWidget, "Tasks")
        self.manualUpdateBtn = self.taskspanel.findChild(QtGui.QToolButton,
                                                         "manualUpdate")
        self.manualUpdateBtn.destroyed.connect(self.tasksSketchClose)
        self.targetStairs = targetStairs  # maybe None
        self.targetArchSketch = targetBaseSketch
        if propSetUuid:
            self.propSetUuid = propSetUuid
        else:
            if targetStairs and hasattr(targetStairs.Proxy,
                                        'ArchSkPropSetPickedUuid')
                self.propSetUuid = targetStairs.Proxy.ArchSkPropSetPickedUuid
            else:
                self.propSetUuid = None
        if self.targetStairs:
            self.targetStairsTransparency= targetStairs.ViewObject.Transparency
            targetStairs.ViewObject.Transparency = 60
            targetStairs.recompute()
        modeDict = dict()
        modeDict['parts'] = 'flight'  #default
        modeDict['edit'] = 'toggle'  #default
        self.mode=modeDict

    def tasksSketchClose(self):
        targetStairsVobj = self.targetStairs.ViewObject
        targetStairsVobj.Transparency = self.targetStairsTransparency
        FreeCADGui.Selection.removeObserver(self)
        self.av.removeEventCallback("SoKeyboardEvent",self.escape)

    def proceed(self, doc, obj, sub, pnt):
        self.edge = sub
        self.pickedEdgePlacement = App.Vector(pnt)
        subIndex = int( sub.lstrip('Edge'))-1
        curStairsStatus = None
        newStairsStatus = None
        targetArchSk = self.targetArchSketch
        targetArchSkPx = targetArchSk.Proxy
        if self.targetStairs.ArchSketchData:
            curStairsStatus = targetArchSkPx.getEdgeTagDictSyncStairsStatus(
                             targetArchSk, None, subIndex, role='flightAxis',
                             propSetUuid=self.propSetUuid)
            if curStairsStatus == False:  # not curStairsStatus:
                newStairsStatus = True  # 'Enabled'
            elif curStairsStatus == True:  # curStairsStatus:
                newStairsStatus = 'Disabled'
            elif curStairsStatus == 'Disabled':
                newStairsStatus = True  # 'Enabled'
            else:  #'Not Used' / False
                newStairsStatus = True  # 'Enabled'
            tempDict = targetArchSkPx.EdgeTagDictSync
            #for i in range(0, len(targetArchSk.Geometry)):
            #    # just turn every edge to false to save time
            #    tempDictI = tempDict[targetArchSk.Geometry[i].Tag]
            #    if self.propSetUuid:
            #        if not tempDictI.get(self.propSetUuid, None):
            #            tempDictI[self.propSetUuid] = {}
            #        tempDictI[self.propSetUuid]['flightAxis'] = 'Disabled'
            #    else:
            #        tempDictI['flightAxis'] = 'Disabled'
            tempDictI = tempDict[targetArchSk.Geometry[subIndex].Tag]
            if self.propSetUuid:
                if not tempDictI.get(self.propSetUuid, None):
                    tempDictI[self.propSetUuid] = {}
                tempDictI[self.propSetUuid]['flightAxis'] = newStairsStatus
            else:
                tempDictI['flightAxis'] = newStairsStatus
            targetArchSkPx.EdgeTagDictSync = tempDict
            self.targetArchSketch.recompute()
        else:
            flightAxis = self.targetStairs.ArchSketchEdges
            if str(subIndex) in flightAxis:
                flightAxis.remove(str(subIndex))
            else:
                flightAxis.append(str(subIndex))
            self.targetStairs.ArchSketchEdges = flightAxis
        FreeCADGui.Selection.clearSelection()
        if self.targetStairs:
            self.targetStairs.recompute()

    def escape(self,info):
        super().escape(info)
        k=info['Key']
        s=info['State']
        if k=="f":
            modeDict = self.mode
            if modeDict.get('parts', None) == 'flight':
                modeDict['parts'] = 'landing'
                App.Console.PrintMessage(" Edit Landing ..." + "\n")
            elif modeDict.get('parts', None) == 'landing':
                modeDict['parts'] = 'flight'
                App.Console.PrintMessage(" Edit Flight ..." + "\n")
            self.mode = modeDict
        elif k=="SHIFT" and s=="DOWN":
            self.shiftDown=True
        elif k=="SHIFT" and s=="UP":
            self.shiftDown=False


class _CommandPropertySet():

    ''' PropertySet Command Definition - Gui to make Variant PropertySet '''

    def GetResources(self):

        return {'Pixmap' : SketchArchIcon.getIconPath() +
                                          '/icons/PropertySet.svg',
                'Accel' : "Alt+T",
                'MenuText': "Variant PropertySet",
                'ToolTip' : "Create Variant Layout, Properties, Layer etc." +
                            "(add extra PropertySet to ArchSketch )"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
        msg1 = ("Select ArchSketch / Arch Objects (Wall, CurtainWall, " +
                "Structure (Slab), Stairs supported currently) with " +
                "underlying Base ArchSketch.")
        msg2 = ("Arch Wall/ CurtainWall/ Structure (Slab)/ Stairs without " +
                "Base ArchSketch is not supported - " + msg1)
        msg3a= ("Create extra PropertySet to base ArchSketch.  Create Arch " +
                "Object as selected and set its ArchSketch PropertySet to " +
                "the new set.  Input PropertySet name here. ")
        msg3b= ("Create extra PropertySet to base ArchSketch.  Input " +
                "PropertySet name here. ")
        msg3c= ("PropertySet Not set to Default.  Could change the selected " +
                "PropertySet name by inputting new name here.  Canel to " +
                "skip and to create new PropertySet.")
        msg4 = ("Select target Edge of the ArchSketch to turn it on/off " +
                "as Wall/CurtainWall/Structure (Slab)/Stairs Segment")
        try:
            sel0 = Gui.Selection.getSelection()[0]
        except:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        targetObjectBase = None
        # Verify selection type and find ArchSkech/Arch Objects
        supportedObjects = ['Wall', 'CurtainWall', 'Structure', 'ArchSketch',
                            'Stairs']
        if Draft.getType(sel0) not in supportedObjects:
            reply = QtGui.QMessageBox.information(None,"",msg1)
            return
        elif hasattr(sel0, "Base"):  # (Curtain)Wall, Stairs can have no Base
            if Draft.getType(sel0.Base) in ['ArchSketch']:
                targetObjectBase = sel0.Base
            else:
                reply = QtGui.QMessageBox.information(None,"",msg2)
                return
        else:  # ArchSketch
            targetObjectBase = sel0
        # If selected ArchSketch/ArcObjects has PropertySet set to one other
        # than Default, may change PropertyName rather than creating one.
        changeName = False
        # sel0 is Wall, CurtainWall, Structure (Slab), Stairs
        if (sel0 != targetObjectBase) and (sel0.ArchSketchPropertySet
                                           != 'Default'):
            changeName = True
            if hasattr(sel0.Proxy,'ArchSkPropSetPickedUuid')
                psUuid = sel0.Proxy.ArchSkPropSetPickedUuid
            else:
                psUuid = None
        # sel0 is only ArchSketch
        elif (sel0 == targetObjectBase) and (targetObjectBase.PropertySet
                                             != 'Default'):
            changeName = True
            psUuid = targetObjectBase.Proxy.PropSetPickedUuid
        if changeName:
            psn = targetObjectBase.Proxy.getPropertySet(targetObjectBase,
                                                        propSetUuid=psUuid)
            reply = QtGui.QInputDialog.getText(None, "Input PropertySet Name",
                                               msg3c, text=psn)
            if reply[1]:  # user clicked OK
                psn = reply[0]
                targetObjectBase.Proxy.PropertySetDict[psUuid]['name'] = psn
                targetObjectBase.recompute()
                if sel0 != targetObjectBase:  # Wall/ CurtainWall/ Structure
                    sel0.recompute()
                return  # No more action
            #else:  # user clicked Cancel, reply [0] will be ""
            #    pass # Cancel changing name
        u = uuid.uuid4()
        us = str(u)
        psn = 'PropetrySet-' + us
        if sel0 != targetObjectBase:  # sel0 is Wall/ CurtainWall/ Structure...
            reply = QtGui.QInputDialog.getText(None, "Input PropertySet Name",
                                               msg3a, text=us)
        else:  # i.e. sel0 is not Wall, only ArchSketch
            reply = QtGui.QInputDialog.getText(None, "Input PropertySet Name",
                                               msg3b, text=us)
        if reply[1]:  # user clicked OK
            psn = reply[0]
        else:  # user clicked Cancel, reply [0] will be ""
            replyText = reply[0]
            return
        targetObjectBase.Proxy.PropertySetDict[us] = {'name':psn}
        targetObjectBase.recompute()
        if sel0 == targetObjectBase:  # i.e. sel0 is ArchSketch
            return  # No more action
        newWall = newCurtainWall = newStructure = newStairs = None
        if Draft.getType(sel0) in ['Wall']:
            newWall = addArchWall(None, targetObjectBase)
        elif Draft.getType(sel0) in ['CurtainWall']:
            newCurtainWall = addCurtainWall(None, targetObjectBase)
        elif Draft.getType(sel0) in ['Structure']:
            newStructure = addStructure(None, targetObjectBase)
        elif Draft.getType(sel0) in ['Stairs']:
            newStairs = addStairs(None, targetObjectBase)
        if newWall or newCurtainWall or newStructure or newStairs:
            targetObjectBase.ViewObject.HideDependent = False
            if newWall:
                newObj = newWall
            elif newCurtainWall:
                newObj = newCurtainWall
            elif newStructure:
                newObj = newStructure
            elif newStairs:
                newObj = newStairs
            newObj.ArchSketchPropertySet = ['Default', psn]
            newObj.ArchSketchPropertySet = psn
            newObj.Proxy.ArchSkPropSetPickedUuid = us
            Gui.ActiveDocument.setEdit(targetObjectBase)
            App.Console.PrintMessage(msg4 + "\n")
            FreeCADGui.Selection.clearSelection()
            if newWall:
                s=GuiEditWallObserver(newWall,targetObjectBase,propSetUuid=us)
            elif newCurtainWall:
                s=GuiEditCurtainWallObserver([newCurtainWall],targetObjectBase,
                                             propSetUuid=us)
            elif newStructure:
                s=GuiEditStructureObserver(newStructure,targetObjectBase,
                                           propSetUuid=us)
            elif newStairs:
                s=GuiEditStairsObserver(newStairs,targetObjectBase,
                                           propSetUuid=us)
            self.observer = s
            FreeCADGui.Selection.addObserver(s)

FreeCADGui.addCommand('PropertySet', _CommandPropertySet())


class _Command_ArchSketch():

    ''' ArchSketch Command Definition - Gui to make an ArchSketch '''

    def GetResources(self):
        return {'Pixmap' : SketchArchIcon.getIconPath() +
                                          '/icons/SketchArchWorkbench.svg',
                'Accel' : "Alt+S",
                'MenuText': "New ArchSketch",
                'ToolTip' : "create an ArchSketch"}

    def IsActive(self):
        return not FreeCAD.ActiveDocument is None

    def Activated(self):
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
            reply = QtGui.QMessageBox.information(None,"",
                          "Select an object with Shape to 'voxelise' ")
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
        return {'Pixmap' : SketchArchIcon.getIconPath() +
                                          '/icons/CellComplex.svg',
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
            reply = QtGui.QMessageBox.information(None,"",
                    "Select an object with Shape to get CellComplexElement ")
        cc = makeCellComplex(sel)

FreeCADGui.addCommand('CellComplex', _Command_CellComplex())


#----------------------------------------------------------------------------#
#                             Functions                                      #
#----------------------------------------------------------------------------#


def attachToHost(subject,target=None,subelement=None,pl=None):

    # Setup subj:subject
    subj = subject

    # Setup host:target (e.g. Wall) and host.Base.Proxy
    if target:
        host = target
    elif subj.Hosts:  #e.g. BimWindow self.include and host is set
        host = subj.Hosts[-1]  #[0]
    else:
        return

    # Get subject's rotation angle based on subject(window)'s placement
    v0 = FreeCAD.Vector(0,0,0)
    revRotation = FreeCAD.Placement(v0,FreeCAD.Rotation(0,0,-90))
    plR = pl.multiply(revRotation)
    plRAxis = plR.Rotation.Axis
    plRAxisZ = plRAxis.z
    plRAng = plR.Rotation.Angle
    if round((plRAxisZ - 1),6) == 0:  # +1
        pass
    elif round((plRAxisZ + 1),6) == 0:  # -1
        plRAng = -plRAng
    else:
        print(' something wrong')

    # Setup point of attachement
    point = pl.Base
    pv = FreeCAD.Vector(point.x, point.y, point.z)
    import Part
    pointShape = Part.Vertex(pv)

    # Get SketchArch attachment values by getMinDistInfo()
    archSkProxy = host.Base.Proxy
    dict = archSkProxy.getMinDistInfo(host.Base,pointShape)
    e = dict['edge']
    off = dict['offset']
    ht = dict['height']
    eAng = dict['edgeAngle']

    # Set subject(Window)'s attachment values
    subj.MasterSketchSubelement = str(e)
    subj.MasterSketchSubelementOffset = off  #str(off)
    subjAttachPl = subj.AttachmentOffsetXyzAndRotation
    subjAttachPl.Base.z = ht
    subj.AttachmentOffsetXyzAndRotation = subjAttachPl
    subj.Normal = (0, 0, 0)
    # Check & set direction of target(Wall) face (Wall Left/Right) to attach
    test1a = round((eAng - plRAng),6)
    test1b = round((eAng - plRAng - math.pi*2),6)
    if not ((test1a == 0) or (test1b == 0)):  # not same angle
        test2 = round((abs(eAng - plRAng) - math.pi), 6)
        if test2 == 0:  # opposite angle
            subj.AttachmentAlignment = 'WallRight'
        else:
            print(' something wrong')


def attachToMasterSketch(subject, target=None, subelement=None,
                         attachmentOffset=None, zOffset='0',
                         intersectingSubelement=None, mapMode='ObjectXY',
                         getPoint=None):

    if Draft.getType(subject) == "ArchSketch":
        subject.MapReversed = False
        subject.MapMode = mapMode
        if hasattr(subject, "AttachmentSupport"):
            subject.AttachmentSupport = subject.MasterSketch
        else:
            subject.Support = subject.MasterSketch



def detachFromMasterSketch(fp):
    fp.MapMode = 'Deactivated'
    if hasattr(fp, "AttachmentSupport"):
        fp.AttachmentSupport = None
    else:
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
    v0 = App.Vector(0,0,0)
    if fp.AttachToAxisOrSketch == "Host":
        if hasattr(fp, "Hosts") and fp.Hosts:
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
        elif hasattr(fp, "Host") and fp.Host:
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
            else:  #  previous tag has no corresponding index
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
    if attachToSubelementOrOffset in ["Attach to Edge",
                                      "Attach To Edge & Alignment"]:
        if (msSubelementIndex != None) and (hostSketch):
            gSkEdgePtV = getSketchEdgeOffsetPointVector
            offsetV = gSkEdgePtV(fp, hostSketch, msSubelementIndex,
                                 msSubelementSnapPreset,
                                 msSubelementSnapCustom, msSubelementOffset,
                                 attachmentOffsetXyzAndRotation,
                                 flipOffsetOriginToOtherEnd, flip180Degree,
                                 attachToSubelementOrOffset,
                                 msIntSubelementIndex,
                                 offsetFromIntersectingSubelement)
            tempAttachmentOffset.Base= offsetV

            # Calculate the rotation of the edge
            if attachToSubelementOrOffset == "Attach To Edge & Alignment":
                edgeAngle = getSketchEdgeAngle(hostSketch, msSubelementIndex)
                if ((flip180Degree and (attachmentAlignment=="WallLeft")) or
                        (not flip180Degree and
                            (attachmentAlignment=="WallRight")) or
                        (flip180Degree and
                            (attachmentAlignment=="Left")) or
                        (not flip180Degree and
                            (attachmentAlignment == "Right"))
                        ):
                    edgeAngle = edgeAngle + math.pi
                tempAttachmentOffset.Rotation.Angle = edgeAngle
            else:
                ang = attachmentOffsetXyzAndRotation.Rotation.Angle
                tempAttachmentOffset.Rotation.Angle = ang

            # Offset Parallel from Line Alignment
            edgV = getSketchEdgeVec
            masterSketchSubelementEdgeVec = edgV(hostSketch, msSubelementIndex)
            msSubelementWidth = zeroMM
            align = None

            if attachmentAlignment in ["WallLeft", "WallRight"]:
                if hasattr(hostSketch, "Proxy"):
                    if (hasattr(hostSkProxy, "getWidth")
                            and hasattr(hostSkProxy,"EdgeTagDictSync")):
                        msSubelementWidth = hostSkProxy.getWidth(hostSketch,
                                            None, msSubelementIndex)
                        if msSubelementWidth != None:
                            msSubelementWidth = msSubelementWidth * MM
                if msSubelementWidth in [zeroMM, None]:
                    if hostWall:
                        try:
                            w = hostWall.OverrideWidth[msSubelementIndex]
                            msSubelementWidth = w * MM
                        except:
                            msSubelementWidth = hostWall.Width
                    elif hostObject:
                        pass
                    elif hostSketch:
                        pass
                    else:
                        print (" something wrong?  msSubelementWidth=0 :" +
                               " Case, ArchSketch on MasterSketch so no" +
                               " hostWall")

                if hasattr(hostSketch, "Proxy"):
                    if (hasattr(hostSkProxy, "getEdgeTagDictSyncAlign") and
                            hasattr(hostSkProxy,"EdgeTagDictSync")):
                        align = hostSkProxy.getEdgeTagDictSyncAlign(hostSketch,
                                            None, msSubelementIndex)
                        if not align:
                            align = hostSketch.Align
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
                        print (" something wrong ?  align=None : Case, " +
                               "ArchSketch on MasterSketch so no hostWall")

            offsetValue = 0
            if msSubelementWidth != None:
                if msSubelementWidth.Value != 0:
                    offsetValue = msSubelementWidth.Value
            offV = attachmentAlignmentOffset.Value
            if attachmentAlignment == "WallLeft":
                if align == "Left":
                    offsetValue = offV
                elif align == "Right":
                    offsetValue = offsetValue + offV
                elif align == "Center":
                    offsetValue = offsetValue/2 + offV
            elif attachmentAlignment == "WallRight":
                if align == "Left":
                    offsetValue = -offsetValue + offV
                elif align == "Right":
                    offsetValue = offV
                elif align == "Center":
                    offsetValue = -offsetValue/2 + offV
            else:
                offsetValue = offV
            if offsetValue != 0:
                vCross = masterSketchSubelementEdgeVec.cross(Vector(0,0,1))
                vOffsetH = DraftVecUtils.scaleTo(vCross, -offsetValue)
                offBase = tempAttachmentOffset.Base
                tempAttachmentOffset.Base = offBase.add(vOffsetH)

    elif attachToSubelementOrOffset == "Follow Only Offset XYZ & Rotation":
        tempAttachmentOffset = attachmentOffsetXyzAndRotation

    # Extra Rotation as user input

    extraRotation = FreeCAD.Placement(v0,App.Rotation(0,0,0))
    if fp.AttachmentOffsetExtraRotation == "X-Axis CCW90":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(0,0,90))
    elif fp.AttachmentOffsetExtraRotation == "X-Axis CW90":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(0,0,-90))
    elif fp.AttachmentOffsetExtraRotation == "X-Axis CW180":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(0,0,180))
    elif fp.AttachmentOffsetExtraRotation == "Y-Axis CW90":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(0,90,0))
    elif fp.AttachmentOffsetExtraRotation == "Y-Axis CCW90":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(0,-90,0))
    elif fp.AttachmentOffsetExtraRotation == "Y-Axis CW180":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(0,180,0))
    elif fp.AttachmentOffsetExtraRotation == "Z-Axis CCW90":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(90,0,0))
    elif fp.AttachmentOffsetExtraRotation == "Z-Axis CW90":
        extraRotation = FreeCAD.Placement(v0,App.Rotation(-90,0,0))
    elif fp.AttachmentOffsetExtraRotation == "Z-Axis CW180":
        extraRotation=FreeCAD.Placement(v0,App.Rotation(180,0,0))
    tempAttachmentOffset = tempAttachmentOffset.multiply(extraRotation)

    # Alternative OriginOffset manually input by user
    originOffset = fp.OriginOffsetXyzAndRotation
    invOriginOffset = originOffset.inverse()
    tempAttachmentOffset = tempAttachmentOffset.multiply(invOriginOffset)

    # ArchObjects, link of ArchSketch, link of ArchObjects
    # i.e. Not ArchSketch
    if linkFp or not hasattr(fp, "AttachmentOffset"):
        hostSketchPl = FreeCAD.Placement()
        if hostSketch:
            hostSketchPl = hostSketch.Placement
        if Draft.getType(fp.getLinkedObject()) == 'Window':
            winSketchPl = fp.Base.Placement
            # Reset Window's placement to factor out base sketch's placement
            invWinSketchPl = winSketchPl.inverse()
            # make the placement 'upright' again
            winSkRotation = FreeCAD.Placement(App.Vector(0,0,0),
                                              App.Rotation(0,0,90))
            tempAttachmentOffset = tempAttachmentOffset.multiply(winSkRotation
                                                        ).multiply(
                                                        invWinSketchPl)
        if hostWall:
            hostWallPl = hostWall.Placement
            hostWallRotation = FreeCAD.Placement(App.Vector(0,0,0),
                                                 hostWallPl.Rotation,
                                                 v0)
            tempBaseOffset = hostWallRotation.multiply(hostSketchPl)
            tempBaseOffset.Base= tempBaseOffset.Base.add(hostWallPl.Base)
            tempAttachmentOffset= tempBaseOffset.multiply(tempAttachmentOffset)
        elif hostObject:
            hostObjectPl = hostObject.Placement
            hostObjectRotation = FreeCAD.Placement(App.Vector(0,0,0),
                                                   hostObjectPl.Rotation,
                                                   v0)
            tempBaseOffset = hostObjectRotation.multiply(hostSketchPl)
            tempBaseOffset.Base = tempBaseOffset.Base.add(hostObjectPl.Base)
            tempAttachmentOffset= tempBaseOffset.multiply(tempAttachmentOffset)
        else:  # Attach to Master Sketch (only)
            tempAttachmentOffset= hostSketchPl.multiply(tempAttachmentOffset)
    if linkFp or not hasattr(fp, "AttachmentOffset"):
        fp.Placement = tempAttachmentOffset
    else:
        fp.AttachmentOffset = tempAttachmentOffset



'''------------------- Creation/Insertion Functions ---------------------'''


def makeArchSketch(grp=None,label="ArchSketch__NAME",attachToAxisOrSketch=None,
                   placementAxis_Or_masterSketch=None,copyFlag=None,
                   visibility=None, ArchSketchLock='Check'):
    # Check if ArchSketchLock is checked before proceed further
    if ArchSketchLock=='Check':
        if hasattr(FreeCAD, 'ArchSketchLock'):
            if not FreeCAD.ArchSketchLock:  # If False
                raise Exception  # BimWall on exception would create Sketch
    name = "ArchSketch"
    if grp:
        archSketch = grp.newObject("Sketcher::SketchObjectPython",name)
    else:
        archSketch=App.ActiveDocument.addObject("Sketcher::SketchObjectPython",
                                                name)
    archSketch.Label = label
    archSketchInsta=ArchSketch(archSketch)
    archSketch.AttachToAxisOrSketch = "Master Sketch"
    return archSketch


def addArchWall(grp=None, baseobj=None, length=None, width=None, height=None,
                align="Center", face=None):
    label = "Wall__" + baseobj.Label
    archWall = Arch.makeWall(baseobj, length, width, height, align, face)
    archWall.ViewObject.Transparency = 0
    archWall.ViewObject.LineWidth = 1
    archWall.ViewObject.Visibility = True
    archWall.Label = label
    if grp:
        grp.addObject(archWall)
    return archWall


def addCurtainWall(grp=None, baseobj=None):
    label = "CurtainWall__" + baseobj.Label
    curtainWall = Arch.makeCurtainWall(baseobj)
    curtainWall.ViewObject.Transparency = 0
    curtainWall.ViewObject.LineWidth = 1
    curtainWall.ViewObject.Visibility = True
    curtainWall.Label = label
    if grp:
        grp.addObject(curtainWall)
    return curtainWall


def addStructure(grp=None, baseobj=None):
    label = "Structure__" + baseobj.Label
    structure = Arch.makeStructure(baseobj)
    structure.ViewObject.Transparency = 0
    structure.ViewObject.LineWidth = 1
    structure.ViewObject.Visibility = True
    structure.Label = label
    if grp:
        grp.addObject(structure)
    return structure


def addStairs(grp=None, baseobj=None):
    from draftutils import params
    label = "Stairs__" + baseobj.Label
    stepsNum = params.get_param_arch("StairsSteps")
    stairs = Arch.makeStairs(baseobj,steps=stepsNum)
    stairs.ViewObject.Transparency = 0
    stairs.ViewObject.LineWidth = 1
    stairs.ViewObject.Visibility = True
    stairs.Label = label
    if grp:
        grp.addObject(stairs)
    return stairs


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


def getSketchEdgeOffsetPointVector(subject, masterSketch, subelementIndex,
                                   snapPreset=None, snapCustom=None,
                                   attachmentOffset=None, zOffset=None,
                                   flipOffsetOriginToOtherEnd=False,
                                   flip180Degree=False,
                                   attachToSubelementOrOffset=None,
                                   intersectingSubelementIndex=None,
                                   offsetFromIntersectingSubelement=False):
    ms = masterSketch
    geom = ms.Geometry
    geoindex = None
    geoindex2 = None
    #geoindex = int(subelement.lstrip('Edge'))-1
    geoindex = subelementIndex
    geoindex2 = intersectingSubelementIndex

    #if True:
    intPoint = None
    if offsetFromIntersectingSubelement and (geoindex2 is not None):
        intPoint = getSketchEdgeIntersection(ms,geoindex,geoindex2)
    if snapPreset != 'CustomValue':
        snapValue = ArchSketch.SnapPresetDict[snapPreset]  # Class.Dict
    else:  # elif snapPreset == 'CustomValue':
        snapValue = snapCustom
    edgeLength = geom[geoindex].length()
    if snapValue == 0:  # 'AxisStart'
        snapPresetCustomLength = 0  # no unit ?
    else:  #elif snapValue != 0:
        if geoindex2 is None:
            snapPresetCustomLength = edgeLength * snapValue
        else:  #elif geoindex2 is not None:  # needs to break the edge
            if not flipOffsetOriginToOtherEnd:
                if not offsetFromIntersectingSubelement: # use 1st portion
                    edgePortionVec = intPoint.sub(geom[geoindex].StartPoint)
                else:  # use 2nd portion
                    edgePortionVec = intPoint.sub(geom[geoindex].EndPoint)
            else:  #elif flipOffsetOriginToOtherEnd:
                if not offsetFromIntersectingSubelement: # use 2nd portion
                    edgePortionVec = intPoint.sub(geom[geoindex].EndPoint)
                else:  # use 1st portion
                    edgePortionVec = intPoint.sub(geom[geoindex].StartPoint)
            snapPresetCustomLength = edgePortionVec.Length * snapValue
    totalAttachmentOffset = snapPresetCustomLength + attachmentOffset.Value
    if not flipOffsetOriginToOtherEnd:
        edgeOffsetPoint = geom[geoindex].value(totalAttachmentOffset)
    else:  #elif flipOffsetOriginToOtherEnd:
        edgeOffsetPoint= geom[geoindex].value(edgeLength-totalAttachmentOffset)
    if intPoint:
        if not flipOffsetOriginToOtherEnd:
            intOffsetVec = intPoint.sub(geom[geoindex].StartPoint)
        else:  #elif flipOffsetOriginToOtherEnd:
            intOffsetVec = intPoint.sub(geom[geoindex].EndPoint)
        edgeOffsetPoint = edgeOffsetPoint.add(intOffsetVec)

    edgeOffsetPoint.z = zOffset.Base.z
    return edgeOffsetPoint


# For All Sketch, Not Only ArchSketch

def getSketchSortedClEdgesOrder(sketch, archSketchEdges=None,
                                propSetUuid=None):

      ''' Call getSortedClEdgesOrder() -
          To do Part.getSortedClusters() on geometry of a Sketch (omit
          construction geometry if no 'wallAxis' role), check the order of
          edges to return lists of indexes in the order of sorted edges.

          Supported role='wallAxis'

          return:
            clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex, and
            clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat
      '''

      skGeom = sketch.Geometry
      skGeomEdgesSet = []
      for c, i in enumerate(skGeom):
          if isinstance(i, ArchSketch.GeomSupported):
              wallAxisStatus = None
              if archSketchEdges is not None:
                  wallAxisStatus = str(c) in archSketchEdges
              elif hasattr(sketch, 'Proxy') and hasattr(sketch.Proxy,
                                            'getEdgeTagDictSyncWallStatus'):
                  skProxy = sketch.Proxy
                  wallAxisStatus = skProxy.getEdgeTagDictSyncWallStatus(sketch,
                                           tag=i.Tag, role='wallAxis',
                                           propSetUuid=propSetUuid)
              else:
                  if hasattr(i, 'Construction'):
                      construction = i.Construction
                  elif hasattr(sketch, 'getConstruction'):
                      construction = sketch.getConstruction(c)
                  if not construction:
                      wallAxisStatus = True
              if wallAxisStatus:
                  skGeomEdgesSet.append(sketch.ShapeList[c])
      return getSortedClEdgesOrder(skGeomEdgesSet, sketch.ShapeList)


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
    # a list of lists (not array/matrix) withindex of found matching geometry
    clEdgePartnerIndex = []
    clEdgeSameIndex = []
    clEdgeEqualIndex = []

    # a flat list with above information (but just flat, not a list of lists)
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
    return (clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex,
            clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat)


def sortSketchAlign(sketch,edgeAlignList,archSketchEdges=None):

    '''
        This function is primarily to support Ordinary Sketch + Arch Wall
        to gain feature that individual edge / wall segment to have
        individual Align setting with OverrideAlign attribute in Arch Wall

        This function arrange the edgeAlignList
        - a list of Align in the order of Edge Indexes -
        into a list of Align following the order of edges
        sorted by Part.getSortedClusters()
    '''

    sortedIndexes = getSketchSortedClEdgesOrder(sketch, archSketchEdges)
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


def sortSketchWidth(sketch,edgeWidthList,archSketchEdges=None):

    '''
        This function is primarily to support Ordinary Sketch + Arch Wall
        to gain feature that individual edge / wall segment to have
        individual Width setting with OverrideWidth attribute in Arch Wall

        This function arrange the edgeWidthList
        - a list of Width in the order of Edge Indexes -
        into a list of Width following the order of edges
        sorted by Part.getSortedClusters()
    '''

    sortedIndexes = getSketchSortedClEdgesOrder(sketch, archSketchEdges)
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
            curWidth = 0  # default to be ArchWall's Offset
        widthList.append(curWidth)
    return widthList


def sortSketchOffset(sketch,edgeOffsetList,archSketchEdges=None):

    '''
        This function is primarily to support Ordinary Sketch + Arch Wall
        to gain Offset setting with OverrideOffset attribute in Arch Wall

        This function arrange the edgeOffsetList
        - a list of Offset in the order of Edge Indexes -
        into a list of Width following the order of edges
        sorted by Part.getSortedClusters()
    '''

    sortedIndexes = getSketchSortedClEdgesOrder(sketch, archSketchEdges)
    offsetList = sortOffset(edgeOffsetList, sortedIndexes)
    return offsetList


def sortOffset(edgeOffsetList, sortedIndexes):
    clEdgeSameIndexFlat = sortedIndexes[4]
    offsetList = []
    for i in clEdgeSameIndexFlat:
        try:
            curOffset = edgeOffsetList[i]
        # if edgeOffsetList does not cover the edge
        except:
            curOffset = 0  # default
        offsetList.append(curOffset)
    return offsetList


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


def boundBoxShape(obj, enlarge=0):

    objPl = obj.Placement
    invPl = objPl.inverse()
    sh=Part.Shape(obj.Shape)
    sh.Placement=sh.Placement.multiply(invPl)
    if not sh.isNull():
        bb=sh.BoundBox  #bb=obj.Shape.BoundBox
        l = bb.XLength+2*enlarge
        w = bb.YLength+2*enlarge
        baseX = bb.XMin-enlarge
        baseY = bb.YMin-enlarge
        baseZ = bb.ZMin
    else:
        l = 2*enlarge
        w = 2*enlarge
        baseX = -enlarge
        baseY = -enlarge
        baseZ = 0
    p=FreeCAD.Placement()
    p.Base=FreeCAD.Vector(baseX, baseY, baseZ)
    rect = Part.makePlane(l, w, p.Base, FreeCAD.Vector(0,0,1) )
    return rect


def getSketchEdges(sk):

    ''' return lists in lists '''

    skGeom = sk.GeometryFacadeList
    skGeomEdges = []
    skGeomEdgesFull = []

    for i in skGeom:
        if isinstance(i.Geometry, ArchSketch.GeomSupported):
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
#from ArchSketchObjectExt import ArchSketch  # Doesn't work
