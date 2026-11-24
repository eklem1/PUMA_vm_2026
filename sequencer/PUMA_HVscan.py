import midas.sequencer
import sys
import numpy as np
import urllib
sys.path.append("/home/daq/online/userfiles/sequencer")
#import function generator control script
import FlashFunctGen as FunctGen
import TalkToODB as talk


def sequence(seq):
    note = "vac run testing. no HV control"
    #change voltage range before run - 1V=1kV
    start = 5 #negative, V    
    stop = 20
    step = 5
    HV_list = np.arange(start, stop, step)/1000 #CONVERT TO Voltage for 
    Npulses = 20
    #should it check HV and then turn on ch2 with switch?
    for HV in HV_list: #loop through HVs to use
        #set the HV
        print(HV)
        #set HV
        #sucess = talk.writeVoltage(HV)
        #if sucess != 0: #setting failed        
        HVread = talk.readVoltage()
        Iread = talk.readCurrent()
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
        host = "http://localhost:8080/?mjsonrpc"
        valuePath = "/Runinfo/Run number"
        runNumber = talk.GetValue(host, valuePath)[0] 
        
        f = open("/home/daq/online/runlogs/PUMA_runlog.txt", "a")
        f.write(f"{runNumber},{HV},{HVread},{Iread},{Npulses},{note}\n")
        f.close()
        seq.wait_seconds(10)

    
#def at_exit(seq):
    #ensure the function generator is turned off
#    if seq.obd_get("/Runinfo/State") == 3: #this fails, do we need it?
#        seq.stop_run()

"""
for getting values:
curl -v -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "db_passet_value", "params": {"path": "/Runinfo/Run numbed", "valge "values", "params": {"paths": ["/Runinfo/Run number"]}, "id": 1}' "localhost:8080

for setting values:
curl -v -s -X POST -H "Content-Type: application/json" -d '{"jsonrpc": "2.0", "method": "db_paste", "params": {"paths":[ "/Runinfo/Run number"], "values":[11]}, "id":1}' "localhost:8080/?mjsonrpc" 
"""