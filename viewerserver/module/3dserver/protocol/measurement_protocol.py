from wslink import register as exportRpc
import vtk

from protocol.vtk_protocol import Dicom3D
from model.presets import *

from measurement.length_measurement import LengthMeasurementPipeline, LengthMeasurementInteractorStyle
from measurement.angle_measurement import AngleMeasurementPipeline, AngleMeasurementInteractorStyle
from measurement.utils import AfterMeasurementInteractorStyle

class Measurement3D(Dicom3D):
    def __init__(self):
        super().__init__()

        self.afterMeasurementInteractorStyle = AfterMeasurementInteractorStyle()

    @exportRpc("vtk.dicom3d.length.measurement")
    def length_measurement_handle(self):
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        pipeline = LengthMeasurementPipeline()
        renderer.AddActor(pipeline.firstSphereActor)
        renderer.AddActor(pipeline.secondSphereActor)
        renderer.AddActor(pipeline.lineActor)
        renderer.AddActor(pipeline.textActor)

        style = LengthMeasurementInteractorStyle(pipeline, self.afterMeasurementInteractorStyle)
        renderWindowInteractor.SetInteractorStyle(style)

        self.getApplication().InvokeEvent('UpdateEvent')

    @exportRpc("vtk.dicom3d.angle.measurement")
    def angle_measurement_handle(self):
        renderWindowInteractor = self.getApplication().GetObjectIdMap().GetActiveObject("INTERACTOR")
        renderWindow = self.getView('-1')
        renderer = renderWindow.GetRenderers().GetFirstRenderer()

        pipeline = AngleMeasurementPipeline()
        renderer.AddActor(pipeline.firstSphereActor)
        renderer.AddActor(pipeline.secondSphereActor)
        renderer.AddActor(pipeline.thirdSphereActor)
        renderer.AddActor(pipeline.firstLineActor)
        renderer.AddActor(pipeline.secondLineActor)
        renderer.AddActor(pipeline.arcActor)
        renderer.AddActor(pipeline.textActor)

        style = AngleMeasurementInteractorStyle(pipeline, self.afterMeasurementInteractorStyle)
        renderWindowInteractor.SetInteractorStyle(style)

        self.getApplication().InvokeEvent('UpdateEvent')