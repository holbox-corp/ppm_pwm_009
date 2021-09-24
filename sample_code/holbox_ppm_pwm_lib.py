# Copyright 2021 Holbox Corporation
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

#PPM PWL Library
import sys
import smbus2 as smbus #,smbus2
import time
import numpy as np

class OutputDrive:
    def __init__(self, slave_address, output_mode, board_type):  # output_mode can be either "led" or "servo"
        self.slave_address = slave_address
        self.output_mode = output_mode
        self.board_type = board_type
        if self.board_type=="PPM_PWM009":
            self.output_pins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            self.MAX_PPM_CHS = 14
            self.NUM_PWM_PINS = 11
        elif self.board_type=="PPM_PWMLC":
            self.output_pins = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            self.MAX_PPM_CHS = 14
            self.NUM_PWM_PINS = 9
        else:
            raise Exception("Wrong board name, please specify correct board name on OutputDrive declaration")
        set_output_mode(self.output_mode, self.slave_address)
        self.output_pin_values = np.zeros(self.NUM_PWM_PINS, dtype=int)  # self.NUM_PWM_PINS Depends on board type.
        time.sleep(.02)  # Sleep time in seconds

    ''' set_pin_value  '''
    def set_pin_value(self, pin_number, value): #  Pin number must match board type. Value must be from 0 to 1023. # pin value check included

        #Convert value to integer
        value = int(value)

        # Verify value range is [0-1023]. Otherwise set value to either 0 or 1023
        if value < 0:
            value = 0
        elif value > 1023:
            value = 1023

        # Verify pin number is valid. Otherwise stop program execution and raise an error
        try:
            pin_index = self.output_pins.index(pin_number)
        except:
            raise Exception("Speficied pin number is not a valid servo/pwm pin")

        self.output_pin_values[pin_index] = value


    '''  write_pin_values  '''
    def write_pin_values(self):
        values_to_send_b36 = np.zeros( 2*len(self.output_pin_values), dtype=int )  # Each [0-1023] value will convert to b36 symbols represented by two [0-35] decimal numbers
        for pair_index, pin_value in enumerate(self.output_pin_values):
            values_to_send_b36[pair_index*2:pair_index*2+2] = b10_to_b36pair(pin_value)

        symbols_to_send = ""
        for current_value in values_to_send_b36:  # Convert all b36 values to b36 symbols
            symbols_to_send += b36_to_symbol(current_value)
        retry = 0
        try:
            send_i2c_unidir("20"+symbols_to_send, self.slave_address)  # Sends b36 xy command plus symbols to slave.
        except:
            print("Warning, write error (1st attempt)")  # If comm error, Do nothig. This will skip i2c transmission but wont fail
            ''' The following is a retry block j '''
            retry = 1
        if retry == 1:  # Retries if write error was present the previous time
            try:
                send_i2c_unidir("20"+symbols_to_send, self.slave_address)  # Sends b36 xy command plus symbols to slave.
            except:
                print("Warning, write error (2nd attempt)")  # If comm error, Do nothig. This will skip i2c transmission but wont fail


class ReceiverPPM:
    def __init__(self, slave_address, board_type): #
        """ Initialize a receiver object """
        self.slave_address = slave_address;
        self.board_type = board_type
        if self.board_type=="PPM_PWM009":
            self.output_pins = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
            self.MAX_PPM_CHS = 14
            self.NUM_PWM_PINS = 11
        elif self.board_type=="PPM_PWMLC":
            self.output_pins = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            self.MAX_PPM_CHS = 14
            self.NUM_PWM_PINS = 9
        else:
            raise Exception("Wrong board name, please specify correct board name on ReceiverPPM declaration")
        self.ch_values = np.zeros(self.MAX_PPM_CHS+1, dtype=int); # Max 14 channels. If rx has less than 14, rest of values will be 0.
        self.num_channels = 0


    ''' Read number of channels '''
    def read_num_channels(self):  #
        try:
            self.num_channels = unicode_to_int_b36_list(send_rec_i2c("40", 1, self.slave_address))[0]
            if self.num_channels < 0:
                self.num_channels = 0
        except:
            print("Warning, reading error")  # If comm error Do nothig. This will return the previous values but wont fail

        return self.num_channels


    ''' Read channel values'''
    def read_channels(self):  # Returns channel values from 0 to 1023. Pos 0 is number of channels
        try:
            expected_bytes = 1 + self.num_channels*2
            b36_ch_values = unicode_to_int_b36_list(send_rec_i2c("50", expected_bytes, self.slave_address))
            num_chs = b36_ch_values[0]
            if num_chs < 0 or num_chs > self.MAX_PPM_CHS:
                num_chs = 0
            self.num_channels = num_chs
            self.ch_values[0] = num_chs

            for i in range(self.num_channels):
                symbol_pair = b36_ch_values[2*i+1:2*i+3]
                self.ch_values[i+1] = b36pair_to_decimal(symbol_pair)
        except:
            print("Warning, reading error")  # If comm error Do nothig. This will return the previous values but wont fail
        return self.ch_values


''' Restart PPWM board '''
def restartPPWM(slave_address):
    send_i2c_unidir("00000", slave_address)


''' Set output mode (led or pwm)'''
def set_output_mode(output_mode, slave_address):  # output_mode can be either "led" or "servo"
    if output_mode == "servo":
        command_xy = "10000"
    elif output_mode == "led":
        command_xy = "11000"
    send_i2c_unidir(command_xy, slave_address)


def b10_to_b36pair(b10_number):
    if (b10_number > 1295):  # 1295 = 36^2-1
        b10_number = 1295
    b36_dec_array = np.zeros(2, dtype=int)
    b36_dec_array[1] = b10_number % 36
    quotient = int(np.floor(b10_number/36))
    b36_dec_array[0] = quotient % 36

    return b36_dec_array


def b36pair_to_decimal(symbol_pair):
    b10_int =  symbol_pair[0]*(36**1)+symbol_pair[1]*(36**0)
    return b10_int



# This function converts a string to an array of bytes each in unicode representation (example. "0" -> 48).
def ConvertStringsToBytes(src):  # Used for converting values before sending to slave device
    converted = []
    for b in src:
        converted.append(ord(b))
    return converted

''' Sends and receive values  '''   #
def send_rec_i2c(xy_string, num_expected_bytes, slave_address): # (xy_string is size 3 type char, x is 1 base36 number, y is another b36 number,  num_expected_bytes is integer value)

    with smbus.SMBus(1) as I2Cbus:
        BytesToSend = ConvertStringsToBytes(xy_string)
        # Sends to slave:
        I2Cbus.write_i2c_block_data(slave_address, 0x00, BytesToSend)

    #with smbus.SMBus(1) as I2Cbus:
        # Reads from Slave
        data = I2Cbus.read_i2c_block_data(slave_address,0x00,num_expected_bytes) #  If number of expected Bytes is smaller, will trim

    # Format of data is unicode number representing string.
    return data

''' Send data to slave (one way) '''
def send_i2c_unidir(string_to_send, slave_address):
    with smbus.SMBus(1) as I2Cbus:
        BytesToSend = ConvertStringsToBytes(string_to_send)
        # Sends to slave:
        I2Cbus.write_i2c_block_data(slave_address, 0x00, BytesToSend)



def unicode_to_int_b36_list(unicode_list): #
    int_b36_list =[0]*len(unicode_list)
    for index, unicode_value in enumerate(unicode_list):
        if unicode_value <= 57:
            int_b36_list[index] = unicode_value - 48
        else:
            int_b36_list[index] = unicode_value - 65 + 10
    return int_b36_list

def b36_to_symbol(b36_value):
    switch_dir = {
      0: "0",
      1: "1",
      2: "2",
      3: "3",
      4: "4",
      5: "5",
      6: "6",
      7: "7",
      8: "8",
      9: "9",
      10: "A",
      11: "B",
      12: "C",
      13: "D",
      14: "E",
      15: "F",
      16: "G",
      17: "H",
      18: "I",
      19: "J",
      20: "K",
      21: "L",
      22: "M",
      23: "N",
      24: "O",
      25: "P",
      26: "Q",
      27: "R",
      28: "S",
      29: "T",
      30: "U",
      31: "V",
      32: "W",
      33: "X",
      34: "Y",
      35: "Z"
    }
    symbol = switch_dir.get(b36_value, "0")
    return symbol
