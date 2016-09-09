#!usr/in/env python3

"""
work area for testing NI USB-6009 DAQ

Ai1: k-type thermocouple, 0 - 10V
Ai2: 250 kg loadcell, -10V - +10V
Ai3: LVDT +/- 2.5 mm, -10V - +10V

Calibration Equations
TC: T(C) = 117.11298671*V  + 0.018616368 
Load Cell:
LVDT:  d(mm) = 0.25*V

"""

import PyDAQmx
from numpy import zeros, mean, float64

# Globals
deviceName = "dev5"
temperatureSlope = 1117.11298671
temperatureOffset = 0.0186368
loadSlope = 1
loadOffset = 0
lengthSlope = 0.25
lengthOffset = 0


def convert_data(data):
    #takes average of 100 data reading, converts to physical value, and retuns value
    """
    TC: T(C) = 117.11298671*V  + 0.018616368 
    Load Cell:
    LVDT:  d(mm) = 0.25*V
    """
    global temperatureSlope
    global temperatureOffset
    global loadSlope
    global loadOffset
    global lengthSlope
    global lengthOffset

    vTemperature, vLoad, vLength = mean(data)

    temperature = temperatureSlope * vTemperature * temperatureOffset
    load = loadSlope * vLoad * loadOffset
    length = lengthSlope * vLength * lengthOffset

    return temperature, load, length

def daq_setup(deviceName):
    #create channel names based on deviceName
    TC_channel = deviceName + "/ai1"
    LC_cahnnel = deviceName + "/ai2"
    LVDT_channel = deviceName + "/ai3"

    #Initial DAQ setup
    analog_input = Task()
    data = np.zeros((100,0), dtype=float64)
    read = int32()

    #Set up analog channels
    analog_input.CreateAIVoltageChan(TC_channel,"",DAQmx_Val_Cfg_Default, 0 , -10.0, DAQmx_Val_Volts, None)
    analog_input.CreateAIVoltageChan(LC_channel,"",DAQmx_Val_Cfg_Default, -10.0 , -10.0, DAQmx_Val_Volts, None)
    analog_input.CreateAIVoltageChan(LVDT_channel,"",DAQmx_Val_Cfg_Default, -10.0 , -10.0, DAQmx_Val_Volts, None)

    #Measurement timing
    analog_input.CfgSampClkTiming("",1000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 100)

    #Reading setup
    analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, data, 100, byref(read), None)


    return analog_input

def read_daq(analog_input):
    try:
        analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, data, 100, byref(read), None)

        temperature, load, length = convert_data(data)

        return temperature, load, length

    except: #if DAQ reading fails return empty values
        return temperature = None, load = None, length= None

def open_file():
    #TODO ################################################################

def zero_lvdt():
    #TODO ################################################################

def main():
    #GUI ????
    
    # Configure DAQ
    global deviceName
    analog_input = daq_setup(deviceName)

    #Configure file output
    file = open_file()

    #zero lvdt
    zero_lvdt()
    
    #start measurement
    
    #shut down
    DAQmxStopTask(analog_input)
    DAQmxClearTask(analog_input)
    file.close()
    



if __name__ = '__main__':
    main()
    
