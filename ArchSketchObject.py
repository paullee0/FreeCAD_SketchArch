#***************************************************************************	
#*                                                                         *	
#*   Copyright (c) 2018, 2019                                              *	
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
										
  ''' ArchSketch - Sketcher::SketchObjectPython for Architectual Layout '''	
										
  def __init__(self, obj):							
      ArchSketchObject.__init__(self, obj)					
										
      ''' call self.setProperties '''						
										
      self.setProperties(obj)							
      self.initEditorMode(obj)							
      obj.ViewObject.Proxy=0							
      return None								
										
										
  def initEditorMode(self, obj):						
										
      ''' Set DispayMode for Data Properties in Combo View Editor '''		
										
      obj.setEditorMode("MapMode",1)						
      obj.setEditorMode("MapReversed",1)					
										
										
  def setProperties(self, fp):							
										
      ''' Add self.Properties _&_ Convert Old Properties: See__Init '''		
										
      if not hasattr(self,"Proxy"):						
          fp.Proxy = self							
      if not hasattr(self,"Type"):						
          self.Type = "ArchSketch"						
      if not hasattr(self,"widths"):						
          self.widths = {}							
										
      if not hasattr(self,"clEdgeSameIndexFlat"):				
          self.clEdgeSameIndexFlat = []						
										
      ''' Added ArchSketch Properties '''					
										
										
  def execute(self, fp):							
										
      ''' Features to Run in Addition to Sketcher.execute() '''			
										
      ''' (IX or XI) - Update the order of edges by getSortedClusters '''	
										
      self.updateSortedClustersEdgesOrder(fp)					
										
      fp.solve()								
      fp.recompute()								
										
										
  def updateSortedClustersEdgesOrder(self, fp):					
										
      clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex, clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat = getSortedClustersEdgesOrder(fp)				
										
      self.clEdgePartnerIndex = clEdgePartnerIndex				
      self.clEdgeSameIndex = clEdgeSameIndex					
      self.clEdgeEqualIndex = clEdgeEqualIndex					
										
      self.clEdgePartnerIndexFlat = clEdgePartnerIndexFlat			
      self.clEdgeSameIndexFlat = clEdgeSameIndexFlat				
      self.clEdgeEqualIndexFlat = clEdgeEqualIndexFlat				
										
										
  def getWidths(self, fp):							
										
      ''' wrapper function for uniform format '''				
										
      return self.getSortedClustersEdgesWidth(fp)				
										
										
  def getSortedClustersEdgesWidth(self, fp):					
										
      '''  This method check the SortedClusters-isSame-(flat)List		
           find the corresponding edgesWidth					
           and make a list of (WidthX, WidthX+1 ...) '''			
										
      '''  Options of data to store width (& other) information conceived	
										
           1st Option - Use self.widths: a Dict of { EdgeX : WidthX, ...}	
                        But when Sketch is edit with some edges deleted, the	
                        edges indexes change, the widths stored become wrong	
										
           2nd Option - Use abdullah's edge geometry				
                        .... bugs found, not working				
										
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
										
										
#---------------------------------------------------------------------------#	
#             FreeCAD Commands Classes & Associated Functions               #	
#---------------------------------------------------------------------------#	
										
class _CommandEditWallAlign():							
										
    '''Edit Wall Segment (Underlying [Arch]Sketch) Align Command Definition'''	
										
    def GetResources(self):							
        return {'Pixmap'  : SketchArchIcon.getIconPath() + '/icons/EdgeGroup_Highlight.svg',		
                'Accel'   : "E, A",						
                'MenuText': "Edit Wall Segment Align",				
                'ToolTip' : "select Wall to Flip Wall Segment Align ",		
                'CmdType' : "ForEdit"}						
										
    def IsActive(self):								
        return not FreeCAD.ActiveDocument is None				
										
    def Activated(self):							
        try:									
            sel0 = Gui.Selection.getSelection()[0]				
        except:									
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch )")	
            return								
        targetObjectBase = None							
										
        if Draft.getType(sel0) != "Wall":					
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch )")	
            return								
        if sel0.Base:								
            targetObjectBase = sel0.Base					
        else:									
            reply = QtGui.QMessageBox.information(None,"","Arch Wall without Base is not supported - Select an Arch Wall ( with underlying Base ArchSketch or Sketch )")	
            return								
        if Draft.getType(targetObjectBase) in ['ArchSketch', 'Sketch']:		
            if Draft.getType(targetObjectBase) is 'Sketch':			
                reply = QtGui.QMessageBox.information(None,"","Multi-Align support Sketch with Part Geometry Extension (abdullah's development) / ArchSketch primarily.  Support on Sketch could only be done 'partially' (indexes of edges is disturbed if sketch is edited) until bug in Part Geometry Extension is fixed - currently for demonstration purpose, procced now. ")	
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
        #    FreeCADGui.Selection.clearSelection()				
        #    App.Console.PrintMessage("Not Implemented yet "+ "\n")		
										
										
FreeCADGui.addCommand('EditWallAlign', _CommandEditWallAlign())			
										
										
class GuiEditWallAlignObserver(SketchArchCommands.selectObjectObserver):	
										
    def __init__(self, targetWall, targetWallBaseArchSketch):			
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,'Edge')					
        self.targetWall = targetWall						
        self.targetArchSketch = targetWallBaseArchSketch			
        self.targetWallTransparentcy = targetWall.ViewObject.Transparency	
        targetWall.ViewObject.Transparency = 60					
        if targetWallBaseArchSketch:						
            if Draft.getType(targetWallBaseArchSketch) == 'Sketch':		
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
            if Draft.getType(self.targetArchSketch) == 'Sketch':		
                print (" It is a Sketch")					
                tempOverrideAlign = self.targetWall.OverrideAlign		
                curAlign = self.targetWall.OverrideAlign[subIndex]		
                if curAlign == 'Left':						
                    curAlign = 'Right'						
                elif curAlign == 'Right':					
                    curAlign = 'Center'						
                elif curAlign == 'Center':					
                    curAlign = 'Left'						
                else:	# 'Center' or else?					
                    curAlign = 'Right'						
                tempOverrideAlign[subIndex] = curAlign				
                self.targetWall.OverrideAlign = tempOverrideAlign		
            self.targetArchSketch.recompute()					
        else:  									
            # nothing implemented if self.targetArchSketch is None		
            pass								
        self.targetWall.recompute()						
										
    def escape(self,info):							
        k=info['Key']								
        if k=="ESCAPE":								
            self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy	
        SketchArchCommands.selectObjectObserver.escape(self,info)		
										
										
class _CommandEditWallWidth():							
										
    '''Edit Wall Segment (Underlying [Arch]Sketch) Width Command Definition'''	
										
    def GetResources(self):							
        return {'Pixmap'  : SketchArchIcon.getIconPath() + '/icons/EdgeGroup_Highlight.svg',	
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
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch )")	
            return								
        targetObjectBase = None							
        if Draft.getType(sel0) != "Wall":					
            reply = QtGui.QMessageBox.information(None,"","Select an Arch Wall ( with underlying Base ArchSketch or Sketch )")	
            return								
        if sel0.Base:								
            targetObjectBase = sel0.Base					
        else:									
            reply = QtGui.QMessageBox.information(None,"","Arch Wall without Base is not supported - Select an Arch Wall ( with underlying Base ArchSketch or Sketch )")	
            return								
        if Draft.getType(targetObjectBase) in ['ArchSketch', 'Sketch']:	
            if Draft.getType(targetObjectBase) is 'Sketch':			
                reply = QtGui.QMessageBox.information(None,"","Multi-Width support Sketch with Part Geometry Extension (abdullah's development) / ArchSketch primarily.  Support on Sketch could only be done 'partially' (indexes of edges is disturbed if sketch is edited) until bug in Part Geometry Extension is fixed - currently for demonstration purpose, procced now. ")	
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
										
    def __init__(self, targetWall, targetWallBaseArchSketch):			
        SketchArchCommands.selectObjectObserver.__init__(self,None,None,None,'Edge')					
        self.targetWall = targetWall						
        self.targetArchSketch = targetWallBaseArchSketch			
        self.targetWallTransparentcy = targetWall.ViewObject.Transparency	
        targetWall.ViewObject.Transparency = 60					
        if targetWallBaseArchSketch:						
            if Draft.getType(targetWallBaseArchSketch) == 'Sketch':		
                tempOverrideWidth = self.targetWall.OverrideWidth		
                wallWidth = targetWall.Width.Value # use Wall's Width			
                # filling OverrideWidth if entry is missing for a particular index	
                while len(tempOverrideWidth) < len(self.targetArchSketch.Geometry):	
                    tempOverrideWidth.append(wallWidth) #(0)			
                self.targetWall.OverrideWidth = tempOverrideWidth		
										
    def proceed(self, doc, obj, sub, pnt):					
        self.edge = sub								
        self.pickedEdgePlacement = App.Vector(pnt)				
        subIndex = int( sub.lstrip('Edge'))-1					
        App.Console.PrintMessage("Input Width"+ "\n")				
        reply = QtGui.QInputDialog.getText(None, "Input Width","Width of Wall Segment")	
        if reply[1]:  # user clicked OK						
            replyWidth = float(reply[0])					
        else:  # user clicked not OK, i.e. Cancel ?				
            return None								
        if self.targetArchSketch is not None:					
            if Draft.getType(self.targetArchSketch) == 'Sketch':		
                tempOverrideWidth = self.targetWall.OverrideWidth		
                tempOverrideWidth[subIndex] = replyWidth			
                self.targetWall.OverrideWidth = tempOverrideWidth		
            self.targetArchSketch.recompute()					
            self.targetWall.recompute()						
        else:  									
            # nothing implemented if self.targetArchSketch is None		
            pass								
										
    def escape(self,info):							
        k=info['Key']								
        if k=="ESCAPE":								
            self.targetWall.ViewObject.Transparency = self.targetWallTransparentcy	
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
        reply = QtGui.QMessageBox.information(None,"","ArchSketch functionalities being added - none at the moment :) ")	
        makeArchSketch()							
										
FreeCADGui.addCommand('ArchSketch', _Command_ArchSketch())			
										
										
#----------------------------------------------------------------------------#	
#                             Functions                                      #	
#----------------------------------------------------------------------------#	
										
										
def makeArchSketch(grp=None, label="ArchSketch__NAME", attachToAxisOrSketch=None, placementAxis_Or_masterSketch=None, copyFlag=None, visibility=None):		
  name = "ArchSketch"								
  if grp:									
      archSketch = grp.newObject("Sketcher::SketchObjectPython",name)		
  else:										
      archSketch=App.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)	
  archSketch.Label = label							
  archSketchInsta=ArchSketch(archSketch)					
  return archSketch								
										
										
def getSortedClustersEdgesOrder(sketch):					
										
      ''' Do Part.getSortedClusters() on geometry of a Sketch,			
          check the order of edges to return lists of indexes in		
          in the order of sorted edges		 			 	
										
          return:								
          - clEdgePartnerIndex, clEdgeSameIndex, clEdgeEqualIndex, and		
          - clEdgePartnerIndexFlat, clEdgeSameIndexFlat, clEdgeEqualIndexFlat	
      '''									
										
      skGeom = sketch.Geometry							
      skGeomEdges = []								
      skGeomEdgesShort = []							
      for i in skGeom:								
          skGeomEdge = i.toShape()						
          skGeomEdges.append(skGeomEdge)					
          if not i.Construction:						
              skGeomEdgesShort.append(skGeomEdge)				
      skGeomEdgesSorted = Part.getSortedClusters(skGeomEdgesShort)		
										
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
              for j, skGeomEdgesI in enumerate(skGeomEdges):			
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
										
    sortedIndexes = getSortedClustersEdgesOrder(sketch)				
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
										
    sortedIndexes = getSortedClustersEdgesOrder(sketch)				
    clEdgeSameIndexFlat = sortedIndexes[4]					
    widthList = []								
    for i in clEdgeSameIndexFlat:						
        try:									
            curWidth = edgeWidthList[i]						
        # if edgeWidthList does not cover the edge				
        except:									
            curWidth = '200'  # default						
        widthList.append(curWidth)						
    return widthList								
										
										
