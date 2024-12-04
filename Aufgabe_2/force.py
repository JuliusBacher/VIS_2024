from mbsObject import mbsObject

from vtkmodules.vtkFiltersSources import (
    vtkLineSource,
    vtkArcSource,
    vtkConeSource
)
from vtkmodules.vtkFiltersCore import (
    vtkTubeFilter
)
from vtkmodules.vtkRenderingCore import (
    vtkPolyDataMapper
)
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkRenderingCore import vtkActor
from vtkmodules.vtkCommonMath import vtkMatrix4x4
import numpy as np

class force(mbsObject):
    def __init__(self,subtype,**kwargs):
        mbsObject.__init__(self,"Force",subtype,**kwargs)

class genericForce(force):
    def __init__(self,**kwargs):
        if "text" in kwargs:
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "PointOfApplication_Body1": {"type": "vector", "value": [0.,0.,0.]},
                "PointOfApplication_Body2": {"type": "vector", "value": [0.,0.,0.]},
                "mode": {"type": "string", "value": ""},
                "direction": {"type": "vector", "value": [0.,0.,0.]},
                "ForceExpression": {"type": "string", "value": ""}
            }
            force.__init__(self,"GenericForce",text=kwargs["text"],parameter=parameter)
        else:
            force.__init__(self,"GenericForce",**kwargs)

        colors = {
            "X": (1, 0, 0),
            "Y": (0, 1, 0),
            "Z": (0, 0, 1),
        }
        for i, axis in enumerate(["X", "Y", "Z"]):
            start = [0, 0, 0]
            end = [0, 0, 0]
            end[i] = self._symbolsScale
            line = vtkLineSource()
            line.SetPoint1(*start)
            line.SetPoint2(*end)

            tube = vtkTubeFilter()
            tube.SetInputConnection(line.GetOutputPort())
            tube.SetRadius(0.05*self._symbolsScale)
            tube.SetNumberOfSides(50) 
            tube.CappingOn()

            tube_mapper = vtkPolyDataMapper()
            tube_mapper.SetInputConnection(tube.GetOutputPort())

            tube_actor = vtkActor()
            self.actors.append(tube_actor)
            tube_actor.SetMapper(tube_mapper)
            tube_actor.GetProperty().SetColor(colors[axis])

        transform = vtkTransform()
        transform.Translate(self.parameter["PointOfApplication_Body1"]["value"])
        
        for actor in self.actors:
            actor.SetUserTransform(transform)
            
        start = self.parameter["PointOfApplication_Body1"]["value"]
        end = self.parameter["PointOfApplication_Body2"]["value"]
        line = vtkLineSource()
        line.SetPoint1(*start)
        line.SetPoint2(*end)

        tube = vtkTubeFilter()
        tube.SetInputConnection(line.GetOutputPort())
        tube.SetRadius(0.025*self._symbolsScale)
        tube.SetNumberOfSides(50) 
        tube.CappingOn()

        tube_mapper = vtkPolyDataMapper()
        tube_mapper.SetInputConnection(tube.GetOutputPort())

        tube_actor = vtkActor()
        self.actors.append(tube_actor)
        tube_actor.SetMapper(tube_mapper)
        tube_actor.GetProperty().SetColor((1, 0, 0))
        
class genericTorque(force):
    def __init__(self,**kwargs):
        if "text" in kwargs:
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "mode": {"type": "string", "value": ""},
                "direction": {"type": "vector", "value": [0.,0.,0.]},
                "TorqueExpression": {"type": "string", "value": ""}
            }
            force.__init__(self,"GenericTorque",text=kwargs["text"],parameter=parameter)
        else:
            force.__init__(self,"GenericTorque",**kwargs)

        vec1 = np.array(self.parameter["direction"]["value"])
        vec1 = vec1/np.linalg.norm(vec1)

        smallest_idx = np.argmin(np.abs(vec1)) 
        unit_vector = np.zeros(3)
        unit_vector[smallest_idx] = 1.0  

        vec2 = np.cross(vec1, unit_vector)
        vec2 /= np.linalg.norm(vec2)
        vec3 = np.cross(vec1, vec2)

        center = np.zeros(3)
        start = center - 0.5*vec1*self._symbolsScale
        end = center + 0.5*vec1*self._symbolsScale
        axis = vtkLineSource()
        axis.SetPoint1(*start)
        axis.SetPoint2(*end)

        axisTube = vtkTubeFilter()
        axisTube.SetInputConnection(axis.GetOutputPort())
        axisTube.SetRadius(0.05*self._symbolsScale)
        axisTube.SetNumberOfSides(50) 
        axisTube.CappingOn()

        axisTube_mapper = vtkPolyDataMapper()
        axisTube_mapper.SetInputConnection(axisTube.GetOutputPort())

        axisTube_actor = vtkActor()
        self.actors.append(axisTube_actor)
        axisTube_actor.SetMapper(axisTube_mapper)
        axisTube_actor.GetProperty().SetColor((1, 0, 0))

        arc = vtkArcSource()
        arc.SetCenter(center)

        arc.SetPoint1(vec2*self._symbolsScale)
        arc.SetPoint2(vec3*self._symbolsScale)
        arc.SetResolution(10)

        tube = vtkTubeFilter()
        tube.SetInputConnection(arc.GetOutputPort())
        tube.SetRadius(0.05*self._symbolsScale)
        tube.SetNumberOfSides(50) 
        tube.CappingOn()

        tube_mapper = vtkPolyDataMapper()
        tube_mapper.SetInputConnection(tube.GetOutputPort())

        tube_actor = vtkActor()
        self.actors.append(tube_actor)
        tube_actor.SetMapper(tube_mapper)
        tube_actor.GetProperty().SetColor((1, 0, 0))

        arrow = vtkConeSource()
        arrow.SetRadius(0.2*self._symbolsScale) 
        arrow.SetHeight(0.5*self._symbolsScale) 
        arrow.SetResolution(50)

        arrow_mapper = vtkPolyDataMapper()
        arrow_mapper.SetInputConnection(arrow.GetOutputPort())

        transform_matrix = np.eye(4) 
        transform_matrix[:3, 0] = -vec2 #arrow is oriented in global x and should point into opposite direction of vec2
        transform_matrix[:3, 1] = vec3
        transform_matrix[:3, 2] = -vec1
        transform_matrix[:3, 3] = vec3*self._symbolsScale

        vtk_matrix = vtkMatrix4x4()
        vtk_matrix.DeepCopy(transform_matrix.ravel()) 

        arrow_transform = vtkTransform()
        arrow_transform.SetMatrix(vtk_matrix)

        arrow_actor = vtkActor()
        self.actors.append(arrow_actor)
        arrow_actor.SetMapper(arrow_mapper)
        arrow_actor.SetUserTransform(arrow_transform)
        arrow_actor.GetProperty().SetColor((1, 0, 0))
