'''
Emma Klemets, Sept 2026

Basic plotting and signal analysis for PUMA - new analysis for 2026 runs
'''
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy as sp
from datetime import datetime, timedelta
from scipy.optimize import curve_fit
import matplotlib as mpl

##################### constants #################################

dateparse = lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

# convert area to charge using calibration for each side
# Trans-impedance is 213 kOhm for amplifier ch.1 and 207 kOhm for ch.2.
ch1_TImpedance = 213 #kOhm # was prev 223?
ch2_TImpedance = 207 #kOhm # was prev 216?

# drift regions
d2 = 3.88 #cm
d1 = d3 = 0.16 #cm
dtotal_averaged = d2 + (d1+d3)/2

def returnX(x):
    return x

##################### functions #################################

def SingleRaw_Plot(fileName, path, View=False, saveType=None):
    '''
    Get plot of all N anode and cathode signals recorded
    '''
        # timeStamp=pd.read_csv(f"{path}/{fileName}",usecols=[0],date_format='%Y%m%d_%H%M%S',
    #                     sep='\t',header=None, skiprows=1, nrows=1)
    # timeStamp=timeStamp.loc[0, 0]
    # timeStamp = datetime.strptime(timeStamp, '%Y%m%d_%H%M%S')
    # print(timeStamp)
    
    # #get how many flashes were taken
    # NDatapoints = len(np.loadtxt(f"{path}/{fileName}", skiprows=2, max_rows=1))
    # nFlashes = int(NDatapoints/2)
    
    # #load the timing in the 1st row, without the time stamp
    # times = np.loadtxt(f"{path}/{fileName}", skiprows=1, usecols=np.arange(1,NDatapoints+1,1), max_rows=1)
    
    # #and load the voltages
    # voltages = np.loadtxt(f"{path}/{fileName}", skiprows=2)
    
    # plt.plot(voltages[:,:nFlashes], color='orange', alpha=0.2, label="cathode signal")
    # plt.plot(voltages[:,nFlashes:], color='blue', alpha=0.2, label="anode signal")
    
    # handles, labels = plt.gca().get_legend_handles_labels()
    # by_label = dict(zip(labels, handles))
    # plt.legend(by_label.values(), by_label.keys())

    # file = folder_path+filecheck

    file_names = os.listdir(path)

    file_names = [f for f in file_names if not f.endswith("bad.csv")]
    file_names = [f for f in file_names if not f.endswith("raw.csv")]
    file_names = [f for f in file_names if f.startswith(fileName)]
    file_names = [f for f in file_names if f.endswith("csv")]

    nFlashes = int(len(file_names))

    for file in file_names:
        data = np.loadtxt(path+file, delimiter=',', skiprows=26).T
        times = data[0]
        voltage1 = data[1]
        voltage2 = data[2]
    
        plt.plot(range(0, len(voltage1)), voltage1*1000, color='orange', alpha=0.2, label="ch1")
        plt.xlabel("$\\mu$S")
        plt.ylabel("Voltage [mV]")
        
        plt.plot(range(0, len(voltage2)), voltage2*1000, color='blue', alpha=0.2, label="ch2")
   
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys())
    
    plt.xlabel("Channel #")
    plt.ylabel("Voltage [V]")
    plt.title(f"Signal for {nFlashes} flashes\n{fileName}")
    plt.grid()
    if saveType is not None:
        plt.savefig(f"{path}/{fileName.split('.')[0]}-rawSignals.{saveType}")
    
    if View:
        plt.show()
    else:
        plt.close()
    return
    
"""
def SingleProcessed_Plot(fileName, path, View=False, saveType='pdf'):
    '''
    Get plot of processed signal for the anode and cathode, and print out
    of total charges and their ratio.
    '''
    timeStamp=pd.read_csv(f"{path}/{fileName}",usecols=[0],
                        sep='\t',header=None, skiprows=1, nrows=1)
    timeStamp=timeStamp.loc[0, 0]
    # print(timeStamp)

    #skipping the first line of data with an extra col
    # data = np.loadtxt(f"{path}/{fileName}", skiprows=2)
    
    endPed = 3000
    processedSignalData = ProcessDataset(f"{path}/{fileName}", endPed=endPed)
    
    timing, voltageCh1, voltageCh2, areaCh1, \
    areaCh2, chargeCh1, chargeCh2, chargeRatio = processedSignalData

    print(f"Cathode chage is {chargeCh1:.3f} pC, anode is {chargeCh2:.3e} pC, ratio is {chargeRatio*100:.1f} %")
    
    #plotting
    fig = plt.figure(figsize=(6, 4))
    plt.plot(timing, voltageCh1, label="cathode", color='salmon', alpha=0.8)
    plt.plot(timing, voltageCh2, label="anode", color='royalblue', alpha=0.8)
    plt.axvspan(0, timing[endPed], label="pedestal sample", color='grey', alpha=0.2)
    
    plt.legend()
    plt.xlabel("time [$\\mu$s]")
    plt.ylabel("Voltage [mV]")
    plt.title(f"Processed signal/{fileName}")
    # plt.xlim()
    # plt.ylim(-10,40)
    plt.tight_layout()
    plt.savefig(f"{path}/{fileName.split('.')[0]}-processedSignal.{saveType}")

    if View:
        plt.show()
    
    return
"""

def HV_to_E(HV):
    '''
    Using the values I currently have in efield.xlsx, calculate the 
    electric field in drift region 3 based on a given HV.
    - The distance d needs to be checked
    '''
    
    RTot = 1209.7 #MOhms
    current = HV/RTot #uA

    d = 0.735 #cm
    Vdrop_drift3 = 196*current #V
    E_drift3 = Vdrop_drift3/d #V/cm
    return E_drift3


# Function to calculate pulse area
def calculate_pulse_area(time_interval, voltages):
    # area = np.trapz(voltages, dx=time_interval) #old np
    area = np.trapezoid(voltages, dx=time_interval)
    return area


# Function to find the pedestal
def find_pedestal(voltages, start_index, end_index):
    return np.mean(voltages[start_index:end_index])


def lorentzian(x, A, x0, gamma ):
    return A * gamma**2 / ( gamma**2 + ( x - x0 )**2)

def lorentzian_param(x, parms, Err=False):
    lor = parms['A'] * parms['gamma']**2 / ( parms['gamma']**2 + ( x - parms['x0'] )**2)
    if Err:
        lor_up = (parms['A']+parms['A err']) * (parms['gamma']+parms['gamma err'])**2 / ( (parms['gamma']+parms['gamma err'])**2 + ( x - (parms['x0']+parms['x0 err']) )**2)
        lor_down = (parms['A']-parms['A err']) * (parms['gamma']-parms['gamma err'])**2 / ( (parms['gamma']-parms['gamma err'])**2 + ( x - (parms['x0']-parms['x0 err']) )**2)
        
        lor = [lor, lor_up-lor, lor_down-lor]

    return lor

def CrystalBall_funct(x, C, alpha, N, sigma, mean):
    x = -x
    mean = -mean
    # crystalball.pdf(x, beta, m, loc, scale)
    CB = C * sp.stats.crystalball.pdf(x, beta=alpha, m=N, loc=mean, scale=sigma)
    return CB


def CrystalBall_param(x, parms, Err=False):
    x = -x
    mean = -parms['mean']
    # crystalball.pdf(x, beta, m, loc, scale)
    CB = parms['C'] * sp.stats.crystalball.pdf(x, beta=parms['alpha'], m=parms['N'], loc=mean, scale=parms['sigma'])
    
    if Err:

        CB_up = (parms['C']+parms['C err']) * sp.stats.crystalball.pdf(x, beta=(parms['alpha']+parms['alpha err']), m=(parms['N']+parms['N err']), loc=( -parms['mean']+parms['mean err']), scale=(parms['sigma']+parms['sigma err']))

        CB_down = (parms['C']-parms['C err']) * sp.stats.crystalball.pdf(x, beta=(parms['alpha']-parms['alpha err']), m=(parms['N']-parms['N err']), loc=( -parms['mean']-parms['mean err']), scale=(parms['sigma']-parms['sigma err']))

        CB = [CB, CB_up-CB, CB_down-CB]
        
    return CB
    
def chiSquared(funct, x, y, popt, sigma=1):
    
    r = y - funct(x, *popt)
    chisq = sum((r / sigma) ** 2)
    Redchisq = chisq/(len(x) - len(popt))

    return chisq, Redchisq

def FitData(processedSignalData):
    timing, voltageCh1, voltageCh2, areaCh1, \
    areaCh2, chargeCh1, chargeCh2, chargeRatio, signalStart, anodeStart = processedSignalData

    AnalysisStats = AnalysisDataset(processedSignalData)
    
    Ch1Max_index, Ch2Min_index, DeltaT, Vdr, eLifetime = AnalysisStats
    
    #first fit lorentzian for initial guesses
    p0 = [voltageCh1[signalStart+Ch1Max_index], timing[signalStart+Ch1Max_index], 1]
    popt, pcov = curve_fit(lorentzian, timing[signalStart:], voltageCh1[signalStart:], p0=p0)

    #then fit crystalBall, but with flipped x axis, for the cathode
    # C, alpha, N, sigma, mean
    p0 = [voltageCh1[signalStart+Ch1Max_index], 1, 10, popt[2], timing[signalStart+Ch1Max_index]]
    # print(p0)
    popt, pcov = curve_fit(CrystalBall_funct, timing[signalStart:], voltageCh1[signalStart:], p0=p0)
    chisq, Redchisq =  chiSquared(CrystalBall_funct,  timing[signalStart:], voltageCh1[signalStart:], popt)

    errors = np.sqrt(np.diag(pcov))
    fit_data_cathode = {'C': popt[0], 'C err': errors[0], 
                'alpha': popt[1], 'alpha err': errors[1],
                'N': popt[2], 'N err': errors[2],
                'sigma': popt[3], 'sigma err': errors[3],
                'mean': popt[4], 'mean err': errors[4],
                'chisqr': chisq,  'Redchisqr': Redchisq 
               }

    #fit a Lorentzian for the anode signal
    p0 = [voltageCh2[anodeStart+Ch2Min_index], timing[anodeStart+Ch2Min_index], 1]
    popt, pcov = curve_fit(lorentzian, timing[anodeStart:], voltageCh2[anodeStart:], p0=p0)
    chisq, Redchisq =  chiSquared(lorentzian, timing[anodeStart:], voltageCh2[anodeStart:], popt)
    
    errors = np.sqrt(np.diag(pcov))
    fit_data_anode = {'A': popt[0], 'A err': errors[0], 
                'x0': popt[1], 'x0 err': errors[1],
                'gamma': popt[2], 'gamma err': errors[2],
                'chisqr': chisq,  'Redchisqr': Redchisq 
               }
    # """
    return fit_data_cathode, fit_data_anode, AnalysisStats


def FitData_err(processedSignalData):
    '''
    Using errors in the fits, and getting them out
    '''
    timing, voltageCh1, voltageCh2, areaCh1, \
    areaCh2, chargeCh1, chargeCh2, chargeRatio, signalStart, anodeStart, errCh1, errCh2 = processedSignalData

    AnalysisStats = AnalysisDataset(processedSignalData)
    
    Ch1Max_index, Ch2Min_index, DeltaT, Vdr, eLifetime = AnalysisStats
    
    #first fit lorentzian for initial guesses
    p0 = [voltageCh1[signalStart+Ch1Max_index], timing[signalStart+Ch1Max_index], 1]
    # print(p0)

    popt, pcov = curve_fit(lorentzian, timing[signalStart:], voltageCh1[signalStart:], p0=p0)

    #then fit crystalBall, but with flipped x axis, for the cathode
    # C, alpha, N, sigma, mean
    p0 = [voltageCh1[signalStart+Ch1Max_index], 1, 10, popt[2], timing[signalStart+Ch1Max_index]]
    try:
        popt, pcov = curve_fit(CrystalBall_funct, timing[signalStart:], voltageCh1[signalStart:], 
                            p0=p0, sigma=errCh1[signalStart:])
    except RuntimeError:
        print("Fit with error weighting failed")
        popt, pcov = curve_fit(CrystalBall_funct, timing[signalStart:], voltageCh1[signalStart:], 
                    p0=p0)
        
    chisq, Redchisq =  chiSquared(CrystalBall_funct,  timing[signalStart:], voltageCh1[signalStart:], popt, sigma=errCh1[signalStart:])
    errors = np.sqrt(np.diag(pcov))

    fit_data_cathode = {'C': popt[0], 'C err': errors[0], 
                'alpha': popt[1], 'alpha err': errors[1],
                'N': popt[2], 'N err': errors[2],
                'sigma': popt[3], 'sigma err': errors[3],
                'mean': popt[4], 'mean err': errors[4],
                'chisqr': chisq,  'Redchisqr': Redchisq 
               }

    
    if (isinstance(anodeStart, (list, tuple))):
        #cut on high time side for anode
        anodeEnd = anodeStart[1]
        anodeStart = anodeStart[0]
        #fit a Lorentzian for the anode signal
        # (x, A, x0, gamma )
        # gamma_guess = 
        p0 = [voltageCh2[anodeStart+Ch2Min_index], timing[anodeStart+Ch2Min_index], 1]
        # print(p0)
        try:
            popt, pcov = curve_fit(lorentzian, timing[anodeStart:anodeEnd], voltageCh2[anodeStart:anodeEnd], 
                                p0=p0, sigma=errCh2[anodeStart:anodeEnd])
        except RuntimeError:
            print("Fit with error weighting failed")
            popt, pcov = curve_fit(lorentzian, timing[anodeStart:anodeEnd], voltageCh2[anodeStart:anodeEnd], 
                                p0=p0)
            
        chisq, Redchisq =  chiSquared(lorentzian, timing[anodeStart:anodeEnd], voltageCh2[anodeStart:anodeEnd], popt, errCh2[anodeStart:anodeEnd])
    else:
        #fit a Lorentzian for the anode signal
        p0 = [voltageCh2[anodeStart+Ch2Min_index], timing[anodeStart+Ch2Min_index], 1]
        # print(p0)
        try:
            popt, pcov = curve_fit(lorentzian, timing[anodeStart:], voltageCh2[anodeStart:], 
                                p0=p0, sigma=errCh2[anodeStart:])
        except RuntimeError:
            print("Fit with error weighting failed")
            popt, pcov = curve_fit(lorentzian, timing[anodeStart:], voltageCh2[anodeStart:], 
                                p0=p0)
            
        chisq, Redchisq =  chiSquared(lorentzian, timing[anodeStart:], voltageCh2[anodeStart:], popt, errCh2[anodeStart:])
        
    errors = np.sqrt(np.diag(pcov))
    fit_data_anode = {'A': popt[0], 'A err': errors[0], 
                'x0': popt[1], 'x0 err': errors[1],
                'gamma': popt[2], 'gamma err': errors[2],
                'chisqr': chisq,  'Redchisqr': Redchisq 
               }

    return fit_data_cathode, fit_data_anode, AnalysisStats


def AnalysisDataset_fit(processedSignalData, returnStats=False):
    timing, voltageCh1, voltageCh2, areaCh1, \
    areaCh2, chargeCh1, chargeCh2, chargeRatio, signalStart, anodeStart = processedSignalData
    # print(signalStart)

    fitData_cath, fitData_anode, AnalysisStats = FitData(processedSignalData)

    #get deltaT from the fits here  
    Ch1Max_time = fitData_cath['mean']
    
    Ch2Min_time = fitData_anode['x0']
    
    DeltaT = Ch2Min_time - Ch1Max_time
    #accounts for the distance on the other side of the grid by using the average of t1 and t3
    #and for the fact that the charge does not all instansouly leave the cathode/hit the anode
    Vdr = dtotal_averaged/(DeltaT*1e-6) #cm/s

    #I should also get the charge ratio from the fits -> integrate over the functions and divide
    time_interval = timing[1]-timing[0]
    areaCh1_fit = calculate_pulse_area(time_interval, CrystalBall_funct(timing[signalStart:], fitData_cath['C'], 
                fitData_cath['alpha'],fitData_cath['N'],fitData_cath['sigma'],fitData_cath['mean'])) #mV * us
    areaCh2_fit = calculate_pulse_area(time_interval, lorentzian(timing[anodeStart:], fitData_anode['A'], 
                fitData_anode['x0'], fitData_anode['gamma']))  #mV * us

    # convert area to charge using calibration for each side: mV*us / kOhm = pC
    # Trans-impedance is 213 kOhm for amplifier ch.1 and 207 kOhm for ch.2.
    chargeCh1 = areaCh1_fit / ch1_TImpedance #resulting in charge in pC
    chargeCh2 = areaCh2_fit / ch2_TImpedance #resulting in charge in pC
    
    chargeRatio = np.abs(chargeCh2/chargeCh1)

    #in practice you also need the grid transparency values
    #our estimate right now is 80% for each, but really we need to measure this
    gridTrans_top = 0.9
    gridTrans_bottom = 0.9
    gridTrans_top_err = 0.1
    gridTrans_bottom_err = 0.1

    #get estimate of electron lifetime: tau_e = - deltaT/ln(Qa/Qc)
    denom = np.log(chargeRatio * 1/(gridTrans_top*gridTrans_bottom)) 
    eLifetime = - DeltaT/denom #microseconds

    eLifetime_err = eLifetime/(gridTrans_top*gridTrans_bottom) * \
        np.abs(np.log(gridTrans_top*gridTrans_bottom)*np.sqrt((gridTrans_top_err/gridTrans_top)**2 + (gridTrans_bottom_err/gridTrans_bottom)**2) /denom)

    if returnStats:
        return Ch1Max_time, Ch2Min_time, chargeRatio, DeltaT, Vdr, [eLifetime, eLifetime_err], \
        fitData_cath, fitData_anode, chargeCh1, chargeCh2, AnalysisStats
    else:
       return Ch1Max_time, Ch2Min_time, chargeRatio, DeltaT, Vdr, [eLifetime, eLifetime_err], \
        fitData_cath, fitData_anode, chargeCh1, chargeCh2

 

def AnalysisDataset_fit_err(processedSignalData):
    timing, voltageCh1, voltageCh2, areaCh1, \
    areaCh2, chargeCh1, chargeCh2, chargeRatio, \
            signalStart, anodeStart, errCh1, errCh2= processedSignalData
        
    # print(signalStart)

    fitData_cath, fitData_anode, AnalysisStats = FitData_err(processedSignalData)

    #get deltaT from the fits here  
    Ch1Max_time = fitData_cath['mean']
    Ch1Max_timeErr = fitData_cath['mean err']

    S = 1
    #rescaling errors based on the pdg idea: https://doi.org/10.1140/epjc/s10052-020-8115-3
    if fitData_anode['Redchisqr'] > 1:
        S = np.sqrt(fitData_anode['Redchisqr'])
        
    Ch2Min_time = fitData_anode['x0']
    Ch2Min_timeErr = fitData_anode['x0 err']*S

    # print("chi cathode: ", fitData_cath['Redchisqr'], "chi anode: ", fitData_anode['Redchisqr'] )

    DeltaT = Ch2Min_time - Ch1Max_time
    DeltaT_err = DeltaT * np.sqrt((Ch1Max_timeErr/Ch1Max_time)**2+(Ch2Min_timeErr/Ch2Min_time)**2)

    #accounts for the distance on the other side of the grid by using the average of t1 and t3
    #and for the fact that the charge does not all instansouly leave the cathode/hit the anode
    Vdr = dtotal_averaged/(DeltaT*1e-6) #cm/s
    Vdr_err = dtotal_averaged/(1e-6)*DeltaT_err / DeltaT**2  #cm/s

    #I should also get the charge ratio from the fits -> integrate over the functions and divide
    time_interval = timing[1]-timing[0]
    areaCh1_fit = calculate_pulse_area(time_interval, CrystalBall_funct(timing[signalStart:], fitData_cath['C'], 
                fitData_cath['alpha'],fitData_cath['N'],fitData_cath['sigma'],fitData_cath['mean'])) #mV * us
    if (isinstance(anodeStart, (list, tuple))):
        areaCh2_fit = calculate_pulse_area(time_interval, lorentzian(timing[anodeStart[0]:anodeStart[1]], fitData_anode['A'], 
                    fitData_anode['x0'], fitData_anode['gamma']))  #mV * us
    else:
        areaCh2_fit = calculate_pulse_area(time_interval, lorentzian(timing[anodeStart:], fitData_anode['A'], 
            fitData_anode['x0'], fitData_anode['gamma']))  #mV * us
    # convert area to charge using calibration for each side: mV*us / kOhm = pC
    # Trans-impedance is 213 kOhm for amplifier ch.1 and 207 kOhm for ch.2.
    chargeCh1 = areaCh1_fit / ch1_TImpedance #resulting in charge in pC
    chargeCh2 = areaCh2_fit / ch2_TImpedance #resulting in charge in pC
    
    chargeRatio = np.abs(chargeCh2/chargeCh1)

    #in practice you also need the grid transparency values
    #our estimate right now is 80% for each, but really we need to measure this
    gridTrans_top = 0.9
    gridTrans_bottom = 0.9
    gridTrans_top_err = 0.1
    gridTrans_bottom_err = 0.1

    #get estimate of electron lifetime: tau_e = - deltaT/ln(Qa/Qc)
    denom = np.log(chargeRatio * 1/(gridTrans_top*gridTrans_bottom)) 
    eLifetime = - DeltaT/denom #microseconds

    eLifetime_err = eLifetime/(gridTrans_top*gridTrans_bottom) * \
        np.abs(np.log(gridTrans_top*gridTrans_bottom)*np.sqrt((gridTrans_top_err/gridTrans_top)**2 + (gridTrans_bottom_err/gridTrans_bottom)**2) /denom)

    return Ch1Max_time, Ch2Min_time, chargeRatio, [DeltaT, DeltaT_err], [Vdr, Vdr_err], \
                [eLifetime, eLifetime_err], fitData_cath, fitData_anode, chargeCh1, chargeCh2, AnalysisStats


def GetVoltagePeaks_data(processedSignalData, AnalysisStats):
    timing, voltageCh1, voltageCh2, areaCh1, \
        areaCh2, chargeCh1, chargeCh2, chargeRatio, \
        signalStart, anodeStart, errCh1, errCh2 = processedSignalData
    
    Ch1Max_index, Ch2Min_index, DeltaTime, Vdr, eLifetime = AnalysisStats
    ch1Max = voltageCh1[signalStart:][Ch1Max_index]
    ch1Max_err = errCh1[signalStart:][Ch1Max_index]
    if hasattr(anodeStart, "__len__"):
        ch2Min = voltageCh2[anodeStart[0]:anodeStart[1]][Ch2Min_index]
        ch2Min_err = errCh2[anodeStart[0]:anodeStart[1]][Ch2Min_index]
    else:
        ch2Min = voltageCh2[anodeStart:][Ch2Min_index]
        ch2Min_err = errCh2[anodeStart:][Ch2Min_index]

    return [ch1Max, ch1Max_err, ch2Min, ch2Min_err]


def GetVoltagePeaks_fit(Ch1Max_time, Ch2Min_time, fitData_cath, fitData_anode):
    CB_fits = CrystalBall_param(Ch1Max_time, fitData_cath, Err=True)
    lorz_fits = lorentzian_param(Ch2Min_time, fitData_anode, Err=True)

    return [CB_fits, lorz_fits]
    

def AnalysisDataset(processedSignalData):
    if len(processedSignalData) > 10:
        #catch for if I pass the updated processedSignalData with errors
        timing, voltageCh1, voltageCh2, areaCh1, \
        areaCh2, chargeCh1, chargeCh2, chargeRatio, \
        signalStart, anodeStart, errCh1, errCh2 = processedSignalData
        if hasattr(chargeCh1, "__len__"):
            chargeCh1=chargeCh1[0]
            chargeCh2=chargeCh2[0]
            chargeRatio=chargeRatio[0]
        if hasattr(anodeStart, "__len__"):
            anodeSt = anodeStart[0]
            anodeEnd = anodeStart[1]
        else:
            anodeSt = anodeStart
            anodeEnd = -1
    else:
        timing, voltageCh1, voltageCh2, areaCh1, \
        areaCh2, chargeCh1, chargeCh2, chargeRatio, signalStart, anodeStart = processedSignalData
        anodeSt = anodeStart
        anodeEnd = -1

    #Get delta T between signals   
    Ch1Max_index = voltageCh1[signalStart:].argmax()
    Ch2Min_index = voltageCh2[anodeSt:anodeEnd].argmin()
    
    Ch1Max_time = timing[signalStart:][Ch1Max_index]
    Ch2Min_time = timing[anodeSt:anodeEnd][Ch2Min_index]
    
    DeltaT = Ch2Min_time - Ch1Max_time
    Vdr = dtotal_averaged/(DeltaT*1e-6) #cm/s

    #in practice you also need the grid transparency values
    #our estimate right now is 80% for each, but really we need to measure this
    gridTrans_top = 0.9
    gridTrans_bottom = 0.9
    gridTrans_top_err = 0.1
    gridTrans_bottom_err = 0.1

    #get estimate of electron lifetime: tau_e = - deltaT/ln(Qa/Qc)
    denom = np.log(chargeRatio * 1/(gridTrans_top*gridTrans_bottom)) 
    
    eLifetime = - DeltaT/denom #microseconds

    eLifetime_err = eLifetime/(gridTrans_top*gridTrans_bottom) * \
        np.abs(np.log(gridTrans_top*gridTrans_bottom)*np.sqrt((gridTrans_top_err/gridTrans_top)**2 + (gridTrans_bottom_err/gridTrans_bottom)**2) /denom)

    return Ch1Max_index, Ch2Min_index, DeltaT, Vdr, [eLifetime, eLifetime_err]


def GetDateTime(path, fileArray):
    dateTimes_list = []
    for file in fileArray:
        #load in the file
        y, x, S = RTxReadBin(f"{path}/{file}.Wfm.bin")

        # get time interval of data taking on scope
        # one_time_interval = S['SignalResolution'] #[s]
    
        time_string = S['Timestamp']
        # Split the string to get the date and time
        datesplit = time_string.split(' ')
        
        date_part = datesplit[0]
        time_part = datesplit[1]
        extra_part  = datesplit[2]
        # print(date_part)

        if date_part[:3] == "202":
            # Set it in the data time
            date_obj = datetime.strptime(date_part+" "+time_part, '%Y:%m:%d %H:%M')
        else:
            #some of the scope files are missing the date part? so use date from the file name
            date_part_other = file.split('_')[-3]   
            # Convert the time part to a datetime object (assuming the date is today)
            date_obj = datetime.strptime(date_part_other+" "+date_part, '%Y-%m-%d %H:%M')
            
        dateTimes_list.append(date_obj)
        
    return dateTimes_list


"""
def FindFiles(folder_path, file):
    '''
    Get sets of files that are output from the R&S scope
    Will need some additions for more than a single set of flashes saved
    '''
        
    # Get a list of file names, not sorted here
    file_names = os.listdir(folder_path)
    # print(file_names)

    #get only one copy of each file
    file_names = [f for f in file_names if f.endswith("Wfm.bin")]
    #get the file names that have the same base name
    file_names = [f for f in file_names if f.startswith(file)]
    
    #remove ending
    file_names = [f.split(".Wfm.bin")[0] for f in file_names]

    return file_names
"""

def GetRawData_lecroy(path, fileArray):
    NDatapoints = len(fileArray)
    nFlashes = int(NDatapoints/2)
    
    voltageCh1_raw = []
    voltageCh2_raw = []
    
    timing  = []
    time_interval = []
    
    for file in fileArray:
        #load in the file
        data = np.loadtxt(f"{path}/{file}", skiprows=26, delimiter=',').T
        one_timing = data[0]
    
        #convert timing inverval to microseconds for integration use later
        one_time_interval = (one_timing[1] - one_timing[0])*1e6 #[us]
        
        #and load the voltages
        one_voltageCh1 =  data[1]*1e3 # mV
        one_voltageCh2 = data[2]*1e3 # mV

        voltageCh1_raw.append(one_voltageCh1)
        voltageCh2_raw.append(one_voltageCh2)
    
        timing.append(one_timing)
        time_interval.append(one_time_interval)
            # put all the data in one array - this will only work if you don't change the timing/resolution between 
        # files for a given set of flashes

    try:
        voltageCh1_raw = np.array(voltageCh1_raw)
        voltageCh2_raw = np.array(voltageCh2_raw)
        timing = np.array(timing)
        time_interval = np.array(time_interval)
    except:
        print("Arrays are different lengths")
        # return None

    #got to check the timing is all the same too:
    are_identical = np.all(timing == timing[0, :])
    all_values_identical = np.all(time_interval == time_interval[0])
    
    if not are_identical and not all_values_identical:
        print("Timing arrays are different")
        # return None
    else:
        timing = timing[0]
        time_interval = time_interval[0]

    return [voltageCh1_raw, voltageCh2_raw, timing]


def ProcessDataset_lecroy(path, fileArray, Ped = [0, 3000], cut_for_integral=True, cutForSignal=True, 
                      anodeShift=False, reversed=False, ChargeError=False):
    '''
    Processes data taken with the lecroy/Tektronix scope. Set up to handle large noise near start

    path : str
        Path to the folder containing the Lecroy oscilloscope data files.
    fileArray : list of str
        List of filenames (within `path`) to be processed.
    Ped : list[int], optional
        Index range [start, end] for pedestal (baseline) calculation. Default [0, 3000].
    cut_for_integral : bool, optional
        If True, integrate only over the signal region; if False, use the full waveform.
    cutForSignal : bool or float, optional
        Determines signal start:
          - True: auto-detect from Ch1 peaks
          - False: no cut, use whole waveform
          - float: set start time manually in µs
    anodeShift : bool, float, or False, optional
        Starting point for anode (Ch2):
          - False: same as signal start
          - True: auto-detect from Ch1
          - float: manual start time in µs
    reversed : bool, optional
        If True, flip the sign of both channels (for reversed HV runs)
    ChargeError : bool, optional
        If True, estimate charge uncertainties with bootstrapping.
        
    '''
    NDatapoints = len(fileArray)
    nFlashes = int(NDatapoints/2)
    
    voltageCh1_raw = []
    voltageCh2_raw = []
    
    timing  = []
    time_interval = []
    
    for file in fileArray:
        #load in the file
        data = np.loadtxt(f"{path}/{file}", skiprows=26, delimiter=',').T
        one_timing = data[0]*1e6
    
        #convert timing inverval to microseconds for integration use later
        one_time_interval = (one_timing[1] - one_timing[0]) #[us]
        
        #and load the voltages
        one_voltageCh1 =  data[1]*1e3 # mV
        one_voltageCh2 = data[2]*1e3 # mV

        voltageCh1_raw.append(one_voltageCh1)
        voltageCh2_raw.append(one_voltageCh2)
    
        timing.append(one_timing)
        time_interval.append(one_time_interval)
        # put all the data in one array - this will only work if you don't change the timing/resolution between 
        # files for a given set of flashes

    try:
        voltageCh1_raw = np.array(voltageCh1_raw)
        voltageCh2_raw = np.array(voltageCh2_raw)
        timing = np.array(timing)
        time_interval = np.array(time_interval)
    except:
        print("Arrays are different lengths")

    #got to check the timing is all the same too:
    are_identical = np.all(timing == timing[0, :])
    all_values_identical = np.all(time_interval == time_interval[0])
    
    if not are_identical and not all_values_identical:
        print("Timing arrays are different")
        return None
    else:
        timing = timing[0]
        time_interval = time_interval[0]
        
    #get average signal for each channel
    voltageCh1 = np.mean(voltageCh1_raw, axis=0)
    voltageCh2 = np.mean(voltageCh2_raw, axis=0)

    #and get an error -> standard error on the mean
    # using ddof = 1 not 0 for an unbiased value since I don't know the true mean value
    errCh1 = np.std(voltageCh1_raw, axis=0, ddof=1) / np.sqrt(nFlashes)
    errCh2 = np.std(voltageCh2_raw, axis=0, ddof=1) / np.sqrt(nFlashes)
    
    # Find the pedestal
    pedestalCh1 = find_pedestal(voltageCh1, start_index=Ped[0], end_index=Ped[1])  # Adjust the range as needed
    pedestalCh2 = find_pedestal(voltageCh2, start_index=Ped[0], end_index=Ped[1])  # Adjust the range as needed
    
    # Subtract the pedestal
    voltageCh1 = voltageCh1 - pedestalCh1
    voltageCh2 = voltageCh2- pedestalCh2

    if reversed:
        #flipped HV run, so flip the signs for the fitting to work
        voltageCh1 = -voltageCh1
        voltageCh2 = -voltageCh2

    signalStart = 0
    
    if isinstance(cutForSignal, float):
        #I am hardcoding in time where to start the fitting, based on the value (in uS) I give in cutForSignal
        signalStart = int(cutForSignal/time_interval) + np.where(np.isclose(timing, 0))[0][0]
    
    elif cutForSignal:
        #split between the starting noise and the signal

        peaks, properties = sp.signal.find_peaks(voltageCh1, height=np.max(voltageCh1)/3, threshold=None, 
                   prominence=10, rel_height=0.5, distance=5)
        bases = properties["right_bases"]    
        pad = 500
        res = [bases[i] for i in range(len(bases)-1) if bases[i] < (bases[i+1]-pad)]

        try:
            signalStart = res[0]+int(pad/2)
        except:
            try:
                if len(bases) > 1:
                    signalStart = bases[-1]
                
            except:
                signalStart = 0

    if anodeShift !=False:
        if anodeShift == True:
            anodeStart = np.argmax(voltageCh1[signalStart:])*2
        else:
            anodeStart = int(anodeShift/time_interval) + np.where(np.isclose(timing, 0))[0][0]
            # print(anodeShift, anodeStart)
    else:
        anodeStart = signalStart
        
    peakHeightCh1 = np.max(voltageCh1[signalStart:])
    peakHeightCh2 = np.min(voltageCh2[anodeStart:]) #this one is negative, so we want the min

    if cut_for_integral:
        # print("Using only signal region", signalStart)
        # Calculate pulse area -> area under curve - using only area after the signal
        areaCh1 = calculate_pulse_area(time_interval, voltageCh1[signalStart:]) #mV*us
        areaCh2 = calculate_pulse_area(time_interval, voltageCh2[anodeStart:]) #mV*us

        if ChargeError:
            # to get errors on an integrated region, I am going to use the bootstrapping method
            N = 1000
            areas1, areas2 = [], []
            for i in range(N):
                BS_Vs1 = np.random.normal(loc=voltageCh1[signalStart:], scale=errCh1[signalStart:])
                BS_areaCh1 = calculate_pulse_area(time_interval, BS_Vs1) #mV*us
                BS_Vs2 = np.random.normal(loc=voltageCh2[anodeStart:], scale=errCh2[anodeStart:])
                BS_areaCh2 = calculate_pulse_area(time_interval, BS_Vs2) #mV*us

                areas1.append(BS_areaCh1)
                areas2.append(BS_areaCh2)

    else:
        # Calculate pulse area -> area under curve
        areaCh1 = calculate_pulse_area(time_interval, voltageCh1) #mV*us
        areaCh2 = calculate_pulse_area(time_interval, voltageCh2) #mV*us

        if ChargeError:
            # to get errors on an integrated region, I am going to use the bootstrapping method
            N = 1000
            areas1, areas2 = [], []
            for i in range(N):
                BS_Vs1 = np.random.normal(loc=voltageCh1, scale=errCh1)
                BS_areaCh1 = calculate_pulse_area(time_interval, BS_Vs1) #mV*us
                BS_Vs2 = np.random.normal(loc=voltageCh2, scale=errCh2)
                BS_areaCh2 = calculate_pulse_area(time_interval, BS_Vs2) #mV*us

                areas1.append(BS_areaCh1)
                areas2.append(BS_areaCh2)
    
    if ChargeError:
        # convert area to charge using calibration for each side
        # Trans-impedance is 213 kOhm for amplifier ch.1 and 207 kOhm for ch.2.
        chargeCh1 = areaCh1 / ch1_TImpedance#resulting in charge in pC
        chargeCh2 = areaCh2 / ch2_TImpedance #resulting in charge in pC

        #and then get the std of the resulting distributions
        areaCh1_std = np.std(areas1)
        areaCh2_std = np.std(areas2)

        chargeCh1_err = areaCh1_std / ch1_TImpedance #resulting in charge in pC
        chargeCh2_err = areaCh2_std / ch2_TImpedance #resulting in charge in pC

        chargeRatio = np.abs(chargeCh2/chargeCh1) 
        chargeRatio_err = chargeRatio*np.sqrt((chargeCh1_err/chargeCh1)**2 + (chargeCh2_err/chargeCh2)**2)

        #package them up
        chargeCh1 = [chargeCh1, chargeCh1_err]
        chargeCh2 = [chargeCh2, chargeCh2_err]
        chargeRatio = [chargeRatio, chargeRatio_err]

    else:
        # convert area to charge using calibration for each side

        # convert area to charge using calibration for each side
        # Trans-impedance is 213 kOhm for amplifier ch.1 and 207 kOhm for ch.2.
        chargeCh1 = areaCh1 / ch1_TImpedance #resulting in charge in pC
        chargeCh2 = areaCh2 / ch2_TImpedance #resulting in charge in pC
        
        chargeRatio = np.abs(chargeCh2/chargeCh1)

    return [timing, voltageCh1, voltageCh2, areaCh1, areaCh2, chargeCh1, 
            chargeCh2, chargeRatio, signalStart, anodeStart, errCh1, errCh2]

def rainbowValueErr(whichScan, groupBy_var, x_var, y_var, err, markerDict=None, Vlim = None, figIm=None):

    grouped = whichScan.groupby(groupBy_var)
    
    if figIm is None:
        fig = plt.figure(figsize=(6, 5))
        
        ax1 = plt.subplot2grid(shape=(1, 8), loc=(0, 0), colspan=7)
        ax2 = plt.subplot2grid(shape=(1, 8), loc=(0, 7), colspan=1)
    else:
        fig, ax1, ax2 = figIm
    
    #setup color bar, you can also force the Vmin and max
    if Vlim is not None:
        Vmin = Vlim[0]
        Vmax = Vlim[1]
    else:
        Vmin = min(whichScan[groupBy_var])
        Vmax = max(whichScan[groupBy_var])
    colors = plt.cm.jet(np.linspace(0,1,len(grouped)))# Initialize holder for trajectories
    cmap = mpl.cm.jet
    norm = mpl.colors.Normalize(vmin=Vmin, vmax=Vmax)
     
    lineS = "-"
    for name, group in grouped:   
        # group
        # dataSet = group["folder"].values[0]
        if markerDict is not None:
            if isinstance(markerDict, dict):
                marker = markerDict[group["folder"].values[-1]]
            else:
                marker = markerDict[0]
                lineS = markerDict[1]
        else:
            marker = "o"
            
        zval= list(group[groupBy_var])[0]
        group = group.sort_values(x_var)
        ax1.errorbar(group[x_var], group[y_var], yerr=group[err], capsize=2,ls=lineS,
                     # marker=markerDict[dataSet], 
                     marker=marker, color=cmap(norm(zval)) )
        
        ax1.fill_between(group[x_var], group[y_var]-group[err], group[y_var]+group[err], 
                         color=cmap(norm(zval)), alpha=0.1)
    
    
    cb1 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                    norm=norm, orientation='vertical')
    ax1.grid()
    ax1.set_ylabel(y_var)
    ax1.set_xlabel(x_var)
    ax2.set_ylabel(groupBy_var)

    return fig, ax1, ax2

def rainbowValueArr(whichScan, groupBy_var, x_var, y_var, markerDict=None, Vlim = None, figIm = None):

    grouped = whichScan.groupby(groupBy_var)

    if figIm is None:
        fig = plt.figure(figsize=(6, 5))
        
        ax1 = plt.subplot2grid(shape=(1, 8), loc=(0, 0), colspan=7)
        ax2 = plt.subplot2grid(shape=(1, 8), loc=(0, 7), colspan=1)
    else:
        fig, ax1, ax2 = figIm
    
    #setup color bar, you can also force the Vmin and max
    if Vlim is not None:
        Vmin = Vlim[0]
        Vmax = Vlim[1]
    else:
        Vmin = min(whichScan[groupBy_var])
        Vmax = max(whichScan[groupBy_var])
    colors = plt.cm.jet(np.linspace(0,1,len(grouped)))# Initialize holder for trajectories
    cmap = mpl.cm.jet
    norm = mpl.colors.Normalize(vmin=Vmin, vmax=Vmax)
    
    for name, group in grouped:   

        lineS = "-"
        if markerDict is not None:
            if isinstance(markerDict, dict):
                marker = markerDict[group["folder"].values[-1]]
            else:
                marker = markerDict[0]
                lineS = markerDict[1]
        else:
            marker = "o"
            
        # dataSet = group["folder"].values[0]
        group = group.sort_values(x_var)
        zval= list(group[groupBy_var])[0]
        
        yval =  group[y_var]
        yval = np.array([sublist[0] for sublist in yval])
    
        yval_e =  group[y_var]
        yval_e = np.array([sublist[1] for sublist in yval_e])
        maskNeg = yval_e>=0
    
        ax1.errorbar(group[x_var][maskNeg], yval[maskNeg], yerr=yval_e[maskNeg], capsize=2,ls=lineS,
                     marker=marker, color=cmap(norm(zval)))
        
        ax1.fill_between(group[x_var][maskNeg], yval[maskNeg]-yval_e[maskNeg], yval[maskNeg]+yval_e[maskNeg], 
                         color=cmap(norm(zval)), alpha=0.1)

    cb1 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                    norm=norm, orientation='vertical')
    ax1.grid()
    ax1.set_ylabel(y_var)
    ax1.set_xlabel(x_var)
    ax2.set_ylabel(groupBy_var)

    plt.tight_layout() 
    return fig, ax1, ax2

def rainbowSingle(whichScan, groupBy_var, x_var, y_var, markerDict=None, Vlim = None, figIm = None):

    grouped = whichScan.groupby(groupBy_var)
    
    if figIm is None:
        fig = plt.figure(figsize=(6, 5))
        
        ax1 = plt.subplot2grid(shape=(1, 8), loc=(0, 0), colspan=7)
        ax2 = plt.subplot2grid(shape=(1, 8), loc=(0, 7), colspan=1)
    else:
        fig, ax1, ax2 = figIm
    
    #setup color bar, you can also force the Vmin and max
    if Vlim is not None:
        Vmin = Vlim[0]
        Vmax = Vlim[1]
    else:
        Vmin = min(whichScan[groupBy_var])
        Vmax = max(whichScan[groupBy_var])
    colors = plt.cm.jet(np.linspace(0,1,len(grouped)))# Initialize holder for trajectories
    cmap = mpl.cm.jet
    norm = mpl.colors.Normalize(vmin=Vmin, vmax=Vmax)

    lineS = "-"
    for name, group in grouped:   
        if markerDict is not None:
            if isinstance(markerDict, dict):
                marker = markerDict[group["folder"].values[-1]]
            else:
                marker = markerDict[0]
                lineS = markerDict[1]
                
        else:
            marker = "o"
            
        group = group.sort_values(x_var)
        zval= list(group[groupBy_var])[0]
        
        plot = group.plot(kind='line', x=x_var, y=y_var, marker=marker, label=f"{name} V", legend=False,
                          ax=ax1, color=cmap(norm(zval)), ls=lineS, alpha=0.8)
        
    cb1 = mpl.colorbar.ColorbarBase(ax2, cmap=cmap,
                                    norm=norm, orientation='vertical')
    ax1.grid()
    ax1.set_ylabel(y_var)
    ax1.set_xlabel(x_var)
    ax2.set_ylabel(groupBy_var)
    plt.tight_layout()

    return fig, ax1, ax2