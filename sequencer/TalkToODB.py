import requests

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
    
    voltageLimit = 30/1000 #1V = 1kV - limit in vac
    #voltageLimit = 1000/1000 #1V = 1kV - limit in gas?
    
    if valuePath=="Equipment/CAEN N472/Variables/MSCB[8]" and value > voltageLimit:
        #STOP voltage too high!!
        print("Voltage attempted to be set over limit!")
        returnVal = "too high"
    else:
        '''
        response = requests.post( host, 
            json=command, 
            headers={"Content-Type": "application/json"})
            
        data = response.json()
        #print(data)
        returnVal = data['result']['status'][0]
         '''
        returnVal = 0

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
    
def writeVoltage(value):
    hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
    valuePath = "Equipment/CAEN N472/Variables/MSCB[8]"
    
    output = SetValue(hostMEG, valuePath, value)
    #print("CAEN ch2: status [4]:", output))
    current = (-228)+1163*output
    return current

    
#hostMEG = "http://pc13513.psi.ch:8081/?mjsonrpc"
#valuePath = "Equipment/CAEN N472/Variables/MSCB[8]"
#print(f"setting {valuePath}, success?", SetValue(hostMEG, valuePath, 33/1000))
