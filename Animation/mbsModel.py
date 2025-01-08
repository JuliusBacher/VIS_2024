
import inputfilereader
import body
import constraint
import force
import measure
import dataobject
import json
import os
import h5py

class mbsModel:
    def __init__(self):
        self.__mbsObjectList = []
        self.__simulationSettings = {
            "type": "Dynamic",
            "SimulationTimeEnd": 1.,
            "OutputTimeBegin": 0.,
            "OutputTimeStepSize": 1.0e-2,
            "isExactOutputTimeEnforced": True,
            "WriteConstraintForceResultFile": False,
            "WriteForceResultFile": False,
            "WriteVelocityResultFile": False,
            "WriteStateResultFile": True,
            "WriteAccelerationResultFile": False,
            "WriteExtConstraintLagrangeResultFile": False,
            "WriteMeasureResultFile": False
        }
        self.__solverSettings = {
            "type": "HHT",
            "Alpha": -0.3,
            "MaxNumberOfInnerIterations": [5,5],
            "GlobalErrorTolerance": 1.0e-4,
            "SolverMinTimeStep": 1.0e-14,
            "SolverMaxTimeStep": 1.0e-2,
            "ModifyNewmark": True,
            "MaxNumOfTimeStepsUsingSameFactorizedJacobian": 0,
            "UsePardisoScalingAndMatching": False,
            "DebugLevel": 0,
            "DebugTimeBegin": 0.0,
            "DebugTimeEnd": 10.0
        }
        self.__currentSrf = []
    
    def importFddFile(self,filepath):
        file_name, file_extension = os.path.splitext(filepath)

        if(file_extension == ".fdd"):
            self.__mbsObjectList = inputfilereader.readInput(filepath)
        else:
            print("Wrong file type: " + file_extension)
            return False
        
        for object in self.__mbsObjectList:
            object.setModelContext(self)

        return True
        
    def exportFdsFile(self,filepath):
        f = open(filepath,"w")
        for object in self.__mbsObjectList:
            object.writeSolverInput(f)

        f.write("Simulation " + self.__simulationSettings["type"] + "\n")
        for key, value in self.__simulationSettings.items():
            if(key != "type"):
                if isinstance(value, bool):
                    value = "yes" if value else "no"
                f.write(f"\t{key} = {value}\n")

        f.write("EndSimulation\n%\n")

        f.write("Solver " + self.__solverSettings["type"] + "\n")
        for key, value in self.__solverSettings.items():
            if(key != "type"):
                if isinstance(value, bool):
                    value = "yes" if value else "no"
                f.write(f"\t{key} = {value}\n")

        f.write("EndSolver\n")

        f.close()
        
    def loadDatabase(self,database2Load):
        f = open(database2Load)
        data = json.load(f)
        f.close()
        for modelObject in data["modelObjects"]:
            if(modelObject["type"] == "Body" and modelObject["subtype"] == "Rigid_EulerParameter_PAI"):
                self.__mbsObjectList.append(body.rigidBody(parameter=modelObject["parameter"]))
            elif(modelObject["type"] == "Constraint" and modelObject["subtype"] == "Generic"):
                self.__mbsObjectList.append(constraint.genericConstraint(parameter=modelObject["parameter"]))
            elif(modelObject["type"] == "Force"):
                if(modelObject["subtype"] == "GenericForce"):
                    self.__mbsObjectList.append(force.genericForce(parameter=modelObject["parameter"]))
                elif(modelObject["subtype"] == "GenericTorque"):
                    self.__mbsObjectList.append(force.genericTorque(parameter=modelObject["parameter"]))
            elif(modelObject["type"] == "Measure"):
                self.__mbsObjectList.append(measure.measure(parameter=modelObject["parameter"]))
            elif(modelObject["type"] == "DataObject" and modelObject["subtype"] == "Parameter"):
                self.__mbsObjectList.append(dataobject.parameter(parameter=modelObject["parameter"]))

        return True

    def saveDatabase(self,dataBasePath):
        # Serializing json
        modelObjects = []
        for object in self.__mbsObjectList:
            modelObject = {"type": object.getType(),
                           "subtype": object.getSubType(),
                           "parameter": object.parameter}
            modelObjects.append(modelObject)
        
        jDataBase = json.dumps({"modelObjects": modelObjects})

        with open(dataBasePath, "w") as outfile:
            outfile.write(jDataBase)
    
    def showModel(self, renderer):
        for object in self.__mbsObjectList:
            object.show(renderer)

    def animateResult(self, h5Path, renWin):
        try:
            with h5py.File(h5Path, "r") as f:
                # Read timestamps
                timestamps = f["timestamps"][:]
                body_ids = [int(key.replace("bodyID:", "")) for key in f.keys() if key.startswith("bodyID")]
                for timestep_index in range(timestamps.size):
                    for body_id in body_ids:
                        self.__mbsObjectList[body_id-1].animate(f[f"bodyID: {body_id}/positions"][timestep_index],f[f"bodyID: {body_id}/rotations"][timestep_index])
                    renWin.Render()

        except FileNotFoundError:
            print(f"File not found: {h5Path}")
        except Exception as e:
            print(f"An error occurred: {e}")