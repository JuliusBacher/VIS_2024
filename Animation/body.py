from mbsObject import mbsObject

from vtkmodules.vtkIOGeometry import vtkOBJReader
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper,
    vtkActor
)
from vtkmodules.all import vtkMatrix4x4, vtkTransform
import numpy as np

class body(mbsObject):
    def __init__(self,subtype,**kwargs):
        mbsObject.__init__(self,"Body",subtype,**kwargs)

class rigidBody(body):
    def __init__(self,**kwargs):
        if "text" in kwargs:
            parameter = {
                "mass": {"type": "float", "value": 1.},
                "COG": {"type": "vector", "value": [0.,0.,0.]},
                "geometry": {"type": "filepath", "value": ""},
                "position": {"type": "vector", "value": [0.,0.,0.]},
                "x_axis": {"type": "vector", "value": [1.,0.,0.]},
                "y_axis": {"type": "vector", "value": [0.,1.,0.]},
                "z_axis": {"type": "vector", "value": [0.,0.,1.]},
                "color": {"type": "colorvector", "value": [0,0,0,0]},
                "i1_axis": {"type": "vector", "value": [1.,0.,0.]},
                "i2_axis": {"type": "vector", "value": [0.,1.,0.]},
                "i3_axis": {"type": "vector", "value": [0.,0.,1.]}
            }

            body.__init__(self,"Rigid_EulerParameter_PAI",text=kwargs["text"],parameter=parameter)
            #compute rgb values in [0,1] as vtk uses rgb in this range and fdd uses [0,255]
            self.parameter["color"]["value"] = [rgb/255 for rgb in self.parameter["color"]["value"]]

        else:
            body.__init__(self,"Rigid_EulerParameter_PAI",**kwargs)

        # read OBJ file (CAD graphics)
        reader = vtkOBJReader()
        reader.SetFileName(self.parameter["geometry"]["value"])  
        reader.Update()
        
        mapper = vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        bodyActor = vtkActor()
        self.actors.append(bodyActor)
        bodyActor.SetMapper(mapper)
        bodyActor.GetProperty().SetDiffuse(0.8)
        bodyActor.GetProperty().SetSpecular(0.3)
        bodyActor.GetProperty().SetSpecularPower(60.0)
        bodyActor.GetProperty().SetColor(self.parameter["color"]["value"][0:3])

        transform_matrix = np.eye(4) 
        transform_matrix[:3, 0] = np.array(self.parameter["x_axis"]["value"])
        transform_matrix[:3, 1] = np.array(self.parameter["y_axis"]["value"])
        transform_matrix[:3, 2] = np.array(self.parameter["z_axis"]["value"])
        transform_matrix[:3, 3] = np.array(self.parameter["position"]["value"])

        vtk_matrix = vtkMatrix4x4()
        vtk_matrix.DeepCopy(transform_matrix.ravel()) 

        transform = vtkTransform()
        transform.SetMatrix(vtk_matrix)
        bodyActor.SetUserTransform(transform)

    def animate(self,COGPos,rotation):
        for actor in self.actors:
            transform_matrix = np.eye(4)

            iniPAI = np.eye(3) 
            iniPAI[:3, 0] = np.array(self.parameter["i1_axis"]["value"])
            iniPAI[:3, 1] = np.array(self.parameter["i2_axis"]["value"])
            iniPAI[:3, 2] = np.array(self.parameter["i3_axis"]["value"])
            iniRot = np.eye(3)
            iniRot[:3, 0] = np.array(self.parameter["x_axis"]["value"])
            iniRot[:3, 1] = np.array(self.parameter["y_axis"]["value"])
            iniRot[:3, 2] = np.array(self.parameter["z_axis"]["value"])
            diffRot = np.linalg.matmul(iniPAI.T,iniRot)
            posLocal = np.linalg.matmul(iniPAI.T,np.array(self.parameter["position"]["value"]) - np.array(self.parameter["COG"]["value"]))
            position = COGPos + np.linalg.matmul(rotation,posLocal)
            transform_matrix[:3, :3] = np.linalg.matmul(rotation,diffRot)
            transform_matrix[:3, 3] = position

            vtk_matrix = vtkMatrix4x4()
            vtk_matrix.DeepCopy(transform_matrix.ravel()) 

            transform = vtkTransform()
            transform.SetMatrix(vtk_matrix)
            actor.SetUserTransform(transform)
