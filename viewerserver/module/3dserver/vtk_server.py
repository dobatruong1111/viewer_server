r"""
    This module is a ParaViewWeb server application.
    The following command line illustrates how to use it::

        $ vtkpython .../server.py

    Any ParaViewWeb executable script comes with a set of standard arguments that can be overrides if need be::

        --port 8080
            Port number on which the HTTP server will listen.

        --content /path-to-web-content/
            Directory that you want to serve as static web content.
            By default, this variable is empty which means that we rely on another
            server to deliver the static content and the current process only
            focuses on the WebSocket connectivity of clients.

        --authKey vtkweb-secret
            Secret key that should be provided by the client to allow it to make
            any WebSocket communication. The client will assume if none is given
            that the server expects "vtkweb-secret" as secret key.

"""
import os
import sys
import argparse

# Try handle virtual env if provided
if '--virtual-env' in sys.argv:
  virtualEnvPath = sys.argv[sys.argv.index('--virtual-env') + 1]
  virtualEnv = virtualEnvPath + '/bin/activate_this.py'
  with open(virtualEnv) as venv:
    exec(venv.read(), dict(__file__=virtualEnv))

# from __future__ import absolute_import, division, print_function

from wslink import server

from vtk.web import wslink as vtk_wslink
from vtk.web import protocols as vtk_protocols

import vtk
from vtk_protocol import Dicom3D

import requests
from pydicom.dataset import Dataset
from typing import Tuple, Dict
from concurrent.futures import ThreadPoolExecutor
import time
import threading
import json
import enum

# =============================================================================
# Server class
# =============================================================================

class Status(enum.Enum):
    NONE = "NONE"
    DOWNLOADING = "DOWNLOADING"
    DONE = "DONE"

class _Server(vtk_wslink.ServerProtocol):
    # Defaults
    authKey = "wslink-secret"
    dicom3d = Dicom3D()
    view = None
    dicomDataPath = None

    @staticmethod
    def add_arguments(parser) -> None:
        parser.add_argument(
            "--virtual-env", 
            default=None,
            help="Path to virtual environment to use"
        )
        parser.add_argument(
            "--studyUUID",
            type=str,
            default=None,
            help="studyUUID"
        )
        parser.add_argument(
            "--seriesUUID",
            type=str,
            default=None,
            help="seriesUUID"
        )
        
    @staticmethod
    def save_all_instances(
        studyUID: str,
        seriesUID: str,
        dicomDataPath: str,
        statusFilePath: str,
        threadCount: int = 4
    ) -> None:
        WADO_URL = "http://192.168.1.32:8042/wado-rs"
        WADO_USER = "orthanc"
        WADO_PASSWORD = "orthanc"
        url = f"{WADO_URL}/studies/{studyUID}/series/{seriesUID}/metadata"
        try:
            response = requests.get(
                url,
                auth = (WADO_USER, WADO_PASSWORD)
            )
            if response.status_code == 200:
                if _Server.get_data_status(statusFilePath) == Status.NONE.value:
                    _Server.add_data_path_and_data_status(statusFilePath, Status.DOWNLOADING.value)

                    metadatas = response.json()
                    futures = [0 for _ in range(threadCount)]
                    chunkSize = len(metadatas) // threadCount

                    with ThreadPoolExecutor(max_workers=threadCount) as executor:
                        for i in range(threadCount):
                            startIndex = i * chunkSize
                            endIndex = (i + 1) * chunkSize if i != threadCount - 1 else len(metadatas)
                            if startIndex < endIndex:
                                futures[i] = executor.submit(
                                    _Server.save_instances,
                                    f"thread {i}",
                                    (startIndex, endIndex),
                                    metadatas,
                                    studyUID,
                                    seriesUID,
                                    dicomDataPath
                                )
                        executor.shutdown(wait=True)
                    _Server.add_data_path_and_data_status(statusFilePath, Status.DONE.value)
                else:
                    while _Server.get_data_status(statusFilePath) == Status.DOWNLOADING.value:
                        print("Waiting 5 seconds...")
                        time.sleep(5)
                _Server.dicomDataPath = dicomDataPath
                print("Data finished")
            else:
                print(f"{url}\nStatus Code: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    
    @staticmethod
    def save_instances(
        name: str,
        indexs: Tuple, 
        metadatas: Dict, 
        studyUID: str, 
        seriesUID: str, 
        dicomDataPath: str
    ) -> None:
        WADO_URL = "http://192.168.1.32:8042/wado"
        WADO_USER = "orthanc"
        WADO_PASSWORD = "orthanc"
        try:
            for i in range(indexs[0], indexs[1]):
                ds = Dataset.from_json(metadatas[i])
                objectUID = ds.SOPInstanceUID
                response = requests.get(
                    WADO_URL,
                    params={
                        "studyUID": studyUID,
                        "seriesUID": seriesUID,
                        "objectUID": objectUID,
                        "requestType": "WADO",
                        "contentType": "application/dicom"
                    },
                    auth = (WADO_USER, WADO_PASSWORD)
                )
                if response.status_code == 200:
                    dicomFile = f"/{objectUID}.dcm"
                    bytes = response.content
                    with open(dicomDataPath + dicomFile, "wb") as file:
                        file.write(bytes)
                else:
                    print(f"{response.url}\nStatus Code: {response.status_code}")
                    return
            print(f"{name}: Done")
        except Exception as e:
            print(f"Error: {e}")

    @staticmethod
    def add_data_path_and_data_status(statusFilePath: str, dataStatus: str) -> None:
        with open(statusFilePath, mode='r+') as file:
            data = json.load(file)
            data["status"] = dataStatus
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()

    @staticmethod
    def get_data_status(statusFilePath: str) -> str:
        with open(statusFilePath, mode='r') as file:
            data = json.load(file)
        return data["status"]

    @staticmethod
    def configure(args) -> None:
        # Standard args
        _Server.authKey = args.authKey

    def onConnect(self, request, client_id) -> None:
        while self.dicomDataPath is None:
            pass
        else:
            self.dicom3d.dataPath = self.dicomDataPath

    def initialize(self) -> None:
        # Bring Used Components
        # A list of LinkProtocol provide rpc and publish functionality
        self.registerVtkWebProtocol(vtk_protocols.vtkWebMouseHandler())
        self.registerVtkWebProtocol(vtk_protocols.vtkWebViewPort())
        self.registerVtkWebProtocol(vtk_protocols.vtkWebPublishImageDelivery(decode=False))
        
        # Custom API
        self.registerVtkWebProtocol(self.dicom3d)

        # tell the C++ web app to use no encoding.
        # ParaViewWebPublishImageDelivery must be set to decode=False to match.
        self.getApplication().SetImageEncoding(0)

        # Update authentication key to use
        self.updateSecret(_Server.authKey)

        if not _Server.view:
            colors = vtk.vtkNamedColors()
            
            renderer = vtk.vtkRenderer()
            renderer.SetBackground(colors.GetColor3d("Black"))
            
            renderWindow = vtk.vtkRenderWindow()
            renderWindow.AddRenderer(renderer)
            renderWindow.OffScreenRenderingOn()

            style = vtk.vtkInteractorStyleTrackballCamera()

            renderWindowInteractor = vtk.vtkRenderWindowInteractor()
            renderWindowInteractor.SetRenderWindow(renderWindow)
            renderWindowInteractor.SetInteractorStyle(style)
            renderWindowInteractor.EnableRenderOff()

            # self.getApplication() -> vtkWebApplication()
            self.getApplication().GetObjectIdMap().SetActiveObject("VIEW", renderWindow)
            self.getApplication().GetObjectIdMap().SetActiveObject("INTERACTOR", renderWindowInteractor)

# =============================================================================
# Main: Parse args and start serverviewId
# =============================================================================

if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="3D Viewer")

    # Add arguments
    server.add_arguments(parser)
    _Server.add_arguments(parser)
    args = parser.parse_args()
    _Server.configure(args)

    dataPath = f"./data/{args.studyUUID}/{args.seriesUUID}"
    dicomDataPath = dataPath + "/data"
    statusFilePath = dataPath + "/status.json"

    if not os.path.exists(dataPath):
        os.makedirs(dicomDataPath)
        with open(statusFilePath, mode='w') as file:
            json.dump({"status": Status.NONE.value}, file, indent=4)

    thread_download_data = threading.Thread(
        target=_Server.save_all_instances,
        args=(args.studyUUID, args.seriesUUID, dicomDataPath, statusFilePath,)
    )
    thread_download_data.start()

    server.start_webserver(
        options=args, 
        protocol=_Server, 
        disableLogging=True, 
    )