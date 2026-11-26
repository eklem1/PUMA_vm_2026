#function to create lamp flashes for PUMA
#in test mode where ch1 is going into the caen DT, not controlling the lamp

import pyvisa as visa
import numpy as np
from time import *
import datetime
import os, sys
import requests

def GetValue(host, valuePath):
    '''
    Read values directly from midas for monitoring
    '''
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

# setup function for the siglent SGD 
def SetupFunctionGen(funGen, pulsefreq = 2, pulseWidth = 0.0002, riseEdge=0.00000002 ):
    # pulseWidth = 0.000012
    # pulsefreq = 1 #unit is Hz
    #set up the waveform we want
    #set to pulse type
    funGen.write('C1:BSWV WVTP,PULSE')
    # Frequency: 2 Hz 
    funGen.write(f'C1:BSWV FRQ,{pulsefreq}') #unit is Hz
    # Use low/high levels (and not Amplitude) 
    #I think this sets the high/low levels correctly - there seems to be be no definite switch you do
    # High level: 6 V 
    funGen.write('C1:BSWV HLEV,5') #unit is V
    # Low level : 0 V 
    funGen.write('C1:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    funGen.write(f'C1:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    funGen.write(f'C1:BSWV RISE,{riseEdge}') #unit is s
    funGen.write('C1:OUTP ON,PLRT,NORM')
    # #query the waveform
    q = funGen.query('C1:BSWV?')
    # print(q)
    
    ## set up channel 2 for triggering on
    funGen.write('C2:BSWV WVTP,PULSE')
    #funGen.write(f'C2:BSWV FRQ,{pulsefreq}') #unit is Hzc
    funGen.write('C2:BSWV HLEV,1.2') #unit is V
    # Low level : 0 V 
    funGen.write('C2:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    funGen.write(f'C1:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    funGen.write(f'C2:BSWV RISE,{riseEdge}') #unit is s
    funGen.write('C2:OUTP ON,PLRT,INVT') #invert channel output
    
    funGen.write('COUP FCOUP,ON')
    funGen.write('COUP PCOUP,ON')
    
    return

# setup function for the siglent SGD 
def SetupFunctionGenTEST(funGen, pulsefreq = 2, pulseWidth = 0.0002, riseEdge=0.00000002 ):
    #set up the waveform we want
    #set to pulse type
    funGen.write('C1:BSWV WVTP,SINE')
    # Frequency: 2 Hz 
    funGen.write(f'C1:BSWV FRQ,200000') #unit is Hz -> 5 us period
    # Use low/high levels (and not Amplitude) 
    #I think this sets the high/low levels correctly - there seems to be be no definite switch you do
    # High level: 6 V 
    funGen.write('C1:BSWV HLEV,0.3') #unit is V
    # Low level : 0 V 
    funGen.write('C1:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    #funGen.write(f'C1:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    #funGen.write(f'C1:BSWV RISE,{riseEdge}') #unit is s
    funGen.write('C1:OUTP ON,PLRT,INVT')
    # #query the waveform
    q = funGen.query('C1:BSWV?')
    #print(funGen.query('C1:OUTP?'))
    
    ## set up channel 2 for triggering on
    funGen.write('C2:BSWV WVTP,PULSE')
    funGen.write(f'C2:BSWV FRQ,{pulsefreq}') #unit is Hzc
    funGen.write('C2:BSWV HLEV,1.2') #unit is V
    # Low level : 0 V 
    funGen.write('C2:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    funGen.write(f'C2:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    funGen.write(f'C2:BSWV RISE,{riseEdge}') #unit is s
    funGen.write('C2:OUTP ON,PLRT,INVT') #invert channel output
    
    #funGen.write('COUP FCOUP,ON')
    #funGen.write('COUP PCOUP,ON')
    
    return

def SingleSetFlashes(Npulses=10):
    ##### Connect to function generator #####

    # Create a VISA resource manager
    rm = visa.ResourceManager()
    print(rm.list_resources())

    # connect to function generator
    #functionGen_address = "TCPIP::129.129.141.91::inst0::INSTR" # at PSI, west side?
    functionGen_address = "TCPIP::129.129.140.180::inst0::INSTR" # at PSI, beam area

    try:
        # Open a connection to the oscilloscope
        funGen = rm.open_resource(functionGen_address)

        # Query the instrument's identification - to ensure it's found
        idn = funGen.query('*IDN?')
        print(f"Function gen identification: {idn}")

    except Exception as e:
        print("Could not connect to function generator")
        print(e)
    else:

        # set pulse frequency, and width if you want
        # 2 Hz is about as fast as it's useful with how fast at least the tektronics scope data saving goes
        pulsefreq = 5 #Hz

        pulseWidth = 0.0002 #s, default is 0.0002 -> 200 uS
        riseEdge=0.00000002 #s, default is 0.00000002 -> 2 ns, minimum of the function gen.
        ##### remove TEST if the lamp is actually being powered instead of funct gen->caen DT directly
        SetupFunctionGen(funGen, pulsefreq=pulsefreq, pulseWidth=pulseWidth, riseEdge=riseEdge)

        ############# data taking #############
        collectN = Npulses #number of pulses to take in a dataset
        #timeBetween = 0.2 #seconds - time between datasets
        dataTakingTime = 60 #seconds - max time to take data for
        totalPulses = Npulses #for collecting a set number of pulses instead
        end_time = time() + (dataTakingTime)
        #print(f'{collectN} pulses every {timeBetween} s')
        print(f"Run started at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

        #to keep track while we loop
        data_number = 0 #total waveforms saved
        set_number = 0 #set counter

        TimePerSet = collectN*(1/pulsefreq) #actual time to run the funct. get for
        print(f'{TimePerSet} s per data set')
        
        #totalEvents=0
        """
        #was trying a different way where we check how many events midas has saved to inform 
        host = "http://localhost:8080/?mjsonrpc"
        valuePath = "/Equipment/fe5725/Statistics/Events sent"
        #print("number of events:", GetValue(host, valuePath))

        totalEvents=GetValue(host, valuePath)[0]

        first=True
        while totalEvents < totalPulses+1:
            if first==True:
                funGen.write('C1:OUTP ON')
                funGen.write('C2:OUTP ON') #turn trigger on second
                
            #check how many events have been run
            totalEvents=GetValue(host, valuePath)[0]
            print(totalEvents)

        """
        endTimeSet = time() + TimePerSet

        #start the data taking
        while time() < endTimeSet: #for time it should take for number of pulses I want

            # wait here until trigger received or time ends
            looptime = time()
            if looptime > end_time:
                break           
        
        #turn off channel 1 and 2 of function gen at end if they aren't off yet
        funGen.write('C2:OUTP OFF') #turn trigger off first
        funGen.write('C1:OUTP OFF')

        print(f"Run ended at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
        print(f"{set_number} sets, total of {data_number} waveforms")
        
    return 0 #totalEvents
