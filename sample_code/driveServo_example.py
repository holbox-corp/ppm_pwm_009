# Copyright 2021 Holbox Corporation
# Use under the MIT license

import holbox_ppm_pwm_lib
import time
import numpy as np

''' Example: Set values to Drive Servos or LEDs'''
# Make sure all your connections are connect and that power is provided to the board, RC receiver and servos as specified in the manual.

# Define board I2C address
I2C_SLAVE_ADDRESS = 41  # Default is 41. Can be set to 51 if jumper cable is connected on board ADDR

#my_pwm = OutputDrive(I2C_SLAVE_ADDRESS, "led", "PPM_PWM009")  # Creates instance of OutputDrive object to control LEDs brightness will be used to set LED values
my_pwm = OutputDrive(I2C_SLAVE_ADDRESS, "servo", "PPM_PWM009")  # Creates instance of OutputDrive object to drive connected servos or brushless motors. Will be used to set PPM values

# In the following loop, all pwm outputs will be set to the value of the variable value which will be incremented by 10 in each cycle
value = 0
while True:
    time1 = time.time()  # time1 will later be used to set a constant 20ms loop period

    # Increment variable value:
    value = value + 10
    if value >=1023
        value = 0

    # Your PID or control code can go somewhere here

    # Set pwm pins to value
    my_pwm.set_pin_value(1, value)
    my_pwm.set_pin_value(2, value)
    my_pwm.set_pin_value(3, value)
    my_pwm.set_pin_value(4, value)
    my_pwm.set_pin_value(5, value)
    my_pwm.set_pin_value(6, value)
    my_pwm.set_pin_value(7, value)
    my_pwm.set_pin_value(8, value)
    my_pwm.set_pin_value(9, value)

    #  Use my_pwm.write_pin_values() to send all previously set pin values to the servo driver board
    my_pwm.write_pin_values() #  Don't miss this instruction in each cycle after setting the pin values, otherwise won't update servos!!!

    execution_time = time.time() - time1
    time.sleep(.02 - execution_time )  #  Sets a consistent cycle time of 20 ms.
    # For best real-time performance make sure your cycle period is always .02 secods which corresponds to 50 cycles per second
    # To display values during testing you can set a cycle period of .1 seconds: time.sleep(.1)
