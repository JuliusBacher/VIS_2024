from mbsObject import mbsObject

class dataobject(mbsObject):
    def __init__(self,subtype,**kwargs):
        mbsObject.__init__(self,"DataObject",subtype,**kwargs)

class parameter(dataobject):
    def __init__(self,**kwargs):
        if "text" in kwargs:
            parameter = {
                "name": {"type": "string", "value": ""},
                "InitialValue": {"type": "float", "value": 0.}
            }
            dataobject.__init__(self,"Parameter",text=kwargs["text"],parameter=parameter)
        else:
            dataobject.__init__(self,"Parameter",**kwargs)
