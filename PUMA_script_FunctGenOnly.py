import pyvisa as visa
import numpy as np
from time import *
import datetime
import os, sys

'''
Don't forget to turn the sync state for channel 1 on on the function gen!!

turns on and off the function generator with no DAQ

Can run for either a set amount of time, or a set number of pulses

'''

################ functions to save data ################

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
    funGen.write('C1:BSWV HLEV 6') #unit is V
  
    # Low level : 0 V 
    funGen.write('C1:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    funGen.write(f'C1:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    funGen.write(f'C1:BSWV RISE,{riseEdge}') #unit is s
    funGen.write('C1:OUTP ON,PLRT,NORM')
    #funGen.write('C1:BSWV OFST,0') #V
    # query the waveform
    q = funGen.query('C1:BSWV?')
    print(q)
    
    ## set up channel 2 for triggering on
    funGen.write('C2:BSWV WVTP,PULSE')
    funGen.write(f'C2:BSWV FRQ,{pulsefreq}') #unit is Hzc
    funGen.write('C2:BSWV HLEV,1.9') #unit is V
    # Low level : 0 V s
    funGen.write('C2:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    funGen.write(f'C2:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    funGen.write(f'C2:BSWV RISE,{riseEdge}') #unit is s
    funGen.write('C2:OUTP ON,PLRT,INVT') #invert channel output
    q = funGen.query('C2:BSWV?')
    print(q)
    
    funGen.write('COUP FCOUP,ON')
    funGen.write('COUP PCOUP,ON')
    
    return
    
# setup function for the siglent SGD 
def SetupFunctionGenTEST(funGen, pulsefreq = 2, pulseWidth = 0.0002, riseEdge=0.00000002 ):

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
    #funGen.write('C1:BSWV HLEV,6') #unit is V
    funGen.write('C1:BSWV HLEV,1') #changed just for daq testing
    # Low level : 0 V 
    funGen.write('C1:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    funGen.write(f'C1:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    funGen.write(f'C1:BSWV RISE,{riseEdge}') #unit is s
    #funGen.write('C1:OUTP ON,PLRT,INVT')
    #funGen.write('C1:BSWV OFST,0') #V
    # query the waveform
    q = funGen.query('C1:BSWV?')
    print(q)
    
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


################ main ################

##### Connect to function generator #####

# #check what is connected and print them out - helpful for finding the addresses
# Create a VISA resource manager
rm = visa.ResourceManager()
print(rm.list_resources())

# connect to function generator
# functionGen_address = "USB0::0xF4EC::0x1101::SDG6XFCQ6R0795::INSTR" #USB connection
#functionGen_address = "TCPIP::10.0.0.9::inst0::INSTR" #siglent funct gen, on triumf labnet, ethernet
#functionGen_address = "TCPIP::129.129.141.91::inst0::INSTR" # at PSI, west side?
#functionGen_address = "TCPIP::129.129.140:177::inst0::INSTR" # at PSI, should be static now, east side - NOT WORKING, WHY??
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
    
# set pulse frequency, and width if you want
# 2 Hz is about as fast as it's useful with how fast at least the tektronics scope data saving goes
pulsefreq = 5.0 #Hz

pulseWidth = 0.0002 #s, default is 0.0002 -> 200 uS
riseEdge=0.00000002 #s, default is 0.00000002 -> 2 ns, minimum of the function gen.
SetupFunctionGen(funGen, pulsefreq=pulsefreq, pulseWidth=pulseWidth, riseEdge=riseEdge)

funGen.write('C2:OUTP ON')
funGen.write('C1:OUTP ON')
#sleep(10)
#funGen.write('C2:OUTP OFF')

"""
############# data taking #############
collectN = 10 #number of pulses to take in a dataset
timeBetween = 10 #60*5 #seconds - time between datasets
dataTakingTime = 30 #seconds - time to take data for
totalPulses = 20 #for collecting a set number of pulses instead
end_time = time() + (dataTakingTime)
print(f'Taking data for {dataTakingTime} s ({dataTakingTime/60:.2} min), {collectN} pulses every {timeBetween} s')
print(f"Run started at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

# omitted in this script: the loop for reading from the scope that somehow checks if the function gen is done all it's cycles or not

#to keep track while we loop
data_number = 0 #total waveforms saved
set_number = 0 #set counter

#pulsefreq
TimePerSet = collectN*(1/pulsefreq)
print(f'{TimePerSet} s per data set')

funGen.write('C1:OUTP ON')
funGen.write('C2:OUTP ON')

endTimeSet = time() + TimePerSet

#start the data taking
while time() < end_time: #for set time
#while data_number < totalPulses: #for set number of pulses
    
    if time() >= endTimeSet:
        #new data set now
        funGen.write('C2:OUTP OFF')
        funGen.write('C1:OUTP OFF') 
        
        print(f"set-{set_number} done")

        data_number += 1*collectN #total waveforms saved
        set_number += 1
        sleep(timeBetween) #this will be our interval we wait between sets
        funGen.write('C1:OUTP ON')
        funGen.write('C2:OUTP ON')
        endTimeSet = time()+TimePerSet

    else:
        # wait here until trigger received or time ends
        looptime = time()
        if looptime > end_time:
            break          

#turn off channel 1 and 2 of function gen at end if they aren't off yet
funGen.write('C2:OUTP OFF')
funGen.write('C1:OUTP OFF')

print(f"Run ended at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
print(f"{set_number} sets, total of {data_number} waveforms")
"""
