## FreeCAD SketchArch Workbench

An experimental module for Architecture and making Arch Objects with SketchObjectPython

### I. Description

To leverage Sketch and/or SketchObjectPython inherent features to help building Architectural Models


### II. Features

#### 1. Sketcher Capabilities
![alt text 1](https://wiki.freecadweb.org/images/9/91/Workbench_Sketcher.svg)

- Leverage Sketch and/or SketchObjectPython inherent features and capabilities
- So Sketch Layout + Arch Wall = Building Layout
- Sketcher have geometric and dimensional constraints to help making and editing 'single-line sketch layouts'

![alt text 1a](https://forum.freecadweb.org/download/file.php?id=102600)

![alt text 1b](https://forum.freecadweb.org/download/file.php?id=102608)



#### 2. Intuitive Automatic Arch Objects Placement

![alt text 2](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Attach.svg)


- Sketch have Mapmode/Attachment Offset so sketch for each floor layout can be fixed at desired position 'mutually as a whole'
- Extend capability to Arch Objects, e.g. Window, Equipment and their Links could 'attach' to 'Wall Segment' /  'Layout Sketch' to fix its position
  - Discussion (Intuitive Automatic Windows/Doors + Equipment Placement) ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=50802)) ([downloadable model](https://forum.freecadweb.org/download/file.php?id=137851))
  - **Note:** (Window Object also use Sketch; alternative use Window's Sketch to attach to Layout Sketch)

![alt text 2a](https://forum.freecadweb.org/download/file.php?id=129408)

#### 3. Width & Align Per Edge
![alt text 3a](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Align.svg)
![alt text 3b](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Width.svg)

- ArchWall base on a Sketch / SketchObjectPython object (ArchSketch) can have different width for each segment - per Sketch Edge
- ArchWall base on a Sketch / ArchSketch can then be treated / moved / edited as single floor layout object, the dimension of which, width of individual wall segment can be modified relatively easily

![alt text 3a](https://forum.freecadweb.org/download/file.php?id=104384)


#### 4. Floor Area Calculation + Room Dimension

- [Feature] Floor Area Calculation + Room Dimension ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=47905&start=70#p485618))

![alt text 3a](https://forum.freecadweb.org/download/file.php?style=10&id=150955)



#### 5. Topological naming tolerant

- The most import feature is to make referencing to a Sketch Edge persistent (not currently as of 0.19_pre, unless use @realthunder's branch),
  3 main approaches :

    1.  Using sketch.Geometry[index].Tag
        Using `sketch.Geometry[index].Tag` == Unique identification survive changes? ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=22&t=28575))
        <br>
        a. **WIP** On-the-fly updating Index referencing `Sketch.Geometry[index].Tag` on `UpdateAttachmentOffset()` (**preferred approach**)
        <br>
        b.  Rebuilding a Dict referencing `Sketch.Geometry[index].Tag` `onDocumentRestore` (**Implemented but not exposed. Solution 1a is preferable**)

    2.  Using PartGeometryExtension / SketchGeometryExtension
        - Part Geometry Extensions - Extension for 'Persistent UUID Tag'  ([forum thread](https://forum.freecadweb.org/viewtopic.php?style=10&f=10&t=33349&start=50#p374767))
        - Sketcher Development - Integration of Extensions  ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=10&t=51716#p444360))

    3.  Using @Realthunder's branch

- Earlier Discussions : Unique and Persistent Sketch Edge Name
  - Ability to (auto) give (unique) name each edges in a sketch which would not be repeated or reused  -  Sketcher: Virtual Space ([forum thread](https://forum.freecadweb.org/viewtopic.php?t=25904#p204581))
  - Tag consistent (for Sketch geometries)  - Civil engineering feature implementation (Transportation Engineering)  ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=8&t=22277&start=520#p280716))


#### 6. Voxelisation
![alt text 6](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Voxel.svg)


- https://forum.freecadweb.org/viewtopic.php?f=23&t=61158&p=535506#p535506
- Current workflow for comment / suggestion: -

1. Select the shape object to 'voxelise', click Voxel button
2. Can select the shape of voxel, like (App::Link to) a Group w/ 4 Walls, Windows, Slab etc.
3. Has 3 modes :-
    - a. Center : If Center of (the BoundBox of) voxel is within the Input Shape, it is shown
    - b. Any Corner : If Any Corner of (the BoundBox of) voxel is within the Input Shape, it is shown
    - c. All Corners : Only if All Corners of (the BoundBox of) voxel are within the Input Shape, it is shown

![alt text 3a](https://forum.freecadweb.org/download/file.php?id=165334)



#### Features in Development, Other Remarks

<details>
  <summary>Click to expand!</summary>
  
#### 6. Space / Room / Zone & Cell Complex Definition

- A Space, Room or Zone could be defined right within (Arch)Sketch itself
- Automatic identification of each enclosed area (room) defined by edges (walls)
- Automatic generation of CellComplex (see below)
- Manual assignment of Space / Zone definition identified by user
- Naming of the Space / Room / Zone by user

- Single Source of 'Information Rich' Sketch to build
  - ArchWall
  - ArchSpace / CellComplex (rooms)

- CellComplex
  - OSArch forum: Talk on Topologic (CellComplex) ([forum thread](https://community.osarch.org/discussion/131/talk-on-topologic#latest))
  - Built on same Sketch as ArchWall (building layout)
  - Share same faces between Cells
  - Cell faces have no thickness

- Space Connectivity
  - So 2 ArchSpace / Cells with same ArchWindow/Door is interconnected

- ArchWindow/Door Attachment
  - 'Attached' to Space / Room / Zone rather than only 'Arch Wall' (or edges)
  - 'Grouped' under 'ArchSpace' as well


#### 7. More concepts of adopting SketchObjectPython / ArchSketch as Building Layout Object

  - Different materials for wall surface on each sides
  - Different wall joint / junction geometrical shape
  - (good for IFCexport ?) Maybe Wall can support different Height for each segment? Similarly, this information be saved in the ArchSketch
  - (good for IFCexport ?) Different materials for different wall segment?

#### Prerequisites / Other Remarks

- The said information (width, align, height, material etc.) is conceived to be saved in Sketch / SketchObjectPython with Part Geometry Extensions feature - the latter currently has a bug which crash FC
- Bugs / IFC export / multi-materials etc. to support Wall base on Sketch to be fixed / implemented

</details>

### III. Examples

Models
- Villa Savoye Discussion ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=41836)) ([downloadable model](https://github.com/paullee0/FreeCAD_Villa-Savoye))
- Carpenter Center Discussion ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=24&t=44186&hilit=carpenter&start=10) ([downloadable model](https://github.com/paullee0/FreeCAD_Carpenter-Center)


### IV. Install

'Semi'- Automatic (recommended)

* Launch FreeCAD and start the [Addons Manager](https://wiki.freecadweb.org/Addon_manager) (Tools > Addon manager)
* Press the Configure... button.
  * The Addon manager options dialog box opens.
  * Add the repository to the Custom repositories list - https://github.com/paullee0/FreeCAD_SketchArch
  * Optionally choose proxy settings.
  * Press the OK button button to close the dialog box.
* Restart FreeCAD
* Locate the workbench dropdown list and switch to the 'SketchArch workbench'

Manual

If necessary, this workbench can be installed manually. Example:
* Find your default local FreeCAD directory and clone SketchArch in to it. Example:
  ```
  cd ~/.FreeCAD/Mod
  git clone https://github.com/paullee0/FreeCAD_SketchArch
  ```
* Restart FreeCAD
* Locate the workbench dropdown list and switch to the 'SketchArch workbench'

For more general info see the general [instructions for manual install](https://wiki.freecadweb.org/Installing_more_workbenches) on the FreeCAD wiki.


### V. Feedback / Discussion / Announcement

There are a few discussion on FreeCAD discussion fourm with different topics:-
  - Intuitive Automatic Windows/  Doors/ Equipment Placement ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=50802&sid=fd179d8d8b15b107a6c98eee7eaa88ec)) 
  - PR / Discussion Thread - ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=39060))
  - ArchSketch + ArchWall = Building Layout - ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=38703))

When bugs/feature-requests are vetted on the forum they will then be tracked in the [issue queue](https://github.com/paullee0/FreeCAD_SketchArch/issues) of this repo.



### VI. About

Maintainer: paullee ([@paullee0](https://github.com/paullee0))
Repository: https://github.com/paullee0/FreeCAD_SketchArch



### VII. License

[LICENSE](LICENSE)


