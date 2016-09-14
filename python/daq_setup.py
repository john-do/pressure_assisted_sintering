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
debug = False

import time
import threading
from PyDAQmx import *
from numpy import zeros, mean, float64


################################    DAQ Class    ################################


class DaqMeasurement:
   
    #LOADCELLSLOPE = 247.258433769
    #LVDTSLOPE = 0.25
    temperatureSlope = 119.746003543    
    temperatureOffset = -2.22923
    loadSlope = 247.258433769
    loadOffset = -44.3671200508
    lengthSlope = 0.25
    lengthOffset = 0
    
            

    def daq_setup(self,deviceName):
        #create channel names based on deviceName
        TC_channel = deviceName + "/ai1"
        LC_channel = deviceName + "/ai2"
        LVDT_channel = deviceName + "/ai3"

        #Initial DAQ setup
        self.analog_input = Task()
        self.data = zeros((300,), dtype=float64)
        self.read = int32()

        #Set up analog channels
        self.analog_input.CreateAIVoltageChan(TC_channel,"",DAQmx_Val_Cfg_Default, 0 , 10.0, DAQmx_Val_Volts, None)
        self.analog_input.CreateAIVoltageChan(LC_channel,"",DAQmx_Val_Cfg_Default, -10.0 , 10.0, DAQmx_Val_Volts, None)
        self.analog_input.CreateAIVoltageChan(LVDT_channel,"",DAQmx_Val_Cfg_Default, -10.0 , 10.0, DAQmx_Val_Volts, None)
        
        #Measurement timing
        self.analog_input.CfgSampClkTiming("",1000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 100)

        #Reading setup
        self.analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, self.data, 300, byref(self.read), None)
        
        if debug:
            print("DAQ Configured")
            
            print(self.data)
            print(type(self.analog_input))
        return self.analog_input

    #TODO def zero_lvdt(self):
    #   self.read_daq(analog_input)

    #TODO def zero_load_cell(self):
    
    def __init__(self, deviceName):
        self.deviceName = deviceName
        self.analog_input = self.daq_setup(self.deviceName)

    def read_daq(self):
        if debug:
            print("Read daq entered")
            print(type(self.analog_input))
        
        self.analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, self.data, 300, byref(self.read), None)

        temperature, loadcell, length = self.convert_data(self.data) ### HOW IS DATA VARIABLE TREATED INSIDE THE CLASS???????????

        return temperature, loadcell, length
 
        
    def convert_data(self,data):
        #takes average of 100 data reading, converts to physical value, and retuns value
        """"
        TC: T(C) = 117.11298671*V  + 0.018616368 
        Load Cell:
        LVDT:  d(mm) = 0.25*V
        
        """
        
        temperatureSlope = 119.746003543    
        temperatureOffset = -2.22923
        loadSlope = 247.258433769
        loadOffset = -44.3671200508
        lengthSlope = 0.25
        lengthOffset = 0
        
        Temperature = mean(data[0:99])
        Load = mean(data[100:199])
        Length = mean(data[200:299])

        temperature = temperatureSlope * Temperature + temperatureOffset
        load = loadSlope * Load + loadOffset
        length = lengthSlope * Length + lengthOffset

        return temperature, load, length
            
    def kill_daq(self):
        del self


################################    File Class    ################################

class FileIO:

    def __init__(self, sample):
        self.file_name = input("File Name: ")
       
        if self.file_name[-4:] != '.txt':
            self.file_name = self.file_name + '.txt'

        self.log_file = open(self.file_name, 'w')

        ## Initiate Header
        date = time.strftime('%Y-%m-%d %H:%M:%S')
        
        self.log_file.write('Pressure Assisted Sintering\t%s\n' %  date)
        self.log_file.write('Inital sample thickness:\t%s\tmm\n' % sample.initial_length)
        self.log_file.write('Inital sample diameter:\t%s\tmm\n' % sample.initial_diameter)
        #TODO CHECK FOR OTHER PARAMETERS: MATERIAL; PRESSURE; E-FIELD; CURRENT LIMIT if mySample.material()
        
        self.log_file.write('')
        self.log_file.write('#\tClock Time\tElapsed Time [s]\tT [C]\tLoad [N]\tdL [mm]\n')
        
        #Set up timing mechanisms
        
        timing_rate = input("Choose recording interval (s) (Default 1/second): ")
        
        if timing_rate is None:
            self.sampling_rate = 1.0
        else:
            self.sampling_rate = float(timing_rate)
        
        self.start_time = None
        self.elapsed_time = 0
        #return self.log_file

    def set_start_time(self):
        self.start_time = time.time()
        
    def get_elapsed_time(self):
        return time.time()-self.start_time
        
    def write_to_file(self,i,measured_data):
        now =  time.strftime('%H:%M:%S')
        elapsed_time = self.get_elapsed_time()
        
        if measured_data[0] is None:
            self.log_file.write('%i\t%s\t%d\t--\t--\t--\n' % (i, now, elapsed_time)) 
        else:
            temperature = measured_data[0]
            load = measured_data[1]
            length = measured_data[2]
            self.log_file.write('%i\t%s\t%f\t%f\t%f\t%f\n' % (i, now, elapsed_time, temperature, load, length))

    def close_file(self):
        self.log_file.close()
        
################################    Sample Class    ################################
class Sample:

    def __init__(self):
        self.initial_length = input('Initial sample thickness (mm): ')
        self.initial_diameter = input('Initial sample diameter (mm): ')
        
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
    
    if debug:
        print(mySample.initial_length)
        print(mySample.initial_diameter)
    
    # Create file and header
    myFile = FileIO(mySample)
    #Setup DAQ
    myDaq = DaqMeasurement('dev5')
    if debug:
        print("Daq class created")
    #TODO Connect Keithly and Agilent ????

    #TODO Zero Load cell
    #myDaq.zero_load_cell()
                         
    #TODO#Zero lvdt
    #myDaq.zero_lvdt()

    
    #start measurement loop
    loops_run = 0
    samples_written = 0
    next_sample_time = 0
    
    myFile.set_start_time()
    
    try:
        while True:
            if debug:
                print("loop started")
        
            loops_run = loops_run + 1
            measured_data = myDaq.read_daq()
            print(measured_data)
            
            #Save to file only at a certain interval
            # Very rough timer
            if myFile.get_elapsed_time()>= next_sample_time:
                samples_written = samples_written + 1 
                myFile.write_to_file(samples_written,measured_data)
                next_sample_time = next_sample_time + myFile.sampling_rate
            
            # Update GUI Displays
    except KeyboardInterrupt:
        print(str(loops_run)+ ' measurements taken')
    
    #shut down
    myFile.close_file()
    myDaq.kill_daq()
                             

if __name__ == '__main__':
    main()
    

