from typing import List
import vtk
from measurement import utils

"""
    Description: class contains objects for angle measurement in the world coordinate system.
"""
class AngleMeasurementPipeline():
    def __init__(self) -> None:
        colors = vtk.vtkNamedColors()
        self.isDragging = False

        # Line
        self.line = vtk.vtkPolyData()

        # Arc
        self.arc = vtk.vtkArcSource()
        self.arc.SetResolution(30)

        # Sphere
        # self.sphere = vtk.vtkSphereSource()
        # self.sphere.SetRadius(5)

        # Filter
        # vtkTubeFilter is a filter that generates a tube around each input line
        self.tubeFilter = vtk.vtkTubeFilter()
        self.tubeFilter.SetInputData(self.line)
        self.tubeFilter.SetNumberOfSides(20)
        self.tubeFilter.SetRadius(1)

        self.arcTubeFilter = vtk.vtkTubeFilter()
        self.arcTubeFilter.SetInputConnection(self.arc.GetOutputPort())
        self.arcTubeFilter.SetNumberOfSides(20)
        self.arcTubeFilter.SetRadius(1)

        # Mappers
        self.firstLineMapper = vtk.vtkPolyDataMapper()
        self.firstLineMapper.SetInputConnection(self.tubeFilter.GetOutputPort())

        self.secondLineMapper = vtk.vtkPolyDataMapper()
        self.secondLineMapper.SetInputConnection(self.tubeFilter.GetOutputPort())

        self.arcMapper = vtk.vtkPolyDataMapper()
        self.arcMapper.SetInputConnection(self.arcTubeFilter.GetOutputPort())

        # self.firstSphereMapper = vtk.vtkPolyDataMapper()
        # self.firstSphereMapper.SetInputConnection(self.sphere.GetOutputPort())

        # self.secondSphereMapper = vtk.vtkPolyDataMapper()
        # self.secondSphereMapper.SetInputConnection(self.sphere.GetOutputPort())

        # self.thirdSphereMapper =  vtk.vtkPolyDataMapper()
        # self.thirdSphereMapper.SetInputConnection(self.sphere.GetOutputPort())

        # Actors
        property = vtk.vtkProperty()
        property.SetColor(colors.GetColor3d("Tomato"))
        property.SetLineWidth(2)

        # Connecting the first point with the second point
        self.firstLineActor = vtk.vtkActor()
        self.firstLineActor.SetMapper(self.firstLineMapper)
        self.firstLineActor.SetProperty(property)
        self.firstLineActor.VisibilityOff()

        # Connecting the second point with the third point
        self.secondLineActor = vtk.vtkActor()
        self.secondLineActor.SetMapper(self.secondLineMapper)
        self.secondLineActor.SetProperty(property)
        self.secondLineActor.VisibilityOff()

        # Arc
        self.arcActor = vtk.vtkActor()
        self.arcActor.SetMapper(self.arcMapper)
        self.arcActor.SetProperty(property)
        self.arcActor.VisibilityOff()

        # Used to display angle between two vectors
        self.textActor = vtk.vtkTextActor()
        textProperty = self.textActor.GetTextProperty()
        textProperty.SetColor(colors.GetColor3d("Tomato"))
        textProperty.SetFontSize(15)
        textProperty.ShadowOn()
        textProperty.BoldOn()
        self.textActor.VisibilityOff()

        # Used to mark the first point
        # self.firstSphereActor = vtk.vtkActor()
        # self.firstSphereActor.SetMapper(self.firstSphereMapper)
        # self.firstSphereActor.GetProperty().SetColor(0, 1, 0)
        # self.firstSphereActor.VisibilityOff()

        # Used to mark the second point
        # self.secondSphereActor = vtk.vtkActor()
        # self.secondSphereActor.SetMapper(self.secondSphereMapper)
        # self.secondSphereActor.GetProperty().SetColor(0, 1, 0)
        # self.secondSphereActor.VisibilityOff()

        # Used to mark the third point
        # self.thirdSphereActor = vtk.vtkActor()
        # self.thirdSphereActor.SetMapper(self.thirdSphereMapper)
        # self.thirdSphereActor.GetProperty().SetColor(0, 1, 0)
        # self.thirdSphereActor.VisibilityOff()

"""
    Description: 
        AngleMeasurementInteractorStyle class extends vtkInteractorStyleTrackballCamera class.
        Set interactor style for angle measurement.
"""
class AngleMeasurementInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(
            self, 
            pipeline: AngleMeasurementPipeline,
            afterInteractorStyle: utils.AfterInteractorStyle
        ) -> None:
        self.pipeline = pipeline
        self.afterInteractorStyle = afterInteractorStyle
        self.checkNumberOfPoints = 0 # used to check current number of points

        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.__leftButtonPressEvent)
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.__mouseMoveEvent)
        self.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.__leftButtonReleaseEvent)
    
    """
        Description:
            A handle function when having mouse move event.
            Used to mark the position of mouse in world coordinates when moving.
            Used to draw two lines connecting the first point with the second point
            and the second point with the third point.
            Display the arc and the text actor.
    """
    def __mouseMoveEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        # vtkCellPicker object, it shoots a ray into the volume and returns the point where the ray intersects an isosurface of a chosen opacity
        cellPicker = self.GetInteractor().GetPicker()
        # The position of mouse in the display coordinate system
        eventPosition = self.GetInteractor().GetEventPosition()
        # vtkRenderer object
        renderer = self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()
        # vtkCamera object
        camera = renderer.GetActiveCamera()

        if not self.pipeline.isDragging:
            # Return a point in the world coordinate system on surface or out
            pickPosition = utils.getPickPosition(eventPosition, cellPicker, renderer, camera)
            # Used to mark the position of mouse in the world coordinate system
            # self.pipeline.firstSphereActor.SetPosition(pickPosition)
            # self.pipeline.firstSphereActor.VisibilityOn()
        else:
            # Return vtkPoints object
            points = self.pipeline.line.GetPoints()
            # The first point used to find the projection point
            firstPoint = points.GetPoint(0)
            # Return a point in the world coordinate system on surface, if out then finding the projection point
            pickPosition = utils.getPickPosition(eventPosition, cellPicker, renderer, camera, True, firstPoint)
            
            if self.checkNumberOfPoints == 1:
                # Used to mark the position of mouse in the world coordinate system
                # self.pipeline.secondSphereActor.SetPosition(pickPosition)
                # self.pipeline.secondSphereActor.VisibilityOn()

                # Save the second point with its id into vtkPoints object
                points.SetPoint(1, pickPosition)
                # Update the modification time for this object and its Data
                points.Modified()

                # vtkIdList may represent any type of integer id, but usually represents point and cell ids
                idList = vtk.vtkIdList()
                idList.InsertNextId(0)
                idList.InsertNextId(1)

                # Insert a cell of type VTK_LINE
                self.pipeline.line.InsertNextCell(vtk.VTK_LINE, idList)
            if self.checkNumberOfPoints == 2:
                # Used to mark the position of mouse in the world coordinate system
                # self.pipeline.thirdSphereActor.SetPosition(pickPosition)
                # self.pipeline.thirdSphereActor.VisibilityOn()

                # Save the third point with its id into vtkPoints object
                points.SetPoint(2, pickPosition)
                # Update the modification time for this object and its Data
                points.Modified()

                # vtkIdList may represent any type of integer id, but usually represents point and cell ids
                idList = vtk.vtkIdList()
                idList.InsertNextId(1)
                idList.InsertNextId(2)

                # Insert a cell of type VTK_LINE
                self.pipeline.line.InsertNextCell(vtk.VTK_LINE, idList)

                # Method used to calculate the angle, the arc and the position of text actor
                utils.buildArcAngleMeasurement(self.pipeline.arc, self.pipeline.textActor, renderer, points)
        self.GetInteractor().Render()

    """
        Description:
            A handle function when having left button event.
            Used to mark the position of points in world coordinates when click.
    """
    def __leftButtonPressEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        # vtkRenderer object
        renderer = self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()
        # vtkCamera object
        camera = renderer.GetActiveCamera()
        # The position of mouse in the display coordinate system
        eventPosition = self.GetInteractor().GetEventPosition()
        # Return vtkCellPicker object, it shoots a ray into the volume and returns the point where the ray intersects an isosurface of a chosen opacity
        cellPicker = self.GetInteractor().GetPicker()
        
        self.checkNumberOfPoints += 1
        if self.checkNumberOfPoints == 1:
            self.pipeline.isDragging = True # Start drawing

            # Return a point in the world coordinate system on surface or out
            pickPosition = utils.getPickPosition(eventPosition, cellPicker, renderer, camera)

            # Marking the first point
            # self.pipeline.firstSphereActor.GetProperty().SetColor(1, 0, 0)
            # self.pipeline.firstSphereActor.SetPosition(pickPosition)

            # vtkPoints represents 3D points used to save 2 points in world coordinates
            points = vtk.vtkPoints()
            # vtkCellArray object to represent cell connectivity
            aline = vtk.vtkCellArray()
            # Set objects into vtkPolyData object
            self.pipeline.line.SetPoints(points)
            self.pipeline.line.SetLines(aline)
        
            # Insert the first point into vtkPoints object when having left button press
            points.InsertNextPoint(pickPosition)
            # Insert the second point into vtkPoints object when having left button press, default value
            points.InsertNextPoint(0, 0, 0)
            # Insert the third point into vtkPoints object when having left button press, default value
            points.InsertNextPoint(0, 0, 0)

            # Turn on the first line actor object
            self.pipeline.firstLineActor.VisibilityOn()
        else:
            # Return vtkPoints object
            points = self.pipeline.line.GetPoints()
            if self.checkNumberOfPoints == 2:
                # Return the second point in vtkPoints object
                pickPosition = points.GetPoint(1)

                # Marking the second point
                # self.pipeline.secondSphereActor.GetProperty().SetColor(1, 0, 0)
                # self.pipeline.secondSphereActor.SetPosition(pickPosition)

                # Turn on the second line actor object
                self.pipeline.secondLineActor.VisibilityOn()
                # Turn on the arc actor object
                self.pipeline.arcActor.VisibilityOn()
                # Turn on the text actor object
                self.pipeline.textActor.VisibilityOn()
            elif self.checkNumberOfPoints == 3:
                # Return the third point in vtkPoints object
                pickPosition = points.GetPoint(2)

                # Marking the third point
                # self.pipeline.thirdSphereActor.GetProperty().SetColor(1, 0, 0)
                # self.pipeline.thirdSphereActor.SetPosition(pickPosition)
        # Override method of super class
        self.OnLeftButtonDown()

    """
        Description:
            A handle function when having left button release event.
            If number of points equals 3 then stop drawing and
            set interactor style after length measurement finished.
    """
    def __leftButtonReleaseEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        self.OnLeftButtonUp()
        if self.checkNumberOfPoints == 3:
            self.pipeline.isDragging = False # Stop drawing

            # Set interactor style when stop drawing
            self.afterInteractorStyle.addAngleMeasurementPipeline(self.pipeline)
            self.GetInteractor().SetInteractorStyle(self.afterInteractorStyle)