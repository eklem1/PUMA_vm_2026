#runs PUMA at a set HV value every X seconds for a given amount of time
import midas.sequencer
import sys
import numpy as np
import urllib
import datetime
import time as time
sys.path.append("/home/daq/online/userfiles/sequencer")
#import function generator control script
import FlashFunctGen as FunctGen
import TalkToODB as talk
import datetime

def sequence(seq):
    note ="time scan in liq"
    #will run at one set HV
    setHV = 1900/1000 #, V  CONVERT TO /1000  
    Npulses = 50
    timeBetween = 5*60 #seconds - time between datasets
    dataTakingTime = 1*60*60 #seconds - total time to take data for
    end_time = time.time() + (dataTakingTime) #based on that, when does data taking stop?    
    runinfo=f"Taking {Npulses} pulses at HV={setHV} V every {timeBetween} sec, until {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
   
    host = "http://localhost:8080/?mjsonrpc"
    valuePath = "/Equipment/fe5725/Settings/V1730/Post Trigger"
    postTrigger = int(talk.GetValue(host, valuePath)[0], 16)
    
    scanN = 0
    
    #set HV
    if setHV<(1950/1000):
            success = talk.writeVoltage(setHV) #MAKE SURE YOU GIVE IT VALUES /1000 already 
            print("try")       
    if success != 1: #setting failed
            message = "HV setting failed, check value and caen HV" 
            seq.wait_seconds(10)
    else:
        seq.wait_seconds(10)
    
        while time.time() < end_time: #for set time
        
            #can we record the HV value, and current, read back
            HVread = talk.readVoltage() #V
            Iread = talk.readCurrent() #uA
            Pread = talk.readPressure() # MPa
            Tread = talk.readTemp() #K
            #check voltage is correct  still to ensure no one changed it by accident
            #print(HVcheck)
        
            #start midas run
            seq.start_run()
            #start function generator
            FunctGen.SingleSetFlashes(Npulses) #for set of X pulses        
            #stop midas run      
            seq.stop_run()
            
            timeNow = datetime.datetime.now()
            timeNow = timeNow.strftime('%Y%m%d_%H%M%S')
            host = "http://localhost:8080/?mjsonrpc"
            valuePath = "/Runinfo/Run number"
            runNumber = talk.GetValue(host, valuePath)[0] 
        
            f = open("/home/daq/online/runlogs/PUMA_runlog.txt", "a")
            f.write(f"{runNumber},{timeNow},{postTrigger},{setHV},{HVread},{Iread},{Pread},{Tread},{Npulses},{scanN},{note}\n")
            f.close()
            scanN = scanN+1 #to group runs
        
            seq.wait_seconds(timeBetween)
    
    endinfo=f"Run ended at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
    
def at_exit(seq):
    #ensure the HV is turned off
    success = talk.writeVoltage(0.0)
#    if seq.obd_get("/Runinfo/State") == 3: #this fails, do we need it?
#        seq.stop_run()