#!/usr/bin/python3

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL

import random, time
import threading

############################################################
################          DAQ Class         ################
############################################################
class DaqMeasurement:
    # Values from calibration of transducers
    # LOADCELLSLOPE = 247.258433769
    # LVDTSLOPE = 0.25
    # temperatureSlope = 119.746003543    
    # temperatureOffset = -2.22923
    # loadSlope = 247.258433769
    # loadOffset = -44.3671200508

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

        return self.analog_input

    
    def __init__(self, deviceName):
        self.deviceName = deviceName
        self.analog_input = self.daq_setup(self.deviceName)
        
        #initialize loadcell and lvdt offsets to zero
        self.loadOffset = 0
        self.lengthOffset = 0

    def read_daq(self):
        
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
        #loadOffset = -44.3671200508
        lengthSlope = 0.25
        #lengthOffset = 0
        
        Temperature = mean(data[0:99])
        Load = mean(data[100:199])
        Length = mean(data[200:299])

        temperature = temperatureSlope * Temperature + temperatureOffset
        load = loadSlope * Load + self.loadOffset
        length = lengthSlope * Length + self.lengthOffset

        return temperature, load, length
    
    def zero_load_cell(self):
        
        #input("Press enter when ready when load cell is at zero load:")
        temperature, loadcell, length = self.read_daq()
        
        self.loadOffset = -1* loadcell
    
    
    def zero_lvdt(self):
        #Adjusts lengthOffset to zero at current value
        #input("Press enter when ready when lvdt is set:")
        temperature, loadcell, length = self.read_daq()
        
        self.lengthOffset = -1* length
        
    def kill_daq(self):
        #deletes object
        del self

############################################################
################         Threads            ################
############################################################

class data_simulator(QThread):
    def __init__(self):
        QThread.__init__(self)

        
    def __del__(self):
        self.wait()
        
    def _gen_signal(self):
    
        temperature = int(random.randint(0,1000))
        force = int(random.randint(0,1000))
        displacement = int(random.randint(0,1000))
        out = [temperature,force,displacement]
        return out    


    def run(self):
        i = 0
        signal_out = [1,1,1,1,1] #i,time, v_temperature, v_force, v_displacement
        while i<50:
            #print(i)
            i +=1
            
            daq_voltages = self._gen_signal()
            
            signal_out[0]=i
            signal_out[1] = time.time()
            signal_out[2] =  daq_voltages[0]
            signal_out[3] =  daq_voltages[1]
            signal_out[4] =  daq_voltages[2]
            
            
            signal_string = ''
            for x in signal_out:
                signal_string=signal_string+str(x) + ','
               
               
            
            signal_string=signal_string+str(1)  
            #singal_out = str(i)+ ',' + str(measurement_time) + ',' + signal_out
            
            self.emit(SIGNAL("update_display(QString)"),signal_string)
            time.sleep(0.1)


class grabDaq(QThread):
    
    def __init__(self, daq):
        QThread.__init__(self)
        self.daq = daq
        
        
    def __del__(self):
        self.wait()
            
    def _gen_signal(self):
        data = self.daq.read_daq()
        return self.daq.convert_data(data)
            
    def run(self):
        i = 0
        signal_out = [1,1,1,1,1]
        while True:
            ###################################### Create output string#################
            daq_out = self._gen_signal
            
            signal_out[0]=i
            signal_out[1] = time.time()
            signal_out[2] =  daq_out[0]
            signal_out[3] =  daq_out[1]
            signal_out[4] =  daq_out[2]
            
            signal_string = ''
            for x in signal_out:
                signal_string=signal_string+str(x) + ','
            
            self.emit(SIGNAL("save_measurement(QString)"),save_measurement)

############################################################
################   User Interface Clases    ################
############################################################

class SetupUi(QtGui.QMainWindow):

    def __init__(self):
        super(self.__class__,self).__init__()

        self.create_menu()
        self.create_main_frame()
        

    def create_menu(self):
        self.statusBar()
        menubar = self.menuBar()

        
        #Define Menu Options
        self.startLiveView = QtGui.QAction('Start Live View',self)
        self.startLiveView.setStatusTip('Start Dispaly')

        self.startMeasurement = QtGui.QAction('Start Measurement',self)
        self.startMeasurement.setStatusTip('Start Recording Measurement')
        
        self.stopMeasurement  = QtGui.QAction('Stop Measurement',self)
        self.stopMeasurement.setShortcut('Ctrl+C')
        self.stopMeasurement.setStatusTip('Stop Recording Measurement')
        
        self.exitAction = QtGui.QAction(QtGui.QIcon(),'&Quit',self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.exitAction.setStatusTip('Exit Application')
        


        self.newSample = QtGui.QAction(QtGui.QIcon(),'Define &New Sample',self)
        self.newSample.setShortcut('Ctrl+N')
        self.newSample.setStatusTip('Define New Sample')

        
        self.zeroLoadCell = QtGui.QAction(QtGui.QIcon(),'&Zero Load Cell',self)
        self.zeroLoadCell.setStatusTip('Zero Load Cell')
 
        self.zeroLVDT = QtGui.QAction(QtGui.QIcon(),'&Zero LVDT',self)
        self.zeroLVDT.setStatusTip('Zero LVDT')
                          
        #Create Menu Structures
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(self.startLiveView)
        file_menu.addAction(self.startMeasurement)
        file_menu.addAction(self.stopMeasurement)
        file_menu.addAction(self.exitAction)

        setup_menu = menubar.addMenu('&Set Up')
        setup_menu.addAction(self.newSample)
        setup_menu.addAction(self.zeroLoadCell)
        setup_menu.addAction(self.zeroLVDT)

                                     

    def create_main_frame(self):

        ##Readout Displays
        temperature_lbl = QtGui.QLabel(r'Temperature (C):',self)
        self.temperature_display = QtGui.QLCDNumber(self)
        
        pressure_lbl = QtGui.QLabel('Force (N):', self)
        self.pressure_display = QtGui.QLCDNumber(self)
        
        lvdt_lbl = QtGui.QLabel('Displacement (mm):', self)
        self.lvdt_display = QtGui.QLCDNumber(self)

        ## Main Frame
        self.main_frame = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        
        layout.addWidget(temperature_lbl)
        layout.addWidget(self.temperature_display)
        
        layout.addWidget(pressure_lbl)
        layout.addWidget(self.pressure_display)
        layout.addWidget(lvdt_lbl)
        layout.addWidget(self.lvdt_display)
        
        
        self.main_frame.setLayout(layout)
        self.setCentralWidget(self.main_frame)
        self.setGeometry(0,0,450,650)
        self.setWindowTitle('Pressure Assisted Sintering Helper')        
    
class NewSampleUi(QtGui.QDialog):
    
    
    def __init__(self, parent=None):
        self.file_name = ''
        self.diameter = None
        self.thickness = None
        
        super(NewSampleUi, self).__init__(parent)
        
        self.file_lbl =  QtGui.QLabel('File:',self)
        self.diameter_lbl = QtGui.QLabel('Sample Diameter',self)
        self.thickness_lbl = QtGui.QLabel('Sample Thickness', self)
        
        self.file_prompt = QtGui.QPushButton('Select File')
        self.file_prompt.clicked.connect(self.getfile)
        
        self.sample_diameter =  QtGui.QLineEdit()
        self.sample_thickness =  QtGui.QLineEdit()
        
        
        self.ok_btn = QtGui.QPushButton('Ok', self)
        self.ok_btn.clicked.connect(self.ok_clicked)
        
        self.cancel_btn = QtGui.QPushButton('Cancel', self)
        self.cancel_btn.clicked.connect(self.cancel_clicked)
        
        
        grid =QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.file_lbl,1,0)
        grid.addWidget(self.file_prompt, 1, 1)
        
        grid.addWidget(self.diameter_lbl, 2, 0)
        grid.addWidget(self.sample_diameter, 2, 1)
        
        grid.addWidget(self.thickness_lbl, 3, 0)
        grid.addWidget(self.sample_thickness, 3, 1)
        
        grid.addWidget(self.ok_btn, 4, 0)
        grid.addWidget(self.cancel_btn, 4, 1)
        
        self.setLayout(grid)
        self.setWindowTitle('New Sample')
        #self.show()
        
        
        
    def getfile(self):
        self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Choose File')
        #print(self.file_name)
        self.file_prompt.setText('Selected')

    def ok_clicked(self):
        print('ok was clicked')
        print(self.file_name)
        try:
            self.diameter = float(self.sample_diameter.text())
            print(self.diameter)
        except:
            pass
            print('diameter error')
        
        try:
            self.thickness = float(self.sample_thickness.text())
            print(self.thickness)
        except:
            pass
            print('thickenss error')
        
        print('im to the if')
        if self.file_name :
            print('in the if')
            #return True, self.diameter, self.thickness, self.file_name
            self.accept()
        else:
            print('ok was skipped')
            pass
            
    def cancel_clicked(self):
        self.close()
        
    def getValues(self):     
        return True, self.diameter, self.thickness, self.file_name
"""
    def __init__(self, parent = None):
        super(SetupUi,self).__init__(parent)
        layout = QGui.QVBoxLayout(self)
        
        
        
        buttons = QGui.QDialogButtonBox(
            QGui.QDialogButtonBox.Ok | QGui.QDialogButtonBox.Cancel,
            QGui.Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
"""

############################################################
################        Main Window         ################
############################################################

class SetUp(QtGui.QMainWindow):
    def __init__(self, parent = None):
        super(self.__class__, self).__init__(parent)

        #Sample Definitions
        self.diameter = None
        self.file_name = None
        self.sample_rate = 1

        #Connect to DAQ
        tryDaq = True
        while tryDaq:
            
            try:
                self.DAQ = DaqMeasurement('dev5')
                tryDaq = False
            
            except:
                QtGui.QMessageBox.critical(self, "DAQ Connection",
                                           "Error Connecting to DAQ",
                                       QtGui.QMessageBox.Ok)
        
        #Operating Definitions
        self.test = True

        self.live_view = False
        self.run_measurment = False
        #self.ldvt_offset = 0
        #self.loadcell_offset = 0
        self.start_time = None
        self.next_write_time = 0 

        #Gui Objects
        self.gui = SetupUi()
        self.new_sample = NewSampleUi()
        
        #Connect required signals to gui objects
        self._connectSignals()
        
        #Show Main Window
        self.gui.show()
        
    def _connectSignals(self):
        #File Menu Signals
        self.gui.startLiveView.triggered.connect(self.start_live_view)
        self.gui.startMeasurement.triggered.connect(self.start_measurement)
        self.gui.stopMeasurement.triggered.connect(self.stop_measurement)
        self.gui.exitAction.triggered.connect(self.exit_action)

        #Setup Menu Signals
        self.gui.newSample.triggered.connect(self.new_sample_pop_up)
        self.gui.zeroLoadCell.triggered.connect(self.DAQ.zero_load_cell)
        self.gui.zeroLVDT.triggered.connect(self.DAQ.zero_lvdt)
        
    @QtCore.pyqtSlot()
    def new_sample_pop_up(self):
        if self.new_sample.exec_() == QtGui.QDialog.Accepted:
            values= self.new_sample.getValues()
            print(values) #self.new_sample.exec_()
            
            self.diameter = values[1]
            self.thickness = values[2]
            self.file_name = values[3]


            #### Write File Header ###
            f = open(self.file_name,'w')
            

            date = time.strftime('%Y-%m-%d %H:%M:%S')
        
            f.write('Pressure Assisted Sintering\t%s\n' %  date)
            f.write('Inital sample thickness:\t%s\tmm\n' % self.thickness)
            f.write('Inital sample diameter:\t%s\tmm\n' % self.diameter)
        
            f.write('')
            f.write('#\tClock Time\tElapsed Time [s]\tT [C]\tLoad [N]\tdL [mm]\n')
            f.close()
    
    ################    File Menu Functions    ################    
    
    def start_live_view(self):  #OK
        
        self.get_thread = data_simulator() #!!!!!!!!!!!!!!!!!!!!
        self.live_view = True
        self.connect(self.get_thread, SIGNAL("update_display(QString)"),self.update_display)
        self.get_thread.start()

    def start_measurement(file_name, sample_rate, self):
        if self.file_name is None:
            QtGui.QMessageBox.critical(self, "Sample Definition",
                                       "Sample must first be defined",
                                       QtGui.QMessageBox.Ok)
        
        
        elif self.live_view:
            #If live view is already running kill thread and start thread connected to save_measurment
            self.get_thread.terminate()
            
            self.get_thread = data_simulator()  #!!!!!!!!!!!!!!!!!!!!
            self.live_view = True
            #self.connect(self.get_thread, SIGNAL("update_display(QString)"),self.update_display)
            self.connect(self.get_thread, SIGNAL("save_measurement(QString)"),self.save_measurement)
            self.get_thread.start()

            self.run_measurement = True

        else:
            #IF live view is not running, connect to view and start s
            self.get_thread = data_simulator()  #!!!!!!!!!!!!!!!!!!!!!!!
            self.live_view = True
            self.start_time = time.time()
            #self.connect(self.get_thread, SIGNAL("update_display(QString)"),self.update_display)
            self.connect(self.get_thread, SIGNAL("save_measurement(QString)"),self.save_measurement)
            self.get_thread.start()

            self.run_measurement = True

    def stop_measurement(self):
        #self.get_thread.terminate()
        self.run_measurement = False

    def exit_action(self):
        if QtGui.QMessageBox.question(None,'',"Are you sure you want to quit?",
                                      QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                      QtGui.QMessageBox.No) == QtGui.QMessageBox.Yes :

            #Clean up

            if self.live_view:
                self.get_thread.terminate()
            
            try:
                self.file_name.close()
            except:
               pass 
            
            ### Disconnect DAQ
            self.DAQ.kill_daq()
            
            QtGui.QApplication.quit()
            

    ################    Setup Menu Functions    ################

    def new_sample(self, parent = None):
        print('define new sample')
        newSample = NewSampleUi(parent)


    ################ Thread Return Functions ################
    def save_measurement(self,signal_text):
        #Unpackage Data
        print(signal_text)
        out = signal_text.split(',')
        index = float(out[0])
        measurement_time = float(out[1])
        elapsed_time = measurement_time-self.start_time
        temperature = float(out[2])
        force = float(out[3])
        displacement = float(out[4])
        
        
        #Update Displays live
        self.gui.temperature_display.display(temperature)
        self.gui.pressure_display.display(force)
        self.gui.lvdt_display.display(displacement)
        
        #Should data be saved?
        if elapsed_time()>= self.next_write_time and self.run_measurement == True:
            
            # !!!  prepare data to write   (Need to fix elapsed time)
            signal_text = signal_text[:-1] + '\n'  #remove extra comma and add carriage return
            #write data and close file
            f = open(self.file_name, 'a')
            f.write(signal_text)
            
            #Update next sample time
            self.next_write_time = self.next_write_time + self.sample_rate
        
        
        #Plot Data and scroll 
        


    def update_display(self, signal_text):
        
        print(signal_text)
        out = signal_text.split(',')
        temperature = float(out[2])
        force = float(out[3])
        displacement = float(out[4])

        self.gui.temperature_display.display(temperature)
        self.gui.pressure_display.display(force)
        self.gui.lvdt_display.display(displacement)

            



############################################################
################        Init Stuff          ################
############################################################
def main():
    app = QtGui.QApplication(sys.argv)
    form = SetUp()
    #form.show()
    sys.exit(app.exec_())
    
    

if __name__ == '__main__':
    main()
