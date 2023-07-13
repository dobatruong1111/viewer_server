from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

import vtk
from model.colormap import CUSTOM_COLORMAP
from model.presets import *

# -------------------------------------------------------------------------
# ViewManager
# -------------------------------------------------------------------------

class Dicom3D(vtk_protocols.vtkWebProtocol):
    def __init__(self):
        self._dicomDataPath = None
        self.colors = vtk.vtkNamedColors()

        # Pipeline
        self.reader = vtk.vtkDICOMImageReader()
        self.modifierLabelmap = vtk.vtkImageData()
        self.mapper = vtk.vtkSmartVolumeMapper()
        self.volProperty = vtk.vtkVolumeProperty()
        self.volume = vtk.vtkVolume()
        self.color = vtk.vtkColorTransferFunction()
        self.scalarOpacity = vtk.vtkPiecewiseFunction()

        self.checkLight = True
        self.cellPicker = vtk.vtkCellPicker()

    @property
    def dicomDataPath(self):
        return self._dicomDataPath
    
    @dicomDataPath.setter
    def dicomDataPath(self, path):
        self._dicomDataPath = path

    @exportRpc("vtk.initialize")
    def createVisualization(self):
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        path = self.dataPath if self.dicomDataPath is not None else "./data/Ankle"

        # Reader
        self.reader.SetDirectoryName(path)
        self.reader.Update()

        self.imageData = self.reader.GetOutput() # vtkImageData
        self.modifierLabelmap.SetExtent(self.imageData.GetExtent())
        self.modifierLabelmap.SetOrigin(self.imageData.GetOrigin())
        self.modifierLabelmap.SetSpacing(self.imageData.GetSpacing())
        self.modifierLabelmap.SetDirectionMatrix(self.imageData.GetDirectionMatrix())
        self.modifierLabelmap.AllocateScalars(self.imageData.GetScalarType(), 1)
        self.modifierLabelmap.GetPointData().GetScalars().Fill(0)

        # Mapper
        self.mapper.SetInputData(self.reader.GetOutput())

        # Volume Property
        self.volProperty.ShadeOn()
        self.volProperty.SetAmbient(0.1)
        self.volProperty.SetDiffuse(0.9)
        self.volProperty.SetSpecular(0.2)

        self.color.RemoveAllPoints()
        rgbPoints = CUSTOM_COLORMAP.get("STANDARD_CT").get("rgbPoints")
        for point in rgbPoints:
            self.color.AddRGBPoint(point[0], point[1], point[2], point[3])
        self.volProperty.SetColor(self.color)

        # Muscle CT
        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = MUSCLE_CT.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)
        self.volProperty.SetScalarOpacity(self.scalarOpacity)

        # Volume
        self.volume.SetMapper(self.mapper)
        self.volume.SetProperty(self.volProperty)

        # Cropping By Box
        self.boxRep.GetOutlineProperty().SetColor(0, 0, 0)
        self.boxRep.SetInsideOut(True)

        self.widget.SetRepresentation(self.boxRep)
        self.widget.SetInteractor(renderWindowInteractor)
        self.widget.GetRepresentation().SetPlaceFactor(1)
        self.widget.GetRepresentation().PlaceWidget(self.reader.GetOutput().GetBounds())
        self.widget.SetEnabled(True)

        ipwcallback = IPWCallback(self.planes, self.mapper)
        self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, ipwcallback)
        self.widget.Off()

        # Cropping Freehand
        self.cellPicker.AddPickList(self.volume)
        self.cellPicker.PickFromListOn()

        # Render
        renderer.AddVolume(self.volume)
        renderer.ResetCamera()

        # Render Window
        renderWindow.Render()

        # Render Window Interactor
        renderWindowInteractor.SetPicker(self.cellPicker)

        return self.resetCamera()

    @exportRpc("vtk.camera.reset")
    def resetCamera(self):
        renderWindow = self.getView('-1')

        renderWindow.GetRenderers().GetFirstRenderer().ResetCamera()
        renderWindow.Render()

        self.getApplication().InvalidateCache(renderWindow)
        self.getApplication().InvokeEvent('UpdateEvent')

        return -1

    @exportRpc("viewport.mouse.zoom.wheel")
    def updateZoomFromWheel(self, event):
        if 'Start' in event["type"]:
            self.getApplication().InvokeEvent('StartInteractionEvent')

        renderWindow = self.getView(event['view'])
        if renderWindow and 'spinY' in event:
            zoomFactor = 1.0 - event['spinY'] / 10.0

            camera = renderWindow.GetRenderers().GetFirstRenderer().GetActiveCamera()
            fp = camera.GetFocalPoint()
            pos = camera.GetPosition()
            delta = [fp[i] - pos[i] for i in range(3)]
            camera.Zoom(zoomFactor)

            pos2 = camera.GetPosition()
            camera.SetFocalPoint([pos2[i] + delta[i] for i in range(3)])
            renderWindow.Modified()

        if 'End' in event["type"]:
            self.getApplication().InvokeEvent('EndInteractionEvent')

    @exportRpc("vtk.dicom3d.light")
    def light(self):
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        if self.checkLight:
            renderer.SetBackground(self.colors.GetColor3d("Black"))
            self.boxRep.GetOutlineProperty().SetColor(1, 1, 1)
            self.checkLight = False
        else:
            renderer.SetBackground(self.colors.GetColor3d("White"))
            self.boxRep.GetOutlineProperty().SetColor(0, 0, 0)
            self.checkLight = True

        renderWindow.Render()
        self.getApplication().InvokeEvent('UpdateEvent')

class IPWCallback():
    def __init__(self, planes: vtk.vtkPlanes, mapper: vtk.vtkSmartVolumeMapper):
        self.planes = planes
        self.mapper = mapper

    def __call__(self, obj: vtk.vtkBoxWidget2, event: str) -> None:
        obj.GetRepresentation().GetPlanes(self.planes)
        self.mapper.SetClippingPlanes(self.planes)