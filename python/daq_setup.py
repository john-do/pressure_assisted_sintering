#!usr/bin/env python3.5

"""
Work area for testing NI USB-6009 DAQ

XBAi1: k-type thermocouple, 0 - 10V
Ai2: 250 kg loadcell, -10V - +10V
Ai3: LVDT +/- 2.5 mm, -10V - +10V

Takes average voltage of 100 samples measured at 1 kHz

Calibration Equations
TC: T(C) = 119.746003543*V  + -2.22923566848 
Load Cell: Force (N) = 247.258433769 * V * -44.3671200508
LVDT:  d(mm) = 0.25*V

File Output:
'#\tClock Time\tElapsed Time [s]\tT [C]\tLoad [N]\tdL [mm]\n'

"""

import time
from PyDAQmx import *
from numpy import zeros, mean, float64





################################    DAQ Class    ################################


class DaqMeasurement:
'''
LOADCELLSLOPE = 247.258433769
LVDTSLOPE = 0.25
temperatureSlope = 119.746003543
temperatureOffset = -2.22923
loadSlope = 247.258433769
loadOffset = -44.3671200508
lengthSlope = 0.25
lengthOffset = 0
'''
            
    def __init__(self, deviceName):
        self.deviceName = deviceName
        self.analog_input = daq_setup(self.deviceName)
        #self.file = FileIO()

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

    #TODO def zero_lvdt(self):
    self.read_daq(self.analog_input)

    #TODO def zero_load_cell(self):

    def read_daq(self.analog_input):
        try:
            self.analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, data, 100, byref(read), None)

            temperature, load, length = convert_data(data) ### HOW IS DATA VARIABLE TREATED INSIDE THE CLASS???????????

            return temperature, load, length

        except: #if DAQ reading fails return empty values
            return temperature = None, load = None, length= None   

    def convert_data(data):
        #takes average of 100 data reading, converts to physical value, and retuns value
        '''
        TC: T(C) = 117.11298671*V  + 0.018616368 
        Load Cell:
        LVDT:  d(mm) = 0.25*V
        
        '''
        
        vTemperature, vLoad, vLength = mean(data)

        temperature = temperatureSlope * vTemperature * temperatureOffset
        load = loadSlope * vLoad * loadOffset
        length = lengthSlope * vLength * lengthOffset

        return temperature, load, length
            
    def close_daq(self):
        DAQmxStopTask(self.analog_input)
        DAQmxClearTask(self.analog_input)


################################    File Class    ################################

class FileIO:

    def __init__(self, sample):
        self.file_name = input("File Name: ")

        if self.file_name[-4:] != '.txt':
            self.file_name = self.file_name + '.txt'

        self.log_file = open(self.file_name, 'w')

        ## Initiate Header
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        
        self.log_file.write('Pressure Assisted Sintering\t%s' %  date)
        self.log_file.write('Inital sample thickness:\t%s' % sample.initial_length())
        self.log_file.write('Inital sample diameter:\t%s' % sample.initial_diameter())
        #TODO CHECK FOR OTHER PARAMTERTE MATERIAL; PRESSURE; E-FIELD; CURRENT LIMIT if mySample.material()
        
        self.log_file.write('')
        self.log_file.write('#\tClock Time\tElapsed Time [s]\tT [C]\tLoad [N]\tdL [mm]\n')

        #return self.log_file

    def set_start_time(self):
        self.start_time = time.time()

    def write_file(self,i,measured_data):
        tempeature = measured_data[0]
        load = measured_data[1]
        length = measured_data[2]
        now =  time.strftime('%H:%M:%S')
        elapsed_time = time.time()-self.start_time()
        self.log_file.write('%i\t%s\t%d\t%d\t%d\t%d\n' % (i, now,elapsed_time, tempearture, load, length)

     def close_file(self):
        self.log_file.close()
        
################################    Sample Class    ################################
class Sample:

    def __init__(self):
        self.initial_length = input('Initial sample thickness (mm): ')
        self.initial_diamter = input('Initial sample diameter (mm): ')
        
        #To be added later
        self.material = None
        self.pressure = None
        self.voltage = None
        self.current_limit = None

############################################################################
################################    Main    ################################
############################################################################
                            
def main():
    # Create Sample Descrition
    mySample = Sample()
    
    # Create file and header
    myFile = FileIO(mySample)
    #Setup DAQ
    myDaq = DaqMeasurement()

    #TODO Connect Keithly and Agilent ????

    #TODO Zero Load cell
    #myDaq.zero_load_cell()
                         
    #TODO#Zero lvdt
    #myDaq.zero_lvdt()

    
    #start measurement loop
    i = 0
    myFile.set_start_time()

    while(i<11):
        i= i+1
        measured_data = myDaq.read_daq()
        myFile.write_to_file(i,measure_data)
        print(measured_data)

        # Update GUI Displays
    
    #shut down
    myFile.close_file()
    myDaq.close_daq()
                             

if __name__ = '__main__':
    main()
    



################################################################
################            OLD STUFF           ################
################################################################

            '''
def read_daq(analog_input):
    try:
        analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, data, 100, byref(read), None)

        temperature, load, length = convert_data(data)

        return temperature, load, length

    except: #if DAQ reading fails return empty values
        return temperature = None, load = None, length= None

'''
"""

def file_init():
    #TODO ################################################################
    #Add sample diameter and make load in Pa
    file_name = input("File Name: ")
    initial_length = input('Initial sample thickness (mm): ')

    if file_name[-4:] != '.txt':
        file_name = file_name + '.txt'

    log_file = open(file_name, 'w')
    date = time.strftime('%Y-%m-%d %H:%M:%S')
    log_file.write('Pressure Assisted Sintering\t%s' %  date)
    log_file.write('Inital sample thickness: %s' % initial_length)
    log_file.write('')
    log_file.write('#\tClock Time\tElapsed Time [s]\tT [C]\tLoad [N]\tdL [mm]\n')


    return file, float(initial_length), float(initial_diameter)
"""

"""
################################    Global Vars    ################################
'''
deviceName = "dev5"
temperatureSlope = 119.746003543
temperatureOffset = -2.22923
loadSlope = 247.258433769
loadOffset = -44.3671200508
lengthSlope = 0.25
lengthOffset = 0

'''


