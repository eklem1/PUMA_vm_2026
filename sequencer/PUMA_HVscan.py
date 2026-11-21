import midas.sequencer
import sys
import numpy as np
import urllib
sys.path.append("/home/daq/online/userfiles/sequencer")
#import function generator control script
import FlashFunctGen as FunctGen

def sequence(seq):
    #change voltage range before run
    start = 100 #negative, V    
    stop = 800
    step = 200
    HV_list = np.arange(start, stop, step) #V    
    Npulses = 10
    for HV in HV_list: #loop through HVs to use
        #set the HV
        #something like? seq.odb_set("Equipment/CAEN N472/Variables/MSCB[??]", HV)
        #use equiv to curl command to talk to main midas to control the caen HV
        
        print(HV)
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