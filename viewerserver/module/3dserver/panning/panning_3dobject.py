import vtk
from vtkmodules.vtkCommonCore import vtkCommand

class PanningInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self):
        self.isPanning = False

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
            self.Pan()
        else:
            self.OnMouseMove()

    def leftButtonReleaseEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        if self.isPanning:
            self.isPanning = False
        self.EndPan()
        self.OnLeftButtonUp()