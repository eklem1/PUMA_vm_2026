import pyvisa as visa
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from time import *
import datetime
import os, sys

'''
On emma's labtop to start the python enviro: source ~/enviros/venv_jlab/bin/activate

Don't forget to turn the sync state for channel 1 on on the function gen!!

things I could add:
- pop out/saved plot of the current waveform - would be nice to actually see what is going on

'''


################ functions to save data ################

# function for the Tektronix scope 
def SetupTektronic(scope, timescale=5, delay=25, ch1Scale=50, ch1Pos=1, ch2Scale=50, ch2Pos=-2, 
                TrgScale=500, VsetTrig=500):
    '''
    Setting up the Tektronic scope
    '''
    #time scale set
    # timescale = 4 #us
    scope.write(f"HORizontal:SCAle {timescale/1e6}") #s
    # HORIZONTAL:SCALE 2E-6 sets the main scale to 2µs per division.

    # delay = 15 #us
    scope.write(f"HORizontal:DELay:TIMe {delay/1e6}") #s

    #set Ch1 vertical scale
    setChn = "CH1"
    # ch1Scale = 200 #mV
    scope.write(f"{setChn}:SCAle {ch1Scale/1000}") #V

    #set Ch1 vertical position
    # ch1Pos = 1 #number of Div
    scope.write(f"{setChn}:POSition {ch1Pos}") #div

    #set Ch2 vertical scale
    setChn = "CH2"
    # ch2Scale = 200 #mV
    scope.write(f"{setChn}:SCAle {ch2Scale/1000}") #V

    #set Ch2 vertical position
    # ch1Pos = -2 #number of Div
    scope.write(f"{setChn}:POSition {ch2Pos}") #div

    #cset up acq and trigger set up here automatically
    setChn = "CH4" #this should really be channel 4
    # TrgScale = 200 #mV
    scope.write(f"{setChn}:SCAle {TrgScale/1000}") #V
    #set scope to single SEQ mode
    scope.write("ACQuire:STOPAfter SEQuence")
    #Specifies that this will be an edge trigger 
    scope.write("TRIGger:A:TYPe EDGE")
    # Specifies the channel as the source waveform.
    scope.write(f"TRIGger:A:EDGE:SOUrce {setChn}")
    scope.write("TRIGger:A:EDGE:SLOpe FALL")

    # Specifies (1.4) volts as the threshold level.
    # VsetTrig = 500 #mV
    scope.write(f"TRIGger:A:LEVel:{setChn} {VsetTrig/1000}")

    print("Trigger set to: ", scope.query("TRIGger:A:EDGE:SLOpe?").rstrip(), 
                scope.query(f"TRIGger:A:LEVel:{setChn}?").rstrip(), "V")

    return

# function for the Tektronix scope 
def convertToWave(datac, scal_info):
    """
    Converts raw data that is output by query_binary_values to the corrected
    time and voltage steps, and returns them as a 2D np.array. This requires the 
    scaling information from the scope, read in through the dictionary scal_info.

    input:
        datac: 1D array that is the output from query_binary_values()
        scal_info: dictionary with scope scaling details
    output:
        2D np.array of the converted data: [[time in s,] [voltages in V]]
    """

    x = []
    y = []
    for i in range(0,len(datac)):
        # print()
        x.append((i-(len(datac)*(scal_info['HPos']/100)))* scal_info['xincr'] + scal_info['HDelay'])
        y.append(((datac[i]-scal_info['yoff']) * scal_info['ymult']) + scal_info['yzero'])
        
    return np.array([x,y])

# function for the Tektronix scope 
def saveData(oscilloscope, name, note=""):
    """
    input:
        oscilloscope: object holding the connection to the oscilloscope to read from
        name: str of full path name of file to save to, without file type extension
        number: int/str of the data set number to added to the end of the name
    output:
        None
    """
    #save the timestamp
    timeNow = datetime.datetime.now()
    timeNow = timeNow.strftime('%Y%m%d_%H%M%S')

    csv_file_path = f'{name}.csv'
    csv_file_path_raw = f'{name}_raw.csv'

    # Configure and query waveform data
    oscilloscope.write('DAT:ENC RPB')  # Set data encoding to binary
    oscilloscope.write('DAT:WID 1')    # Set data width to 1 byte
    oscilloscope.write('DAT:STAR 1')   # Set start of data to first byte
    dateLength = 10000 #but will be limited by the record length set on the scope really
    oscilloscope.write(f'DAT:STOP {dateLength}') # Set end of data to 10,000th byte
    # oscilloscope.write(f"DATA:SOURCE {channel_id}") #change channel source being used
    
    # Only one waveform can be transferred at a time.
    #first do channel 1
    channel_id = "CH1"
    oscilloscope.write(f"DATA:SOURCE CH1") #change channel source being used
    raw_waveform_data = oscilloscope.query_binary_values('CURV?', datatype='B', container=np.array)

    #get data for converting the waveform
    info = oscilloscope.query('WFMOutpre?') 
    info = info.split(",")
    VerticalScale_1 = info[2]
    VerticalPos = info[3]
    infoSplit = info[-1].split(";")
    xincr = float(infoSplit[5])

    #Vertical scale multiplying factor
    ymult = float(infoSplit[9])
    #Vertical position of the source waveform in digitizing levels
    yoff = float(infoSplit[10])
    yzero_1 = float(infoSplit[11])
    Hscale = float(oscilloscope.query("HOR:SCA?"))
    HDelay = float(oscilloscope.query("HORizontal:DELay:TIMe?"))
    HPos = float(oscilloscope.query("HORIZONTAL:POSITION?"))

    #Other info for the header
    Vunits = infoSplit[8]
    Hunits = infoSplit[4]
    waveType = infoSplit[13]
    pointsFormat = infoSplit[2]
    ProbeA = int(float(oscilloscope.query("TRIGger:EXTernal:PRObe?").rstrip()))
    firmware = idn.split()[1].split(",")[-1]

    headerInfo = {
        'Model': idn.strip(),
        'Channel': channel_id,      
        'xincr': xincr,
        'ymult': ymult, 
        'yoff': yoff, 
        'yzero': yzero_1,
        'Hscale': Hscale, 
        'HDelay': HDelay, 
        'HPos': HPos
    }

    #convert to [time [s], voltage [V]] using the scope settings
    waveform_data_ch1 = convertToWave(raw_waveform_data, headerInfo)

    #then do channel 2
    channel_id = "CH2"
    oscilloscope.write(f"DATA:SOURCE CH2") #change channel source being used
    raw_waveform_data = oscilloscope.query_binary_values('CURV?', datatype='B', container=np.array)
  
    #get data for converting the waveform
    info = oscilloscope.query('WFMOutpre?') 
    info = info.split(",")
    VerticalScale_2 = info[2]
    VerticalPos = info[3]
    infoSplit = info[-1].split(";")
    xincr = float(infoSplit[5])

    #Vertical scale multiplying factor
    ymult = float(infoSplit[9])
    #Vertical position of the source waveform in digitizing levels
    yoff = float(infoSplit[10])
    yzero_2 = float(infoSplit[11])
    Hscale = float(oscilloscope.query("HOR:SCA?"))
    HDelay = float(oscilloscope.query("HORizontal:DELay:TIMe?"))
    HPos = float(oscilloscope.query("HORIZONTAL:POSITION?"))

    #Other info for the header
    Vunits = infoSplit[8]
    Hunits = infoSplit[4]
    waveType = infoSplit[13]
    pointsFormat = infoSplit[2]
    ProbeA = int(float(oscilloscope.query("TRIGger:EXTernal:PRObe?").rstrip()))
    firmware = idn.split()[1].split(",")[-1]

    headerInfo = {
        'Model': idn.strip(),
        'Channel': channel_id,      
        'xincr': xincr,
        'ymult': ymult, 
        'yoff': yoff, 
        'yzero': yzero_2,
        'Hscale': Hscale, 
        'HDelay': HDelay, 
        'HPos': HPos
    }

    #convert to [time [s], voltage [V]] using the scope settings
    waveform_data_ch2 = convertToWave(raw_waveform_data, headerInfo)

    #Add channel 2 data to the csv
    # waveform_data = np.concatenate((waveform_data_ch1, waveform_data_ch2[0]))
    #the time array should be exactly the same, so we don't need to save that again
    waveform_data = np.append(waveform_data_ch1, [waveform_data_ch2[1]], axis=0)

    #need to update this to work for ch1 & 2 settings
    headerInfo_forCSV = {
        "#Notes: ": note,
        'TimeStamp': timeNow,
        'Model': idn.split(",")[1],
        'Firmware Version': firmware,    
        '':'',  
        'Waveform Type': waveType,
        'Point Format': pointsFormat, 
        'Horizontal Units': Hunits.split('"')[1], 
        'Horizontal Scale': Hscale,
        'Horizontal Delay': HDelay, 
        'Sample Interval': xincr, 
        'Record Length': dateLength,
        'Gating': "NA",
        'Probe Attenuation': ProbeA,
        'Vertical Units': Vunits.split('"')[1],
        'Vertical CH1 Offset': yzero_1,
        'Vertical CH1 Scale': VerticalScale_1,
        'Vertical CH1 Position': 'NA',
        'Vertical CH2 Offset': yzero_2,
        'Vertical CH2 Scale': VerticalScale_2,
        'Vertical CH2 Position': 'NA'
    }

    #save just the raw reading
    np.savetxt(csv_file_path_raw, raw_waveform_data, delimiter=",")

    #and the fully converted waveform
    #header info
    (pd.DataFrame.from_dict(data=headerInfo_forCSV, orient='index').to_csv(csv_file_path, header=False, mode='w'))

    #the data
    with open(csv_file_path,'a') as f:
        subheader = np.array([["","", ""], ["","", ""], ["","", ""], 
                              ["Label","", ""],
                              ["TIME [s]","CH1 [V]", "CH2 [V]"]])

        np.savetxt(f,subheader, delimiter=",", fmt="%s")
        np.savetxt(f,waveform_data.T, delimiter=",")

    print(f"Waveform data saved to {csv_file_path}")

    return

# setup function for the siglent SGD 
def SetupFunctionGen(funGen, pulsefreq = 2, pulseWidth = 0.0002, riseEdge=0.00000002 ):
    # pulsefreq = 1 #unit is Hz
    #set up the waveform we want
    #set to pulse type
    funGen.write('C1:BSWV WVTP,PULSE')
    # Frequency: 2 Hz 
    funGen.write(f'C1:BSWV FRQ,{pulsefreq}') #unit is Hz
    # Use low/high levels (and not Amplitude) 
    #I think this sets the high/low levels correctly - there seems to be be no definite switch you do
    # High level: 6 V 
    funGen.write('C1:BSWV HLEV,6') #unit is V
    # Low level : 0 V 
    funGen.write('C1:BSWV LLEV,0')
    # Pulse width: 200 us  
    # pulseWidth = 0.0002
    funGen.write(f'C1:BSWV WIDTH,{pulseWidth}') #unit is s
    # Rise edge: 20 ns 
    # riseEdge=0.00000002
    funGen.write(f'C1:BSWV RISE,{riseEdge}') #unit is s
    # #query the waveform
    q = funGen.query('C1:BSWV?')
    # print(q)
    
    ## set up channel 2 for triggering on
    funGen.write('C2:BSWV WVTP,PULSE')
    #funGen.write(f'C2:BSWV FRQ,{pulsefreq}') #unit is Hzc
    funGen.write('C2:BSWV HLEV,1') #unit is V
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

### to be function for the lecroy scope
def saveDataLecroy(ChA, CHB):
    '''
    This should read out 2 channels of the scope, and save them
    '''

    return 0 

################ main ################

#date to save data to - default is todays date
today = datetime.datetime.now()
d1 = today.strftime("%y-%m-%d")

#general run name
Filename = f"run5-GAr"

#add other info, V, P, T
T_set = 295.75 #K
P_set = 0.28#torr
HV_set = 480 #V

ch1scaleSet= 50
ch2scaleSet= 50

# run2_Filling_T-195_P-780_HV-1700_2025-01-28_0_113456

folder = f"./PUMADAQtesting_data/{d1}/{Filename}/"

#putting all the naming and folder together
name = f"{folder}{Filename}_T-{T_set}_P-{P_set}_HV-{HV_set}_{d1}_"

isExist = os.path.exists(folder)
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs(folder)
   print(f"Creating folder: {folder}")

##### Now connect to the electronics #####

# #check what is connected and print them out - helpful for finding the addresses
# Create a VISA resource manager
rm = visa.ResourceManager()
print(rm.list_resources())

# connect to scope
# Replace 'USB0::0x0699::0x0363::C065087::INSTR' with your instrument's VISA address
# oscilloscope_address = "USB0::0xF4EC::0xEE38::SDSMMGKQ7R4922::INSTR" #siglent scope beign used for PUMA at triumf
# oscilloscope_address = "USB0::0x0699::0x0401::C011659::INSTR" #tektronix scope
oscilloscope_address = "TCPIP::10.0.0.8::inst0::INSTR" #tektronix scope, on triumf labnet, ethernet

# oscilloscope_address = "?" #scope in electronics lab
# oscilloscope_address = "TCPIP::142.90.115.154::inst0::INSTR" 

try:
    # Open a connection to the oscilloscope
    scope = rm.open_resource(oscilloscope_address)

    # Query the instrument's identification - to ensure it's found
    idn = scope.query('*IDN?')
    print(f"Scope identification: {idn}")

except Exception as e:
    print("Could not connect to scope")
    print(e)

# saveData(scope, "test", note="Just testing with the Tektronic scope, \n#Presure 0, ")

# set the range of the scope, V/div and s/Div
# Time scale: 5 us/div 
# Decay: 25 us 
# Ch1: 50 mV/div 
# Ch2: 50 mV/div 
# Ch3: 500 mV/div 
# Trigger on ch4, level: 500 mV 
# scope.write(f"TRIGger:SOUrce 4")
# scope.write(f"TRIGger:A:LEVel 4") - prob doesn't work
# set up the trigging of the scope off of channel 4

#for the tektronic scope setup
# set scaling and offset
'''
defaults: 
    Time scale: 5 us/div 
    Decay: 25 us 
    Ch1: 50 mV/div 
    Ch2: 50 mV/div 
    Ch3: 500 mV/div 
    Trigger on ch4, level: 500 mV 
'''

SetupTektronic(scope, timescale=2, delay=8, ch1Scale=ch1scaleSet, ch1Pos=-3,
                ch2Scale=ch2scaleSet, ch2Pos=0, 
                TrgScale=200, VsetTrig=-150)


# connect to function generator
# functionGen_address = "USB0::0xF4EC::0x1101::SDG6XFCQ6R0795::INSTR"
functionGen_address = "TCPIP::10.0.0.9::inst0::INSTR" #siglent funct gen, on triumf labnet, ethernet

try:
    # Open a connection to the oscilloscope
    funGen = rm.open_resource(functionGen_address)

    # Query the instrument's identification - to ensure it's found
    idn = funGen.query('*IDN?')
    print(f"Function gen identification: {idn}")

except Exception as e:
    print("Could not connect to function generator")
    print(e)

#set pulse frequency, and width if you want
# 2 Hz is about as fast as it's useful with how fast at least the tektronics daat saving goes
SetupFunctionGen(funGen, pulsefreq = 1)


############# data taking #############
collectN = 10 #number of pulses to take in a dataset
timeBetween = 5 #seconds - time between datasets
dataTakingTime = 30 #seconds - time to take data for

end_time = time() + (dataTakingTime)
print(f"Taking data for {dataTakingTime} s ({dataTakingTime/60:.2} min), {collectN} pulses every {timeBetween} s")
print(f"Run started at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")

# make a a big loop for reading from the scope that somehow checks if the function gen is done all it's cycles or not

#to keep track while we loop
data_number = 0 #total waveforms saved
pulse_number = 0 #pulse counter -> per dataset
set_number = 0 #set counter

funGen.write('C2:OUTP ON')
funGen.write('C1:OUTP ON')

firstTrigger=True
totalPulses = 10

#start the data taking
# while time() < end_time: #for set time
while data_number < totalPulses: #for set number of pulses
    #start the acquiring mode
    scope.write("ACQ:STATE RUN")
    waiting = 1
    looptime = time()
    triggertime = time()

    #so do X pulses at once here - leave the pulser on until I get X?
    #turn on the function gen
    #turn on channel 1 on function gen
    

    # wait here until trigger received or time ends
    while (waiting == 1):
        #returns 1 if in acquiring mode, 0 if stopped
        waiting = int(scope.query("ACQ:STATE?"))
        # print("waiting...", waiting)

        #later
        if waiting == 0:
            # Saved the data as CSV file if the acquisition has stopped
            if firstTrigger==True:
                firstTrigger=False
                print("skip")
            else:
                trigger = scope.query("TRIGGER:STATE?").rstrip()
                print(f"acquisition stopped, {trigger}")
                print(f"set-{set_number}_pulse-{pulse_number}")

                #need to figure out how to actually save the data - and quickly
                    # csv_file_path = f'{name}_waveform_{number}.csv'
                nameSingle = f"{name}waveform_set-{set_number}_pulse-{pulse_number}"
                saveData(scope, nameSingle)

                data_number += 1 #total waveforms saved
                pulse_number += 1 #pulse counter
                # triggertime = time()

        looptime = time()
        if looptime > end_time:
            if scope.query("TRIGGER:STATE?").rstrip() == 'REA':
                print("No trigger event for finale capture")
            break

        if pulse_number == collectN:
            # now wait for X amount of time before starting a new set
            print(f"Set {int(set_number)} complete.")
            #turn off the pulser
            funGen.write('C1:OUTP OFF') 
            pulse_number = 0
            firstTrigger=True
            waiting = 1 #reset to wating
            set_number += 1
            sleep(timeBetween) #this will be our interval we wait between sets
            funGen.write('C1:OUTP ON')


#turn off channel 1 of function gen
funGen.write('C1:OUTP OFF')
funGen.write('C2:OUTP OFF')

print(f"Run ended at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}")
print(f"{set_number} sets taken, total of {data_number} waveforms")
