#-------------------------------------------------------------------------------
# -*- coding: UTF-8 -*-
# Name:        basic_logic.py
# Purpose:
#
# Author:      yangyuexun
#
# Created:     03/07/2017
# Copyright:   (c) HBTE-YF-1 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import socket
import time
import sys
from hbteLog import HbteLog
                
def withRetry(Max_Retry = 3, Interval = 1.0):
    def wrapper(fun):
        def __wrapper(self, *args, **kw):
            error = "";
            for i in range(Max_Retry):
                try:
                    return fun(self, *args, **kw);
                except HbteException as e:
                    error = e.error;
                
                time.sleep(Interval);
                
            self.writeDebug("__sendData error: {0}".format(e));            
            raise HbteException(error);
            
        return __wrapper;
    return wrapper;

def main():
    pass

class HbteException(Exception):
    def __init__(self, args):
        self.error = args

class Logic(object):
    def __init__(self, ip, port, _debug = False, source_address = None, errCount = 10):
        self._ip = ip;
        self._port = port;
        self._socket = None;
        self._id = "";
        self._device = ""
        self._freFlag = "";
        self._waring = "Please get the device type first."
        self._version = "1.0.0.5"
        self._channelRange = 0
        self._source_address = source_address
        self._log = HbteLog();
        self._debug = _debug;
        self._errCount = errCount;
        self.__dealZDirective(self.__sendData("$TA,Z*\r\n"));
#         if self._isAttenuation == "AttenuationPhase":
#             self.__getDeviceID__(ip);
#         print ip, port
    
    def writeDebug(self, data):
        if self._debug:
            self._log.writeFile(data);

    def checkIPIsExist(self, ip):
        if ip != None and self._ip != ip:
            self._ip = ip
            self.__init__(self, self._ip, self._port)
        if self._device == None:
            return False
        return True
    
    def convertScientific(self, data):
        return str('{:.3e}'.format(data * 1000000.0));    
    
    def intConvertToStr(self, data, wide=2):
        return str(data).zfill(wide);
    
    def hexConvertToStr(self, data, wide=2):
        return str(hex(data))[2:].zfill(wide).upper();

    
#     switchBox设备查询设备信息时，不回帧头：$TA,帧尾：*\r\n,所以单独写了一个查询函数；回的数据格式：HBTE Calibration Switch Box 64-16
    def __searchSwitchBoxConfig(self, data, ip = None):
        self._ip = self._ip if ip == None else ip;
        try:
            self._socket = socket.create_connection((self._ip, self._port), 2)
            self._socket.sendall(data)
            recvData = self._socket.recv(1024);
            errCount = 0;
            print(recvData);
#             while not recvData.endswith("\r\n"):
#                 recvData += self._socket.recv(1024)
#                 errCount += 1
#                 if errCount == 3:
#                     raise Exception, "read more than the maximum number of times."
            return recvData;
        except socket.error as e:
            print("search switch Box config error: {0}".format(e));
            raise HbteException("search Switch Box config error: {0}".format(e))
        finally:
            if self._socket != None:
                self._socket.close();
    
    @withRetry()
    def __sendData(self, data, ip = None):
        time.sleep(0.1);
        self._ip = self._ip if ip == None else ip
        self.writeDebug("send data: {0},{1}".format(self._ip, data[:-3]));
        try:
            self._socket = socket.create_connection((self._ip, self._port), 3, self._source_address)
            
            self._socket.sendall(data.encode("utf8"));
            recvData = self._socket.recv(1024);
            errCount = 0;
            self.writeDebug("recv data {0}: {1}".format(0, recvData));
            while recvData.startswith("$TA,".encode()) and not recvData.endswith("*\r\n".encode()):
                recvData += self._socket.recv(1024)
                errCount += 1
                self.writeDebug("recv data {0}: {1}".format(errCount, recvData));
                if errCount == self._errCount:
                    print("read more than the maimum number of times.");
                    raise Exception("read more than the maximum number of times.")
            self.writeDebug("recv data: {0},{1}".format(self._ip, recvData[:-2]));
            if "FF\r\n" == recvData.decode():
                print("recv data error: {0}".format("This command is invalid."));
                self.writeDebug("recv data error: {0}".format("This command is invalid."));
                raise HbteException("This command is invalid.");
            recvData = recvData[6:]
            return (recvData[:len(recvData) - 3]).decode();
        except socket.error as e:
            raise HbteException("__sendData error: {0}".format(e))
        
        finally:
            if self._socket != None:
                self.writeDebug("socket has closed.");
                self._socket.close()
                
    def __sendPData(self, data, ip = None):
        time.sleep(0.1);
        self._ip = self._ip if ip == None else ip
        self.writeDebug("send data: {0},{1}".format(self._ip, data[:-3]));
        try:
            self._socket = socket.create_connection((self._ip, self._port), 2, self._source_address)
            self._socket.sendall(data.encode("utf8"))
            recvData = self._socket.recv(1024);
            errCount = 0;
            while recvData.startswith("$TA,".encode()) and not recvData.endswith("*\r\n".encode()):
                recvData += self._socket.recv(1024)
                errCount += 1
                if errCount == self._errCount:
                    raise Exception("read more than the maximum number of times.")
            recvData = self._socket.recv(1024);
            errCount = 0;
            while recvData.startswith("$TA,".encode()) and not recvData.endswith("*\r\n".encode()):
                recvData += self._socket.recv(1024)
                errCount += 1
                if errCount == self._errCount:
                    raise Exception("read more than the maximum number of times.")
            if "FF\r\n" == recvData.decode():
                raise HbteException("This command is invalid.");
            self.writeDebug("recv data: {0},{1}".format(self._ip, recvData[:-2]));
            recvData = recvData[6:]
            return (recvData[:len(recvData) - 3]).decode();
        except socket.error as e:
            print("__sendData error: {0}".format(e));
            raise HbteException("__sendData error: {0}".format(e))
        finally:
            if self._socket != None:
                self._socket.close()

    def __dealZDirective(self, data):
        print("data:", data)
        self.writeDebug("data: {0}".format(data));
        if "HBTE-PA-" in data:
            device = "PA";
            phaseStep = 0;
            if "*" in data:
                row = int(data.split("-")[2].split("*")[0]);
                col = int(data.split("-")[2].split("*")[1]);
                maxdB = int(data.split("-")[3]);
                isAttenuation = "Attenuation";
                isMatrix = "Matrix";
                types = "{0}x{1}".format(row, col);
                attStep = float(data.split("-")[4]);
                if len(data.split("-")) >= 6:
                    digit = float(data.split("-")[5]);
                    if digit <= 1:
                        phaseStep = float(data.split("-")[5]);
                    else:
                        phaseStep = 360.0 / pow(2, int(data.split("-")[5]));
                    isAttenuation = "AttenuationPhase";
                    device = "PAP";    
                    self._freFlag = "I";
                if len(data.split("-")) >= 10:
                    self._freFlag = data.split("-")[-1];          
            else:
                row = int(data.split("-")[2]);
                col = int(data.split("-")[3]);
                types = "{0}-{1}".format(row, col);
                maxdB = int(data.split("-")[4]);
                isAttenuation = "Attenuation";
                isMatrix = "NoMatrix";
                try:
                    if (len(data.split("-")) == 6):
                        attStep = float(data.split("-")[5]);                        
                    elif len(data.split("-")) >= 7:
                        attStep = float(data.split("-")[5]);
                        digit = float(data.split("-")[6]);
                        if digit <= 1:
                            phaseStep = 360.0 / float(data.split("-")[6]);
                        else:
                            phaseStep = 360.0 / pow(2, int(data.split("-")[6]));
                        isAttenuation = "AttenuationPhase";
                        device = "PAP";   
                except Exception as e:
                    self.writeDebug("parse data AttenuationPhase error: {0}".format(e));
                             
            self.__setDeviceInfo(row = row, column = col, isAttenuation = isAttenuation, isMatrix = isMatrix, maxdB = maxdB, types = types, device = device, attStep = attStep, phaseStep = phaseStep)    
        elif not self.cmp(data, "04-04"):
            self.__setDeviceInfo(4, 4, "Attenuation", "NoMatrix", 127, "04-04", "PA")
        elif not self.cmp(data, "04-04-90"):
            self.__setDeviceInfo(4, 4, "Attenuation", "NoMatrix", 90, "04-04", "PA")
        elif not self.cmp(data, "04-04-60-P"):
            self.__setDeviceInfo(4, 4, "AttenuationPhase", "NoMatrix", 90, "04-04", "PAP", 0.5, 5.625)
        elif not self.cmp(data, "05-05"):
            self.__setDeviceInfo(5, 5, "Attenuation", "NoMatrix", 127, "05-05", "PA")
        elif not self.cmp(data, "08-08"):
            self.__setDeviceInfo(8, 8, "Attenuation", "NoMatrix", 127, "08-08", "PA")
        elif not self.cmp(data, "08-08-60"):
            self.__setDeviceInfo(8, 8, "Attenuation", "NoMatrix", 60, "08-08", "PA")
        elif not self.cmp(data, "08-08-90"):
            self.__setDeviceInfo(8, 8, "Attenuation", "NoMatrix", 90, "08-08", "PA")
        elif not self.cmp(data, "08-08-63"):
            self.__setDeviceInfo(8, 8, "Attenuation", "NoMatrix", 63, "08-08", "PA")
        elif not self.cmp(data, "08-02"):
            self.__setDeviceInfo(8, 2, "Attenuation", "NoMatrix", 127, "08-02", "PA")
        elif not self.cmp(data, "16-02"):
            self.__setDeviceInfo(16, 2, "Attenuation", "NoMatrix", 127, "16-02", "PA")
        elif not self.cmp(data, "16-03"):
            self.__setDeviceInfo(16, 2, "Attenuation", "NoMatrix", 127, "16-03", "PA")
        elif not self.cmp(data, "16-04"):
            self.__setDeviceInfo(16, 4, "Attenuation", "NoMatrix", 127, "16-04", "PA")
        elif not self.cmp(data, "16-16"):
            self.__setDeviceInfo(16, 16, "Attenuation", "NoMatrix", 127, "16-16", "PA")
        elif not self.cmp(data, "16-08"):
            self.__setDeviceInfo(16, 8, "Attenuation", "NoMatrix", 127, "16-08", "PA")
        elif not self.cmp(data, "16-12-0F"):
            self.__setDeviceInfo(16, 16, "Attenuation", "NoMatrix", 127, "16-12", "PA")
        elif not self.cmp(data, "24-06"):
            self.__setDeviceInfo(24, 6, "Attenuation", "NoMatrix", 127, "24-06", "PA")
        elif not self.cmp(data, "24-04"):
            self.__setDeviceInfo(24, 4, "Attenuation", "NoMatrix", 127, "24-04", "PA")
        elif not self.cmp(data, "24-24"):
            self.__setDeviceInfo(24, 24, "Attenuation", "NoMatrix", 127, "24-24", "PA")
        elif not self.cmp(data, "32-04"):
            self.__setDeviceInfo(32, 4, "Attenuation", "NoMatrix", 127, "32-04", "PA")
        elif not self.cmp(data, "32-32"):
            self.__setDeviceInfo(32, 32, "Attenuation", "NoMatrix", 127, "32-32", "PA")
        elif not self.cmp(data, "08*04-127"):
            self.__setDeviceInfo(8, 4, "Attenuation", "Matrix", 127, "08x04", "PAM")
        elif not self.cmp(data, "08*08-63-0F"):
            self.__setDeviceInfo(8, 8, "Attenuation", "Matrix", 63, "08x08", "PAM")
        elif not self.cmp(data, "08*08-90"):
            self.__setDeviceInfo(8, 8, "Attenuation", "Matrix", 90, "08x08", "PAM")
        elif not self.cmp(data, "08*08-63"):
            self.__setDeviceInfo(8, 8, "AttenuationSwitch", "Matrix", 60, "08x08", "PAM")
        elif not self.cmp(data, "08*08-127"):
            self.__setDeviceInfo(8, 8, "Attenuation", "Matrix", 127, "08x08", "PAM")
        elif not self.cmp(data, "16*04"):
            self.__setDeviceInfo(16, 4, "Attenuation", "Matrix", 90, "16x04", "PAM")
        elif not self.cmp(data, "16*08-90"):
            self.__setDeviceInfo(16, 8, "Attenuation", "Matrix", 90, "16x08", "PAM")
        elif not self.cmp(data, "16*08-63-0F"):
            self.__setDeviceInfo(16, 8, "Attenuation", "Matrix", 63, "16x08", "PAM")
        elif not self.cmp(data, "16*08-63"):
            self.__setDeviceInfo(16, 8, "AttenuationSwitch", "Matrix", 60, "16x08", "PAM")
        elif not self.cmp(data, "16*16-90"):
            self.__setDeviceInfo(16, 16, "Attenuation", "Matrix", 90, "16x16", "PAM")
        elif not self.cmp(data, "16*16-63-OF"):
            self.__setDeviceInfo(16, 16, "Attenuation", "Matrix", 63, "16x16", "PAM")
        elif not self.cmp(data, "16*16-63"):
            self.__setDeviceInfo(16, 16, "AttenuationSwitch", "Matrix", 60, "16x16", "PAM")
        elif not self.cmp(data, "16*16-90-P"):
            self.__setDeviceInfo(16, 16, "AttenuationPhase", "Matrix", 90, "16x16", "PAP", 0.5, 2.8)
        elif not self.cmp(data, "18*18-90"):
            self.__setDeviceInfo(18, 18, "Attenuation", "Matrix", 90, "18x18", "PAM")
        elif not self.cmp(data, "18*18-63-0F"):
            self.__setDeviceInfo(18, 18, "Attenuation", "Matrix", 63, "18x18", "PAM")
        elif not self.cmp(data, "18*18-63"):
            self.__setDeviceInfo(18, 18, "AttenuationSwitch", "Matrix", 60, "18x18", "PAM")
        elif not self.cmp(data, "32*08-63"):
            self.__setDeviceInfo(32, 8, "Attenuation", "Matrix", 63, "32x08", "PAM")
        elif not self.cmp(data, "32*16-63-0F"):
            self.__setDeviceInfo(32, 16, "Attenuation", "Matrix", 63, "32x16", "PAM")
        elif not self.cmp(data, "32*16-63-OF"):
            self.__setDeviceInfo(32, 16, "Attenuation", "Matrix", 63, "32x16", "PAM")
        elif not self.cmp(data, "32*16-63"):
            self.__setDeviceInfo(32, 16, "Attenuation", "Matrix", 63, "32x16", "PAM")
        elif not self.cmp(data, "64-48-90-P"):
            self.__setDeviceInfo(32, 32, "AttenuationPhase", "Matrix", 90, "64-48", "PAP", 0.5, 5.625)
        elif not self.cmp(data, "64*16-90-7P"):
            self.__setDeviceInfo(64, 16, "AttenuationPhase", "Matrix", 90, "64x16", "PAP", 0.5, 2.8125)
        elif not self.cmp(data, "64*32-90-P"):
            self.__setDeviceInfo(64, 32, "AttenuationPhase", "Matrix", 90, "64x32", "PAP", 0.5, 5.625)
        elif not self.cmp(data, "08*08-11T"):
            self.__setDeviceInfo(8, 8, "Switch", "Matrix", 1, "8x8-11T", "RFBox")
        elif not self.cmp(data, "08*02-11T"):
            self.__setDeviceInfo(8, 2, "Switch", "Matrix", 1, "16x4-1", "RFBox")
        elif not self.cmp(data, "08*02-12T"):
            self.__setDeviceInfo(8, 2, "Switch", "Matrix", 1, "16x4-2", "RFBox")
        elif not self.cmp(data, "64-02"):
            self.__setDeviceInfo(64, 2, "Switch", "Matrix", 1, "64-2", "RFBox")
        elif not self.cmp(data, "HBTE-PPB-1-6-4825"):
            self.__setPBDeviceInfo(6, data, "1-6", "PB")
        elif not self.cmp(data, "HBTE-PPB-1-8-22010"):
            self.__setPBDeviceInfo(8, data, "1-8", "PB")
        elif not self.cmp(data, "HBTE-PPB-1-8-4820"):
            self.__setPBDeviceInfo(8, data, "1-8", "PB")
        elif not self.cmp(data, "HBTE-PPB-6-6-4860"):
            self.__setPBDeviceInfo(6, data, "6-6", "PB")
        elif not self.cmp(data, "HBTE-PPB-2000-1-4-1240"):
            self.__setPBDeviceInfo(4, data, "1-4", "PB")
        elif not self.cmp(data, "HBTE-PPB-2400-1-88-1220"):
            self.__setPBDeviceInfo(8, data, "1-88", "PB")
        elif not self.cmp(data, "HBTE-PPB-1-10-2201605"):
            self.__setPBDeviceInfo(8, data, "1-10", "PB")
        else:
            print("unknown device.")
            self._device = None;
            self._deviceVersion = None;
    
    def cmp(self, str1, str2):
            return str1 != str2;

    def __setPBDeviceInfo(self, row, firmware, types, device):
        self._row = row
        self._firmware = firmware
        self._type = types
        self._device = device
        self._channelRange = self._row
        self._deviceVersion = self.__getDeviceVersion__()

    def __setDeviceInfo(self, row, column, isAttenuation, isMatrix, maxdB, types, device, attStep = 0.5, phaseStep = None):
        self._row = row
        self._column = column
        self._isAttenuation = isAttenuation
        self._isMatrix = isMatrix
        self._maxdB = maxdB;
        self._type = types;
        self._device = device;
        self._phaseStep = phaseStep;
        self._attStep = attStep;
        
        self.writeDebug("device: {0}".format(self._device));
        
        if self._isMatrix == "Matrix":
            self._channelRange = self._row * self._column
        else:
            self._channelRange = self._row if self._row > self._column else self._column;

    def __getPortName__(self, ip = None):
        return self.__sendData("$TA,W*\r\n", ip = ip).split('-')

    def __getDeviceVersion__(self, ip = None):
        self._deviceVersion = self.__sendData("$TA,Q*\r\n", ip = ip)
        return self._deviceVersion;
    
    def __getDeviceID__(self, ip = None):
        self._id = self.__sendData("$TA,q*\r\n", ip = ip);
        print(self._id);
        return self._id;

    def __getVersion__(self):
        return self._version

    def __sendRDirective__(self, ip = None):
        self.__sendData("$TA,R*\r\n", ip = ip)

    def sendDDirective(self, data, ip = None):
        return self.__sendData("$TA,D,{0}*\r\n".format(data.upper()), ip = ip)

    def senddDirective(self, data, ip = None):
        return self.__sendData("$TA,d,{0}*\r\n".format(data.upper()), ip = ip)

    def sendcDirective(self, data, ip = None):
        return self.__sendData("$TA,c,{0}*\r\n".format(data.upper()), ip = ip)

    def sendCDirective(self, data, ip = None):
        return self.__sendData("$TA,C,{0}*\r\n".format(data.upper()), ip = ip)

    def sendaDirective(self, data, ip = None):
        return self.__sendData("$TA,a,{0}*\r\n".format(data.upper()), ip = ip);

    def sendGDirective(self, data, ip = None):
        return self.__sendData("$TA,G,{0}*\r\n".format(data.upper()), ip = ip)

    def sendgDirective(self, data, ip = None):
        return self.__sendData("$TA,g,{0}*\r\n".format(data.upper()), ip = ip)
    
    def _searchFrePoints(self, ip = None):
        return self.__sendData("$TA,z*\r\n", ip = ip);
    
    def sendPDirective(self, data, ip = None):
        return self.__sendPData("$TA,P,{0}*\r\n".format(data.upper()), ip = ip);
    
    def sendpDirective(self, data, ip = None):
        return self.__sendData("$TA,p,{0}*\r\n".format(data.upper()), ip = ip);
    
    def _queryCurrentFrePoint(self, ip = None):
        return self.__sendData("$TA,z,F8*\r\n");
    
    def _setCurrentFrePoints(self, fre = 2300, index = 0, ip = None):
        if not self.cmp(self._freFlag, "F"):
            recvData = self.__sendData("$TA,z,F8,{0}-{1}*\r\n".format(fre, fre), ip = ip);
            return (str(fre) in recvData);
        elif not self.cmp(self._freFlag, "I"):
            recvData = self.__sendData("$TA,z,{0}*\r\n".format(self.intConvertToStr(index)), ip = ip);
            return int(recvData) == index;
    
    def startSendCsvData(self):
        self.__sendCSVData("$TA,c,000*\r\n");
        
    def sendCsvRowTimeData(self, row, delayTime):
        self.__sendCSVData("$TA,T,{0}-{1}*\r\n".format(str(row).zfill(6), str(delayTime).zfill(5)));
        
    def sendCsvAttData(self, data):
        self.__sendCSVData("$TA,FG,{0}*\r\n".format(data.upper()));
        
    def sendCsvPhaseData(self, data):
        self.__sendCSVData("$TA,Fg,{0}*\r\n".format(data.upper()));
                
    def EndSendCsvData(self):
        self.__sendCSVData("$TA,s,000*\r\n");
        
    def runExternalCSv(self, loopCount = 1):
        print("run external csv");
        self.__sendCSVData("$TA,c,005-{0}*\r\n".format(str(loopCount).zfill(5)));
        
    def runCsv(self, loopCount = 1):
        print("run csv");
        self.__sendCSVData("$TA,c,001-{0}*\r\n".format(str(loopCount).zfill(5)));
        
    def queryCsvState(self):
        recvData = self.__sendCSVData("$TA,s,010*\r\n");
        if "02" in recvData:
            return "pause";
        elif "03" in recvData:
            return "step debug"
        elif "00" in recvData:
            return "stoped";
        elif "01" in recvData:
            return "running";
        else:
            return "error";
    
    def pauseCsv(self):
        print("pause csv");
        self.__sendCSVData("$TA,s,001*\r\n");
        
    def continueCsv(self):
        print("continue csv");
        self.__sendCSVData("$TA,c,002*\r\n");
        
    def stopCsv(self):
        print("stop csv");
        self.__sendCSVData("$TA,s,000*\r\n");
        
    @withRetry()
    def __sendCSVData(self, data, ip = None):
#         time.sleep(0.1);
        self._ip = self._ip if ip == None else ip
#         self.writeDebug("send csv data: {0},{1}".format(self._ip, data[:-3]));
        try:
            self._socket = socket.create_connection((self._ip, self._port), 2, self._source_address)
            
            self._socket.sendall(data.encode("utf8"))
            print("send data: {0}".format(data));
            recvData = self._socket.recv(1024);
#             self.writeDebug("recv data: {0},{1}".format(self._ip, recvData[:-2]));
            if "FF\r\n" == recvData.decode():
                print("send csv data: ", data, recvData);
                raise HbteException("This command is invalid.");
            
            if "01\r\n" != recvData.decode():
                print("send csv data: ", data, recvData);
                raise HbteException("send csv data failed.");
            
            return recvData.decode();
            
        except socket.error as e:
            print("__send csv data error: {0}".format(e));
            raise HbteException("__send csv data error: {0}".format(e))
        finally:
            if self._socket != None:
                self._socket.close()
                self._socket = None;
                
#     适用于FDD设备；
    def sendFDDDirective(self, data):
        return self.__sendData("$TA,F,DD,{0}*\r\n".format(data.upper()));
    
    def queryFDDDirective(self):
        return self.__sendData("$TA,F,DD*\r\n");

    def reBootDevice(self, ip = None):
        self.__sendData("$TA,R*\r\n")

    def changeIP(self, addr, mask, gw, ip = None):
        """
        FunctionName:   ChangeIP
        FunctionParam:  as follow
    		            addr - as "192.168.127.100"
		                mask - as "255.255.255.0"
                        gw   - as "192.168.127.1"
                        ip  - as None or "192.168.1.254"
        """
        self.__sendData("$TA,X,{0}-{1}-{2}*\r\n".format(addr.strip(), mask.strip(), gw.strip()), ip = ip)


if __name__ == '__main__':
    try:
        logic = Logic("192.168.2.101", 5000)
    except HbteException as e:
        print(e.error)

