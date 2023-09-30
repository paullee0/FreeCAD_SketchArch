import ArchSketchObject, Draft, Arch, time
s = Gui.Selection.getSelection()[0]
archSk = ArchSketchObject.makeArchSketch(label="ArchSketch__Layout")
archSk.recompute()
archSk.Placement=s.Placement
archSk.Geometry=s.Geometry
archSk.Constraints=s.Constraints
archSk.recompute()
w=s.InList[0]
w.Base=archSk
