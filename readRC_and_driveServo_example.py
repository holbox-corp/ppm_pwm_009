# Copyright 2021 Holbox Corporation
# Use under MIT license

import holbox_ppm_pwm_lib
import time
import numpy as np

''' Example: Read channel values from RC receiver and set those values to Drive Servos'''
# Make sure all your connections are connect and that power is provided to the board, RC receiver and servos as specified in the manual.

# Define board I2C address
I2C_SLAVE_ADDRESS = 41  # Default is 41. Can be set to 51 if jumper cable is connected on board ADDR

my_receiver = ReceiverPPM(I2C_SLAVE_ADDRESS, "PPM_PWM009") # Creates instance of ReceiverPPM object. Will be used to read RC values

#my_pwm = OutputDrive(I2C_SLAVE_ADDRESS, "led", "PPM_PWM009")  # Creates instance of OutputDrive object to control LEDs brightness will be used to set LED values
my_pwm = OutputDrive(I2C_SLAVE_ADDRESS, "servo", "PPM_PWM009")  # Creates instance of OutputDrive object to drive connected servos or brushless motors. Will be used to set PPM values

# Mirror RC values to servos:
# Read and write control loop: This example will first read channel values from my_receiver. Then will set those  values to the servo pins.
# In reality you can set any values from [0-1023]
# For example, you can read channel values from RC, use those values in a PID control loop, and then use the resulting values to drive servos
while True:
    time1 = time.time()  # time1 will later be used to set a constant 20ms loop period
    # read channel values:
    channel_values = my_receiver.read_channels() # Reads RC channel values. Values are from 0 to 1023

    # Your PID code can go somewhere here

    # In this example we'll set my_pwm pin values to what was read and stored in channel_values. This will directly mirror Transmitter control to servos
    # my_pwm.set_pin_value(pin_number, value)
    my_pwm.set_pin_value(1, channel_values[1])
    my_pwm.set_pin_value(2, channel_values[2])
    my_pwm.set_pin_value(3, channel_values[3])
    my_pwm.set_pin_value(4, channel_values[4])

    #  Use my_pwm.write_pin_values() to send all previously set pin values to the servo driver board
    my_pwm.write_pin_values() #  Don't miss this instruction in each cycle after setting the pin values, otherwise won't update servos!!!

    execution_time = time.time() - time1
    time.sleep(.02 - execution_time )  #  Sets a consistent cycle time of 20 ms.
    # For best real-time performance make sure your cycle period is always .02 secods which corresponds to 50 cycles per second
    # To display values during testing you can set a cycle period of .1 seconds: time.sleep(.1)

    print('ch vals', channel_values); # Print channel values. Display channel values only for testing. Comment this line for real-time use!!!
    #channel_values[0] is the total number of channels avaiable in your RC receiver.
    #channel_values[1] is the value of channel 1, channel_values[2] is the value of channel 2, channel_values[3] is the value of channel 3... channel_values[N] is the value of channel N
