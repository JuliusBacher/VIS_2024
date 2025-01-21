
import os
import sys

class mbsObject:
    def __init__(self,type,subtype,**kwargs):
        self.__type = type
        self._subtype = subtype
        self._symbolsScale = 10.
        if "parameter" in kwargs:
            self.parameter = kwargs["parameter"]
        else:
            sys.exit("parameter not provided, cannot create mbsObject!")    

        self.actors = []

        if "text" in kwargs:
            for line in kwargs["text"]:
                splitted = line.split(":")
                for key in self.parameter.keys():
                    keyString = splitted[0].strip()
                    valueString = line[len(key)+1:].strip()
                    if(keyString == key):
                        if(self.parameter[key]["type"] == "float"):
                            self.parameter[key]["value"] = self.str2float(valueString)
                        elif(self.parameter[key]["type"] == "vector"):
                            self.parameter[key]["value"] = self.str2vector(valueString)
                        elif(self.parameter[key]["type"] == "colorvector"):
                            self.parameter[key]["value"] = self.str2colorvector(valueString)
                        elif(self.parameter[key]["type"]=="string"):
                            self.parameter[key]["value"] = valueString
                        elif(self.parameter[key]["type"]=="filepath"):
                            self.parameter[key]["value"] = os.path.normpath(valueString)
                        elif(self.parameter[key]["type"]=="bool"):
                            self.parameter[key]["value"] = self.str2bool(valueString)

    def getType(self):
        return self.__type
    
    def getSubType(self):
        return self._subtype
    
    def setModelContext(self, modelContext):
        return
    
    def writeSolverInput(self,file):
        text = []
        text.append(self.__type + " " + self._subtype + "\n")
        for key in self.parameter.keys():
            value = self.parameter[key]["value"]
            if(self.parameter[key]["type"] == "float"):
                text.append("\t"+key+" = "+self.float2str(value)+"\n")
            elif(self.parameter[key]["type"] == "vector"):
                text.append("\t"+key+" = "+self.vector2str(value)+"\n")
            elif(self.parameter[key]["type"] == "string"):
                text.append("\t"+key+" = "+value+"\n")
            elif(self.parameter[key]["type"] == "filepath"):
                text.append("\t"+key+" = "+value+"\n")
            elif(self.parameter[key]["type"] == "bool"):
                text.append("\t"+key+" = "+self.bool2str(value)+"\n")
        text.append("End"+self.__type+"\n%\n")

        file.writelines(text)

    @staticmethod
    def str2float(inString):
        return float(inString)
    @staticmethod
    def float2str(inFloat):
        return str(inFloat)
    
    @staticmethod
    def str2vector(inString):
        return [float(inString.split(",")[0]),float(inString.split(",")[1]),float(inString.split(",")[2])]
    @staticmethod
    def vector2str(inVector):
        return str(inVector[0]) + "," + str(inVector[1]) + "," + str(inVector[2])
    
    @staticmethod
    def str2colorvector(inString):
        splitted = inString.split(" ")
        return [int(splitted[0]),int(splitted[1]),int(splitted[2]),int(splitted[1])]
    
    @staticmethod
    def str2bool(inString):
        return bool(int(inString))
    @staticmethod
    def bool2str(inBool):
        if inBool:
            return "yes"
        else:
            return "no"
    
    def show(self, renderer):
        for actor in self.actors:
            renderer.AddActor(actor)
    def hide(self, renderer):
        for actor in self.actors:
            renderer.RemoveActor(actor)