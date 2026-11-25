import requests
from time import *
import numpy as np

def GetValue(host, valuePath):
    command = { "jsonrpc":"2.0",
            "method": "db_get_values",
            "params":{
                "paths":[valuePath]
            },
            "id":1
    }

    response = requests.post( host, 
        json=command, 
        headers={"Content-Type": "application/json"})
        
    data = response.json()
    #print(data)

    return data['result']['data']
    
def SetValue(host, valuePath, value):
    command = { "jsonrpc":"2.0",
            "method": "db_paste",
            "params":{
                "paths":[valuePath],
                "values":[value],
            },
            "id":1
    }
    
    voltageLimit = 50/1000 #1V = 1kV - limit in vac
    #voltageLimit = 1000/1000 #1V = 1kV - limit in gas?
    
    if valuePath=="Equipment/CAEN N472/Variables/MSCB[8]" and value > voltageLimit:
        #STOP voltage too high!!
        print("Voltage attempted to be set over limit!")
        returnVal = "too high"
    else:
        response = requests.post( host, 
            json=command, 
            headers={"Content-Type": "application/json"})
            
        data = response.json()
        print(data)
        returnVal = data['result']['status'][0]

    return returnVal

'''
CH4: measured Ch2 - read out voltage, uncalibrated
CH5: current Ch2 - read out current, uncalibrated
CH6: status Ch2 - 
CH7: switch Ch2 - 0 is enabled, 5 is disabled
CH8: demand Ch2 - to set demand HV (is already negative), 1V here = 1 kV !!
'''

def readVoltage():
    hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
    valuePath = "Equipment/CAEN N472/Variables/MSCB[4]"
    output = GetValue(hostMEG, valuePath)[0]
    #print("CAEN ch2: status [4]:", output))
    current = (-228)+1163*output
    return current
    
def readCurrent():
    hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
    valuePath = "Equipment/CAEN N472/Variables/MSCB[5]"
    output = GetValue(hostMEG, valuePath)[0]
    #print("CAEN ch2: status [5]:", output)
    current = (-223)+1136*output
    return current

def readPressure():
    hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
    valuePath = "Equipment/Xenon/Variables/MSCB[13]"
    output = GetValue(hostMEG, valuePath)[0]
    #print("pressure:", output)
    return output

def readTemp():
    hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
    valuePath = "Equipment/Xenon/Variables/MSCB[8]"
    output = GetValue(hostMEG, valuePath)[0]
    #print("pressure:", output)
    return output
    
def writeVoltage(value):
    hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
    #first read current value that it's set to
    valuePath = "Equipment/CAEN N472/Variables/MSCB[8]"
    currentVset = GetValue(hostMEG, valuePath)[0]
    print(currentVset)
    if abs(currentVset-value) > 0.01 : #if change bigger than 10 V, step it down
        if currentVset < value: #going up
            steps = np.arange(currentVset+0.01, value, 0.01)
        else:
            steps = np.arange(currentVset-0.01, value, -0.01)
        
        print(steps)
        for HV in steps:
            print("stepping to", HV)
            valuePath = "Equipment/CAEN N472/Variables/MSCB[8]"
            output = SetValue(hostMEG, valuePath, HV)
            sleep(5)
        #final step to value in case it's not a multiple of 0.01
        output = SetValue(hostMEG, valuePath, value)
        
    else:
        print("small step already")
        #small change, do it in one gos
        valuePath = "Equipment/CAEN N472/Variables/MSCB[8]"
        output = SetValue(hostMEG, valuePath, value)
        #print("success:", output))
    
    return output

    
#hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
#valuePath = "Equipment/CAEN N472/Variables/MSCB[8]"
#print(f"setting {valuePath}, success?", SetValue(hostMEG, valuePath, 33/1000))


#output = writeVoltage(0.02)
#print(output)
