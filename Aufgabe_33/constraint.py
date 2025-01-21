from mbsObject import mbsObject

from vtkmodules.vtkFiltersSources import (
    vtkLineSource,
    vtkSphereSource,
    vtkRegularPolygonSource
)
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper
)
from vtkmodules.vtkRenderingCore import vtkActor
from vtkmodules.all import vtkMatrix4x4, vtkTransform
import numpy as np

class constraint(mbsObject):
    def __init__(self,subtype,**kwargs):
        mbsObject.__init__(self,"Constraint",subtype,**kwargs)

class genericConstraint(constraint):
    def __init__(self,**kwargs):
        if "text" in kwargs:
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "position": {"type": "vector", "value": [0.,0.,0.]},
                "x_axis": {"type": "vector", "value": [0.,0.,0.]},
                "y_axis": {"type": "vector", "value": [0.,0.,0.]},
                "z_axis": {"type": "vector", "value": [0.,0.,0.]},
                "dx": {"type": "bool", "value": False},
                "dy": {"type": "bool", "value": False},
                "dz": {"type": "bool", "value": False},
                "ax": {"type": "bool", "value": False},
                "ay": {"type": "bool", "value": False},
                "az": {"type": "bool", "value": False}
            }
            constraint.__init__(self,"Generic",text=kwargs["text"],parameter=parameter)
        else:
            constraint.__init__(self,"Generic",**kwargs)

        self.__locks = {"translation":  [self.parameter["dx"]["value"],self.parameter["dy"]["value"],self.parameter["dz"]["value"]],
                        "rotation":     [self.parameter["ax"]["value"],self.parameter["ay"]["value"],self.parameter["az"]["value"]]}

        colors = {
            "X": (1, 0, 0),
            "Y": (0, 1, 0),
            "Z": (0, 0, 1),
        }

        for i, axis in enumerate(["X", "Y", "Z"]):
            line = vtkLineSource()
            start = [0, 0, 0]
            end = [0, 0, 0]
            end[i] = self._symbolsScale
            line.SetPoint1(*start)
            line.SetPoint2(*end)

            line_mapper = vtkPolyDataMapper()
            line_mapper.SetInputConnection(line.GetOutputPort())

            line_actor = vtkActor()
            self.actors.append(line_actor)
            line_actor.SetMapper(line_mapper)
            line_actor.GetProperty().SetColor(colors[axis])

            if self.__locks["translation"][i]:
                sphere = vtkSphereSource()
                sphere.SetCenter(*end)
                sphere.SetRadius(0.05*self._symbolsScale)

                sphere_mapper = vtkPolyDataMapper()
                sphere_mapper.SetInputConnection(sphere.GetOutputPort())

                sphere_actor = vtkActor()
                self.actors.append(sphere_actor)
                sphere_actor.SetMapper(sphere_mapper)
                sphere_actor.GetProperty().SetColor(colors[axis])

            if self.__locks["rotation"][i]:
                ring = vtkRegularPolygonSource()
                ring.SetCenter([0.7 * v for v in end])
                ring.SetRadius(0.2*self._symbolsScale)
                ring.SetNumberOfSides(50)
                if axis == "X":
                    ring.SetNormal(1, 0, 0)
                elif axis == "Y":
                    ring.SetNormal(0, 1, 0)
                elif axis == "Z":
                    ring.SetNormal(0, 0, 1)

                ring_mapper = vtkPolyDataMapper()
                ring_mapper.SetInputConnection(ring.GetOutputPort())

                ring_actor = vtkActor()
                self.actors.append(ring_actor)
                ring_actor.SetMapper(ring_mapper)
                ring_actor.GetProperty().SetColor(colors[axis])

        transform_matrix = np.eye(4) 
        transform_matrix[:3, 0] = np.array(self.parameter["x_axis"]["value"])
        transform_matrix[:3, 1] = np.array(self.parameter["y_axis"]["value"])
        transform_matrix[:3, 2] = np.array(self.parameter["z_axis"]["value"])
        transform_matrix[:3, 3] = np.array(self.parameter["position"]["value"])

        vtk_matrix = vtkMatrix4x4()
        vtk_matrix.DeepCopy(transform_matrix.ravel()) 
        
        transform = vtkTransform()
        transform.SetMatrix(vtk_matrix)

        for actor in self.actors:
            actor.SetUserTransform(transform)