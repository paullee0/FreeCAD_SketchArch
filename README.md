# FreeCAD_SketchArch
An experimental module for Architecure and making Arch Objects with SketchObjectPython


### Short Description

To leverage Sketch and/or SketchObjectPython inherent features to help building Architectural Models


### Sketcher Capabilities

- Leverage Sketch and/or SketchObjectPython inherent features and capabilties
- So Sketch Layout + Arch Wall = Building Layout
- Sketcher have geometric and dimensional constraints to help making and editing 'single-line sketch layouts'


### Attachment

- Sketch have Mapmode/Attachment Offset so sketch for each floor layout can be fixed at desired position 'mutually as a whole'
- Extend capability to Arch Objects, e.g. Window, Equipment and their Links could 'attach' to 'Wall Segment' /  'Layout Sketch' to fix its position
  - Discussion (Intuitive Automatic Windows/Doors + Equipment Placement) - https://forum.freecadweb.org/viewtopic.php?f=23&t=50802
              <br>               Model      - https://forum.freecadweb.org/download/file.php?id=137851

  <br> (Window Object also use Sketch; alternative use Window's Sketch to attach to Layout Sketch)


### Width & Align Per Edge

- ArchWall base on a Sketch / SketchObjectPython object (ArchSketch) can have different width for each segment - per Sketch Edge
- ArchWall base on a Sketch / ArchSketch can then be treated / moved / edited as single floor layout object, the dimension of which, width of individual wall segment can be modified relatively easily


### TopoNaming Tolorent

- The most import feature is to make referencing to a Sketch Edge persistent (not currently as of 0.19_pre, unless use @realthunder's branch),
  3 approaches
    1.  Rebuilding Sketch.Geometry[index].Tag onDocumentRestore
    <br> (**Implemented but not exposed, in favour of solution 2 below**)
        -  sketch.Geometry[index].Tag == Unique identification survive changes? - https://forum.freecadweb.org/viewtopic.php?f=22&t=28575
    2.  Using PartGeometryExtension / SketchGeometryExtension
    <br> (Prefer approach)
        - Part Geometry Extensions - Extension for 'Persistent UUID Tag'  -  https://forum.freecadweb.org/viewtopic.php?style=10&f=10&t=33349&start=50#p374767
        - Sketcher Development - Integration of Extensions  -  https://forum.freecadweb.org/viewtopic.php?f=10&t=51716#p444360
    3.  Using @Realthunder's branch

- Earlier Discussion : Unique and Persistent Sketch Edge Name
  - Ability to (auto) give (unique) name each edges in a sketch which would not be repeated or reused  -  Sketcher: Virtual Space  -  https://forum.freecadweb.org/viewtopic.php?t=25904#p204581
  - Tag consistent (for Sketch geometries)  - Civil engineering feature implementation (Transportation Engineering)  -  https://forum.freecadweb.org/viewtopic.php?f=8&t=22277&start=520#p280716


### Space / Room / Zone & Cell Complex Definition

- A Space, Room or Zone could be defined right within (Arch)Sketch itself
- Automatic identification of each enclosed area (room) defined by edges (walls)
- Automatic generation of CellComplex (see below) 
- Manual assignment of Space / Zone definition identified by user
- Naming of the Space / Room / Zone by user

- Single Source of 'Information Rich' Sketch to build
  - ArchWall
  - ArchSpace / CellComplex (rooms)

- CellComplex
  - OSArch forum :  Talk on Topologic (CellComplex) https://community.osarch.org/discussion/131/talk-on-topologic#latest
  - Built on same Sketch as ArchWall (building layout)
  - Share same faces beteen Cells
  - Cell faces have no thickness

- Space Connectivity
  - So 2 ArchSpace / Cells with same ArchWindow/Door is interconnected

- ArchWindow/Door Attachment
  - 'Attached' to Space / Room / Zone rather than only 'Arch Wall' (or edges)
  - 'Grouped' under 'ArchSpace' as well

Discussion
- [Feature] Floor Area Calculation + Room Dimension https://forum.freecadweb.org/viewtopic.php?f=23&t=47905&start=70#p485618


### Examples

Models
- Villa Savoye Discussion - https://forum.freecadweb.org/viewtopic.php?f=23&t=41836
              <br>               Model      - https://github.com/paullee0/FreeCAD_Villa-Savoye
- Carpenter Center Discussion - https://forum.freecadweb.org/viewtopic.php?f=24&t=44186&hilit=carpenter&start=10
      <br>   Model - https://github.com/paullee0/FreeCAD_Carpenter-Center

Discussion / Announcement
- Intuitive Automatic Windows/Doors Placement - https://forum.freecadweb.org/viewtopic.php?f=23&t=50802
    <br> (Adding Features to Arch Windows / Doors) 
- PR / Discussion Thread - https://forum.freecadweb.org/viewtopic.php?f=23&t=39060
- ArchSketch + ArchWall = Building Layout - https://forum.freecadweb.org/viewtopic.php?f=23&t=38703


### More concepts of adopting SketchObjectPython / ArchSketch as Building Layout Object

  - Different materials for wall surface on each sides
  - Different wall joint / junction geometrical shape
  - (good for IFCexport ?) Maybe Wall can support different Height for each segment? Similarly, this information be saved in the ArchSketch
  - (good for IFCexport ?) Different materials for different wall segment?


### Prerequisites
- The said information (widht, align, height, material etc.) is conceived to be saved in Sketch / SketchObjectPython with Part Geometry Extensions feature - the latter currently has bug which crash FC
- Bugs / IFC export / multi-materials etc. to support Wall base on Sketch to be fixed / implemented


About


### Install
- See https://wiki.freecadweb.org/Installing_more_workbenches on manual installation procedure


Usage


Feedback
(FC thread)


License
