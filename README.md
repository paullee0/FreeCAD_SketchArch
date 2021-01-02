# FreeCAD_SketchArch
A module for Architecure and making Arch Objects with SketchObjectPython


Short Description

- Leverage Sketch and/or SketchObjectPython inherent features to help building Architectural Models
- So Sketch Layout + Arch Wall = Building Layout
- Sketch have geometric and dimensional constraints to help making and editing 'single-line sketch layouts'
- Sketch have Mapmode/Attachment Offset so sketch for each floor layout can be fixed at desired position 'mutually as a whole'
- ArchObject, e.g. Window, Equipment and their Links could 'attach' to 'Wall Segment' /  'Layout Sketch' to fix its position
  - Discussion (Intuitive Automatic Windows/Doors + Equipment Placement) - https://forum.freecadweb.org/viewtopic.php?f=23&t=50802
              <br>               Model      - https://forum.freecadweb.org/download/file.php?id=137851

  <br> (Window Object also use Sketch; alternative use Window's Sketch to attach to Layout Sketch ?)

- ArchWall base on a Sketch / SketchObjectPython object (ArchSketch) can have different width for each segment - per Sketch Edge
- ArchWall base on a Sketch / ArchSketch can then be treated / moved / edited as single floor layout object, the dimension of which, width of individual wall segment can be modified relatively easily
- The most import feature is to make referencing to a Sketch Edge persistent (not currently as of 0.19_pre, unless use @realthunder's branch)
  3 approaches
    1.  Rebuilding Sketch.Geometry[index].Tag onDocumentRestore
    sketch.Geometry[index].Tag == Unique identification survive changes? - https://forum.freecadweb.org/viewtopic.php?f=22&t=28575
    2.  Using PartGeometryExtension / SketchGeometryExtension
    Part Geometry Extensions - Extension for 'Persistent UUID Tag'  -  https://forum.freecadweb.org/viewtopic.php?style=10&f=10&t=33349&start=50#p374767
                  <br>               Sketcher Development - Integration of Extensions  -  https://forum.freecadweb.org/viewtopic.php?f=10&t=51716#p444360
    3.  Using @Realthunder's branch
    
  Earlier Discussion - Unique and Persistent Skedch Edge Name
                <br>               Ability to (auto) give (unique) name each edges in a sketch which would not be repeated or reused  -  Sketcher: Virtual Space  -  https://forum.freecadweb.org/viewtopic.php?t=25904#p204581
                <br>               Tag consistent (for Sketch geometries)  - Civil engineering feature implementation (Transportation Engineering)  -  https://forum.freecadweb.org/viewtopic.php?f=8&t=22277&start=520#p280716
        
- Examples
    - Villa Savoye Discussion - https://forum.freecadweb.org/viewtopic.php?f=23&t=41836
              <br>               Model      - https://github.com/paullee0/FreeCAD_Villa-Savoye
    - Carpenter Center Discussion - https://forum.freecadweb.org/viewtopic.php?f=24&t=44186&hilit=carpenter&start=10
      <br>   Model - https://github.com/paullee0/FreeCAD_Carpenter-Center
    - Discussion / Announcement
      - Intuitive Automatic Windows/Doors Placement - https://forum.freecadweb.org/viewtopic.php?f=23&t=50802
    <br> (Adding Features to Arch Windows / Doors) 
    - PR / Discussion Thread - https://forum.freecadweb.org/viewtopic.php?f=23&t=39060
    - ArchSketch + ArchWall = Building Layout - https://forum.freecadweb.org/viewtopic.php?f=23&t=38703

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
