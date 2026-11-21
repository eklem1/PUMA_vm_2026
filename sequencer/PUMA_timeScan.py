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

def sequence(seq):
    #will run at one set HV
    setHV = 20 #negative, V    
    Npulses = 10
    timeBetween = 5*60 #seconds - time between datasets
    dataTakingTime = 10*60 #seconds - total time to take data for
    end_time = time.time() + (dataTakingTime) #vased on that, when does data taking stop    
    runinfo=f"Taking {Npulses} pulses at HV={setHV} V every {timeBetween} sec, until {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
    
    while time.time() < end_time: #for set time
        
        #can we record the HV value, and current, read back?
        #check voltage is correct  still to ensure no one changed it by accident
        #print(HVcheck)
        
        #start midas run
        seq.start_run()
        #start function generator
        FunctGen.SingleSetFlashes(Npulses) #for set of X pulses        
        #stop midas run      
        seq.stop_run()
        
        seq.wait_seconds(timeBetween)
    
    endinfo=f"Run ended at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}"
    
def at_exit(seq):
    #ensure the HV is turned off
    print()
#    if seq.obd_get("/Runinfo/State") == 3: #this fails, do we need it?
#        seq.stop_run()