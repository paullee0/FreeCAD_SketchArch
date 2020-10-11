# FreeCAD_SketchArch
A module for Architecure and making Arch Objects with SketchObjectPython


Short Description

- Leverage Sketch and/or SketchObjectPython inherent features to help building Architectural Models
- So Sketch Layout + Arch Wall = Building Layout
- Sketch have geometric and dimensional constraints to help making and editing 'single-line sketch layouts'
- Sketch have Mapmode/Attachment Offset so sketch for each floor layout can be fixed at desired position 'mututally as a whole'
- Window Object also use Sketch; so Window Sketch could 'attach' to 'Layout Sketch' to fix its position
- Examples
  - Villa Savoye Discussion - https://forum.freecadweb.org/viewtopic.php?f=23&t=41836
  - Villa Savoye Model      - https://github.com/paullee0/FreeCAD_Villa-Savoye
  - Carpenter Center Discussion - https://forum.freecadweb.org/viewtopic.php?f=24&t=44186&hilit=carpenter&start=10
  - Carpenter Center Model      - https://github.com/paullee0/FreeCAD_Carpenter-Center
- Discussion / Announcement
  - Intuitive Automatic Windows/Doors Placement (Adding Features to Arch Windows / Doors) - https://forum.freecadweb.org/viewtopic.php?f=23&t=50802
  - PR / Discussion Thread - https://forum.freecadweb.org/viewtopic.php?f=23&t=39060
  - ArchSketch + ArchWall = Building Layout - https://forum.freecadweb.org/viewtopic.php?f=23&t=38703
  
- ArchWall base on a Sketch / SketchObjectPython object (ArchSketch) can have different width for each segment - per Sketch Edge
- ArchWall base on a Sketch / ArchSketch can then be treated / moved / edited as single floor layout object, the dimension of which, width of individual wall segment can be modified relatively easily
- More concepts of adopting SketchObjectPython / ArchSketch as Building Layout Object
  - Different materials for wall surface on each sides
  - Different wall joint / junction geometrical shape
  - (good for IFCexport ?) Maybe Wall can support different Height for each segment? Similarly, this information be saved in the ArchSketch
  - (good for IFCexport ?) Different materials for different wall segment?


About


Prerequisites
- The said information (widht, align, height, material etc.) is conceived to be saved in Sketch / SketchObjectPython with Part Geometry Extensions feature - the latter currently has bug which crash FC
- Bugs / IFC export / multi-materials etc. to support Wall base on Sketch to be fixed / implemented


Install


Usage


Feedback
(FC thread)


License
