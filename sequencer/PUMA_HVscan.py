import midas.sequencer
import sys
import numpy as np
import urllib
sys.path.append("/home/daq/online/userfiles/sequencer")
#import function generator control script
import FlashFunctGen as FunctGen
import TalkToODB as talk
import datetime

def sequence(seq):
    note = "in liq. bigger window. post=4450. HV scan"
    #change voltage range before run - 1V=1kV. 
    #vac < 30 V
    start = 200 #postive, V    
    stop = 1950
    step = 50
    HV_list = np.arange(start, stop+step, step)/1000 #CONVERT TO Voltage for 
    Npulses = 50
    scanN = 0
    
    host = "http://localhost:8080/?mjsonrpc"
    valuePath = "/Equipment/fe5725/Settings/V1730/Post Trigger"
    postTrigger = int(talk.GetValue(host, valuePath)[0], 16) 

    #should it check HV and then turn on ch2 with switch?
    for HV in HV_list: #loop through HVs to use
        #set the HV
        print(HV)
        #set HV
        
        success=0
        if HV<(1900/1000):
            success = talk.writeVoltage(HV) #MAKE SURE YOU GIVE IT VALUES /1000 already 
            print("placeholder")       
        if success != 1: #setting failed
            message = "HV setting failed, check value and caen HV" 
            seq.wait_seconds(10)
            break
        seq.wait_seconds(2)
        
        HVread = talk.readVoltage() #V
        Iread = talk.readCurrent() #uA
        Pread = talk.readPressure() # MPa
        Tread = talk.readTemp() #K
        seq.wait_seconds(5) #might need to be even slower depending on ramp speed
        #can we record the HV value, and current, read back?
        #check voltage is correct
        #print(HVcheck)
        #start midas run

        seq.start_run()
        #start function generato
        eventsSaved = FunctGen.SingleSetFlashes(Npulses) #for set of X pulses        
        #stop midas run      
        seq.stop_run()
        
        #log run info
        
        #runNumber = seq.obd_get("/Runinfo/Run number") #this does not work
        timeNow = datetime.datetime.now()
        timeNow = timeNow.strftime('%Y%m%d_%H%M%S')       
        host = "http://localhost:8080/?mjsonrpc"
        valuePath = "/Runinfo/Run number"
        runNumber = talk.GetValue(host, valuePath)[0] 
        
        f = open("/home/daq/online/runlogs/PUMA_runlog.txt", "a")
        f.write(f"{runNumber},{timeNow},{postTrigger},{HV},{HVread},{Iread},{Pread},{Tread},{Npulses},{scanN},{note}\n")
        f.close()
        scanN = scanN+1 #to group runs
        seq.wait_seconds(2)

def at_exit(seq):
    #ensure the HV is turned off
    success = talk.writeVoltage(0.0)
#    if seq.obd_get("/Runinfo/State") == 3: #this fails, do we need it?
#        seq.stop_run()

"""
for getting values:
curl -v -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "db_passet_value", "params": {"path": "/Runinfo/Run numbed", "valge "values", "params": {"paths": ["/Runinfo/Run number"]}, "id": 1}' "localhost:8080

for setting values:
curl -v -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "db_paste", "params": {"paths":[ "/Runinfo/Run number"], "values":[11]}, "id":1}' "localhost:8080/?mjsonrpc" 
"""