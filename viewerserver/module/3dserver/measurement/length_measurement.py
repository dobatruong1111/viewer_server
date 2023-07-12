import vtk
import utils
from typing import List

"""
    Description:
        Class contains objects for drawing line in the world coordinate system.
"""
class LengthMeasurementPipeline():
    def __init__(self) -> None:
        colors = vtk.vtkNamedColors()
        self.isDragging = False

        # Line
        # vtkPolyData represents a geometric structure consisting of vertices, lines, polygons, and/or triangle strips
        self.line = vtk.vtkPolyData()

        # Sphere source
        self.sphere = vtk.vtkSphereSource()
        self.sphere.SetRadius(5)

        # Filter
        # vtkTubeFilter is a filter that generates a tube around each input line
        self.tubeFilter = vtk.vtkTubeFilter()
        self.tubeFilter.SetInputData(self.line)
        self.tubeFilter.SetNumberOfSides(20)
        self.tubeFilter.SetRadius(1)

        # Mappers
        self.lineMapper = vtk.vtkPolyDataMapper()
        self.lineMapper.SetInputConnection(self.tubeFilter.GetOutputPort())

        self.firstSphereMapper = vtk.vtkPolyDataMapper()
        self.firstSphereMapper.SetInputConnection(self.sphere.GetOutputPort())

        self.secondSphereMapper = vtk.vtkPolyDataMapper()
        self.secondSphereMapper.SetInputConnection(self.sphere.GetOutputPort())
        
        # Actors
        self.lineActor = vtk.vtkActor()
        self.lineActor.SetMapper(self.lineMapper)
        self.lineActor.GetProperty().SetColor(colors.GetColor3d("Tomato"))
        self.lineActor.GetProperty().SetLineWidth(2)
        self.lineActor.VisibilityOff()

        # Display the length of two points in the world coordinate system
        # vtkTextActor is an actor that displays text
        self.textActor = vtk.vtkTextActor()
        textProperty = self.textActor.GetTextProperty()
        textProperty.SetColor(colors.GetColor3d("Tomato"))
        textProperty.SetFontSize(15)
        textProperty.ShadowOn()
        textProperty.BoldOn()
        self.textActor.VisibilityOff()

        # Marking the first point and the second point by two spheres
        self.firstSphereActor = vtk.vtkActor()
        self.firstSphereActor.GetProperty().SetColor(0, 1, 0)
        self.firstSphereActor.SetMapper(self.firstSphereMapper)
        self.firstSphereActor.VisibilityOff()
        
        self.secondSphereActor = vtk.vtkActor()
        self.secondSphereActor.GetProperty().SetColor(0, 1, 0)
        self.secondSphereActor.SetMapper(self.secondSphereMapper)
        self.secondSphereActor.VisibilityOff()

"""
    Description: 
        MeasureLengthInteractorStyle class extends vtkInteractorStyleTrackballCamera class.
        Set interactor style for length measurement.
"""
class LengthMeasurementInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self, pipeline: LengthMeasurementPipeline) -> None:
        self.pipeline = pipeline
        self.checkNumberOfPoints = 0 # used to check current number of points, max = 2 points
        self.AddObserver(vtk.vtkCommand.LeftButtonPressEvent, self.__leftButtonPressEvent)
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.__mouseMoveEvent)
        self.AddObserver(vtk.vtkCommand.LeftButtonReleaseEvent, self.__leftButtonReleaseEvent)

    """
        Description:
            A handle function when having mouse move event.
            Used to mark the position of mouse in world coordinates when moving.
            Used to draw a line connecting two points.
    """
    def __mouseMoveEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        # vtkRenderer object
        renderer = self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()
        # vtkCamera object
        camera = renderer.GetActiveCamera()
        # The position of mouse in the display coordinate system
        eventPosition = list(self.GetInteractor().GetEventPosition())
        # vtkCellPicker object, it shoots a ray into the volume and returns the point where the ray intersects an isosurface of a chosen opacity
        cellPicker = self.GetInteractor().GetPicker()

        if self.pipeline.isDragging:
            if self.checkNumberOfPoints == 1:
                # Return vtkPoints object
                points = self.pipeline.line.GetPoints()

                firstPoint = list(points.GetPoint(0)) # Return the first point
                # Return a point in the world coordinate system on surface, if out then finding the projection point
                pickPosition = utils.getPickPosition(eventPosition, cellPicker, renderer, camera, True, firstPoint)
                
                # Marking the second point when drawing
                self.pipeline.secondSphereActor.SetPosition(pickPosition)
                self.pipeline.secondSphereActor.VisibilityOn() # Turn on the second sphere

                # Save the second point
                points.SetPoint(1, pickPosition)
                # Update the modification time for this object and its Data
                points.Modified()

                # vtkIdList may represent any type of integer id, but usually represents point and cell ids
                idList = vtk.vtkIdList()
                idList.InsertNextId(0) # Insert id of the first point
                idList.InsertNextId(1) # Insert id of the second point

                # Insert a cell of type VTK_LINE
                self.pipeline.line.InsertNextCell(vtk.VTK_LINE, idList)
                # Method used to calculate the position of text actor
                utils.buildTextActorLengthMeasurement(self.pipeline.textActor, renderer, points)

        else: # TODO: code need to processed in javascript
            pickPosition = utils.getPickPosition(eventPosition, cellPicker, renderer, camera)
            # Marking the position of mouse in world coordinates
            self.pipeline.firstSphereActor.SetPosition(pickPosition)
            self.pipeline.firstSphereActor.VisibilityOn() # Turn on the first sphere
        self.GetInteractor().Render()
    
    """
        Description:
            A handle function when having left button press event.
            Used to mark the position of points in world coordinates when click.
    """
    def __leftButtonPressEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        # vtkRenderer object
        renderer = self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()
        # vtkCamera object
        camera = renderer.GetActiveCamera()
        # The position of mouse in the display coordinate system
        eventPosition = list(self.GetInteractor().GetEventPosition()) # the position of mouse in display coordinate system 
        # vtkCellPicker object, it shoots a ray into the volume and returns the point where the ray intersects an isosurface of a chosen opacity
        cellPicker = self.GetInteractor().GetPicker()

        self.checkNumberOfPoints += 1 # Add a point
        if self.checkNumberOfPoints == 1:
            self.pipeline.isDragging = True # Start drawing

            # Return a point in the world coordinate system on surface or out
            pickPosition = utils.getPickPosition(eventPosition, cellPicker, renderer, camera)
    
            # Marking the first point when having left button down event
            self.pipeline.firstSphereActor.GetProperty().SetColor(1, 0, 0)
            self.pipeline.firstSphereActor.SetPosition(pickPosition)

            # vtkPoints represents 3D points used to save 2 points in world coordinates
            points = vtk.vtkPoints()
            # vtkCellArray object to represent cell connectivity
            aline = vtk.vtkCellArray()
            # Set objects into vtkPolyData object
            self.pipeline.line.SetPoints(points)
            self.pipeline.line.SetLines(aline)

            # Insert the first point into vtkPoints object when having left button down
            points.InsertNextPoint(pickPosition)
            # Insert the second point into vtkPoints object
            points.InsertNextPoint(0, 0, 0) # defauld

            self.pipeline.lineActor.VisibilityOn() # Turn on line actor object
            self.pipeline.textActor.VisibilityOn() # Turn on text actor object
        elif self.checkNumberOfPoints == 2:
            points = self.pipeline.line.GetPoints()
            pickPosition = points.GetPoint(1) # Return the second point
            self.pipeline.secondSphereActor.GetProperty().SetColor(1, 0, 0) # Set red color for the second sphere
            self.pipeline.secondSphereActor.SetPosition(pickPosition) # Set position for the second sphere
        # Override method of super class
        self.OnLeftButtonDown()

    """
        Description:
            A handle function when having left button release event.
            If number of points equals 2, set interactor style after length measurement finished.
    """
    def __leftButtonReleaseEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        # Override method of super class
        self.OnLeftButtonUp()
        if self.checkNumberOfPoints == 2:
            self.pipeline.isDragging = False # Stop drawing
            # Set interactor style when stop drawing
            style = AfterLengthMeasurementInteractorStyle(self.pipeline)
            self.GetInteractor().SetInteractorStyle(style)

"""
    Description:
        UpdateLengthPositionInteractorStyle class extends vtkInteractorStyleTrackballCamera class.
        Class used to rotate, pan,... after angle measurement.
"""
class AfterLengthMeasurementInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    def __init__(self) -> None:
        self.pipelines = []
        self.AddObserver(vtk.vtkCommand.MouseMoveEvent, self.__mouseMoveEvent)
    
    def addPipeline(self, pipeline) -> None:
        self.pipelines.append(pipeline)

    """
        Description:
            A handle function used to update the position of text actor when having mouse move event.
    """
    def __mouseMoveEvent(self, obj: vtk.vtkInteractorStyleTrackballCamera, event: str) -> None:
        renderer = self.GetInteractor().GetRenderWindow().GetRenderers().GetFirstRenderer()
        if len(self.pipelines):
            for pipeline in self.pipelines:
                points = self.pipeline.line.GetPoints()
                # Method used to update the position of text actor
                utils.buildTextActorLengthMeasurement(pipeline.textActor, renderer, points)
            self.GetInteractor().Render()
        # Override method of super class
        self.OnMouseMove()