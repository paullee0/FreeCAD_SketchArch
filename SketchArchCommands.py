#***************************************************************************	#&&&
#*                                                                         *	#&&&
#*   Copyright (c) 2018, 2019                                              *	#&&&
#*   Paul Lee <paullee0@gmail.com>                                         *	#&&&
#*                                                                         *	#&&&
#*   This program is free software; you can redistribute it and/or modify  *	#&&&
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *	#&&&
#*   as published by the Free Software Foundation; either version 2 of     *	#&&&
#*   the License, or (at your option) any later version.                   *	#&&&
#*   for detail see the LICENCE text file.                                 *	#&&&
#*                                                                         *	#&&&
#*   This program is distributed in the hope that it will be useful,       *	#&&&
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *	#&&&
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *	#&&&
#*   GNU Library General Public License for more details.                  *	#&&&
#*                                                                         *	#&&&
#*   You should have received a copy of the GNU Library General Public     *	#&&&
#*   License along with this program; if not, write to the Free Software   *	#&&&
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *	#&&&
#*   USA                                                                   *	#&&&
#*                                                                         *	#&&&
#***************************************************************************	#&&&
										#&&&
import FreeCAD, FreeCADGui, Part, Draft, Sketcher				#&&&
import math
from PySide import QtGui, QtCore						#&&&
#from pivy import coin
										#&&&
#import SketchArch_Functions
#import ArchSketchObject							# Circular Dependency, so e.g. SketchArchCommands.selectObjetObserver() can't be loaded from ArchSketchObject ...
										#&&&
App = FreeCAD									#&&&
Gui = FreeCADGui								#&&&
										#&&&
#----------------------------------------------------------------------------#
#                             Testing                                        # 
#----------------------------------------------------------------------------#


# https://www.freecadweb.org/wiki/Embedding_FreeCADGui

# from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(508, 436)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.mdiArea = QtGui.QMdiArea(self.centralwidget)
        self.mdiArea.setViewMode(QtGui.QMdiArea.TabbedView)
        self.mdiArea.setTabPosition(QtGui.QTabWidget.South)
        self.mdiArea.setObjectName("mdiArea")
        self.gridLayout.addWidget(self.mdiArea, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 508, 27))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))

#ui=Ui_MainWindow()
#my_mw=QtGui.QMainWindow()
#ui.setupUi(my_mw)
#ui.mdiArea.addSubWindow(v)
#my_mw.show()


#----------------------------------------------------------------------------#	#&&&
#                             Class Definition                               #	#&&&
#----------------------------------------------------------------------------#	#&&&
										#&&&
''' ___ This works afterall? ___ Alternative? ___ As a SuperClass? '''

class selectObjectObserver:							#&&&
										#&&&
    ''' General Purpose Selection Observer '''					#&&&
										#&&&
    def __init__(self, callerNextDef, filterDoc=None,				#&&&
                 filterObj=None, filterSub=None):				#&&&
        #self.callerNextDef=str(callerNextDef)
        self.filterDoc=str(filterDoc)						#&&&
        #print ("filterDoc, self.filterDoc")
        #print (filterDoc)
        self.filterObj=str(filterObj)						#&&&
        self.filterSub=str(filterSub)						#&&&
        self.av = FreeCADGui.activeDocument().activeView()			#&&&
        self.escape = self.av.addEventCallback("SoKeyboardEvent",self.escape)	#&&&
        FreeCAD.Console.PrintMessage('\n'+'\n')					#&&&
        FreeCAD.Console.PrintWarning('PRESS [ESC] to Exit \n')			#&&&
										#&&&
    def addSelection(self,doc,obj,sub,pnt):					#&&&
        App.Console.PrintMessage(" OK - Here is addObserver's Instance's addSelection Method"+ "\n")
        App.Console.PrintMessage("addSelection"+ "\n")
        App.Console.PrintMessage(str(doc)+ "\n")				# Name of the document
        App.Console.PrintMessage(str(obj)+ "\n")				# Name of the object
        App.Console.PrintMessage(str(sub)+ "\n")				# The part of the object name
        App.Console.PrintMessage(str(pnt)+ "\n")				# Coordinates of the object
        App.Console.PrintMessage("______"+ "\n")
        #winToSketch.changed = True						# NO___add attribute to see if it trigger onChanged()- No! This is FC's mechanism on Obj...
        #print (" self.filterSub - ")
        #print (self.filterSub)
        if self.filterSub:							#&&&	# if self.filterObj:
            if self.filterSub in sub:						#&&&	# if obj in self.filterObj:
                self.proceed(doc, obj, sub, pnt)				#&&&	# OK!
        #Gui.ActiveDocument.resetEdit()					# ___CRASH FC !!!???
										#&&&
    def removeSelection(self,doc,obj,sub):					#&&&	# Delete the selected object
        App.Console.PrintMessage("removeSelection"+ "\n")			#&&&
    def setSelection(self,doc):						#&&&	# Selection in ComboView
        App.Console.PrintMessage("setSelection"+ "\n")				#&&&
    def clearSelection(self,doc):						#&&&	# If click on the screen, clear the selection
        App.Console.PrintMessage("clearSelection"+ "\n")			#&&&	# If click on another object, clear the previous object
    def escape(self,info):							#&&&
        #down = (info["State"] == "DOWN")						## TODO any use this 'down' ?
        k=info['Key']								#&&&
        if k=="ESCAPE":							#&&&
            FreeCAD.Console.PrintMessage("Escaped \n")				#&&&
            self.av.removeEventCallback("SoKeyboardEvent",self.escape)		#&&&
            FreeCADGui.Selection.removeObserver(self)				#&&&
										#&&&
class selectObject:								#&&&
    ''' General Purpose Selection Observer '''					#&&&
										#&&&
    def __init__(self, callerInstance, callerNextDef, filterDoc=None,		#&&&
                 filterObj=None, filterSub=None):				#&&&
        self.callerInstance=callerInstance					#&&&
        self.callerNextDef=str(callerNextDef)					#&&&
        self.filterDoc=str(filterDoc)						#&&&
        self.filterObj=str(filterObj)						#&&&
        self.filterSub=str(filterSub)						#&&&
        App.Console.PrintMessage(self.callerInstance)
        App.Console.PrintMessage("\n")
        self.av = FreeCADGui.activeDocument().activeView()			#&&&
        self.escape = self.av.addEventCallback("SoKeyboardEvent",self.escape)	#&&&
        FreeCAD.Console.PrintMessage('\n'+'\n')				#&&&
        FreeCAD.Console.PrintWarning('PRESS [ESC] to Exit \n')			#&&&
										#&&&
    def addSelection(self,doc,obj,sub,pnt):					#&&&
        App.Console.PrintMessage(" OK - Here is addObserver's Instance's addSelection Method"+ "\n")
        App.Console.PrintMessage("addSelection"+ "\n")
        App.Console.PrintMessage(str(doc)+ "\n")				# Name of the document
        App.Console.PrintMessage(str(obj)+ "\n")				# Name of the object
        App.Console.PrintMessage(str(sub)+ "\n")				# The part of the object name
        App.Console.PrintMessage(str(pnt)+ "\n")				# Coordinates of the object
        App.Console.PrintMessage("______"+ "\n")
        #winToSketch.changed = True						# NO___add attribute to see if it trigger onChanged()- No! This is FC's mechanism on Obj...
        #self.callerInstance.proceed()						# OK! Can save who is calling and 'callBack' 
        #print (" self.filterSub - ")
        #print (self.filterSub)
        if self.filterSub:							#&&&	# if self.filterObj:
            if self.filterSub in sub:						#&&&	# if obj in self.filterObj:
                self.callerInstance.proceed(doc, obj, sub, pnt)		#&&&	# OK!
        #Gui.ActiveDocument.resetEdit()							# ___CRASH FC !!!???
										#&&&
    def removeSelection(self,doc,obj,sub):					#&&&	# Delete the selected object
        App.Console.PrintMessage("removeSelection"+ "\n")			#&&&
    def setSelection(self,doc):						#&&&	# Selection in ComboView
        App.Console.PrintMessage("setSelection"+ "\n")				#&&&
    def clearSelection(self,doc):						#&&&	# If click on the screen, clear the selection
        App.Console.PrintMessage("clearSelection"+ "\n")			#&&&	# If click on another object, clear the previous object
    def escape(self,info):							#&&&
        down = (info["State"] == "DOWN")					#&&&
        k=info['Key']								#&&&
        if k=="ESCAPE":							#&&&
            FreeCAD.Console.PrintMessage("Escaped \n")				#&&&
            self.av.removeEventCallback("SoKeyboardEvent",self.escape)		#&&&
            FreeCADGui.Selection.removeObserver(self)				#&&&
										#&&&
class testSubSelectObject(selectObject):
    def __init__(self, callerInstance, callerNextDef, filterDoc=None,
                 filterObj=None, filterSub=None):
        pass

    ## TODO


class gui_SelectObjects_and_CloneAttach:

    def getWindowOrExtrusion(self, sourceObject):
          typeSourceObject = Draft.getType(sourceObject)
          if typeSourceObject == "Window":					# Clone also return "Window"
            reply = QtGui.QMessageBox.information(None,"","A Window or Door is selected as Subject!")
            reply = QtGui.QMessageBox.information(None,"","Now select Target Wall(Block) to attach!")
            return sourceObject, None
          if typeSourceObject == "Part" and sourceObject.isDerivedFrom("Part::Extrusion"):
                reply = QtGui.QMessageBox.information(None,"","A Extrusion Solid is selected as Subject!")
                reply = QtGui.QMessageBox.information(None,"","Now select Target Wall(block) to attach!")
                return None, sourceObject
          else:
              reply = QtGui.QMessageBox.information(None,"","Select a Window/Door or Extrusion Solid as Subject!")
              return None, None

    def __init__(self, sourceObject): #, targetObject):				# Seem can't 'pre-select' targetObject.... see below  (seem targetWin ok)
        App.Console.PrintMessage(" OK - Here is Instance' __init__ Method"+ "\n")
        self.sourceWin, self.sourceExtrusion = self.getWindowOrExtrusion(sourceObject)
        self.targetObject = None
        self.targetSketch = None
        self.edge = None
        self.intersectingEdge = None
        self.pickedEdgePlacement = App.Vector()					# FreeCAD.Placement()
        #s=selectObject(self, nextDef) #s=selectObject(self) #s=selectObject()	# works! 'self' is passed to class instance selectObject for it to 'call back' / 'return'
        #FreeCADGui.Selection.addObserver(s)
        #self.observer = s
        #self.sourceWin = None
        #self.targetObject = None
        self.getSourceTargetEdge()

    def getSourceTargetEdge(self):
        App.Console.PrintMessage(" OK - Here is Instance' getSourceTargetEdge() Method"+ "\n")

        class observerSelectSourceTargetEdge:
            def __init__(self, callerInstance):
                self.callerInstance=callerInstance
            def addSelection(self,doc,obj,sub,pnt):
                App.Console.PrintMessage(" OK - Here is addObserver's Instance's addSelection Method"+ "\n")
                App.Console.PrintMessage("addSelection"+ "\n")
                App.Console.PrintMessage(str(doc)+ "\n")			# Name of the document
                App.Console.PrintMessage(str(obj)+ "\n")			# Name of the object
                App.Console.PrintMessage(str(sub)+ "\n")			# The part of the object name
                App.Console.PrintMessage(str(pnt)+ "\n")			# Coordinates of the object
                App.Console.PrintMessage("______"+ "\n")
                if not self.callerInstance.sourceWin and not self.callerInstance.sourceExtrusion: # as call another addobserver in another def not working, do all in this def and to proceed()..by if
                    testObject = App.ActiveDocument.getObject(obj)
                    self.callerInstance.sourceWin, self.callerInstance.sourceExtrusion = self.callerInstance.getWindowOrExtrusion(testObject)
                    #if self.callerInstance.sourceWin or self.callerInstance.sourceExtrusion:
                        #App.Console.PrintMessage("Then, select Target Wall(Block) to attach "+ "\n")
                        #reply = QtGui.QMessageBox.information(None,"","Then, select Target Wall(Block) to attach") 
                elif not self.callerInstance.targetObject:
                    targetObject = App.ActiveDocument.getObject(obj)
                    self.callerInstance.targetObject = targetObject

                #findTargetMasterArchSketch(targetObject)
                ## Check targetObject to find target(MasterArch)Sketch
                #def findTargetMasterArchSketch(targetObject):

                    def notFoundTargetMasterArchSketch():
                        self.callerInstance.targetObject = None
                        reply = QtGui.QMessageBox.information(None,"","TRY AGAIN, select Target Wall(Block) to attach") 
                        #return

                    if Draft.getType(targetObject) == "Wall":
                        #if hasattr(targetObject, "CloneOf"):
                        targetObjectBase = targetObject.Base
                        #if hasattr(base, "CloneOf"):	# only Arch Object has 'CloneOf'
                        if Draft.getType(targetObjectBase) == "Clone":
                            if Draft.getType(targetObjectBase.Objects[0]) == "ArchSketch":
                                if hasattr(targetObjectBase.Objects[0], "MasterSketch") and targetObjectBase.Objects[0].MasterSketch:
                                    print (targetObjectBase.Objects[0].MasterSketch)
                                    foundMasterArchSketch=targetObjectBase.Objects[0].MasterSketch
                                else:
                                  notFoundTargetMasterArchSketch()
                            else:
                              notFoundTargetMasterArchSketch()
                        else:
                          notFoundTargetMasterArchSketch()
                    else:
                        notFoundTargetMasterArchSketch()

                    #self.callerInstance.targetObject.ViewObject.HideDependent = False
                    print (foundMasterArchSketch)
                    self.callerInstance.targetSketch = foundMasterArchSketch
                    self.callerInstance.targetSketch.ViewObject.HideDependent = False
                    Gui.ActiveDocument.ActiveView.setCameraType("Orthographic")
                    #Gui.ActiveDocument.setEdit(self.callerInstance.targetObject)
                    Gui.ActiveDocument.setEdit(foundMasterArchSketch)
                    App.Console.PrintMessage("Then, select target Edge of the ArchSketch "+ "\n")
                    reply = QtGui.QMessageBox.information(None,"","Then, select target Edge of the ArchSketch ") 

                elif not self.callerInstance.edge:
                    self.callerInstance.edge = sub
                    self.callerInstance.pickedEdgePlacement = App.Vector(pnt)
                    print("pnt")
                    print(pnt)
                    print("self.callerInstance.pickedEdgePlacement")
                    print(self.callerInstance.pickedEdgePlacement)
                    App.Console.PrintMessage("Then, select target Intersecting Edge of the ArchSketch "+ "\n")
                    reply = QtGui.QMessageBox.information(None,"","Then, select target Intersecting Edge of the ArchSketch") 
                    #self.callerInstance.getTargetSketch(doc, obj, sub, pnt)
                    #self.callerInstance.proceed(doc, obj, sub, pnt)
                else: # i.e. elif not self.callerInstance.intersectingEdge
                    self.callerInstance.intersectingEdge = sub
                    reply = QtGui.QMessageBox.information(None,"","Attaching Window/Door... Remember to Press 'Esc' to escape sketch Edit Mode afterwards! ") 
                    self.callerInstance.proceed()				# doc, obj1, sub1, pnt1, obj2, sub2, pnt2)

            def removeSelection(self,doc,obj,sub):				# Delete the selected object
                App.Console.PrintMessage("removeSelection"+ "\n")
            #def setSelection(self,doc):					# Selection in ComboView TODO
                #App.Console.PrintMessage("setSelection"+ "\n")

        s=observerSelectSourceTargetEdge(self)
        self.observer = s
        FreeCADGui.Selection.addObserver(s)
        if False: # i.e. skip following
              if not self.sourceWin and self.targetSketch:
                App.Console.PrintMessage(" Select source Window or Door object... calling observerSelectSourceTargetEdge" + "\n")
                reply = QtGui.QMessageBox.information(None,"","Select source Window or Door object") 
              elif self.sourceWin and not self.targetSketch:
                App.Console.PrintMessage(" Select target ArchSketch object... calling observerSelectSourceTargetEdge" + "\n")
                reply = QtGui.QMessageBox.information(None,"","Select target ArchSketch object") 
              elif not self.sourceWin and not self.targetSketch:
                App.Console.PrintMessage(" 1) Select source Window object & 2) Then, Select target ArchSketch object... calling observerSelectSourceTargetEdge" + "\n")
                reply = QtGui.QMessageBox.information(None,""," 1) Select source Window object & 2) Then, Select target ArchSketch object") 
              else:
                print (" What happen???")

    def getTargetSketch(self, doc, obj, sub1, pnt):				# ___ calling another addobserver not working --- only 'adopt' previous selection...???
        App.Console.PrintMessage(" OK - Here is  Instance' get___????_TargetSketch() Method"+ "\n")
        App.Console.PrintMessage(str(doc)+ "\n")
        App.Console.PrintMessage(str(obj)+ "\n")
        App.Console.PrintMessage(str(sub)+ "\n")
        App.Console.PrintMessage(str(pnt)+ "\n")
        App.Console.PrintMessage(self.sourceWin)
        App.Console.PrintMessage("\n")
        App.Console.PrintMessage(self.targetSketch)
        App.Console.PrintMessage("\n")
        Gui.Selection.clearSelection()
        Gui.Selection.removeObserver(self.observer)
        del self.observer
        if not self.targetSketch:
            class selectTargetSketch:
                def __init__(self, callerInstance):
                    self.callerInstance=callerInstance
                def addSelection(self,doc,obj,sub,pnt):
                    App.Console.PrintMessage(" OK - Here is addObserver's Instance's addSelection Method"+ "\n")
                    App.Console.PrintMessage("addSelection"+ "\n")
                    App.Console.PrintMessage(str(doc)+ "\n")			# Name of the document
                    App.Console.PrintMessage(str(obj)+ "\n")			# Name of the object
                    App.Console.PrintMessage(str(sub)+ "\n")			# The part of the object name
                    App.Console.PrintMessage(str(pnt)+ "\n")			# Coordinates of the object
                    App.Console.PrintMessage("______"+ "\n")
                    self.callerInstance.targetSketch = App.ActiveDocument.getObject(obj)
                    self.callerInstance.proceed(doc, obj, sub, pnt)		# OK!
            sSkt=selectTargetSketch(self)
            self.observer = sSkt
            FreeCADGui.Selection.addObserver(sSkt)
            App.Console.PrintMessage("... calling selectTargetSketch")
            App.Console.PrintMessage("\n")

    def proceed(self): #self, doc, obj1, sub1, pnt1, obj2, sub2, pnt2):					# This is actually the 2nd Step
        App.Console.PrintMessage(" OK - Here is Instance' proceed() Method"+ "\n")
        App.Console.PrintMessage(self.sourceWin)
        App.Console.PrintMessage("\n")
        App.Console.PrintMessage(self.targetSketch)
        App.Console.PrintMessage("\n")
        Gui.Selection.clearSelection()
        Gui.Selection.removeObserver(self.observer)
        del self.observer
        if True: # self.sourceWin and self.targetSketch: # TODO ___This should be always True (added sourceExtrusion)
            sourceWin = self.sourceWin
            targetSketch = self.targetSketch
            App.Console.PrintMessage("Print global sourcewin")
            App.Console.PrintMessage(sourceWin)
            App.Console.PrintMessage("\n")
            App.Console.PrintMessage("Print global targetSketch")
            App.Console.PrintMessage(targetSketch)
            App.Console.PrintMessage("\n")
            cloneWinReplaceInWallAttachToSketch(sourceWin, self.sourceExtrusion, self.targetObject, targetSketch, self.edge, self.intersectingEdge, self.pickedEdgePlacement) # obj) # doc, obj1, sub1, pnt1)
            #return sourceWin, targetSketch, self.edge, self.intersectingEdge, self.pickedEdgePlacement	# ___ Not working like this?
            App.ActiveDocument.recompute()					# No_TRY IF recompute make resetEdit works or not_ Still Crash
            #Gui.ActiveDocument.resetEdit()					# ___ CRASH FC !!!???
            #Gui.ActiveDocument.resetEdit(targetSketch)				# No_this survive? CRASH FC !!!???_ No Argument allowed
            #afterAction()							# No_move to another (afterAction) def survive? CRASH FC !!!???_ No still crash
            ##del self								# ___ Does it need and work???
        elif not self.sourceWin: # No longer use				# ___ see getTargetSourceEdge comment - separate Addobserver + Def not working
            if not obj:
                s=selectObject(self, None)
                self.observer = s
                FreeCADGui.Selection.addObserver(s)
                self.currentProceed = 'sourceWin'
                App.Console.PrintMessage(self.currentProceed)
                App.Console.PrintMessage("... calling selectObject")
                App.Console.PrintMessage("\n")
            else:
                Gui.Selection.removeObserver(self.observer)
                #del s
                del self.observer
                App.Console.PrintMessage(self.currentProceed)
                App.Console.PrintMessage("... back from selectObject")
                App.Console.PrintMessage("\n")
                self.sourceWin = App.ActiveDocument.getObject(obj)
                #self.sourceWin = obj
                # ___ supposedly "not self.targetSketch" if "not self.sourceWin"???
                App.Console.PrintMessage("print... self.sourceWin" + "\n")
                App.Console.PrintMessage(self.sourceWin)
                App.Console.PrintMessage("\n")
                self.proceed(None, None, None, None)
        elif not self.targetSketch: # Seem no longer use			# ___ see getTargetSourceEdge comment - separate Addobserver + Def not working
            App.Console.PrintMessage("print... Now up to proceed() method 'elif not self.targetSketch' " + "\n")
            if not obj:
                s=selectObject(self, None)
                self.observer = s
                FreeCADGui.Selection.addObserver(s)
                self.currentProceed = 'targetSketch'
                App.Console.PrintMessage(self.currentProceed)
                App.Console.PrintMessage("... calling selectObject")
                App.Console.PrintMessage("\n")
            else:
                Gui.Selection.removeObserver(self.observer)
                #del s
                del self.observer
                App.Console.PrintMessage(self.currentProceed)
                App.Console.PrintMessage("... back from selectObject")
                App.Console.PrintMessage("\n")
                self.targetSketch = App.ActiveDocument.getObject(obj)
                #self.targetSketch = obj
                self.proceed(None, None, None, None)


def cloneWinReplaceInWallAttachToSketch(sourceWin, sourceExtrusion, targetObject, targetSketch, edge, intersectingEdge, pickedEdgePlacement): # obj): # doc, obj, sub, pnt):
      ''' Argument	:	sourceWin, targetSketch, edge, intersectingEdge '''

      geoindex_org = int(edge.lstrip('Edge'))-1 # int(sub.lstrip('Edge'))-1
      print (geoindex_org)
      print (targetSketch.Geometry[geoindex_org])
      lp1=targetSketch.getPoint(geoindex_org,1)
      lp2=targetSketch.getPoint(geoindex_org,2)
      print (lp1)
      print (lp2)
      print (lp1.x, " , ", lp1.y)
      print (lp2.x, " , ", lp2.y)
      vec = lp1 - lp2
      ang = vec.getAngle(FreeCAD.Base.Vector(1,0,0))				#ang= vec1.getAngle(vec2)
      print (ang)
      angle=math.degrees(ang)
      print (angle)

      ## setup 'Placement Sketch'
      placementSk = ArchSketchObject.makeArchSketch(None,"Sk_Placement_")
      sampleGeometryToSketch3_Circle(placementSk)				# ___Add circle geometry until attach to Null/empty Sketch is accepted

      if sourceWin:
          ## find window object if clone, remember Window's Sketch, Window's Hosts & Window's Sketch's Placement
          sourceWinHosts=sourceWin.Hosts					# ___not used?	# ... Base won't change in this script... But Hosts and Placement would...
          #if hasattr(sourceWin, "CloneOf"): # TODO ___ Should alway has this attribute, no need to test
          if sourceWin.CloneOf:
              if Draft.getType(sourceWin) == "Window":
                  sourceWin = sourceWin.CloneOf
          sourceWinSk = sourceWin.Base						# ___ is this '=' a copy or assignment??? Probably the latter according to Python tutorials...
          sourceExtruHoleSk = sourceWinSk
          #sourceWinSkPlacement = sourceWinSk.Placement
          sourceExtruHoleSkPlacement = sourceWinSk.Placement			# ___ '=' here seem to be copy, as line below set this zero, but then PrintMessage below return 'correct' fig.

          ## set zero to window Sketch as new placement + clone Window then	# TODO ___ If window is not level 0, should better sk geometry be drawn like that, Or, the sk placement set at that level?
          if sourceWinSk.Placement != App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(1,0,0),90)):
              print ("Debug - should not happen if used SketchArch WB ")
              reply = QtGui.QMessageBox.information(None,"","sourceWindow's Base Sketch is not at (0,0,0)Rotation(1,0,0),90 - Resetting it to Zero - May affect other Window Based on this Sketch") 
              # Testing___
              sourceWinSk.Placement=App.Placement(App.Vector(0,0,0),App.Rotation(App.Vector(1,0,0),90))
          else:
              print ("Yes, sourceWindow's Base Sketch IS at (0,0,0) Rotation(1,0,0),90   ")

          cloneWin = Draft.clone(sourceWin)

      if sourceExtrusion:
          if Draft.getType(sourceExtrusion.Base) == "Clone":			# underlying sketch should be a clone (to manipulate its placement) if created by SketchArch...
              sourceExtrusionBaseSk = sourceExtrusion.Base.Objects[0]		# ___ only assume 1 object?
          else:
              sourceExtrusionBaseSk = sourceExtrusion.Base
          if Draft.getType(sourceExtrusionBaseSk) == "Clone":
              sourceExtrusionBaseSk = sourceExtrusionBaseSk.Objects[0]
          sourceExtruHoleSk = sourceExtrusionBaseSk
          sourceExtruHoleSkPlacement = sourceExtrusionBaseSk.Placement		# ___ '=' here seem to be copy, as line below set this zero, but then PrintMessage below return 'correct' fig.

      #App.Console.PrintMessage("Sketch for placement...is set to Previous window placement" + "\n")
      pickedPlacement = pickedEdgePlacement					# ___only used .z?
      #print (sourceWinSkPlacement.Base.z)					# ___ Testing ____
      #pickedPlacement.z = sourceWinSkPlacement.Base.z				# Add back original Win Sketch level / z-coord # TODO ___Should have win sketch w/.z? Or Sketch geomtry above Y-axis only?
      print (sourceExtruHoleSkPlacement.Base.z)					# ___ Testing ____
      pickedPlacement.z = sourceExtruHoleSkPlacement.Base.z			# Add back original Win Sketch level / z-coord # TODO ___Should have win sketch w/.z? Or Sketch geomtry above Y-axis only?
      print (pickedPlacement)

      ## attach  Placement_Sketch to TargetSketch
      # TODO _ SketchArch default is 'Attach To Edge & Alignment' + attachToMasterSketch does not change SketchArch to 'Follow Only Offset XYZ & Rotation' - so just set 'pickedPlacment' -> just use .z
      ArchSketchObject.attachToMasterSketch(placementSk, targetSketch, edge, pickedPlacement, '0', intersectingEdge) # targetSketch, sub already set in ArchSketch - 

      ## attach Clone of Window to Placement_Sketch 1st, then Placement_Sketch to TargetSketch
      if sourceWin:
          ArchSketchObject.attachToMasterSketch(cloneWin, placementSk)
          ## old window out of wall, if any
          #sourceWin.Hosts = []
          #cloneWin.Hosts = sourceWinHosts		## commented out, as window has problem in locating opening in wall when wall not at 0,0,0 - new window inside wall
          ## move placement_sketch into window for better organisation only...
          cloneWin.Additions = placementSk						# can use object directly... no need to setup a list =[], then list.append(), then .Additions=list...

      ''' If FC Arch has solved 'Window opening disposition problem', no need to use below method to circumve
          This create a solid out of the original Window Sketch, and attach to the Window/Door's 'Placement ArchSketch' 
          And also create a solid out of the original Solid, and attach to the created 'Placement ArchSketch'          '''  

      cloneSourceExtruHoleSk = Draft.clone(sourceExtruHoleSk)
      ArchSketchObject.attachToMasterSketch(cloneSourceExtruHoleSk, placementSk, None, None, '0', None, 'ObjectXZ')
      extruHole = ArchSketchObject.extrudeSketchToSolid(cloneSourceExtruHoleSk, 'Extru__WinDr_Solid', 'Normal', 800, 0, True, False, True, 'Part::FaceMakerSimple')
      subtractionsLst = targetObject.Subtractions 
      subtractionsLst.append(extruHole)
      targetObject.Subtractions = subtractionsLst

      #App.ActiveDocument.recompute()						# no need - all recompute
      #
      ## __ testing traslate + rotate _placement_Sketch
      #placementSk.Placement =   placementSk.Placement.multiply(App.Placement(App.Vector(1000,1000,1000), App.Vector(0,1,0), 90).Rotation)
      #placementSk.Placement =   placementSk.Placement.multiply(App.Placement(App.Vector(1000,1000,1000), App.Vector(0,1,0), 90.Rotation))
      #placementSk.Placement =   placementSk.Placement.multiply(App.Placement(App.Vector(1000,1000,1000), App.Vector(0,1,0), 0))
      #placementSk.Placement =   placementSk.Placement.multiply(App.Placement(App.Vector(1000,1000,1000), App.Vector(0,1,0), 90))
      #reply = QtGui.QMessageBox.information(None,"","Press 'Esc' to escape sketch Edit Mode")


def sampleGeometryToSketch3_Circle(sk):
    #skGeom = ["Circle (Radius : 500, Position : (0, 0, 0), Direction : (0, 0, 1))"]
    #sk.Geometry = skGeom
    #archSk.Constraints = skConstrt
    circleGeom = Part.Circle(FreeCAD.Base.Vector(0,0,0),FreeCAD.Base.Vector(0,0,1),500)
    sk.addGeometry(circleGeom)
    sk.addConstraint(Sketcher.Constraint('Coincident',-1,1,0,3))    
    #Sketch.addConstraint(Sketcher.Constraint('Coincident',LineFixed,PointOfLineFixed,LineMoving,PointOfLineMoving))    
    #ssc0=ss.Constraints[0]
    #ssc0.Content
    #'<Constrain Name="" Type="1" Value="0" First="0" FirstPos="3" Second="-1" SecondPos="1" Third="-2000" ThirdPos="0" LabelDistance="10" LabelPosition="0" IsDriving="1" IsInVirtualSpace="0" />\n'

##Based on def sort_copy_edges(sketchSubElements):
def sort___edges(targetSketch, sketchSubElements):
  print ('Sorting ___Edges....')
  print ('\n')
  print ('  These are subElement in the selected sketch... ' + '\n')
  for i, a in enumerate(sketchSubElements):
    print (i, " : ", a)
    # check the selection and filter out those not edges
    # below 'for ...' does not work... used the above
    #        for i in selEx0SubElements:
    #             print i, " : ", selEx0SubElements[i]
    if sketchSubElements[i].startswith('Edge'):				# Currently filter Straight Edges only... To Do curve, circular, spline, vertex(?)...
      selSketchEdge = sketchSubElements[i]
      print (selSketchEdge)
      geoindex_org = int(selSketchEdge.lstrip('Edge'))-1
      print (geoindex_org)
      # about from this part onward some differ from Offset & Parallel...
      print ('construction is ' , targetSketch.Geometry[geoindex_org].Construction)
      try:
      #if sketch.Geometry[geoindex_org].Construction == False:		# i.e. if edge is not construction mode
        print (targetSketch.Geometry[geoindex_org])
        # 
        lp1=sx0.Object.getPoint(geoindex_org,1)
        lp2=sx0.Object.getPoint(geoindex_org,2)
        print (lp1)
        print (lp2)
        print (lp1.x, " , ", lp1.y)
        print (lp2.x, " , ", lp2.y)
        #Edge_list_org.append(geoindex_org) # or keep int? or str(geoindex_org)
        ## Now copy to another sketch - sketch001 as example...
        #Edge_geom = Part.LineSegment(lp1, lp2)
        #print (Edge_geom)
        #copy = sketch_c.addGeometry(Edge_geom)
        ## Now set original or copy of edge to be construction mode depend on Copy_Flag
        #if sketch.CopyFlag == 1:	# App.ActiveDocument.Spreadsheet.Copy_Flag == 1:
          #sx0.Object.setConstruction(geoindex_org, True) # Original line become Construction mode
        #if sketch.CopyFlag == 0:	# if App.ActiveDocument.Spreadsheet.Copy_Flag == 0:
          #sketch_c.setConstruction(copy, True) # Original Keep Normal, Copy line become Construction mode
        ## Now annoucing linking constraints...but code not ready...
        #print sketch_c.Name+'.Constraints.'+" <-- " + sketch.Name+".Constraints."
        ## Now copies of edges appended in a list like the original
        ##____seem 'copy' return by .addGeometry() is already ____no 'L,)'____a str or int ____??
        ##testing to remark below out....
        ##        geoindex_c_str = (str(copy).rstrip('L,)')).lstrip('(') #need to strip the 'L'  # At least this line is not necessary
        ##        geoindex_c = int(geoindex_c_str) #no need to -1 right?
        ## So this line
        ##        geoindex_c = copy # str
        #geoindex_c = int(copy) #no need to -1 right? / int or str???
        ## Or this line
        #print copy, ' , ', geoindex_c
        #Edge_list_copy.append(geoindex_c)
        ##        Edge_list_copy.append(str(geoindex_c))
        ##___'strange' - print copy... return 2 nos...(3, 6 e.g.) but pinrt Edge_list_org + Edge_list_copy (at the end) return something like [3] [6L]___??
        ##
        ## no distance constraints in Sketch_Copy_and_Link
        ##      sketch.addConstraint(Sketcher.Constraint('Distance',geoindex_c,1,geoindex_org,100))
        ##      sketch.addConstraint(Sketcher.Constraint('Parallel',geoindex_c,geoindex_org))
        ##
      except:
        pass
    else:
      print (sketchSubElements[i], ' is not an edge')
    print ('\n')
  #print 'Edge_list_org: ', Edge_list_org
  #print 'Edge_list_copy: ', Edge_list_copy
  print ('\n')
  ##
  ## add back the original selection to distinguish from the copies
  ## ... or add the copies...????
  ## No Complaint ... but not working....
  #Gui.Selection.addSelection(sketch,selEx0SubElements)
  ## NOT working yet ...ValueError: type must be 'DocumentObject[,subname[,x,y,z]]' or 'DocumentObject, list or tuple of subnames'
  ##Gui.Selection.addSelection(sx0,selEx0SubElements)
  print ('Sorted ___Edges....')
  print ('\n')
  print ('\n')


##
#class SelectionGate(object):
  #def allow(self, doc, obj, sub):
    #if not obj.isDerivedFrom("Part::Feature"):
      #return False
    #if not str(sub).startswith("Edge"):
      #return False
    ## #edge = getattr(obj.Shape, sub)

    #if edge.isClosed():
      #if isinstance(edge.Curve, Part.Circle):
        #self.circle = edge
        #return True
    #return False
#
#gate=SelectionGate()
#Gui.Selection.addSelectionGate(gate)


##
#filter=Gui.Selection.Filter("SELECT Part::Feature SUBELEMENT Edge")
#Gui.Selection.addSelectionGate(filter)
#
#if filter.match():
  #o=filter.result()[0][0]
  # from here on use your code above
##


##
#from PySide import QtGui
#QtGui.QInputDialog.getText(None, "Get text", "Input:")[0]
##


## from DraftTools.py
#def selectObject(arg):
#    '''this is a scene even handler, to be called from the Draft tools
#    when they need to select an object'''
## from DraftTools.py



#------------------------------------------------------------------------------#
#                FreeCAD Commands Classes & Associated Functions               #
#------------------------------------------------------------------------------#

''' Clone and attach a Window/Door object to a WallGroup's underlying ArchSketch
  May select a window before initial command; select wall to attach by Sketch Edit mode '''

class _Command_selectObjects_and_cloneAttachWin():
    ''' CloneAttachWin Command Definition '''

    def GetResources(self):
        return {'Pixmap'  : 'My_Command_Icon',
                'Accel' : "",
                'MenuText': "CloneAttachWin",
                'ToolTip' : "CloneAttachWin: Attach Window/Door Wall & MasterArchSketch",
                'CmdType' : "ForEdit"}						# DeepSOIC's advice - https://forum.freecadweb.org/viewtopic.php?f=22&t=29088&sid=a696599d234cd1f7b3e49919988bffe0#p237034
    def IsActive(self):
        return True
    def Activated(self):
        "Do something here"
        #printMessage = ""
        #printMessage1 = "Select a Window or Door as subject"
        #printMessage2 = "Select an ArchSketch as target"
        if False: # no longer run below- alway select through addObserver to find target(MasterArch)Sketch after selecting targetObject during Observer- otherwise can't think of a code that can do this...
            try:
                targetSketch=Gui.Selection.getSelection()[1]
                print ("targetSketch")
                print (targetSketch)
                if Draft.getType(targetSketch) != "ArchSketch":
                    #except1()
                    printMessage = printMessage2
                    targetSketch = None
            except:
                #except1()
                printMessage = printMessage2
                targetSketch = None
                #exit()
        try:
            sourceObject=Gui.Selection.getSelection()[0]
            print ("sourceObject")
            print (sourceObject)
            if False:
            #if Draft.getType(sourceWin) != "Window":
                #except2()
                if printMessage:
                    printMessage = " & 2) " + printMessage
                    printMessage = "1) " + printMessage1 + printMessage
                else:
                    printMessage = printMessage1
                    sourceWin = None
        except:
            #except2()
            #if printMessage:
                #printMessage = " & 2) " + printMessage
                #printMessage = "1) " + printMessage1 + printMessage
            #else:
            #printMessage = printMessage1
            sourceObject = None
            #exit()
        #if printMessage:
            #print (printMessage)  
            #reply = QtGui.QMessageBox.information(None,"",printMessage)
        #FreeCAD.Console.PrintMessage(printMessage + "\n")
        Gui.Selection.clearSelection()
        instance = gui_SelectObjects_and_CloneAttach(sourceObject) # , None)	# No longer pre-select - (can pre-select sourceWin in fact...) , targetSketch)	# ___not work like this way???
        #sourceWin, targetSketch, doc, obj, sub, pnt = gui_SelectObjects_and_CloneAttach(sourceWin, targetSketch)	# ___not work like this way???
        #cloneWinReplaceInWallAttachToSketch(sourceWin, targetSketch, doc, obj, sub, pnt)

FreeCADGui.addCommand('CloneAttachWin', _Command_selectObjects_and_cloneAttachWin()) 
