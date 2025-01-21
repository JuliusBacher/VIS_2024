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
import numpy as np

class measure(mbsObject):
    def __init__(self,**kwargs):
        if "text" in kwargs:
            parameter = {
                "body1": {"type": "string", "value": "no"},
                "body2": {"type": "string", "value": "no"},
                "type": {"type": "string", "value": ""},
                "component": {"type": "int", "value": "0"},
                "location_body1": {"type": "vector", "value": [0.,0.,0.]},
                "location_body2": {"type": "vector", "value": [0.,0.,0.]},
                "vector_body1": {"type": "vector", "value": [0.,0.,0.]},
                "vector1_body2": {"type": "vector", "value": [0.,0.,0.]},
                "vector2_body2": {"type": "vector", "value": [0.,0.,0.]},
                "use_initial_value": {"type": "bool", "value": False}
            }
            mbsObject.__init__(self,"Measure","",text=kwargs["text"],parameter=parameter)
        else:
            mbsObject.__init__(self,"Measure","",**kwargs)

        if(self.parameter["type"]["value"] == "displacement"):
            self._subtype = "Translational"
        if(self.parameter["type"]["value"] == "velocity"):
            self._subtype = "Translational"        
        if(self.parameter["type"]["value"] == "angle"):
            self._subtype = "Rotational"   
        if(self.parameter["type"]["value"] == "angular velocity"):
            self._subtype = "Rotational"

        colors = {
            "X": (1, 0, 0),
            "Y": (0, 1, 0),
            "Z": (0, 0, 1),
        }

        if self._subtype == "Translational":
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
            transform.Translate(self.parameter["location_body1"]["value"])
            
            for actor in self.actors:
                actor.SetUserTransform(transform)
                
            start = self.parameter["location_body1"]["value"]
            end = self.parameter["location_body2"]["value"]
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

        elif self._subtype == "Rotational":
            vec2 = np.array(self.parameter["vector1_body2"]["value"])
            vec3 = np.array(self.parameter["vector2_body2"]["value"])
            normal = np.cross(vec2, vec3)
            normal = normal/np.linalg.norm(normal)

            center = [0, 0, 0]

            start = center - 0.5*normal*self._symbolsScale
            end = center + 0.5*normal*self._symbolsScale
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

            arrow = vtkConeSource()
            arrow.SetRadius(0.2*self._symbolsScale)
            arrow.SetHeight(0.5*self._symbolsScale)
            arrow.SetResolution(50)

            arrow_mapper = vtkPolyDataMapper()
            arrow_mapper.SetInputConnection(arrow.GetOutputPort())

            arrow_transform = vtkTransform()
            arrow_transform.Translate(vec3*self._symbolsScale)
            angle = np.arccos(np.dot(vec3, vec2))*180/np.pi
            arrow_transform.RotateZ(90+angle)

            arrow_actor = vtkActor()
            self.actors.append(arrow_actor)
            arrow_actor.SetMapper(arrow_mapper)
            arrow_actor.SetUserTransform(arrow_transform)