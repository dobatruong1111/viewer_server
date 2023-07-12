import vtk
from vtkmodules.vtkCommonCore import vtkMath
from typing import List
import math

"""
    Description:
        1. convert the focal point to homogenous coordinates.
        2. convert the focal point to display coordinates then select z-axis.
        3. convert the input point (in display coordinates) with selected z-axis above to world coordinates.
    Params:
        point: a point in display coordinates with z = 0
        focalPoint: the focal point of camera object (in world coordinates) used to select z-axis
        renderer: used to convert coordinates
    Return: a point (in world coordinates)
"""
def convertFromDisplayCoords2WorldCoords(point: List[int], focalPoint: List[float], renderer: vtk.vtkRenderer) -> List[float]:
    # Select z-axis when convert the focal point from homogeneous coordinates to display coordinates
    renderer.SetWorldPoint(focalPoint[0], focalPoint[1], focalPoint[2], 1) 
    renderer.WorldToDisplay()
    displayCoord = renderer.GetDisplayPoint()
    selectionz = displayCoord[2] # the distance from the position of camera to screen

    # Convert from display coordinates to world coordinates
    renderer.SetDisplayPoint(point[0], point[1], selectionz)
    renderer.DisplayToWorld()
    worldPoint = renderer.GetWorldPoint()

    # Convert from homogeneous coordinates to world coordinates
    pickPosition = [0, 0, 0]
    for i in range(3):
        pickPosition[i] = worldPoint[i] / worldPoint[3] if worldPoint[3] else worldPoint[i]
    return pickPosition

"""
    Description: convert a point from world coordinates to display coordinates.
    Params:
        point: a point (in world coordinates)
        renderer: used to convert coordinates
    Return: a point (in display coordinates)
"""
def convertFromWorldCoords2DisplayCoords(point: List[float], renderer: vtk.vtkRenderer) -> List[float]:
    # Specify a point location in world coordinates. This method takes homogeneous coordinates
    renderer.SetWorldPoint(point[0], point[1], point[2], 1)
    renderer.WorldToDisplay()
    return list(renderer.GetDisplayPoint()) # Return specified point location in display coordinates 

"""
    Description:
        Calculate the euclide distance between two points.
        Note: two points in the same coordinate system.
    Params: two points
    Return: the euclidean distance
"""
def getEuclideanDistanceBetween2Points(firstPoint: List[float], secondPoint: List[float]) -> float:
    distSquared = vtkMath.Distance2BetweenPoints(firstPoint, secondPoint)
    dist = math.sqrt(distSquared)
    return dist

"""
    Description: 
        1. building a plane by the first point and the direction vector of projection.
        2. after finding the projection point of the second point.
    Params:
        firstPoint, sencondPoint: two points (in world coordinates)
        directionOfProjection: a vector (in world coordinates)
    Return: the projection point of the second point
"""
def findProjectionPoint(firstPoint: List[float], secondPoint: List[float], directionOfProjection: List[float]) -> List[float]:
    x1 = firstPoint[0]; y1 = firstPoint[1]; z1 = firstPoint[2]
    a = directionOfProjection[0]; b = directionOfProjection[1]; c = directionOfProjection[2]
    x2 = secondPoint[0]; y2 = secondPoint[1]; z2 = secondPoint[2]
    '''
        The first point: [x1, y1, z1] (in world coordinates)
        The direction of projection: [a, b, c] (the normal vector of the plane, the direction vector of the straight line)
        The second point: [x2, y2, z2] (in world coordinates)
        The plane equation: 
            a(x - x1) + b(y - y1) + c(z - z1) = 0
        Linear equations:
            x = x2 + at
            y = y2 + bt
            z = z2 + ct
    '''
    x = lambda t: x2 + a * t
    y = lambda t: y2 + b * t
    z = lambda t: z2 + c * t
    t = (a * x1 - a * x2 + b * y1 - b * y2 + c * z1 - c * z2) / (a*a + b*b + c*c)
    return [x(t), y(t), z(t)]

"""
    Description:
        Method returns a point (on surface or out in world coordinates) through vtkCellPicker object.
        Method can return a projection point (in case out).
    Params:
        point: a point (in display coordinates)
        cellPicker: used to get a point on surface
        renderer: used to convert coordinates
        camera: used to get focal point and direction of projection

        checkToGetProjectionPoint: check to get a projection point of the second point, default=False, type=bool
        firstPoint: a point (in world coordinates), default=None, type=List
        if checkToGetProjectionPoint=True, finding a plane thought the first point. After finding a projection point of the second point on plane
    Return: a point (in world coordinates)
"""
def getPickPosition(point: List[int], cellPicker: vtk.vtkCellPicker, renderer: vtk.vtkRenderer, camera: vtk.vtkCamera, checkToGetProjectionPoint=False, firstPoint=None) -> List[float]:
    pickPosition = None
    check = cellPicker.Pick(point[0], point[1], 0, renderer)
    if check:
        pickPosition = list(cellPicker.GetPickPosition())
    else:
        pickPosition = convertFromDisplayCoords2WorldCoords(list(point), list(camera.GetFocalPoint()), renderer)
        if checkToGetProjectionPoint:
            projectionPoint = findProjectionPoint(firstPoint, pickPosition, list(camera.GetDirectionOfProjection()))
            pickPosition = projectionPoint
    return pickPosition

"""
    Description:
        Method returns the angle between two vectors.
        The first vector created by the first point and the second point.
        The second vector created by the third point and the second point.
    Params:
        firstPoint, secondPoint, thirdPoint: three points in world coordinates
    Return: the angle between two vectors
"""
def getAngleDegrees(firstPoint: List[float], secondPoint: List[float], thirdPoint: List[float]) -> float:
    EPSILON = 1e-3 # threshold

    if vtkMath.Distance2BetweenPoints(firstPoint, secondPoint) <= EPSILON and vtkMath.Distance2BetweenPoints(thirdPoint, secondPoint) <= EPSILON:
        return 0.0

    vector1 = [firstPoint[0] - secondPoint[0], firstPoint[1] - secondPoint[1], firstPoint[2] - secondPoint[2]]
    vector2 = [thirdPoint[0] - secondPoint[0], thirdPoint[1] - secondPoint[1], thirdPoint[2] - secondPoint[2]]
    vtkMath.Normalize(vector1)
    vtkMath.Normalize(vector2)

    angleRad = math.acos(vtkMath.Dot(vector1, vector2)) # Dot: tich vo huong
    angleDeg = vtkMath.DegreesFromRadians(angleRad)

    return angleDeg
    # TODO: need to develop other options such as: OrientedSigned (-180 -> 180) and OrientedPositive (0 -> 360)

"""
    Description:
        Method used to calculate the position of text actor for length measurement.
    Params:
        textActor: need to set its position and input data
        renderer: used to convert coordinates
        points: object contains points in world coordinates
    Return: None
"""
def buildTextActorLengthMeasurement(textActor: vtk.vtkTextActor, renderer: vtk.vtkRenderer, points: vtk.vtkPoints) -> None:
    if points.GetNumberOfPoints() == 2:
        firstPoint = list(points.GetPoint(0))
        secondPoint = list(points.GetPoint(1))

        # Calculate the middle point
        midPoint = list(map(lambda i,j: (i+j)/2, firstPoint, secondPoint))
        # Calculate the euclidean distance between the first point and the second point
        distance = getEuclideanDistanceBetween2Points(firstPoint, secondPoint)
        # Convert the middle point from the world coordinate system to the display coordinate system 
        displayCoords = convertFromWorldCoords2DisplayCoords(midPoint, renderer)

        # Display the euclide distance and set position of text actor
        textActor.SetInput(f"{round(distance, 1)}mm")
        textActor.SetDisplayPosition(round(displayCoords[0]), round(displayCoords[1]))

"""
    Description:
        Method used to calculate the angle between vectors (in world coordinates),
        the arc and the position of text actor (in display coordinates).
    Params:
        arc: need to set its properties
        textActor: need to set its position and input data
        renderer: used to convert coordinates
        points: object contains points in world coordinates
    Return: None
"""
def buildArcAngleMeasurement(arc: vtk.vtkArcSource, textActor: vtk.vtkTextActor, renderer: vtk.vtkRenderer, points: vtk.vtkPoints) -> None:
    if points.GetNumberOfPoints() == 3:
        # Get three points
        firstPoint = points.GetPoint(0)
        secondPoint = points.GetPoint(1)
        thirdPoint = points.GetPoint(2)

        angle = getAngleDegrees(firstPoint, secondPoint, thirdPoint) # Calculate the angle
        longArc = False # By default the arc spans the shortest angular sector

        vector1 = [firstPoint[0] - secondPoint[0], firstPoint[1] - secondPoint[1], firstPoint[2] - secondPoint[2]]
        vector2 = [thirdPoint[0] - secondPoint[0], thirdPoint[1] - secondPoint[1], thirdPoint[2] - secondPoint[2]]

        if (abs(vector1[0]) < 0.001 and abs(vector1[1]) < 0.001 and abs(vector1[2]) < 0.001) or (abs(vector2[0]) < 0.001 and abs(vector2[1]) < 0.001 and abs(vector2[2]) < 0.001):
            return
        
        # Return norm of vector
        l1 = vtkMath.Normalize(vector1) 
        l2 = vtkMath.Normalize(vector2)

        length = l1 if l1 < l2 else l2 # Get min
        anglePlacementRatio = 0.5
        angleTextPlacementRatio = 0.7
        lArc = length * anglePlacementRatio
        lText = length * angleTextPlacementRatio

        arcp1 = [lArc * vector1[0] + secondPoint[0], lArc * vector1[1] + secondPoint[1], lArc * vector1[2] + secondPoint[2]]
        arcp2 = [lArc * vector2[0] + secondPoint[0], lArc * vector2[1] + secondPoint[1], lArc * vector2[2] + secondPoint[2]]

        arc.SetPoint1(arcp1)
        arc.SetPoint2(arcp2)
        arc.SetCenter(secondPoint)
        arc.SetNegative(longArc)
        arc.Update()

        # Add two vectors
        vector3 = [vector1[0] + vector2[0], vector1[1] + vector2[1], vector1[2] + vector2[2]]
        vtkMath.Normalize(vector3)

        # Calculate the position of text actor in the world coordinate system
        textActorPositionWorld = [
            lText * (-1.0 if longArc else 1.0) * vector3[0] + secondPoint[0],
            lText * (-1.0 if longArc else 1.0) * vector3[1] + secondPoint[1],
            lText * (-1.0 if longArc else 1.0) * vector3[2] + secondPoint[2]
        ]
        # Convert to the display coordinate system
        textActorPositionDisplay = convertFromWorldCoords2DisplayCoords(textActorPositionWorld, renderer)
        textActor.SetInput(f"{round(angle, 1)}deg")
        textActor.SetPosition(round(textActorPositionDisplay[0]), round(textActorPositionDisplay[1]))