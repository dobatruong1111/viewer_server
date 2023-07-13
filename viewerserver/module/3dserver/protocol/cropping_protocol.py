from wslink import register as exportRpc
import vtk

from protocol.vtk_protocol import Dicom3D
from model.presets import *

class Cropping3D(Dicom3D):
    def __init__(self):
        super().__init__()
        self.checkBox = True
        self.boxRep = vtk.vtkBoxRepresentation()
        self.widget = vtk.vtkBoxWidget2()
        self.planes = vtk.vtkPlanes()

    @exportRpc("vtk.dicom3d.crop")
    def crop3d(self):
        # self.getApplication() -> vtkWebApplication()
        renderWindow = self.getView('-1')

        if self.checkBox:
            self.widget.On()
            self.checkBox = False
        else:
            self.widget.Off()
            self.checkBox = True

        renderWindow.Render()
        self.getApplication().InvokeEvent('UpdateEvent')