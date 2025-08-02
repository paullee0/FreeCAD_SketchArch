## FreeCAD SketchArch Workbench

![alt text 2](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/SketchArchWorkbench.svg)  An experimental add-on module to augment Arch Objects with additional features <br>
 <br>
(This Add-On is usually developed in conjunction with the stock FreeCAD development particularly BIM workbench, so use the latest development weekly build release {or even compile from latest source} if there is update in this add-on to ensure everything works, thanks!)

### I. Description

For better and more intuitive architectural modelling workflow, this workbench leverage Sketch (or SketchObjectPython) inherent features and enhance it with smarter and information-rich features for use as Base of Arch Objects (e.g. Wall, Structure, Curtain Wall).


### II. Features

#### 1. ArchSketch : Sketcher Capabilities - Enhanced with Smarter and Information-Rich Features
![alt text 1](https://wiki.freecadweb.org/images/9/91/Workbench_Sketcher.svg)

- Leverage Sketch inherent features and capabilities
- So [ArchSketch + Arch Wall + Structure + Curtain Wall etc. = Building Layout](https://github.com/paullee0/FreeCAD_SketchArch#4-arch-structure-curtain-wall-wall-etc---same-archsketch--building-layout)
- Sketcher have geometric and dimensional constraints to help making and editing 'single-line sketch layouts'


(Click To PLAY VIDEO !)
[![ Youtube Video](https://i9.ytimg.com/vi/uhf5TH3WKAc/mq2.jpg?sqp=CKy6opQG&rs=AOn4CLAvBRVX4w5_4ykpze3cDoRvkNEnZA)](https://youtu.be/uhf5TH3WKAc "Click To PLAY VIDEO !")
[![ Youtube Video](https://i9.ytimg.com/vi/D7x-UCGlZy4/mq3.jpg?sqp=CKy6opQG&rs=AOn4CLCqVE1L0buawaqPVzXZK0zFX3o7vA)](https://youtu.be/D7x-UCGlZy4 "Click To PLAY VIDEO !")

![alt text 1a](https://forum.freecadweb.org/download/file.php?id=102600)

![alt text 1b](https://forum.freecadweb.org/download/file.php?id=102608)



#### 2. Parametric Placement/Attachment of Arch Objects Intuitively  
([Toponaming-Tolerant](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/README.md#7-topological-naming-tolerant))

![alt text 2](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Attach.svg)


- Sketch have Mapmode/Attachment Offset so sketch for each floor layout can be fixed at desired position 'mutually as a whole'
- Extend capability to Arch Objects, e.g. Window, Equipment and their Links could 'attach' to 'Wall Segment' /  'Layout Sketch' to fix its position
  - Discussion (Intuitive Automatic Windows/Doors + Equipment Placement) ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=50802)) ([downloadable model](https://forum.freecadweb.org/download/file.php?id=137851))
  - **Note:** (Window Object also use Sketch; alternative use Window's Sketch to attach to Layout Sketch)

[ Special Remarks :
-  For this feature to work, use at least the 0.20_pre-release version git 26720 (e.g. FreeCAD_weekly-builds-26720-Linux-Conda_glibc2.12-x86_64.AppImage)
-  Otherwise, needs to follow the FreeCAD forum discussion to use the tweaked ArchWindow.py, ArchEquipment.py etc. ]

(Click To PLAY VIDEO !)
[![ Youtube Video](https://i9.ytimg.com/vi/FpdWlKFVQhg/mq3.jpg?sqp=CIS_opQG&rs=AOn4CLDg6xiu_ZOkemBpgKn9Uyt1NaHnjw)](https://youtu.be/FpdWlKFVQhg "Click To PLAY VIDEO - Placement of Arch Window(Door) !")
[![ Youtube Video](https://i9.ytimg.com/vi/1W_-QjcQOXI/mq2.jpg?sqp=CIS_opQG&rs=AOn4CLBzHiOve-g3uWsoN10pQi72j4_Ugw)](https://youtu.be/1W_-QjcQOXI "Click To PLAY VIDEO - Automatic (Parametric) Placement of Arch Window(Door) !")

(Click To PLAY VIDEO !)
[![ Youtube Video](https://i9.ytimg.com/vi/ozZ-jl-BSjU/mq2.jpg?sqp=CIS_opQG&rs=AOn4CLDlLCx-Car66Bfg-UvVre1gT-DE3A)](https://youtu.be/ozZ-jl-BSjU "Click To PLAY VIDEO - Placement of Arch Equipment!")

![alt text 2a](https://forum.freecadweb.org/download/file.php?id=129408)
![alt text 2b](https://forum.freecad.org/download/file.php?style=4&id=191612)
![alt text 2c](https://forum.freecad.org/download/file.php?style=4&id=191611J)

#### 3. Width, Align & Offset Per Edge
([Toponaming-Tolerant](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/README.md#7-topological-naming-tolerant))

![alt text 3a](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Width.svg)
![alt text 3b](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Align.svg)
![alt text 3ca](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Offset.svg)

- ArchWall base on a ArchSketch / Sketch can have different Width, Align & Offset for each segment - per Sketch Edge
- ArchWall base on a ArchSketch / Sketch  can then be treated / moved / edited as single floor layout object, the dimension of which, width of individual wall segment can be modified relatively easily

(Click To PLAY VIDEO !)
[![ Youtube Video](https://i9.ytimg.com/vi/sHejQI3PxNg/mq2.jpg?sqp=CKSsopQG&rs=AOn4CLCQlFsdFh1t5kmKRwNjq0Z3bFCwlg)](https://www.youtube.com/watch?v=sHejQI3PxNg "Click To PLAY VIDEO - EDIT ALIGN!")
[![ Youtube Video](https://i9.ytimg.com/vi/UZktE6BUIJ8/mq2.jpg?sqp=CNzDopQG&rs=AOn4CLAMkiBCktSwWA6H-9ImQx5X3ubaSQ)](https://youtu.be/UZktE6BUIJ8 "Click To PLAY VIDEO - EDIT WIDTH!")

![alt text 3a](https://forum.freecadweb.org/download/file.php?id=104384)



#### 4. Arch Structure, Curtain Wall, Wall etc. +  Same ArchSketch = Building Layout
(with User Selected Edges in ArchSketch)

![alt text 4a](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Wall_Toggle.svg) 
![alt text 4b](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Structure_Toggle.svg) 
![alt text 4c](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_CurtainWall_Toggle.svg)
![alt text 4d](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Edit_Stairs_Toggle.svg)
<br>

ArchSketch + ArchWall = Wall Layout <br>
ArchSketch + ArchStructure = Slab Layout <br>
ArchSketch + ArchCurtainWall = CurtainWall Layout <br>
ArchSketch + ArchStairs = ArchStairs Layout <br>

Have your ever set out your building layout in a sketch like below, and wonder if -

- ArchWall would build walls based on edges in the middle part
- ArchStructure build slab based on the outermost one, with an opening in the middle
- ArchCurtainWall build panels based on the outermost one edges
- ArchCurtainWall build flights based on edges forming slab void

So you have just 1 simple ArchSketch, just like any architectural student start learning sketching building layout in school. Now, you can select the Edges in ArchSketch you want for your Wall, Slab, Curtain Wall or Stairs separately though on same ArchSketch; and you just edit the same ArchSketch,  and you have e.g. the shape / dimension of the slab and curtain wall changed at the same time. 

[FreeCAD Forum Discussion Thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=73018&sid=ba2732dd08a70b09011f667ae874e322)


(Click To PLAY VIDEO !)
[![ Youtube Video](https://i9.ytimg.com/vi/ozZ-jl-BSjU/mq2.jpg?sqp=CIS_opQG&rs=AOn4CLDlLCx-Car66Bfg-UvVre1gT-DE3A)](https://youtu.be/DjxBXsw6z2I "Click To PLAY VIDEO - ArchSketch + ArchStructure = Slab Layout !")

![alt text 3a](https://forum.freecadweb.org/download/file.php?id=205759)
![alt text 3a](https://forum.freecadweb.org/download/file.php?id=205758)
![alt text 3a](https://forum.freecadweb.org/download/file.php?id=205755)
![alt text 3a](https://forum.freecadweb.org/download/file.php?id=205754)


#### 5. Variant PropertySets : Variant Arch Layout / Objects
![alt text 5](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons//PropertySet.svg) 

- See YouTube Video and FreeCAD Forum Discussion at the moment - https://forum.freecad.org/viewtopic.php?p=784622#p784622
- (Click To PLAY VIDEO !)
[![Youtub Video](https://youtu.be/N3OAd1ykAag?si=phtlBXa9CzZ9CVPZ)](https://youtu.be/N3OAd1ykAag?si=phtlBXa9CzZ9CVPZ "Click To PLAY VIDEO !")
[![Youtub Video](https://i9.ytimg.com/vi/1rlPwVOXWKc/mq3.jpg?sqp=CNS1opQG&rs=AOn4CLBho4vSSl9OJ3Ce44ZdC-_zjwg10g)](https://youtu.be/_UERVIczKMY "Click To PLAY VIDEO !")
[![Youtub Video](https://youtu.be/pYUG3FHiyw0?si=0kNtpGtnEByD9vRt)](https://youtu.be/pYUG3FHiyw0?si=0kNtpGtnEByD9vRt "Click To PLAY VIDEO !")
[![Youtub Video](https://youtu.be/pIgYn1Pppmk?si=5bFSWOuIXXwTPjka)](https://youtu.be/pIgYn1Pppmk?si=5bFSWOuIXXwTPjka "Click To PLAY VIDEO !")
[![Youtub Video](https://youtu.be/FMuiW3wNG3o?si=t0ZCZyNqBF6syCKm)](https://youtu.be/FMuiW3wNG3o?si=t0ZCZyNqBF6syCKm "Click To PLAY VIDEO !")


#### 6. Floor Area Calculation + Room Dimension

- [Feature] Floor Area Calculation + Room Dimension ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=47905&start=70#p485618))
- See below on CellComplex

![alt text 3a](https://forum.freecadweb.org/download/file.php?style=10&id=150955)



#### 7. CellComplex Creation [Topologic]
![alt text 6](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/CellComplex.svg)

- CellComplex is a Topologic concept and object : see ([OSArch discussion - Talk on Topologic: Redefining BIM through Spatial Topology, Information, and Grammars](https://community.osarch.org/discussion/131/talk-on-topologic-redefining-bim-through-spatial-topology-information-and-grammars#latest))
- [Feature] CellComplex & ArchWall Creation on 1 ArchSketch ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=63920))
- In addition to build ArchWall based on an ArchSketch, CellComplex can be created automatically also

(Click To PLAY VIDEO !)
[![Youtub Video](https://i9.ytimg.com/vi/1rlPwVOXWKc/mq3.jpg?sqp=CNS1opQG&rs=AOn4CLBho4vSSl9OJ3Ce44ZdC-_zjwg10g)](https://youtu.be/1rlPwVOXWKc "Click To PLAY VIDEO !")

![alt text 3a](https://forum.freecadweb.org/download/file.php?id=170539)
![alt text 3a](https://forum.freecadweb.org/download/file.php?id=170540)
![alt text 3a](https://forum.freecadweb.org/download/file.php?id=170538)


#### 8. Topological Naming Tolerant

- Progress / Status of Implementation :
  
    1.  10.7.2021 Exposed - [Arch Object Intuitive Automatic Placement](https://forum.freecad.org/viewtopic.php?t=60034)
    2.  27.4.2024 Exposed - [Arch Wall Width Setting for Each Wall Segment](https://forum.freecad.org/viewtopic.php?p=755689#p755689)
    3.  27.4.2024 Exposed - [Arch Wall Align Setting for Each Wall Segment](https://forum.freecad.org/viewtopic.php?p=755689#p755689)
    4.  (Above 3 Features Implemented in 2019-21)
 
- The most important feature is to make referencing to a Sketch Edge persistent (not currently as of 0.19_pre, unless use @realthunder's branch),
  3 main approaches :

    1.  Using sketch.Geometry[index].Tag
        Using `sketch.Geometry[index].Tag` == Unique identification survive changes? ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=22&t=28575))
        <br>
        a. **Implemented** On-the-fly updating Index referencing `Sketch.Geometry[index].Tag` on `UpdateAttachmentOffset()` (**preferred approach**) [Need every object recompute() to keep in sync]
        <br>
        b.  Rebuilding a Dict referencing `Sketch.Geometry[index].Tag` `onDocumentRestore` (**Implemented but not exposed. Solution 1a is preferable**)
        <br>
        (As of Marh 2024, a mix use of 1a and 1b are used)
    2.  Using PartGeometryExtension / SketchGeometryExtension
        <br>
        **Being Implemented as of March 2024**
        - Part Geometry Extensions - Extension for 'Persistent UUID Tag'  ([forum thread](https://forum.freecadweb.org/viewtopic.php?style=10&f=10&t=33349&start=50#p374767))
        - Sketcher Development - Integration of Extensions  ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=10&t=51716#p444360))
    4.  Using @Realthunder's branch

- Earlier Discussions : Unique and Persistent Sketch Edge Name
  - Ability to (auto) give (unique) name each edges in a sketch which would not be repeated or reused  -  Sketcher: Virtual Space ([forum thread](https://forum.freecadweb.org/viewtopic.php?t=25904#p204581))
  - Tag consistent (for Sketch geometries)  - Civil engineering feature implementation (Transportation Engineering)  ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=8&t=22277&start=520#p280716))

(Click To PLAY VIDEO !)
[![ Youtube Video](https://i9.ytimg.com/vi/Sqt2rezgPZk/mq2.jpg?sqp=CIzNopQG&rs=AOn4CLC1cDMCGaulTNjBOEkRnu0fJNmyKw)](https://youtu.be/Sqt2rezgPZk "Click To PLAY VIDEO - 'TopoNaming Tolerant' Feature !")


#### 9. Voxelisation
![alt text 6](https://github.com/paullee0/FreeCAD_SketchArch/blob/master/icons/Voxel.svg)


- https://forum.freecadweb.org/viewtopic.php?f=23&t=61158&p=535506#p535506
- Current workflow for comment / suggestion: -

1. Select the shape object to 'voxelise', click Voxel button
2. Can select the shape of voxel, like (App::Link to) a Group w/ 4 Walls, Windows, Slab etc.
3. Has 3 modes :-
    - a. Center : If Center of (the BoundBox of) voxel is within the Input Shape, it is shown
    - b. Any Corner : If Any Corner of (the BoundBox of) voxel is within the Input Shape, it is shown
    - c. All Corners : Only if All Corners of (the BoundBox of) voxel are within the Input Shape, it is shown

What's created ?
1. Under the hood, pressing the button creates 2 objects
2. First is a 'VoxelPart' object with a propertyLink to an 'Input Shape Object'
3. Second is an App::Link which produce the Array of Voxels
    - The VoxelPart calculates the placement of every Voxels
    - It creates a Box, or copy the shape of 'VoxelObj' (usecase:  point to a object with Shape, or to a Link to a Group containing a numbers of objects)
    - The  2nd Object App::Link actually create the array of Voxels according to VoxelPart calculation

![alt text 6a](https://forum.freecadweb.org/download/file.php?id=165334)
![alt text 6b](https://forum.freecadweb.org/download/file.php?id=165337)


#### Features in Development, Other Remarks

<details>
  <summary>Click to expand!</summary>
  
#### 10. Space / Room / Zone & Cell Complex Definition

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


#### 11. More concepts of adopting ArchSketch as Building Layout Object

  - Different materials for wall surface on each sides
  - Different wall joint / junction geometrical shape
  - (good for IFCexport ?) Maybe Wall can support different Height for each segment? Similarly, this information be saved in the ArchSketch
  - (good for IFCexport ?) Different materials for different wall segment?

#### Prerequisites / Other Remarks

- The said information (width, align, height, material etc.) is conceived to be saved in ArchSketch with Part Geometry Extensions feature - the latter currently has a bug which crash FC
- Bugs / IFC export / multi-materials etc. to support Wall base on Sketch to be fixed / implemented

</details>


### III. Examples

Models
- Villa Savoye Discussion ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=23&t=41836)) ([downloadable model](https://github.com/paullee0/FreeCAD_Villa-Savoye))
- Carpenter Center Discussion ([forum thread](https://forum.freecadweb.org/viewtopic.php?f=24&t=44186&hilit=carpenter&start=10) ([downloadable model](https://github.com/paullee0/FreeCAD_Carpenter-Center)


### IV. Install

'Semi'- Automatic (recommended)

(From 1.0 Onward)
* Find the Edit menu, then Preference to call the dialog box
  * Go to Add-on Manager, find the Custom Repositories section
  * Press + to add the repository to the list - https://github.com/paullee0/FreeCAD_SketchArch
* Restart FreeCAD
* Locate the workbench dropdown list and switch to the 'SketchArch workbench'

(Before 1.0)
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
  - Auto-creating ArchSketch - ([forum thread](https://forum.freecad.org/viewtopic.php?t=71917))
  - Automatic Building Generator - ([forum thread](https://forum.freecad.org/viewtopic.php?t=81285))

When bugs/feature-requests are vetted on the forum they will then be tracked in the [issue queue](https://github.com/paullee0/FreeCAD_SketchArch/issues) of this repo.



### VI. About

Maintainer: paullee ([@paullee0](https://github.com/paullee0))
Repository: https://github.com/paullee0/FreeCAD_SketchArch



### VII. License

[LICENSE](LICENSE)


