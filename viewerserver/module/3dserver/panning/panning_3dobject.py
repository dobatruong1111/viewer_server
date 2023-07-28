import vtk
from vtkmodules.vtkCommonCore import vtkCommand

from measurement.utils import buildArcAngleMeasurement, buildTextActorLengthMeasurement

class PanningInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, afterInteractorStyle):
        self.isPanning = False
        self.afterInteractorStyle = afterInteractorStyle

        self.AddObserver(vtkCommand.MouseMoveEvent, self.mouseMoveEvent)
        self.AddObserver(vtkCommand.LeftButtonPressEvent, self.leftButtonPressEvent)
        self.AddObserver(vtkCommand.LeftButtonReleaseEvent, self.leftButtonReleaseEvent)

    def leftButtonPressEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        self.StartPan()
        if not self.isPanning:
            self.isPanning = True
        self.OnLeftButtonDown()

    def mouseMoveEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        if self.isPanning:
            renderer = self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()
            if self.afterInteractorStyle.getAngleMeasurementPipelines() or self.afterInteractorStyle.getLengthMeasurementPipelines():
                if self.afterInteractorStyle.getAngleMeasurementPipelines():
                    for pipeline in self.afterInteractorStyle.getAngleMeasurementPipelines():
                        points = pipeline.line.GetPoints()
                        buildArcAngleMeasurement(pipeline.arc, pipeline.textActor, renderer, points)
                if self.afterInteractorStyle.getLengthMeasurementPipelines():
                    for pipeline in self.afterInteractorStyle.getLengthMeasurementPipelines():
                        points = pipeline.line.GetPoints()
                        buildTextActorLengthMeasurement(pipeline.textActor, renderer, points)
                self.GetInteractor().Render()
            self.Pan()
        else:
            self.OnMouseMove()

    def leftButtonReleaseEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        if self.isPanning:
            self.isPanning = False
        self.EndPan()
        self.OnLeftButtonUp()