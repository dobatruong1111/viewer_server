import vtk
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk
from vtkmodules.vtkCommonCore import vtkMath

import math, logging
from typing import List
from utils.utils import getInfoMemory

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

'''
Description: Get the geometry matrix that includes the spacing and origin information
Params: 
    imageData: used to calculator the geometry matrix 
    mat: save the geometry matrix
'''
def GetImageToWorldMatrix(
        imageData: vtk.vtkImageData, 
        mat: vtk.vtkMatrix4x4
    ) -> None:
    mat.Identity()
    origin = imageData.GetOrigin()
    spacing = imageData.GetSpacing()
    directionMatrix = imageData.GetDirectionMatrix()
    for row in range(3):
        for col in range(3):
            mat.SetElement(row, col, spacing[col] * directionMatrix.GetElement(row, col))
        mat.SetElement(row, 3, origin[row])

'''
Description: Convenience method to set direction matrix, spacing, and origin from a matrix
Params:
    imageData: Set direction matrix, spacing, and origin
    argMat: The geometry matrix that includes the spacing and origin information
'''
def SetImageToWorldMatrix(
        imageData: vtk.vtkImageData, 
        argMat: vtk.vtkMatrix4x4
    ) -> None:
    mat = vtk.vtkMatrix4x4()
    mat.DeepCopy(argMat)

    isModified = False
    nspacing = list(imageData.GetSpacing())
    norigin = list(imageData.GetOrigin())
    ndirections = imageData.GetDirectionMatrix()

    for col in range(3):
        len = 0
        for row in range(3):
            len += mat.GetElement(row, col) * mat.GetElement(row, col)
        len = math.sqrt(len)
        # Set spacing
        if nspacing[col] != len:
            nspacing[col] = len
            isModified = True
        for row in range(3):
            mat.SetElement(row, col, mat.GetElement(row, col) / len)
    for row in range(3):
        for col in range(3):
            # Set directions
            if ndirections.GetElement(row, col) != mat.GetElement(row, col):
                ndirections.SetElement(row, col, mat.GetElement(row, col))
                isModified = True
            # Set origin
            if norigin[row] != mat.GetElement(row, 3):
                norigin[row] = mat.GetElement(row, 3)
                isModified = True
    if isModified:
        imageData.SetSpacing(nspacing)
        imageData.SetOrigin(norigin)
        imageData.Modified()

'''
Description: Calculation the clipping range smaller than default clipping range of camera
'''
def calcClipRange(
        imageData: vtk.vtkImageData, 
        segmentationToCameraTransform: vtk.vtkTransform, 
        camera: vtk.vtkCamera
    ) -> List:
    segmentationBounds_Camera = [0, -1, 0, -1, 0, -1]
    vtkMath.UninitializeBounds(segmentationBounds_Camera) # [1.0, -1.0, 1.0, -1.0, 1.0, -1.0]

    imageExtentCenter = imageData.GetExtent()
    if imageExtentCenter[0] > imageExtentCenter[1] or imageExtentCenter[2] > imageExtentCenter[3] or imageExtentCenter[4] > imageExtentCenter[5]:
        # Empty image
        return

    imageToWorldMatrix = vtk.vtkMatrix4x4()
    GetImageToWorldMatrix(imageData, imageToWorldMatrix)

    imageExtent = [
        imageExtentCenter[0] - 0.5, imageExtentCenter[1] + 0.5,
        imageExtentCenter[2] - 0.5, imageExtentCenter[3] + 0.5,
        imageExtentCenter[4] - 0.5, imageExtentCenter[5] + 0.5
    ]

    # Được sử dụng để kết hợp nhiều đối tượng vtkPolyData thành một đối tượng vtkPolyData.
    appendPolyData = vtk.vtkAppendPolyData()

    for i in range(6):
        normalAxis = int(i/2) # 0, 0, 1, 1, 2, 2
        currentPlaneOriginImage = [imageExtent[0], imageExtent[2], imageExtent[4], 1.0]
        currentPlaneOriginImage[normalAxis] += (imageExtent[i] - imageExtent[normalAxis * 2])
        currentPlaneOriginWorld = [0, 0, 0, 1]
        imageToWorldMatrix.MultiplyPoint(currentPlaneOriginImage, currentPlaneOriginWorld)

        currentPlanePoint1Image = [currentPlaneOriginImage[0], currentPlaneOriginImage[1], currentPlaneOriginImage[2], 1.0]
        point1Axis = (normalAxis + 1) % 3 # 1, 1, 2, 2, 0, 0
        currentPlanePoint1Image[point1Axis] = imageExtent[point1Axis * 2 + 1]
        currentPlanePoint1World = [0, 0, 0, 1]
        imageToWorldMatrix.MultiplyPoint(currentPlanePoint1Image, currentPlanePoint1World)

        currentPlanePoint2Image = [currentPlaneOriginImage[0], currentPlaneOriginImage[1], currentPlaneOriginImage[2], 1.0]
        point2Axis = 3 - normalAxis - point1Axis # 2, 2, 0, 0, 1, 1
        currentPlanePoint2Image[point2Axis] = imageExtent[point2Axis * 2 + 1]
        currentPlanePoint2World = [0, 0, 0, 1]
        imageToWorldMatrix.MultiplyPoint(currentPlanePoint2Image, currentPlanePoint2World)

        planeSource = vtk.vtkPlaneSource()
        planeSource.SetOrigin(currentPlaneOriginWorld[0], currentPlaneOriginWorld[1], currentPlaneOriginWorld[2])
        planeSource.SetPoint1(currentPlanePoint1World[0], currentPlanePoint1World[1], currentPlanePoint1World[2])
        planeSource.SetPoint2(currentPlanePoint2World[0], currentPlanePoint2World[1], currentPlanePoint2World[2])
        planeSource.SetResolution(5, 5)
        planeSource.Update()

        appendPolyData.AddInputData(planeSource.GetOutput())

    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(appendPolyData.GetOutputPort())
    transformFilter.SetTransform(segmentationToCameraTransform)
    transformFilter.Update()
    transformFilter.GetOutput().ComputeBounds()
    segmentationBounds_Camera = transformFilter.GetOutput().GetBounds()

    clipRangeFromModifierLabelmap = [
        min(segmentationBounds_Camera[4], segmentationBounds_Camera[5]),
        max(segmentationBounds_Camera[4], segmentationBounds_Camera[5])
    ]
    clipRangeFromModifierLabelmap[0] -= 0.5
    clipRangeFromModifierLabelmap[1] += 0.5

    clipRangeFromCamera = camera.GetClippingRange()
    clipRange = [
        max(clipRangeFromModifierLabelmap[0], clipRangeFromCamera[0]),
        min(clipRangeFromModifierLabelmap[1], clipRangeFromCamera[1])
    ]
    return clipRange

'''
Description:
Set scalar values for baseImage
baseImage and modifierImage must have the same geometry (origin, spacing, directions)
and scalar type.
''' 
def modifyImage(
        baseImage: vtk.vtkImageData, 
        modifierImage: vtk.vtkImageData
    ) -> None:
    # 6337 MB

    sourceArray = vtk_to_numpy(modifierImage.GetPointData().GetScalars())
    targetArray = vtk_to_numpy(baseImage.GetPointData().GetScalars())

    # 6337 MB

    targetArray[sourceArray > 0] = 1

    # 6337 MB

    baseImage.GetPointData().SetScalars(numpy_to_vtk(targetArray))

    # 6337 MB

def gaussianFilter(
        imageData: vtk.vtkImageData, 
        softEdgeMm: float
    ) -> vtk.vtkImageData:
    # Bộ lọc gaussian được sử dụng để làm mờ ảnh
    gaussianFilter = vtk.vtkImageGaussianSmooth()
    gaussianFilter.SetInputData(imageData)

    spacing = imageData.GetSpacing()
    standardDeviationPixel = [1, 1, 1]
    for index in range(3):
        standardDeviationPixel[index] = softEdgeMm / spacing[index]
    # Sử dụng để thiết lập các độ lệch chuẩn (standard deviations) của bộ lọc Gaussian trong quá trình làm mờ ảnh.
    # Các độ lệch chuẩn này xác định mức độ làm mờ của bộ lọc Gaussian theo từng chiều. 
    # Khi giá trị độ lệch chuẩn càng lớn, hiệu ứng làm mờ càng mạnh.
    gaussianFilter.SetStandardDeviations(standardDeviationPixel)
    # Sử dụng để thiết lập hệ số bán kính (radius factor) cho bộ lọc Gaussian. 
    # Hệ số này ảnh hưởng đến kích thước của bán kính thực tế của bộ lọc.
    gaussianFilter.SetRadiusFactor(3)

    gaussianFilter.Update() # bộ lọc sẽ thực hiện convolution (tích chập)

    return gaussianFilter.GetOutput()

'''
Description: Normalize mask with the actual min/max values.
'''
def normalizeMask(maskArray):
    # Normalize mask
    maskMin = maskArray.min()
    maskMax = maskArray.max()
    mask = (maskArray.astype(float) - maskMin) / float(maskMax - maskMin)

    return mask

'''
Description: Callback class for cropping by box
'''
class IPWCallback():
    def __init__(self, planes: vtk.vtkPlanes, mapper: vtk.vtkSmartVolumeMapper):
        self.planes = planes
        self.mapper = mapper

    def __call__(self, obj: vtk.vtkBoxWidget2, event: str) -> None:
        obj.GetRepresentation().GetPlanes(self.planes)
        self.mapper.SetClippingPlanes(self.planes)