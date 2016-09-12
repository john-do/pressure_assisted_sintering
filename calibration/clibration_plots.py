#!/usr/bin/env python3.5

"""
Calibration curves for data covertion of pressure assisted sintering



"""

import matplotlib.pyplot as plt
import numpy as np


################ Thermocouple  ################

Temperature = [0, 100]
TC_voltage = [18.616368e-3, 853.717307e-3]

m,b = np.polyfit(TC_voltage, Temperature, 1)

#PRINT(TC_FIT_VALUES)
fit_equation= 'T ($^{\circ}$C) = '+ str(m) + '*V \n               + ' + str(b)
xi = np.arange(0,2)
fit_line = m*xi + b
#print(fit_equation)
plt.figure(1)

plt.plot(TC_voltage, Temperature, 'yo', xi, fit_line)#, TC_voltage,(TC_fit_values[0]*TC_voltage+ TC_fit_values[1]), '--k')

plt.title('Thermocouple Calibration')


#plt.xlim(-0.1, 1.1)
plt.ylim(-2, 102)

plt.annotate(fit_equation, xy = (0.05,80))
plt.xlabel('DAQ Voltage (V)')
plt.ylabel('Temperature $^{\circ}$C')

plt.savefig('TC_calibration.png')



################ Load cell ################
force = [0, 250.0, 500.0, 750.0 , 1000.0] # Newtons
lc_voltage = [192.1467e-3, 1.181098, 2.191091, 3.211605, 4.232119]

m,b = np.polyfit(lc_voltage,force, 1)

fit_equation= 'Force (N) = '+ str(m) +'*V\n                  + ' + str(b)
xi = np.arange(0,6)
fit_line=m*xi+b

plt.figure(2)
plt.title('Load Cell Calibration')

plt.plot(lc_voltage, force, 'k^',xi, fit_line)
plt.xlabel('Load Cell Voltage (V)')
plt.ylabel('Load (N)')

plt.ylim(-20, 1020)

plt.annotate(fit_equation, xy = (0.05,800))

plt.savefig('LC_calibration.png')





################ LVDT ################






plt.show()
