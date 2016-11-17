#!/usr/bin/python3

import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import QThread, SIGNAL
from PyDAQmx import *
from numpy import zeros, mean, float64
import random, time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas

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
        #print('in daq_setup')
        #create channel names based on deviceName
        TC_channel = deviceName + "/ai1"
        LC_channel = deviceName + "/ai2"
        LVDT_channel = deviceName + "/ai3"
        #print('channels namesd')
        #Initial DAQ setup
        self.analog_input = Task()
        self.data = zeros((300,), dtype=float64)
        self.read = int32()
        
        #print('Initial setup passed')
        #Set up analog channels
        self.analog_input.CreateAIVoltageChan(TC_channel,"",DAQmx_Val_Cfg_Default, 0 , 10.0, DAQmx_Val_Volts, None)
        self.analog_input.CreateAIVoltageChan(LC_channel,"",DAQmx_Val_Cfg_Default, -10.0 , 10.0, DAQmx_Val_Volts, None)
        self.analog_input.CreateAIVoltageChan(LVDT_channel,"",DAQmx_Val_Cfg_Default, -10.0 , 10.0, DAQmx_Val_Volts, None)
        #print('channels set up')
        
        #Measurement timing
        self.analog_input.CfgSampClkTiming("",1000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 100)
        #print('timing set')
        
        #Reading setup
        self.analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, self.data, 300, byref(self.read), None)
        
        
        print("DAQ Configured")

        return self.analog_input

    
    def __init__(self, deviceName):
        print('daq setup started')      
        self.deviceName = deviceName
        self.analog_input = self.daq_setup(self.deviceName)
        
        
        #initialize loadcell and lvdt offsets to zero
        self.loadOffset = 0
        self.lengthOffset = 0

    def read_daq(self):
        
        self.analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, self.data, 300, byref(self.read), None)
        #print(self.data)
        temperature, loadcell, length = self.convert_data(self.data) 
        print(temperature, loadcell, length)
        
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
        """
        try:
            Temperature = mean(data[0:99])
            Load = mean(data[100:199])
            Length = mean(data[200:299])
        except:
            Temperature = 0
            Load = 0
            Length = 0
            
        """
        try:
            Temperature = mean(data[0:99])
            Load = mean(data[100:199])
            Length = mean(data[200:299])
            
            
        except:
            Temperature = 0
            Load = 0
            Length = 0
        
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
        print('grabDAQ initiated')
        
    def __del__(self):
        self.wait()
            
    def _gen_signal(self):
        #print('generating daq signals')
        return self.daq.read_daq()
            
    def run(self):
        print('starting grabDAQ run')
        i = 0
        signal_out = [1,1,1,1,1]
        while True:
            ###################################### Create output string#################
            i += 1
            daq_out = self._gen_signal()
            
            signal_out[0]= i
            signal_out[1] = time.time()
            signal_out[2] =  daq_out[0]
            signal_out[3] =  daq_out[1]
            signal_out[4] =  daq_out[2]
            
            signal_string = ''
            for x in signal_out:
                signal_string = signal_string+str(x) + ','
            
            #print('Signal STring: ' + signal_string)
            self.emit(SIGNAL("update_display(QString)"),signal_string)

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
        self.temperature_display.setDigitCount(6)
        temp_palette =self.temperature_display.palette()
        temp_palette.setColor(temp_palette.WindowText, QtGui.QColor(255,0,0))
        temp_palette.setColor(temp_palette.Background, QtGui.QColor(0,0,0))
        temp_palette.setColor(temp_palette.Light, QtGui.QColor(255,0,0))
        temp_palette.setColor(temp_palette.Dark, QtGui.QColor(255,0,0))
        self.temperature_display.setPalette(temp_palette)
        
        pressure_lbl = QtGui.QLabel('Force (N):', self)
        self.pressure_display = QtGui.QLCDNumber(self)
        self.pressure_display.setDigitCount(6)
        p_palette =self.temperature_display.palette()
        p_palette.setColor(p_palette.WindowText, QtGui.QColor(0,255,0))
        p_palette.setColor(p_palette.Background, QtGui.QColor(0,0,0))
        p_palette.setColor(p_palette.Light, QtGui.QColor(0,255,0))
        p_palette.setColor(p_palette.Dark, QtGui.QColor(0,255,0))
        self.pressure_display.setPalette(p_palette)
        
        lvdt_lbl = QtGui.QLabel('Displacement (mm):', self)
        self.lvdt_display = QtGui.QLCDNumber(self)
        self.lvdt_display.setDigitCount(6)
        l_palette =self.temperature_display.palette()
        l_palette.setColor(l_palette.WindowText, QtGui.QColor(0,0,255))
        l_palette.setColor(l_palette.Background, QtGui.QColor(0,0,0))
        l_palette.setColor(l_palette.Light, QtGui.QColor(0,0,255))
        l_palette.setColor(l_palette.Dark, QtGui.QColor(0,0,255))
        self.lvdt_display.setPalette(l_palette)
        
        
        ## Plotting Frame
        
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        """
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.SetupUi)
        """
        ## Build Main Frame
        self.main_frame = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        
        disp_layout = QtGui.QVBoxLayout()
        
        disp_layout.addWidget(temperature_lbl)
        disp_layout.addWidget(self.temperature_display)
        
        disp_layout.addWidget(pressure_lbl)
        disp_layout.addWidget(self.pressure_display)
        disp_layout.addWidget(lvdt_lbl)
        disp_layout.addWidget(self.lvdt_display)
        
        layout.addLayout(disp_layout)
        layout.addWidget(self.canvas)
        
        self.main_frame.setLayout(layout)
        self.setCentralWidget(self.main_frame)
        self.setGeometry(0,0,900,650)
        self.move(10,10)
        self.setWindowTitle('Pressure Assisted Sintering Helper')        
    
class NewSampleUi(QtGui.QDialog):
    
    
    def __init__(self, parent=None):
        self.file_name = ''
        self.diameter = None
        self.thickness = None
        self.rate = 1
        super(NewSampleUi, self).__init__(parent)
        
        ## Define GUI Widgets
        self.file_lbl =  QtGui.QLabel('File:',self)
        self.diameter_lbl = QtGui.QLabel('Sample Diameter (mm)',self)
        self.thickness_lbl = QtGui.QLabel('Sample Thickness (mm)', self)
        self.sample_rate_lbl = QtGui.QLabel('Sample Interval (s)', self)
        
        self.file_prompt = QtGui.QPushButton('Select File')
        self.file_prompt.clicked.connect(self.getfile)
        
        self.sample_diameter =  QtGui.QLineEdit()
        self.sample_thickness =  QtGui.QLineEdit()
        self.sample_rate = QtGui.QLineEdit('1')
        
        
        self.ok_btn = QtGui.QPushButton('Ok', self)
        self.ok_btn.clicked.connect(self.ok_clicked)
        
        self.cancel_btn = QtGui.QPushButton('Cancel', self)
        self.cancel_btn.clicked.connect(self.cancel_clicked)
        
        ##Build Layout
        grid =QtGui.QGridLayout()
        grid.setSpacing(10)
        
        grid.addWidget(self.file_lbl,1,0)
        grid.addWidget(self.file_prompt, 1, 1)
        
        grid.addWidget(self.diameter_lbl, 2, 0)
        grid.addWidget(self.sample_diameter, 2, 1)
        
        grid.addWidget(self.thickness_lbl, 3, 0)
        grid.addWidget(self.sample_thickness, 3, 1)
        
        grid.addWidget(self.sample_rate_lbl, 4,0)
        grid.addWidget(self.sample_rate,4,1)
        
        grid.addWidget(self.ok_btn, 5, 0)
        grid.addWidget(self.cancel_btn, 5, 1)
        
        self.setLayout(grid)
        self.setWindowTitle('New Sample')
        #self.show()
        
        
        
    def getfile(self):
        self.file_name = QtGui.QFileDialog.getSaveFileName(self, 'Choose File','',"txt (*.txt)")
        #print(self.file_name)
        self.file_prompt.setText('Selected')

    def ok_clicked(self):
        
        #print(self.file_name)
        try:
            self.diameter = float(self.sample_diameter.text())
            #print(self.diameter)
        except:
            pass
            #print('diameter error')
        
        try:
            self.thickness = float(self.sample_thickness.text())
            #print(self.thickness)
        except:
            pass
            #print('thickenss error')
        
        try:
            self.rate = int(self.sample_rate.text())
            #print(self.thickness)
        except:
            pass
            #print('thickenss error')

        if self.file_name :
            
            #return True, self.diameter, self.thickness, self.file_name
            self.accept()
        else:
            pass
            
    def cancel_clicked(self):
        self.close()
        
    def getValues(self):
        if self.file_name[-4:] != '.txt':
            self.file_name = self.file_name + '.txt'
            
        return True, self.diameter, self.thickness, self.file_name, self.rate


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

        #Try to Connect to DAQ

        try:
            self.DAQ = DaqMeasurement('dev5')
            tryDaq = False
        
        except:
            QtGui.QMessageBox.critical(self, "DAQ Connection",
                                       "Error Connecting to DAQ",
                                   QtGui.QMessageBox.Ok)
            sys.exit()
        
        #Create Operating Definitions
        self.live_view = False
        self.run_measurement = False
        self.start_time = None
        self.next_write_time = 0 
        self.i = 0
        
        #ploting variables
        self.x = []
        self.y_temperature = []
        self.y_force =[]
        self.y_displacement = []
        
        #Create Gui Objects
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
        self.gui.stopMeasurement.setEnabled(False)
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
            self.sample_rate = values[4]
            print('Sample rate set as:', self.sample_rate)
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
        self.get_thread = grabDaq(self.DAQ)
        print('DAQ Thread Created')
        self.live_view = True
        self.connect(self.get_thread, SIGNAL("update_display(QString)"),self.update_display)
        self.get_thread.start()
        print('DAQ Thread started')

    def start_measurement(self):
        if self.file_name is None:
            #if file doesn't exist, then measurement cannot be started
            QtGui.QMessageBox.critical(self, "Sample Definition",
                                       "Sample must first be defined",
                                       QtGui.QMessageBox.Ok)
        
        elif self.live_view:
            #If live view is already running, set measurement status to true and set start time
            self.run_measurement = True
            self.start_time = time.time()
            self.gui.stopMeasurement.setEnabled(True)
            
        else:
            #IF live view is not running, start live view, set measure status to true, set start time 
            self.start_live_view()
            self.start_time = time.time()
            self.run_measurement = True
            self.gui.stopMeasurement.setEnabled(True)
            
    def stop_measurement(self):
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

    def update_display(self, signal_text):
        out = signal_text.split(',')
        measurement_time = float(out[1])
        
        try:
            elapsed_time = measurement_time-self.start_time
        except:
            pass
            
        temperature = float(out[2])
        force = float(out[3])
        displacement = float(out[4])
        self.gui.temperature_display.display(str("%.1f'"%temperature))
        self.gui.pressure_display.display(str("%.1f"%force))
        self.gui.lvdt_display.display(str("%.3f"%displacement))

        if self.run_measurement:
            if elapsed_time>= self.next_write_time:
                self.i += 1
                
                text_out = str(self.i) + '\t' + time.strftime('%H:%M:%S') + '\t'+ str("%.2f"%elapsed_time)+ '\t' + str("%.2f"%temperature) + '\t' + str("%.2f"%force)+ '\t' + str("%.4f"%displacement) + '\n'
                f = open(self.file_name, 'a')
                f.write(text_out)
                f.close()
                self.next_write_time = self.next_write_time + self.sample_rate
                
                if self.i%2:
                    self.update_plot(elapsed_time, temperature, force, displacement)
            
    def update_plot(self, new_time, temperature, force, displacement): 
        
        ##Update data
        if len(self.x)>300:
            #self.x = self.x[1:]
            #self.y_temperature = self.y_temperature[1:]
            #self.y_force = self.y_force[1:]
            #self.y_displacement = self.y_displacement[1:]
            del self.x[0]
            del self.y_temperature[0]
            del self.y_force[0]
            del self.y_displacement[0]
            
        self.x.append(new_time)
        self.y_temperature.append(temperature)
        self.y_force.append(force)
        self.y_displacement.append(displacement)
        
        ##Update Plots
        if len(self.x)<2:
            self.axes = [self.gui.ax, self.gui.ax.twinx(), self.gui.ax.twinx()]
            self.gui.fig.subplots_adjust(right=0.75)
            self.axes[-1].spines['right'].set_position(('axes', 1.2))
            self.axes[2].set_frame_on(True)
            self.axes[2].patch.set_visible(False)
            print(id(self.axes[1]), id(self.axes[2]))
        #self.axes[0].hold(False)
        self.axes[0].plot(self.x,self.y_temperature,  color='Red')[0]
        self.axes[0].set_ylabel('Temperature $^{\circ}$C', color='Red')
        self.axes[0].tick_params(axis='y', colors='Red')

        #self.axes[1].hold(False)
        self.axes[1].plot(self.x,self.y_force,  color='Green')[0]
        self.axes[1].set_ylabel('Force (N)', color='Green')
        self.axes[1].tick_params(axis='y', color='Green')
        
        #self.axes[2].hold(False)
        self.axes[2].plot(self.x,self.y_displacement,  color='Blue')[0]
        self.axes[2].set_ylabel('Displacement (mm)', color='Blue')
        self.axes[2].tick_params(axis='y', colors='Blue')

        self.axes[0].set_xlim(self.x[0],self.x[len(self.x)-1])
                
        self.axes[0].set_xlabel('Elapsed Time(s)')

        """
        ax = self.gui.fig.add_subplot(111)
        ax.hold(False)
        ax.plot(self.x,self.y_temperature)
        ax.set_xlabel('Elapsed Time (s)')
        ax.set_ylabel('Temperature $^{\circ}$')
        ax.set_xlim(self.x[0],self.x[len(self.x)-1])
        """
        #time.sleep(0.1)
        self.gui.canvas.draw()
        time.sleep(0.3)
       
        
        
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
