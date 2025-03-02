#***************************************************************************	
#*                                                                         *	
#*   Copyright (c) 2018 - 2022                                              *	
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
										
class SketchArchWorkbench(Workbench):						
										
    ''' Sketch Arch Workbench '''						
										
    MenuText = "SketchArch"							
    ToolTip = "SketchArch Workbench for Architecture "				
										
    def __init__(self):								
										
        import SketchArchIcon							
        self.__class__.Icon = SketchArchIcon.getIconPath() + "/icons/SketchArchWorkbench.svg"				
										
    def Initialize(self):							
										
        ''' This function is executed when FreeCAD starts '''			
										
        import SketchArch							
        self.ArchSketchTools = ["ArchSketch", "EditWallAlign", "EditWallWidth",	
                                "EditWallOffset", "EditWallAttach", "EditWall",	
                                "EditStructure", "EditCurtainWall",		
                                "EditStairs",					
                                "PropertySet", "Voxel",	"CellComplex",		
                                "ArchSketchLock"]				
        self.appendToolbar("Sketch Arch", self.ArchSketchTools)			
        self.appendMenu("Sketch Arch", self.ArchSketchTools)			
										
    def Activated(self):							
        ''' This function is executed when the workbench is activated '''	
        pass									
                								
    def Deactivated(self):							
        ''' This function is executed when the workbench is deactivated '''	
        pass									
										
    def ContextMenu(self, recipient):						
        ''' This is executed whenever the user right-clicks on screen '''	
										
    def GetClassName(self):							
        return "Gui::PythonWorkbench"						
										
FreeCADGui.addWorkbench(SketchArchWorkbench)					
										
										
