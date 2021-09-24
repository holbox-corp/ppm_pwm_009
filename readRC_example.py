# Copyright 2021 Holbox Corporation
# Use under MIT license

import holbox_ppm_pwm_lib
import time
import numpy as np

''' Example: Read and display channel values from RC receiver '''
# Make sure all your connections are connect and that power is provided to the board, RC receiver and servos as specified in the manual.

# Define board I2C address
I2C_SLAVE_ADDRESS = 41  # Default is 41. Can be set to 51 if jumper cable is connected on board ADDR

my_receiver = ReceiverPPM(I2C_SLAVE_ADDRESS, "PPM_PWM009") # Creates instance of ReceiverPPM object. Will be used to read RC values

# Loop to read and display channel values from RC receiver:
while True:
    time1 = time.time()  # time1 will later be used to set a constant loop period
    # read channel values:
    channel_values = my_receiver.read_channels() # Reads RC channel values. Values are from 0 to 1023

    # Your PID code can go somewhere here

    execution_time = time.time() - time1
    time.sleep(.1 - execution_time )  #  Sets a consistent cycle time .
    # For best real-time performance make sure your cycle period is always .02 secods which corresponds to 50 cycles per second
    # To display values during testing you can set a cycle period of .1 seconds: time.sleep(.1)

    print('ch vals', channel_values); # Print channel values. Display channel values only for testing. Comment this line for real-time use!!!
    #channel_values[0] is the total number of channels avaiable in your RC receiver.
    #channel_values[1] is the value of channel 1, channel_values[2] is the value of channel 2, channel_values[3] is the value of channel 3... channel_values[N] is the value of channel N
