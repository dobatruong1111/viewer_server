from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

import vtk
from vtkmodules.vtkCommonCore import vtkCommand
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk

from model.colormap import CUSTOM_COLORMAP
from model.presets import *

from measurement.utils import AfterInteractorStyle
from measurement.length_measurement import LengthMeasurementPipeline, LengthMeasurementInteractorStyle
from measurement.angle_measurement import AngleMeasurementPipeline, AngleMeasurementInteractorStyle

from cropping.crop_freehand import Contour2DPipeline, CropFreehandInteractorStyle, Operation
from cropping.utils import IPWCallback

from panning.panning_3dobject import PanningInteractorStyle
from utils.utils import getInfoMemory

import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# -------------------------------------------------------------------------
# ViewManager
# -------------------------------------------------------------------------

class Dicom3D(vtk_protocols.vtkWebProtocol):
    def __init__(self):
        # Data
        self._dicomDataPath = None
    
        # Pipeline
        self.colors = vtk.vtkNamedColors()
        self.reader = vtk.vtkDICOMImageReader()
        # self.mask = vtk.vtkImageData()
        self.mask = None
        self.mapper = vtk.vtkSmartVolumeMapper()
        # self.mapper = vtk.vtkFixedPointVolumeRayCastMapper()
        self.volProperty = vtk.vtkVolumeProperty()
        self.volume = vtk.vtkVolume()
        
        # Transfer Function
        self.color = vtk.vtkColorTransferFunction()
        self.scalarOpacity = vtk.vtkPiecewiseFunction()

        # Background Dark/Light
        self.checkLight = False

        # Cropping By Box
        self.checkBox = False
        # self.boxRep = vtk.vtkBoxRepresentation()
        # self.widget = vtk.vtkBoxWidget2()
        # self.planes = vtk.vtkPlanes()
        self.boxRep = None
        self.widget = None
        self.planes = None

        # Measurement
        # self.cellPicker = vtk.vtkCellPicker()
        # self.afterInteractorStyle = AfterInteractorStyle()
        self.cellPicker = None
        self.afterInteractorStyle = None

        # Camera
        # self.focalPoint = None
        # self.oriPositionOfCamera = None
        # self.viewUp = None

        # Panning
        self.checkPanning = False

        # Crop Freehand
        self.contour2Dpipeline = None
        self.cropFreehandInteractorStyle = None

    @property
    def dicomDataPath(self):
        return self._dicomDataPath
    
    @dicomDataPath.setter
    def dicomDataPath(self, path):
        self._dicomDataPath = path

    def colorMappingWithStandardCT(self) -> None:
        self.color.RemoveAllPoints()
        rgbPoints = CUSTOM_COLORMAP.get("STANDARD_CT").get("rgbPoints")
        for point in rgbPoints:
            self.color.AddRGBPoint(point[0], point[1], point[2], point[3])
        self.volProperty.SetColor(self.color)
    
    def setDefaultPreset(self) -> None:
        # Bone Preset
        self.colorMappingWithStandardCT()

        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = BONE_CT.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)

    def resetBox(self) -> None:
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")

        # Set clipping planes outside 3D object
        planes = vtk.vtkPlanes()
        self.mapper.SetClippingPlanes(planes)

        if self.boxRep is None:
            self.boxRep = vtk.vtkBoxRepresentation()
            self.boxRep.GetOutlineProperty().SetColor(1, 1, 1)
            self.boxRep.SetInsideOut(True)

        if self.widget is None:
            self.widget = vtk.vtkBoxWidget2()
            self.widget.SetRepresentation(self.boxRep)
            self.widget.SetInteractor(renderWindowInteractor)
            self.widget.GetRepresentation().SetPlaceFactor(1)
            self.widget.GetRepresentation().PlaceWidget(self.imageData.GetBounds())
            self.widget.SetEnabled(True)

        if self.planes is None:
            self.planes = vtk.vtkPlanes()
            ipwcallback = IPWCallback(self.planes, self.mapper)
            self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, ipwcallback)
            self.widget.Off()

        # Set origin bounds of box
        self.widget.GetRepresentation().PlaceWidget(self.imageData.GetBounds())

        # Turn off box
        if self.checkBox:
            self.widget.Off()
            self.checkBox = False

    @exportRpc("vtk.initialize")
    def createVisualization(self) -> None:
        # 4121 MB

        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        path = self.dicomDataPath if self.dicomDataPath is not None else "./viewerserver/module/3dserver/data/Ankle"

        # Reader
        self.reader.SetDirectoryName(path)
        self.reader.Update()

        # 4662 MB

        # self.imageData = self.reader.GetOutput() # vtkImageData
        self.imageData = vtk.vtkImageData()
        self.imageData.DeepCopy(self.reader.GetOutput())

        # 5201 MB

        # Mapper
        self.mapper.SetInputData(self.imageData)

        # 5201 MB

        # Volume Property
        self.volProperty.ShadeOn()
        self.volProperty.SetScalarOpacityUnitDistance(0.1)
        self.volProperty.SetInterpolationTypeToLinear() # default: Nearest Neighbor
        # Light
        self.volProperty.SetAmbient(0.1)
        self.volProperty.SetDiffuse(0.9)
        self.volProperty.SetSpecular(0.2)

        # 5201 MB

        # Color Mapping
        self.colorMappingWithStandardCT()

        # 5201 MB

        # Bone CT: Opacity Mapping
        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = BONE_CT.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)

        self.volProperty.SetScalarOpacity(self.scalarOpacity)

        # 5201 MB

        # Volume
        self.volume.SetMapper(self.mapper)
        self.volume.SetProperty(self.volProperty)

        # 5202 MB

        # Render
        renderer.AddVolume(self.volume)
        renderer.ResetCamera()

        # Render Window
        renderWindow.Render()

        # 5806 MB

    @exportRpc("vtk.dicom3d.light")
    def light(self) -> None:
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        if self.boxRep is None:
            self.boxRep = vtk.vtkBoxRepresentation()
            self.boxRep.GetOutlineProperty().SetColor(1, 1, 1)
            self.boxRep.SetInsideOut(True)

        if not self.checkLight:
            renderer.SetBackground(self.colors.GetColor3d("White"))
            self.boxRep.GetOutlineProperty().SetColor(0, 0, 0)
            self.checkLight = True
        else:
            renderer.SetBackground(self.colors.GetColor3d("Black"))
            self.boxRep.GetOutlineProperty().SetColor(1, 1, 1)
            self.checkLight = False

        renderWindow.Render()
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)
        
    @exportRpc("vtk.dicom3d.presets.bone.ct")
    def showBoneCT(self) -> None:
        renderWindow = self.getView('-1')
        self.colorMappingWithStandardCT()

        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = BONE_CT.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)

        renderWindow.Render()
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)
      
    @exportRpc("vtk.dicom3d.presets.angio.ct")
    def showAngioCT(self) -> None:
        renderWindow = self.getView('-1')
        self.colorMappingWithStandardCT()

        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = ANGIO_CT.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)

        renderWindow.Render()
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    @exportRpc("vtk.dicom3d.presets.muscle.ct")
    def showMuscleCT(self) -> None:
        renderWindow = self.getView('-1')
        self.colorMappingWithStandardCT()

        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = MUSCLE_CT.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)

        renderWindow.Render()
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    @exportRpc("vtk.dicom3d.presets.mip")
    def showMip(self) -> None:
        renderWindow = self.getView('-1')

        self.color.RemoveAllPoints()
        rgbPoints = MIP.get("colorMap").get("rgbPoints")
        if len(rgbPoints):
            for point in rgbPoints:
                self.color.AddRGBPoint(point[0], point[1], point[2], point[3])

        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = MIP.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)

        renderWindow.Render()
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    def initObjectsMeasurementTool(self, renderWindowInteractor: vtk.vtkRenderWindowInteractor) -> None:
        if self.afterInteractorStyle is None:
            self.afterInteractorStyle = AfterInteractorStyle()

        if self.cellPicker is None:
            self.cellPicker = vtk.vtkCellPicker()
            self.cellPicker.AddPickList(self.volume)
            self.cellPicker.PickFromListOn()
            renderWindowInteractor.SetPicker(self.cellPicker)

    @exportRpc("vtk.dicom3d.length.measurement")
    def lengthMeasurementHandle(self) -> None:
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        self.initObjectsMeasurementTool(renderWindowInteractor)

        pipeline = LengthMeasurementPipeline()
        # renderer.AddActor(pipeline.firstSphereActor)
        # renderer.AddActor(pipeline.secondSphereActor)
        renderer.AddActor(pipeline.lineActor)
        renderer.AddActor(pipeline.textActor)

        style = LengthMeasurementInteractorStyle(pipeline, self.afterInteractorStyle)
        renderWindowInteractor.SetInteractorStyle(style)

        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    @exportRpc("vtk.dicom3d.angle.measurement")
    def angleMeasurementHandle(self) -> None:
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        self.initObjectsMeasurementTool(renderWindowInteractor)

        pipeline = AngleMeasurementPipeline()
        # renderer.AddActor(pipeline.firstSphereActor)
        # renderer.AddActor(pipeline.secondSphereActor)
        # renderer.AddActor(pipeline.thirdSphereActor)
        renderer.AddActor(pipeline.firstLineActor)
        renderer.AddActor(pipeline.secondLineActor)
        renderer.AddActor(pipeline.arcActor)
        renderer.AddActor(pipeline.textActor)
        renderer.AddActor(pipeline.markText)

        style = AngleMeasurementInteractorStyle(pipeline, self.afterInteractorStyle)
        renderWindowInteractor.SetInteractorStyle(style)

        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    @exportRpc("vtk.dicom3d.crop")
    def crop3d(self) -> None:
        # self.getApplication() -> vtkWebApplication()
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')

        if self.boxRep is None:
            self.boxRep = vtk.vtkBoxRepresentation()
            self.boxRep.GetOutlineProperty().SetColor(1, 1, 1)
            self.boxRep.SetInsideOut(True)

        if self.widget is None:
            self.widget = vtk.vtkBoxWidget2()
            self.widget.SetRepresentation(self.boxRep)
            self.widget.SetInteractor(renderWindowInteractor)
            self.widget.GetRepresentation().SetPlaceFactor(1)
            self.widget.GetRepresentation().PlaceWidget(self.imageData.GetBounds())
            self.widget.SetEnabled(True)

        if self.planes is None:
            self.planes = vtk.vtkPlanes()
            ipwcallback = IPWCallback(self.planes, self.mapper)
            self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, ipwcallback)
            self.widget.Off()

        if not self.checkBox:
            self.widget.On()
            self.checkBox = True
        else:
            self.widget.Off()
            self.checkBox = False

        renderWindow.Render()
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    @exportRpc("vtk.dicom3d.crop.freehand")
    def cropFreehandHandle(self, operation: Operation = Operation.INSIDE, fillValue: int = -1000) -> None:
        # 5788 MB

        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderer = self.getView('-1').GetRenderers().GetFirstRenderer()

        if self.contour2Dpipeline is None:
            self.contour2Dpipeline = Contour2DPipeline()

        # 5788 MB

        if self.mask is None:
            self.mask = vtk.vtkImageData()
            self.mask.SetExtent(self.imageData.GetExtent())
            self.mask.SetOrigin(self.imageData.GetOrigin())
            self.mask.SetSpacing(self.imageData.GetSpacing())
            self.mask.SetDirectionMatrix(self.imageData.GetDirectionMatrix())
            # self.mask.AllocateScalars(self.imageData.GetScalarType(), 1)
            self.mask.AllocateScalars(vtk.VTK_UNSIGNED_CHAR, 1)
            self.mask.GetPointData().GetScalars().Fill(0)

        # 6058 MB

        if self.afterInteractorStyle is None:
            self.afterInteractorStyle = AfterInteractorStyle()

        # 6058 MB

        if self.cropFreehandInteractorStyle is None:
            self.cropFreehandInteractorStyle = CropFreehandInteractorStyle(
                contour2Dpipeline=self.contour2Dpipeline,
                imageData=self.imageData,
                mask=self.mask,
                operation=Operation.INSIDE,
                fillValue=-1000,
                afterInteractorStyle=self.afterInteractorStyle
            )

        # 6058 MB

        renderer.AddActor(self.contour2Dpipeline.actor)
        renderer.AddActor(self.contour2Dpipeline.actorThin)

        self.cropFreehandInteractorStyle.setOperation(operation)
        self.cropFreehandInteractorStyle.setFillValue(fillValue)

        renderWindowInteractor.SetInteractorStyle(self.cropFreehandInteractorStyle)
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

        # 6058 MB

    @exportRpc("vtk.camera.reset")
    def resetHandle(self) -> None:
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        if not self.mask is None:
            shape = tuple(reversed(self.reader.GetOutput().GetDimensions())) # (z, y, x)
            oriImageDataArray = vtk_to_numpy(self.reader.GetOutput().GetPointData().GetScalars()).reshape(shape)
            maskArray = vtk_to_numpy(self.mask.GetPointData().GetScalars()).reshape(shape)
            imageDataArray = vtk_to_numpy(self.imageData.GetPointData().GetScalars()).reshape(shape)

            imageDataArray[maskArray > 0] = oriImageDataArray[maskArray > 0]

            self.imageData.GetPointData().SetScalars(numpy_to_vtk(imageDataArray.reshape(1, -1)[0]))
            self.mask.GetPointData().GetScalars().Fill(0)

        # Set origin 3D object
        # self.mapper.SetInputData(self.imageData)

        # Set origin box status
        self.resetBox()

        # Set default bone preset
        # self.setDefaultPreset()

        # Remove actors
        renderer.RemoveAllViewProps()
        renderer.AddVolume(self.volume)

        # Render window
        renderWindow.Render()

        # Turn off panning interactor
        self.checkPanning = False

        # Set default interactor style
        style = vtk.vtkInteractorStyleTrackballCamera()
        renderWindowInteractor.SetInteractorStyle(style)
        
        self.getApplication().InvalidateCache(renderWindow)
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)
    
    @exportRpc("vtk.dicom3d.panning")
    def panning(self) -> None:
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")

        if self.afterInteractorStyle is None:
            self.afterInteractorStyle = AfterInteractorStyle()

        if not self.checkPanning:
            self.checkPanning = True
            style = PanningInteractorStyle(self.afterInteractorStyle)
        else:
            self.checkPanning = False
            style = self.afterInteractorStyle

        renderWindowInteractor.SetInteractorStyle(style)

        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    def onClose(self, client_id) -> None:
        # print("close...!")
        logging.info("Server is closing...")
