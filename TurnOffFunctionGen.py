import pyvisa as visa 
from time import * 
import datetime 
import os, sys 

''' 
Just a little script to ensure the function gen is turned off 
'''

# Create a VISA resource manager 
rm = visa.ResourceManager() 

#functionGen_address = "TCPIP::129.129.141.91::inst0::INSTR" # at PSI, west side?
functionGen_address = "TCPIP::129.129.140.180::inst0::INSTR" # at PSI, beam area

try: 
    # Open a connection to the oscilloscope 

    funGen = rm.open_resource(functionGen_address) 

    # Query the instrument's identification - to ensure it's found 
    idn = funGen.query('*IDN?') 
    print(f"Function gen identification: {idn.rstrip()}") 

except Exception as e: 
    print(e) 
    print("Could not connect to function generator, exiting program.") 
    sys.exit() 

funGen.write('C1:OUTP OFF')
funGen.write('C2:OUTP OFF')
#funGen.write("OUTPut:TRIGger OFF") 
#funGen.write("SOURce1:BURSt:STATe OFF") 

print("Funct gen CH1 and CH2 should now be turned off") 
