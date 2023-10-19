from vtk.web import protocols as vtk_protocols
from wslink import register as exportRpc

import vtk
from vtkmodules.vtkCommonCore import vtkCommand

from model.colormap import CUSTOM_COLORMAP
from model.presets import *

from measurement.utils import AfterInteractorStyle
from measurement.length_measurement import LengthMeasurementPipeline, LengthMeasurementInteractorStyle
from measurement.angle_measurement import AngleMeasurementPipeline, AngleMeasurementInteractorStyle

from cropping.crop_freehand import Contour2DPipeline, CropFreehandInteractorStyle, Operation
from cropping.utils import IPWCallback

from panning.panning_3dobject import PanningInteractorStyle
from utils.utils import getInfoMemory

import time, logging, os

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
        # self.modifierLabelmap = vtk.vtkImageData()
        self.modifierLabelmap = None
        # self.mapper = vtk.vtkSmartVolumeMapper()
        self.mapper = vtk.vtkFixedPointVolumeRayCastMapper()
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
        if getInfoMemory() is not None:
            total_memory, used_memory, free_memory = getInfoMemory()
            logging.info("Total Memory: " + str(total_memory) + "MB" + " - Used Memory: " + str(used_memory) + "MB" + r" - RAM Memory % Used: " + str(round((used_memory/total_memory) * 100, 2)))

        # renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        path = self.dicomDataPath if self.dicomDataPath is not None else "./viewerserver/module/3dserver/data/Ankle"

        # Reader
        self.reader.SetDirectoryName(path)
        self.reader.Update()

        self.imageData = self.reader.GetOutput() # vtkImageData
        # self.modifierLabelmap.SetExtent(self.imageData.GetExtent())
        # self.modifierLabelmap.SetOrigin(self.imageData.GetOrigin())
        # self.modifierLabelmap.SetSpacing(self.imageData.GetSpacing())
        # self.modifierLabelmap.SetDirectionMatrix(self.imageData.GetDirectionMatrix())
        # self.modifierLabelmap.AllocateScalars(self.imageData.GetScalarType(), 1)
        # self.modifierLabelmap.GetPointData().GetScalars().Fill(0)

        # Mapper
        self.mapper.SetInputData(self.imageData)

        # Volume Property
        self.volProperty.ShadeOn()
        # Light
        self.volProperty.SetAmbient(0.1)
        self.volProperty.SetDiffuse(0.9)
        self.volProperty.SetSpecular(0.2)

        # Color Mapping
        self.colorMappingWithStandardCT()

        # Bone CT: Opacity Mapping
        self.scalarOpacity.RemoveAllPoints()
        scalarOpacityRange = BONE_CT.get("transferFunction").get("scalarOpacityRange")
        self.scalarOpacity.AddPoint(scalarOpacityRange[0], 0)
        self.scalarOpacity.AddPoint(scalarOpacityRange[1], 1)

        self.volProperty.SetScalarOpacity(self.scalarOpacity)

        # Volume
        self.volume.SetMapper(self.mapper)
        self.volume.SetProperty(self.volProperty)

        # Cropping By Box
        # self.boxRep.GetOutlineProperty().SetColor(1, 1, 1)
        # self.boxRep.SetInsideOut(True)

        # self.widget.SetRepresentation(self.boxRep)
        # self.widget.SetInteractor(renderWindowInteractor)
        # self.widget.GetRepresentation().SetPlaceFactor(1)
        # self.widget.GetRepresentation().PlaceWidget(self.reader.GetOutput().GetBounds())
        # self.widget.SetEnabled(True)

        # ipwcallback = IPWCallback(self.planes, self.mapper)
        # self.widget.AddObserver(vtk.vtkCommand.InteractionEvent, ipwcallback)
        # self.widget.Off()

        # Measurement
        # self.cellPicker.AddPickList(self.volume)
        # self.cellPicker.PickFromListOn()

        # Cropping Freehand
        # self.contour2Dpipeline = Contour2DPipeline()
        # self.cropFreehandInteractorStyle = CropFreehandInteractorStyle(
        #     contour2Dpipeline=self.contour2Dpipeline,
        #     imageData=self.imageData,
        #     modifierLabelmap=self.modifierLabelmap,
        #     operation=Operation.INSIDE,
        #     fillValue=-1000,
        #     mapper=self.mapper,
        #     afterInteractorStyle=self.afterInteractorStyle
        # )

        # Render
        renderer.AddVolume(self.volume)
        renderer.ResetCamera()

        # Render Window
        renderWindow.Render()

        # Get original properties of camera
        # self.focalPoint = renderer.GetActiveCamera().GetFocalPoint()
        # self.oriPositionOfCamera = renderer.GetActiveCamera().GetPosition()
        # self.viewUp = renderer.GetActiveCamera().GetViewUp()

        # Render Window Interactor
        # renderWindowInteractor.SetPicker(self.cellPicker)

        if getInfoMemory() is not None:
            total_memory2, used_memory2, free_memory2 = getInfoMemory()
            logging.info("Total Memory: " + str(total_memory2) + "MB" + " - Used Memory: " + str(used_memory2) + "MB" + r" - RAM Memory % Used: " + str(round((used_memory2/total_memory2) * 100, 2)))
            logging.info("Initialize 3D Object Function" + " - Used Memory: " + str(used_memory2 - used_memory) + "MB" + r" - RAM Memory % Used: " + str(round(((used_memory2/total_memory2) * 100) - ((used_memory/total_memory) * 100), 2)))

        # return self.resetCamera()

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
    def length_measurement_handle(self) -> None:
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
    def angle_measurement_handle(self) -> None:
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
    def crop_freehand_handle(self, operation: Operation = Operation.INSIDE, fillValue: int = -1000) -> None:
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        if self.contour2Dpipeline is None:
            self.contour2Dpipeline = Contour2DPipeline()

        if self.modifierLabelmap is None:
            self.modifierLabelmap = vtk.vtkImageData()
            self.modifierLabelmap.SetExtent(self.imageData.GetExtent())
            self.modifierLabelmap.SetOrigin(self.imageData.GetOrigin())
            self.modifierLabelmap.SetSpacing(self.imageData.GetSpacing())
            self.modifierLabelmap.SetDirectionMatrix(self.imageData.GetDirectionMatrix())
            self.modifierLabelmap.AllocateScalars(self.imageData.GetScalarType(), 1)
            self.modifierLabelmap.GetPointData().GetScalars().Fill(0)

        if self.afterInteractorStyle is None:
            self.afterInteractorStyle = AfterInteractorStyle()

        if self.cropFreehandInteractorStyle is None:
            self.cropFreehandInteractorStyle = CropFreehandInteractorStyle(
                contour2Dpipeline=self.contour2Dpipeline,
                imageData=self.imageData,
                modifierLabelmap=self.modifierLabelmap,
                operation=Operation.INSIDE,
                fillValue=-1000,
                mapper=self.mapper,
                afterInteractorStyle=self.afterInteractorStyle
            )

        renderer.AddActor(self.contour2Dpipeline.actor)
        renderer.AddActor(self.contour2Dpipeline.actorThin)

        self.cropFreehandInteractorStyle.setOperation(operation)
        self.cropFreehandInteractorStyle.setFillValue(fillValue)

        renderWindowInteractor.SetInteractorStyle(self.cropFreehandInteractorStyle)
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)

    @exportRpc("vtk.camera.reset")
    def resetCamera(self) -> None:
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        # Set origin mask volume
        if self.modifierLabelmap is None:
            self.modifierLabelmap = vtk.vtkImageData()
            self.modifierLabelmap.SetExtent(self.imageData.GetExtent())
            self.modifierLabelmap.SetOrigin(self.imageData.GetOrigin())
            self.modifierLabelmap.SetSpacing(self.imageData.GetSpacing())
            self.modifierLabelmap.SetDirectionMatrix(self.imageData.GetDirectionMatrix())
            self.modifierLabelmap.AllocateScalars(self.imageData.GetScalarType(), 1)
        self.modifierLabelmap.GetPointData().GetScalars().Fill(0)

        # Set origin 3D object
        self.mapper.SetInputData(self.imageData)

        # Set origin box status
        self.resetBox()

        # Set default bone preset
        # self.setDefaultPreset()

        # Remove actors
        renderer.RemoveAllViewProps()
        renderer.AddVolume(self.volume)

        # Set original the camera status
        # renderer.GetActiveCamera().SetFocalPoint(self.focalPoint)
        # renderer.GetActiveCamera().SetPosition(self.oriPositionOfCamera)
        # renderer.GetActiveCamera().SetViewUp(self.viewUp)
        # renderer.ResetCamera()

        # Render window
        renderWindow.Render()

        # Turn off panning interactor
        self.checkPanning = False

        # Set default interactor style
        style = vtk.vtkInteractorStyleTrackballCamera()
        renderWindowInteractor.SetInteractorStyle(style)
        
        self.getApplication().InvalidateCache(renderWindow)
        self.getApplication().InvokeEvent(vtkCommand.UpdateEvent)
        return -1
    
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
