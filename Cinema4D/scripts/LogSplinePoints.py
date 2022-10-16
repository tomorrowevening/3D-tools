import c4d
import json
import subprocess


def copy2clip(txt):
    cmd = 'echo '+txt.strip()+'|pbcopy'
    return subprocess.check_call(cmd, shell=True)


# The active document
doc: c4d.documents.BaseDocument
# The active object
op: c4d.BaseObject


class ScaleDialog(c4d.gui.GeDialog):
    ID_EDIT_NUMBER = 10000
    ID_EDIT_BOOL = 10001

    def __init__(self):
        self.defaultValue = 1.0
        self.defaultWorld = True
        self.value = None
        self.world = None
        self.userCancel = False

    def AskClose(self):
        if self.value is None and not self.userCancel:
            return True
        return False

    def CreateLayout(self):
        self.SetTitle("Log Vertices")

        if self.GroupBegin(0, c4d.BFH_SCALEFIT | c4d.BFV_SCALEFIT, cols=2):
            self.AddStaticText(0, c4d.BFH_LEFT, name="Scale:")
            self.AddEditSlider(self.ID_EDIT_NUMBER, c4d.BFH_SCALEFIT)
        self.GroupEnd()

        self.AddCheckbox(self.ID_EDIT_BOOL, c4d.BFV_CENTER,
                         200, 20, "World Coordinates")

        self.AddDlgGroup(c4d.DLG_OK | c4d.DLG_CANCEL)

        return True

    def InitValues(self):
        self.SetFloat(self.ID_EDIT_NUMBER, float(
            self.defaultValue), min=0.0, max=1000.0)
        self.SetBool(self.ID_EDIT_BOOL, bool(self.defaultWorld))
        return True

    def Command(self, id, msg):
        if id == self.ID_EDIT_NUMBER and msg[c4d.BFM_ACTION_RESET]:
          self.SetFloat(self.ID_EDIT_NUMBER, self.defaultValue)
          self.SetBool(self.ID_EDIT_BOOL, self.defaultWorld)

        if id == c4d.DLG_OK:
            self.value = self.GetFloat(self.ID_EDIT_NUMBER)
            self.world = self.GetBool(self.ID_EDIT_BOOL)
            self.userCancel = False
            self.Close()

        elif id == c4d.DLG_CANCEL:
            self.value = None
            self.world = None
            self.userCancel = True
            self.Close()

        return True


def main():
    if isinstance(op, c4d.PointObject):
        dlg = ScaleDialog()

        dlg.Open(c4d.DLG_TYPE_MODAL)

        if dlg.userCancel:
            return

        points = op.GetAllPoints()
        offset = op.GetAbsPos()
        if dlg.world == False:
            offset.x = 0.0
            offset.y = 0.0
            offset.z = 0.0

        scale = dlg.value
        print("Point array for spline: " + op.GetName())
        absPts = []
        for pt in points:
            x = float(f'{(pt.x+offset.x)*scale:.3f}')
            y = float(f'{(pt.y+offset.y)*scale:.3f}')
            z = float(f'{(pt.z+offset.z)*scale:.3f}')
            absPts.append([x, y, z])
        data = json.dumps({
            'name': op.GetName(),
            'points': absPts,
            'tension': 0.5,
            'closed': op.IsClosed(),
            'subdivide': 50,
            'type': 'catmullrom'
        }, sort_keys=False, indent=2)
        print(data)

        dataStr = json.dumps(data)
        copy2clip(dataStr)
        c4d.gui.MessageDialog("Spline JSON copied!")
    else:
        c4d.gui.MessageDialog("Please select a Spline")


if __name__ == "__main__":
    main()
