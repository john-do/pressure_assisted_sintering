from PyDAQmx import *
from numpy import zeros, mean, float64

deviceName = 'dev5'
TC_channel = deviceName + "/ai1"
LC_channel = deviceName + "/ai2"
LVDT_channel = deviceName + "/ai3"

analog_input = Task()
data = zeros((300,), dtype=float64)
read = int32()
analog_input.CreateAIVoltageChan(TC_channel,"",DAQmx_Val_Cfg_Default, 0 , 10.0, DAQmx_Val_Volts, None)
analog_input.CreateAIVoltageChan(LC_channel,"",DAQmx_Val_Cfg_Default, 0 , 10.0, DAQmx_Val_Volts, None)
analog_input.CreateAIVoltageChan(LVDT_channel,"",DAQmx_Val_Cfg_Default, -10.0 , 10.0, DAQmx_Val_Volts, None)
analog_input.CfgSampClkTiming("",1000.0, DAQmx_Val_Rising, DAQmx_Val_FiniteSamps, 100)

analog_input.ReadAnalogF64(100, 10.0,  DAQmx_Val_GroupByChannel, data, 300, byref(read), None)

analog_input.ReadAnalogF64(100,10.0,DAQmx_Val_GroupByChannel,data,300,byref(read),None)

print("data collected read to average")
#print(type(data))
print(data)

T=mean(data[0:99])
LC=mean(data[100:199])
LVDT = mean(data[200:299])

T=119.746003543*T  + -2.22923566848 
LC = 247.258433769 * LC + -44.3671200508
LVDT = 0.25*LVDT


print(T)
print(LC)
print(LVDT)

DAQmxStopTask(analog_input)
DAQmxClearTask(analog_input)