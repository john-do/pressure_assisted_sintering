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


