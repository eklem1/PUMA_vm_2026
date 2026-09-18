import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from time import *
import datetime
import os, sys

folder_path = "./PUMADAQtesting_data/26-09-17/run1-vac/" 
filename = "run1-vac_T-295.75_P-0.0_HV-30_26-09-17_waveform_set-0_pulse-1.csv" 

#folder_path = "../data/26-09-08/run3-vac/" 
#filename = "run3-vac_T-295.75_P-0.00052_HV-0_26-09-08_waveform_set-0_pulse-0.csv" 

file = folder_path+filename 

data = np.loadtxt(file, delimiter=',', skiprows=26).T 
print(len(data[0])) 
times = data[0] 
voltage1 = data[1] 
voltage2 = data[2] 

#plt.plot(range(0, len(voltage1)), voltage1*1000, label="ch1") # look at counts instead of time 

plt.plot(times*1e6, voltage1*1000, label="ch1") 
plt.xlabel("$\mu$S") 
plt.ylabel("Voltage [mV]") 

plt.plot(times*1e6, voltage2*1000, label="ch2") 

#plt.ylim(-30, 50) 

plt.legend() 
plt.show() 

 
