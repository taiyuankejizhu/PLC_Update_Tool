#!/bin/python/
#encoding=utf-8
# Copyright 2017 Jiangshuai.Zhu <taiyuankejizhu@163.com>
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

"""
This tool is used for update bin file of plc modules
"""

import sys
import serial
import json
import zlib
import sys
import time
import os
import logging
import platform
import argparse
from ctypes import *

SERIAL_PORT = 0
BOOT_FILE_NAME = '1boot.bin'
PZ_FILE_NAME = '2pz.bin'
CCO_CFG_FILE_NAME = '3CCO.plccfg'
CKQ_CFG_FILE_NAME = '3CKQ.plccfg'
STA_CFG_FILE_NAME = '3STA.plccfg'
CFG_FILE_NAME = '3STA.plccfg'
CPU0_FILE_NAME = '4cpu0.bin'
CPU1_FILE_NAME = '5cpu1.bin'
FILES_PATH = './Bins/'

SerialPort = ''

def getc(size, timeout=1):
    return SerialPort.read(size) or None
def putc(data, timeout=1):
    ret = SerialPort.write(data)
    print(ret)
    return ret  # note that this ignores the timeout

def GotoWaitInputMode():
    while True:
        Buffer = SerialPort.readline()
        print(Buffer)
        if len(Buffer) > 0:
            continue
        else:
            break
    SerialPort.reset_input_buffer()
    SerialPort.reset_output_buffer()
    time.sleep(0.5)

PCOMM_DLL = windll.LoadLibrary('.\\Lib\\x86\\PCOMM.DLL')

def TransmitFileByXmodem(name):
    PCOMM_DLL.sio_open(SERIAL_PORT)
    PCOMM_DLL.sio_ioctl(SERIAL_PORT, 0x10, 0x00 | 0x03 | 0x00)
    PCOMM_DLL.sio_flowctrl(SERIAL_PORT, 0x03)

    CALLBACK = WINFUNCTYPE(c_int, c_long, c_int, POINTER(c_char), c_long)
    TransmitCallBack = CALLBACK(TransmitCompleteCallBack)
    File_PATH = sys.path[0]
    File_URL = File_PATH + '\\'
    File_URL += name
    print (File_URL)
    File_URL_pStr = c_char_p()
    File_URL_pStr.value = File_URL.encode()
    ret = PCOMM_DLL.sio_FtXmodemCheckSumTx(c_int(SERIAL_PORT), File_URL_pStr, TransmitCallBack, 0)

    return ret

def TransmitFileFinished():
    PCOMM_DLL.sio_close(SERIAL_PORT)

def TransmitCompleteCallBack(xmitlen, buflen, pbuf, flen):
    print ('Transmit %d bytes, Total %d bytes' % (xmitlen, flen))
    return xmitlen

def GotoUpdateFile(number, name):
    print(" ********** PLC update %s file *********** "%name)
    OutputBuffer = number
    SerialPort.write(OutputBuffer.encode())
    SerialPort.flush()
    while True:
        InputBuffer = SerialPort.readline()
        if str(InputBuffer).find('Y/N') > 0:
            print(InputBuffer)
            break

    GotoWaitInputMode()
    OutputBuffer = 'Y\n'
    SerialPort.write(OutputBuffer.encode())
    SerialPort.flush()

    while True:
        InputBuffer = SerialPort.readline()
        if str(InputBuffer).find('Xmodem') > 0:
            print(InputBuffer)
            break

    SerialPort.reset_output_buffer()
    SerialPort.reset_input_buffer()
    SerialPort.flush()
    SerialPort.close()
    print(" ********** PLC send %s file *********** "%name)
    UpdateFile = open(name, 'rb')
    #UpdateStream = UpdateFile.readlines()
    TransmitFileByXmodem(name)
    TransmitFileFinished()

    SerialPort.open()
    SerialPort.flush()

    GotoWaitInputMode()
    GotoWaitInputMode()
    GotoWaitInputMode()
    GotoWaitInputMode()
    GotoWaitInputMode()
    GotoWaitInputMode()
    print(" ********** PLC update finish *********** ")

def LoopRun():
    print(" ********** PLC Update Tools *********** ")

    OutputBuffer = '\n\r'
    InputBuffer = ''

    SerialPort.flush()

    while True:
        #time.sleep(1)
        SerialPort.write(OutputBuffer.encode())
        InputBuffer = SerialPort.readline()
        if str(InputBuffer).find('main') > 0:
            print(InputBuffer)
            break

    GotoWaitInputMode()
    print(" ********** PLC Enter update mode *********** ")

    GotoWaitInputMode()
    print(" ********** PLC Erase flash *********** ")
    OutputBuffer = '13\n'
    SerialPort.write(OutputBuffer.encode())
    SerialPort.flush()

    while True:
        InputBuffer = SerialPort.readline()
        if str(InputBuffer).find('Y/N') > 0:
            print(InputBuffer)
            break

    OutputBuffer = 'Y\n'
    SerialPort.write(OutputBuffer.encode())
    SerialPort.flush()
    while True:
        time.sleep(0.2)
        InputBuffer = SerialPort.readline()
        if str(InputBuffer).find('default N') > 0:
            print(InputBuffer)
            break
    print(" ********** PLC flash finish *********** ")

    OutputBuffer = '\n\r'
    while True:
        #time.sleep(1)
        SerialPort.write(OutputBuffer.encode())
        InputBuffer = SerialPort.readline()
        if str(InputBuffer).find('main') > 0:
            print(InputBuffer)
            break

    GotoWaitInputMode()
    GotoUpdateFile('1\n', FILES_PATH + BOOT_FILE_NAME)
    GotoUpdateFile('2\n', FILES_PATH + PZ_FILE_NAME)
    GotoUpdateFile('3\n', FILES_PATH + CFG_FILE_NAME)
    GotoUpdateFile('4\n', FILES_PATH + CPU0_FILE_NAME)
    GotoUpdateFile('5\n', FILES_PATH + CPU1_FILE_NAME)

    SerialPort.flush()

description = 'example : PLC_Update_Multi.py -p [0 ....] -t [sta cco ckq] \n'
ArgParser = argparse.ArgumentParser(description = description)
if __name__ == '__main__':
    ArgParser.add_argument('--port', '-p', type=int, default=0)
    ArgParser.add_argument('--type', '-t', type=str, default='sta')

    Args = ArgParser.parse_args()
    SERIAL_PORT = Args.port
    print('Serial port : %d'%SERIAL_PORT)
    if Args.type.find('sta') >= 0:
        CFG_FILE_NAME = STA_CFG_FILE_NAME
    elif Args.type.find('cco') >= 0:
        CFG_FILE_NAME = CCO_CFG_FILE_NAME
    elif Args.type.find('ckq') >= 0:
        CFG_FILE_NAME = CKQ_CFG_FILE_NAME
    else:
        print('Invaild module type')
        sys.exit()
    print('Module type: %s'%CFG_FILE_NAME)

    SerialPort = serial.Serial('COM' + str(SERIAL_PORT), baudrate = 115200, bytesize = 8,
        parity = 'N', stopbits = 1, timeout = 0.2)

    if platform.architecture()[0].find('32') >= 0:
        PCOMM_DLL = windll.LoadLibrary('.\\Lib\\x86\\PCOMM.DLL')
        print('Load x86 dll file')
    else:
        PCOMM_DLL = windll.LoadLibrary('.\\Lib\\x64\\PCOMM.DLL')
        print('Load x64 dll file')

    while True:
        UsrInput = input("Continue ? : (y/n)")
        if UsrInput.find('y') >= 0:
            UsrInput = 'y'
        else:
            break
        LoopRun()
    SerialPort.close()
    sys.exit()
