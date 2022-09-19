#-------------------------------------------------------------------------------
# -*- coding: UTF-8 -*-
# Name:        HBTE
# Purpose:
#
# Author:      yangyuexun
#
# Created:     05/07/2017
# Copyright:   (c) HBTE-YF-1 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import time
from base_logic import Logic, HbteException
from base_logic import HbteException
import os
import re
from math import sin, cos
import csv
import socket
import datetime
from ctypes.test.test_prototypes import positive_address
# from test.double_const import PI

PI    = 3.14159265358979324

class PA(Logic):
    def __init__(self, ip = "127.0.0.1", port = 5000, source_address = None, errCount = 10):
        Logic.__init__(self, ip, port, True, source_address, errCount)
        self._fres = {};
        
#        switchUplink, switchDownlink, queryLinkStatus只适用于FDD产品
    def switchUplink(self, ip = None):
        if not self.checkIPIsExist(ip):
            return None;
        
        recvData = self.sendFDDDirective("01");
        if "01" in recvData:
            return True;
        else:
            return False;
    
    def switchDownlink(self, ip = None):
        if not self.checkIPIsExist(ip):
            return None;
        recvData = self.sendFDDDirective("00");
        if "00" in recvData:
            return True;
        else:
            return False;
        
    def queryLinkStatus(self, ip = None):
        if not self.checkIPIsExist(ip):
            return None;
        recvData = self.queryFDDDirective();
        if "01" in recvData:
            print("Currently in uplink state");
            return "uplink";
        else:
            print("Currently in downlink state");
            return "downlink";

    def operateRow(self, rowList, value, ip = None):
        """
        FunctionName:   operateRow
        FunctionParam:  rowList - as [1] or [1,3,5]
                        value  - as 5.5
                        ip  - as None or "192.168.1.254"
        FunctionReturn: True    ok
                        False    fail
        """
        if not self.checkIPIsExist(ip):
            return None;
        if self._isMatrix == "NoMatrix":
            raise HbteException("operate row error: The non-matrix attenuatior does not support this operation.")

        channelList = list()
        valueList = list()
        for row in rowList:
            if row > self._row or row < 1:
                raise HbteException("operate row error: The set channel over the maximum or lass than 1.")
            for col in range(self._column):
                channelList.append(row + col * self._row)
                valueList.append(value)

        return self.operateChannel(channelList, valueList, ip = ip)

    def operateColumn(self, columnList, value, ip = None):
        """
        FunctionName:   operateColumn
        FunctionParam:  columnList - as [1] or [1,3,5]
                        value - as 5.5
                        ip - as None or "192.168.1.254"
        FunctionReturn: True  ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None
        if self._isMatrix == "NoMatrix":
            raise HbteException("operate column error: The non-matrix attenuatior does not support this operation.")
        channelList = list()
        valueList = list()
        for column in columnList:
            if column > self._column or column < 1:
                raise HbteException("operate column error: The set channel over the maximum or lass than 1.")

            for row in range(self._row):
                channelList.append(row + (column - 1) * self._row + 1)
                valueList.append(value)
        return self.operateChannel(channelList, valueList, ip = ip)

    def operateMulChannel(self, startChannel, endChannel, value, ip = None):
        """
        FunctionName:   operateMulChannel
        FunctionParam:  startChannel - as 1
                        endChannel - as 5
                        value - as 5.5
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None
        if startChannel > endChannel:
            temp = startChannel
            startChannel = endChannel
            endChannel = temp
        if startChannel < 1 or endChannel > self._channelRange:
            raise HbteException("operate mul channel error: The set channel over the maximum or lass than 1.")

        channelList= list()
        valueList = list()
        for channel in range(startChannel, endChannel + 1):
            channelList.append(channel)
            valueList.append(value)
        return self.operateChannel(channelList, valueList, ip = ip)
    
    def loadCSV(self, fileName, channelList, ip = None):
        return self.__loadCSV(fileName = fileName, channelList = channelList, flag = True, ip = ip);
    
    def loadPhaseCSV(self, fileName, channelList, ip = None):
        return self.__loadCSV(fileName = fileName, channelList = channelList, flag = False, ip = ip);
    
    def __loadCSV(self, fileName, channelList, flag = True, ip = None):
        if not self.checkIPIsExist(ip):
            return None;
                
        channels = list()
        tempList = list() 
        if os.access(r"{0}".format(fileName), os.R_OK):
            with open(r"{0}".format(fileName), 'r') as fp:
                header = fp.readline();
#                 载入思博伦提供的文件格式                
                if "-" not in header and "*" not in header:
                    headers = header.split(",")[1:];
                    chMap = {};
                    for item in headers:
                        row = int(item[1:]);
                        if row >= self._row:
                            continue;
                        chMap[headers.index(item)] = row;
                    for line in fp:
                        col = int(line.split(",")[0][1:]);
                        valueList = line.split(",")[1:];
                        for i in range(len(valueList)):
                            if i not in chMap.keys():
                                continue;
                            row = chMap[i];
                            ch = (col - 1) * self._row + row;
                            
                            if ch not in channelList:
                                continue;
                            
                            value = float(valueList[i]);
                            if flag == True:
                                value = 0 if value < 0 else value;
                            else:
                                value = 180 + value if value < 0 else value; 
                            tempList.append(value);
                            channels.append(ch);
                else:
                    header = fp.readline();
                    header = header.replace("\r\n", "");
                    header = header.replace("\n", "");
                    headers = header.split(",");
                    chMap = {};
                    for item in headers:    
                        if "" == item:
                            continue;                        
                        col = int(item[1:]);
                        if col > self._column:
                            continue;
                        chMap[headers.index(item)] = col;
                    row = 1;
                    for line in fp:
                        valueList = line.split(",");
                        for i in range(len(valueList)):
                            if i not in chMap.keys():
                                continue;
                            if self._isMatrix == "NoMatrix":
                                ch = chMap[i];
                            else:
                                ch = (chMap[i] - 1) * self._row + row;
                            if ch not in channelList:
                                continue;
                            
                            value = float(valueList[i]);
                            if flag == True:
                                value = 0 if value < 0 else value;
                            else:
                                value = 360 + value if value < 0 else value;
                            tempList.append(value);
                            channels.append(ch);
                        row += 1;      
#                                     确保csv文件包含全部的待申请控制的通道；
                if len(channels) != len(channelList):
                    print("Not all channels applying for control are in the CSV file.")        
                
                if flag == True:
                    self.operateChannel(channels, tempList, ip = ip)   
                else:
                    self.operateChannelPhase(channels, tempList, ip) 
                return True;
        else:
            raise HbteException("operate {0} error.".format(fileName))

    def operateCSV(self, fileName, channelList, csvFlag = 1, ip = None):
        """
        FunctionName:   operateCSV
        FunctionParam:  fileName - as "D:\\workplace\\Example16-04.csv"
                        csvFlag - as "1: csv file start with I:1 O:1, 0: csv file start with I:0 O:0
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None
        print(fileName)
        if os.access(r"{0}".format(fileName), os.R_OK):
            with open(r"{0}".format(fileName), 'r') as fp:
                header = fp.readline().split(",")[1:];
                chMap = {};
                for item in header:
                    
                    #csv文件以I:0 O:0开始，csvFlag = 0；
                    #csv文件以I:1 O:1开始，csvFlag = 1；
                    #矩阵（8*8）表头以I:0 O:0或者I:1 O:1开始，非矩阵（8-8）以I:0或者O:1开始。
                    #csv文件头必须以I:0 O:0开始，如果csv文件头以I:1 O:1开始，row，col均需要-1；
                    if len(re.findall("\d+", item)) > 1:
                        row = int(re.findall("\d+", item)[0]) - csvFlag;
                        col = int(re.findall("\d+", item)[1]) - csvFlag;
                        
                        ch = col * self._row + row + 1;
                    else:
                        row = int(re.findall("\d+", item)[0]) - csvFlag; 
                        ch = row + 1;
                    if ch > self._channelRange:
                        continue;
                    if ch in channelList:
                        chMap[header.index(item)] = ch;
                for line in fp:
                    valueList = line.split(",")
                    time.sleep(float(valueList[0]) / 1000)
                    valueList.pop(0)
                    channels = list()
                    tempList = list()
                    phaseList = list()
                    for i in range(len(valueList)):
                        if i not in chMap.keys():
                            continue;
                        
                        value = valueList[i];
                        channels.append(chMap[i]);
                        if ":" in value:
                            tempList.append(float(value.split(":")[0]))
                            phaseList.append(float(value.split(":")[1]))
                        else:
                            tempList.append(float(value))
#                     channelRange = self._channelRange if len(valueList) > self._channelRange else len(valueList)
#                     for i in range(channelRange):
#                         channelList.append(i + 1)
#                         value = valueList[i]
#                         if ":" in value:
#                             tempList.append(float(value.split(":")[0]))
#                             phaseList.append(float(value.split(":")[1]))
#                         else:
#                             tempList.append(float(value))
#                     print channelList
#                     print tempList

#                                     确保csv文件包含全部的待申请控制的通道；
                    if len(channels) != len(channelList):
                        print("Not all channels applying for control are in the CSV file.")
                    self.operateChannel(channels, tempList, ip = ip)
                    if self._isAttenuation == "AttenuationPhase" and self.cmp(0, len(phaseList)):
                        self.operateChannelPhase(channels, phaseList, ip = ip)
                return True
        else:
            raise HbteException("operate {0} error.".format(fileName))
        
    def operateOneChannel(self, channel, value, ip = None):
        return self.operateChannel([channel], [value]);

    def operateChannel(self, channelList, valueList, ip = None):
        """
        FunctionName:   operateChannel
        FunctionParam:  channelList - as [1] or [1,3,5]
                        valueList - as [1.5] or [1,3,5]
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if len(channelList) != len(valueList):
            raise HbteException("operate channel error: The number of channels to be set and the number of channel values do not match.")

        if not self.checkIPIsExist(ip):
            return None;
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("operate channel error: The set channel over the maximum or lass than 1.")

        tempList = list()
        for value in valueList:
            if value < 0:
                value = 0;
            if value > self._maxdB:
                if self._isAttenuation == "AttenuationSwitch":
                    tempList.append("FE")
                else:
                    value = self._maxdB;
                    if self._attStep < 0.5:
                        tempList.append(hex(int(value / self._attStep))[2:].zfill(3));
                    else:
                        tempList.append(hex(int(value * 2))[2:].zfill(2))
            else:
                if self._attStep < 0.5:
                    tempList.append(hex(int(value / self._attStep))[2:].zfill(3));
                else:
                    tempList.append(hex(int(value * 2))[2:].zfill(2))
                
        self.writeDebug("PA in self._device {0}: ".format("PA" in self._device));
        
        if "PA" in self._device:
            if self._isMatrix == "Matrix":
                recvData = self.__sendMatrixData(channelList, tempList)
#                 return self.__checkDataEqual(channelList, recvData, tempList)
#                 考虑到设置完预衰后，设置的db值和接收到的db值不相同。
                return True;
            else:
                recvData = self.__sendNoMatrixData(channelList, tempList)
#                 return self.__checkDataEqual(channelList, recvData, tempList)
                return True;
        else:
            raise HbteException("operate channel error: The currently accessed device is not a PA type device.")
        
    def operatePreChannel(self, channelList, valueList, ip = None):
        """
        FunctionName:   operatePreChannel
        FunctionParam:  channelList - as [1] or [1,3,5]
                        valueList - as [1.5] or [1,3,5]
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if len(channelList) != len(valueList):
            raise HbteException("operate pre channel error: The number of channels to be set and the number of channel values do not match.")

        if not self.checkIPIsExist(ip):
            return None;
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("operate pre channel error: The set channel over the maximum or lass than 1.")

        tempList = list()
        for value in valueList:
            if value < 0:
                value = 0;
            if value > self._maxdB:
                if self._isAttenuation == "AttenuationSwitch":
                    tempList.append("FE")
                else:
                    value = self._maxdB;
                    if self._attStep < 0.5:
                        tempList.append(hex(int(value / self._attStep))[2:].zfill(3));
                    else:
                        tempList.append(hex(int(value * 2))[2:].zfill(2))
            else:
                if self._attStep < 0.5:
                        tempList.append(hex(int(value / self._attStep))[2:].zfill(3));
                else:
                    tempList.append(hex(int(value * 2))[2:].zfill(2))
        
        if "PA" in self._device:
            recvData = self.__sendMatrixPreData(channelList, tempList);
            if "$TA,P" in recvData:
                recvData = recvData.split("$TA,P,")[1];
            return self.__checkPreDataEqual(channelList, recvData, tempList);
        else:
            raise HbteException("operate channel error: The currently accessed device is not a PA type device.")
        
    def queryPreChannel(self, channelList, ip = None):
        """
        FunctionName:   queryPreChannel
        FunctionParam:  channelList - as [1] or [1,3,5]
                        valueList - as [1.5] or [1,3,5]
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None;
        valueList = list()
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("query pre channel error: The set channel over the maximum or lass than 1.")
            
            if self._attStep < 0.5:
                valueList.append("FFF");
            else:
                valueList.append("FF")
            
        if "PA" in self._device:
            recvData = self.__sendMatrixPreData(channelList, valueList);
            if "$TA,P" in recvData:
                recvData = recvData.split("$TA,P,")[1];
            
            valueList = list()
            for channel in channelList:  
                if self._attStep < 0.5:                 
                    position = (int(channel) - 1) * 3;
                    valueList.append(float(int(recvData[position:position + 2], 16)) * self._attStep);
                else:
                    position = (int(channel) - 1) * 2
                    valueList.append(float(int(recvData[position:position + 2], 16)) * self._attStep);
            return valueList
        else:
            raise HbteException("query channel error: The currently accessed device is not a PA type device.")
        
    def operateRowPhase(self, rowList, value, ip = None):
        """
        FunctionName:   operateRowPhase
        FunctionParam:  rowList - as (1) or (1,3,5)
                        value  - as 5.625
                        ip  - as None or "192.168.1.254"
        FunctionReturn: True    ok
                        False    fail
        """
        if not self.checkIPIsExist(ip):
            return None;
        if self._isMatrix == "NoMatrix":
            raise HbteException("operate row phase error: The non-matrix attenuatior does not support this operation.")

        channelList = list()
        valueList = list()
        for row in rowList:
            if row > self._row or row < 1:
                raise HbteException("operate row phase error: The set channel over the maximum or lass than 1.")
            for col in range(self._column):
                channelList.append(row + col * self._row)
                valueList.append(value)

        return self.operateChannelPhase(channelList, valueList, ip = ip)

    def operateColumnPhase(self, columnList, value, ip = None):
        """
        FunctionName:   operateColumnPhase
        FunctionParam:  columnList - as (1) or (1,3,5)
                        value - as 5.625
                        ip - as None or "192.168.1.254"
        FunctionReturn: True  ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None
        if self._isMatrix == "NoMatrix":
            raise HbteException("operate column phase error: The non-matrix attenuatior does not support this operation.")
        channelList = list()
        valueList = list()
        for column in columnList:
            if column > self._column or column < 1:
                raise HbteException("operate column phase error: The set channel over the maximum or lass than 1.")

            for row in range(self._row):
                channelList.append(row + (column - 1) * self._row + 1)
                valueList.append(value)
        return self.operateChannelPhase(channelList, valueList, ip = ip)

    def operateMulChannelPhase(self, startChannel, endChannel, phaseValue, ip = None):
        """
        FunctionName:   operateMulChannelPhase
        FunctionParam:  startChannel - as 1
                        endChannel - as 5
                        phaseValue - as 5.625
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None
        if startChannel > endChannel:
            temp = startChannel
            startChannel = endChannel
            endChannel = temp
        if startChannel < 1 or endChannel > self._channelRange:
            raise HbteException("operate mul channel phase error: The set channel over the maximum or lass than 1.")

        channelList= list()
        valueList = list()
        for channel in range(startChannel, endChannel + 1):
            channelList.append(channel)
            valueList.append(phaseValue)
        return self.operateChannelPhase(channelList, valueList, ip = ip)
    
    def operateOneChannelPhase(self, channel, phase, ip = None):
        return self.operateChannelPhase([channel], [phase], ip);

    def operateChannelPhase(self, channelList, phaseList, ip = None):
        """
        FunctionName:   operateChannelPhase
        FunctionParam:  channelList - as [1] or [1,3,5]
                        phaseList - as [5.625] or [5.625, 11, 15]
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if self._isAttenuation != "AttenuationPhase":
            if "PA" in self._device:
                raise HbteException("Interface call error, the current device is not a phase modulation device," 
                "please use the 'operateChannel' interface.")
            raise HbteException("operate channel phase error: The currently accessed device is not a PA type device.")

        if len(channelList) != len(phaseList):
            raise HbteException("operate channel phase error: The number of channels to be set and the number of channel values do not match.")

        if not self.checkIPIsExist(ip):
            return None;
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("operate channel phase error: The set channel over the maximum or lass than 1.")

        tempList = list()
        for value in phaseList:
            while value < 0:
                value += 360;
            while value > 360:
                value -= 360;                
            temp = float(value) / self._phaseStep;
            tmp = temp - int(temp) > 0.5 and int(temp + 1) or int(temp); 
            if tmp == int(360 / self._phaseStep):
                tmp = 0;
            if int(self._phaseStep) > 1.0: 
                tempList.append(hex(int(tmp))[2:].zfill(2))
            else:
                tempList.append(hex(int(tmp))[2:].zfill(3))
#         channelList.sort()
        if self._isMatrix == "Matrix":
            recvData = self.__sendMatrixPhaseData(channelList, tempList)
            return self.__checkDataEqualPhase(channelList, recvData, tempList)
        else:
            recvData = self.__sendNoMatrixPhaseData(channelList, tempList)
            return self.__checkDataEqualPhase(channelList, recvData, tempList)
    
    def operatePreChannelPhase(self, channelList, phaseList, ip = None):
        """
        FunctionName:   operatePreChannelPhase
        FunctionParam:  channelList - as [1] or [1,3,5]
                        phaseList - as [5.625] or [5.625, 11, 15]
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if self._isAttenuation != "AttenuationPhase":
            if "PA" in self._device:
                raise HbteException("Interface call error, the current device is not a phase modulation device," 
                "please use the 'operateChannel' interface.")
            raise HbteException("operate pre channel phase error: The currently accessed device is not a PA type device.")
        
        if len(channelList) != len(phaseList):
            raise HbteException("operate pre channel phase error: The number of channels to be set and the number of channel values do not match.")

        if not self.checkIPIsExist(ip):
            return None;
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("operate channel phase error: The set channel over the maximum or lass than 1.")

        tempList = list()
        for value in phaseList:
            while value < 0:
                value += 360;
            while value > 360:
                value -= 360;                
            temp = float(value) / self._phaseStep;
            tmp = temp - int(temp) > 0.5 and int(temp + 1) or int(temp); 
            if tmp == int(360 / self._phaseStep):
                tmp = 0;
            if int(self._phaseStep) > 1.0: 
                tempList.append(hex(int(tmp))[2:].zfill(2))
            else:
                tempList.append(hex(int(tmp))[2:].zfill(3))
        
        recvData = self.__sendMatrixPrePhaseData(channelList, tempList);
        return self.__checkDataEqualPhase(channelList, recvData, tempList);
            
    def queryPreChannelPhase(self, channelList, ip = None):
        """
        FunctionName:   queryPreChannelPhase
        FunctionParam:  channelList - as [1] or [1,3,5]
                        ip - as None or "192.168.1.254"
        FunctionReturn: [90] or [90, 180, 90]
        """
        if not self.checkIPIsExist(ip):
            return None;
        valueList = list()
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("query pre channel phase error: The set channel over the maximum or lass than 1.")
            
            if int(self._phaseStep) > 1.0:
                valueList.append("FF")
            else:
                valueList.append("FFF")
            
        if "PA" in self._device:
            recvData = self.__sendMatrixPrePhaseData(channelList, valueList);
            
            valueList = list()
            for channel in channelList:
                if int(self._phaseStep) > 1.0:
                    position = (int(channel) - 1) * 2
                else:
                    position = (int(channel) - 1) * 3
                val = 0;
                if int(self._phaseStep) > 1.0:
                    val = int(recvData[position:position + 2], 16)
                else:
                    val = int(recvData[position:position + 3], 16)
                valueList.append(float(val) * self._phaseStep);
            return valueList
        else:
            raise HbteException("query pre channel phase error: The currently accessed device is not a PA type device.")
        
    def queryChannelPhase(self, channelList, ip = None):
        """
        FunctionName:   queryChannelPhase
        FunctionParam:  channelList - as [1] or [1,3,5]
                        ip - as None or "192.168.1.254"
        FunctionReturn: [90] or [90, 180, 90]
        """
        if not self.checkIPIsExist(ip):
            return None;
        valueList = list()
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("query channel phase error: The set channel over the maximum or lass than 1.")
            if int(self._phaseStep) > 1.0:
                valueList.append("FF")
            else:
                valueList.append("FFF")
        if "PA" in self._device:
            if self._isMatrix == "Matrix":
                recvData = self.__sendMatrixPhaseData(channelList, valueList)
            else:
                recvData = self.__sendNoMatrixPhaseData(channelList, valueList);
            valueList = list()
            for channel in channelList:
                if int(self._phaseStep) > 1.0:
                    position = (int(channel) - 1) * 2
                else:
                    position = (int(channel) - 1) * 3
                val = 0;
                if int(self._phaseStep) > 1.0:
                    val = int(recvData[position:position + 2], 16)
                else:
                    val = int(recvData[position:position + 3], 16)
                valueList.append(float(val) * self._phaseStep);
            return valueList
        else:
            raise HbteException("query channel phase error: The currently accessed device is not a PA type device.")

    def queryChannel(self, channelList, ip = None):
        """
        FunctionName:   queryChannel
        FunctionParam:  channelList - as [1] or [1,3,5]
                        ip - as None or "192.168.1.254"
        FunctionReturn: [1.5] or [1.5, 2.5, 3]
        """
        if not self.checkIPIsExist(ip):
            return None;
        valueList = list()
        for channel in channelList:
            if channel > self._channelRange or channel < 1:
                raise HbteException("query channel error: The set channel over the maximum or lass than 1.")

#             channelList.remove(channel)
#             channelList.insert(0, str(channel).zfill(2))
            if self._attStep < 0.5:
                valueList.append("FFF");
            else:
                valueList.append("FF");
#         channelList.sort()
        if "PA" in self._device:
            if self._isMatrix == "Matrix":
                recvData = self.__sendMatrixData(channelList, valueList)
            else:
                recvData = self.__sendNoMatrixData(channelList, valueList);
            valueList = list()
            for channel in channelList:
                if self._isMatrix == "NoMatrix":
                    if self._attStep < 0.5:
                        position = (int(channel) - 1) * 5;
                        position = position + 2;
                    else:
                        position = (int(channel) - 1) * 4
                        position = position + 2;
                else:   
                    if self._attStep < 0.5:
                        position = (int(channel) - 1) * 3;
                    else:                                  
                        position = (int(channel) - 1) * 2
                if self._attStep < 0.5:
                    valueList.append(float(int(recvData[position:position + 3], 16)) * self._attStep);
                else:
                    valueList.append(float(int(recvData[position:position + 2], 16)) / 2.0);
            return valueList
        else:
            raise HbteException("query channel error: The currently accessed device is not a PA type device.")
        
    def exportAtt(self, fileName = "", ip = None):
        if not self.checkIPIsExist(ip):
            return None;
        dateTime = datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S");
        fileName = "att" + dateTime if fileName == "" else fileName;
        if not fileName.endswith(".csv"):
            fileName = fileName + ".csv";
            
        channels = list();
        for channel in range(1, self._channelRange + 1):
            channels.append(channel);
        values = self.queryChannel(channelList = channels);
        with open(r"{0}".format(fileName), 'w') as fp:
            header = self._type.replace("x", "*");
            fp.write("{0}\n".format(header));
            header = "";
            for col in range(1, self._column + 1):
                header = header + "B{0},".format(col);
            header = header[:-1];
            fp.write(header);
            fp.write("\n");
            
            for row in range(1, self._row + 1):
                line = "";
                for col in range(1, self._column + 1):
                    if self._isMatrix == "NoMatrix":
                        line = line + "{0},".format(values[col - 1]);
                    else:
                        line = line + "{0},".format(values[(col - 1) * self._row + row - 1]);
                line = line[:-1];
                fp.write(line)  ;
                fp.write("\n");   
                
                if self._isMatrix == "NoMatrix":
                    break;
    
    def exportPhase(self, fileName = "", ip = None):
        if not self.checkIPIsExist(ip):
            return None;
        dateTime = datetime.datetime.now().strftime("%Y_%m_%d %H_%M_%S");
        fileName = "phase" + dateTime if fileName == "" else fileName;
        if not fileName.endswith(".csv"):
            fileName = fileName + ".csv";
            
        channels = list();
        for channel in range(1, self._channelRange + 1):
            channels.append(channel);
        values = self.queryChannelPhase(channelList = channels);
        print(fileName);
        with open(r"{0}".format(fileName), 'w') as fp:
            header = self._type.replace("x", "*");
            fp.write("{0}\n".format(header));
            header = "";
            for col in range(1, self._column + 1):
                header = header + "B{0},".format(col);
            header = header[:-1];
            fp.write(header);
            fp.write("\n");
            
            for row in range(1, self._row + 1):
                line = "";
                for col in range(1, self._column + 1):
                    line = line + "{0},".format(values[(col - 1) * self._row + row - 1]);
                line = line[:-1];
                fp.write(line)  ;
                fp.write("\n");   

    def __sendMatrixData(self, channelList, valueList):
        data = list()
        for row in range(self._row):
            for col in range(self._column):
                if self._attStep < 0.5:
                    data.append("FFF");
                else:
                    data.append("FF")
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = valueList[i]
        return self.sendGDirective("".join(data))
    
    def __sendMatrixPreData(self, channelList, valueList):
        data = list()
        for channel in range(self._channelRange):
            if self._attStep < 0.5:
                data.append("FFF");
            else:
                data.append("FF")
            
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = valueList[i]
        return self.sendPDirective("".join(data))
    
    def __sendMatrixPrePhaseData(self, channelList, valueList):
        data = list()
        for index in range(self._channelRange):
            if int(self._phaseStep) > 1.0:
                data.append("FF");
            else:
                data.append("FFF");
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = valueList[i]
        return self.sendpDirective("".join(data))
    
    def __sendMatrixPhaseData(self, channelList, valueList):
        data = list()
        for row in range(self._row):
            for col in range(self._column):
                if int(self._phaseStep) > 1.0: 
                    data.append("FF")
                else:
                    data.append("FFF")
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = valueList[i]
        return self.sendgDirective("".join(data))

    def __sendNoMatrixData(self, channelList, valueList):
        data = list()
#         channelList.sort()
#        data: ['01', 'FF', '02', 'FF', '03', 'FF', '04', 'FF', '05', 'FF', '06', 'FF', '07', 'FF', '08', 'FF']
        for row in range(1, self._channelRange + 1):
            data.append("{0}".format(str(row).zfill(2)));
            if self._attStep < 0.5:
                data.append("FFF");
            else:
                data.append("FF")
        for i in range(len(channelList)):
            data[int(channelList[i]) * 2 - 1] = valueList[i];
        return self.sendDDirective("".join(data))
    
    def __sendNoMatrixPhaseData(self, channelList, valueList):
        data = list()
#         channelList.sort()
        for row in range(1, self._channelRange + 1):
            data.append("{0}".format(str(row).zfill(2)));
            data.append("FF")
        for i in range(len(channelList) * 2):
            data[int(channelList[i]) - 1] = valueList[i];
        return self.senddDirective("".join(data))
    
    def __checkDataEqual(self, positionList, target, objectList):
        for i in range(len(positionList)):
            if self._isMatrix == "Matrix":
                start = (int(positionList[i]) - 1) * 2
                val = int(target[start:start + 2], 16);
                if val == int(objectList[i], 16):
                    pass
                else:
                    return False
            else:
                for j in range(0, len(target), 4):
                    if int(target[j:j + 2]) == int(positionList[i]):
                        if int(target[j + 2:j + 4], 16) == int(objectList[i], 16):
                            pass
                        else:
                            return False
        return True;
    
    def __checkPreDataEqual(self, positionList, target, objectList):
        for i in range(len(positionList)):
            if self._isMatrix == "Matrix":
                start = (int(positionList[i]) - 1) * 2;
                val = int(target[start:start + 2], 16);
                if val == int(objectList[i], 16):
                    pass;
                else:
                    return False;
        
        return True;

    def __checkDataEqualPhase(self, positionList, target, objectList):
        for i in range(len(positionList)):
            if self._isMatrix == "Matrix":
                if int(self._phaseStep) > 1.0:
                    start = (int(positionList[i]) - 1) * 2
                else:
                    start = (int(positionList[i]) - 1) * 3
                val = 0;
                if int(self._phaseStep) > 1.0:
                    val = int(target[start:start + 2], 16);
                else:
                    val = int(target[start:start + 3], 16);
                if val == int(objectList[i], 16):
                    pass
                else:
                    return False
            else:
                for j in range(0, len(target), 4):
                    if int(target[j:j + 2]) == int(positionList[i]):
                        if int(target[j + 2:j + 4], 16) == int(objectList[i], 16):
                            pass
                        else:
                            return False
        return True;
    
    def queryFrePoints(self, ip = None):
        if self._isAttenuation != "AttenuationPhase":
            if "PA" in self._device:
                raise HbteException("Interface call error, the current device is not a phase modulation device.")
            raise HbteException("search fre points error: The currently accessed device is not a PA type device.")

        if not self.checkIPIsExist(ip):
            return None;
        
        recvData = self._searchFrePoints(ip);
        fres = recvData.split("-");
        self._startFre = fres[0];
        self._stopFre = fres[1];
        for i in range(2,len(fres), 2):
            if fres[i+1] != "":
                self._fres[fres[i]] = (i - 2) / 2;
        self.writeDebug(self._fres);
        return list(self._fres.keys());  
    
    def setCurrentFrePoints(self, fre = 2300, ip = None):
        fres = self.queryFrePoints(ip);
        if str(fre) not in fres:
            raise HbteException("The current frequency does not exist. Please query the frequency first.")
        
        return self._setCurrentFrePoints(fre = fre, index = self._fres[str(fre)], ip = ip);
    
    def queryCurrentFrePoint(self, ip=None):
        if self._isAttenuation != "AttenuationPhase":
            if "PA" in self._device:
                raise HbteException("Interface call error, the current device is not a phase modulation device.")
            raise HbteException("search fre point error: The currently accessed device is not a PA type device.")

        if not self.checkIPIsExist(ip):
            return None;
        
        fre = self._queryCurrentFrePoint(ip = ip);
        return fre.split(",")[1];

    def downloadCSVToDevice(self, fileName, channelList):
        """
        FunctionName:   downloadCSVToDevice
        FunctionParam:  fileName - as "D:\\workplace\\Example16-04.csv"
                        channelList - as [0] or [1, 3, 5]
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
                
        if len(channelList) == 0:
            raise HbteException("The parameter channelList cannot be empty, please try again.");
        
        print(fileName)
        if os.access(r"{0}".format(fileName), os.R_OK):
            with open(r"{0}".format(fileName), 'r') as fp:
                print("start download {0} to device. {1}".format(fileName, self._log.getNowDateTime()));
                
                self.startSendCsvData();
                
                header = fp.readline().split(",")[1:];
                count = 0;
                chMap = {};
                for item in header:
                    #csv文件头必须以I:0 O:0开始，如果csv文件头以I:1 O:1开始，row，col均需要-1；
#                     csv文件已I:1 O:1开头;
#                     row = int(re.findall("\d+", item)[0]) - 1;
#                     col = int(re.findall("\d+", item)[1]) - 1;
#                     csv文件已I:0 O:0开头
                    row = int(item.split(" ")[0].split(":")[1]);
                    col = int(item.split(" ")[1].split(":")[1]);
                    if row >= self._row or col >= self._column:
                        continue;
                    ch = col * self._row + row + 1;
                    if ch in channelList:
                        chMap[header.index(item)] = ch;
                for line in fp:
                    valueList = line.split(",")
                    
                    self.sendCsvRowTimeData(count, int(valueList[0]));
                    count += 1;
                    
                    valueList.pop(0)
                    channels = list()
                    tempList = list()
                    phaseList = list()
                    for i in range(len(valueList)):
                        if i not in chMap.keys():
                            continue;
                        value = valueList[i];
                        channels.append(chMap[i]);
                        if ":" in value:
                            tempList.append(float(value.split(":")[0]))
                            phaseList.append(float(value.split(":")[1]))
                        else:
                            tempList.append(float(value))
#                   确保csv文件包含全部的待申请控制的通道；
                    if len(channels) != len(channelList):
                        print("Not all channels applying for control are in the CSV file.")
                        
                    self.__sendCsvAttData(channels, tempList);
                    if self._isAttenuation == "AttenuationPhase" and self.cmp(0, len(phaseList)):
                        self.__sendCsvPhaseData(channels, phaseList);
                                        
                self.EndSendCsvData(); 
                print("finish download csv. {0}".format(self._log.getNowDateTime()));
                return True
        else:
            raise HbteException("operate {0} error.".format(fileName))
        
    def _downloadCSVToDevice(self, fileName, channelList):
        if len(channelList) == 0:
            raise HbteException("The parameter channelList cannot be empty, please try again.");
        
        _socket = None;
        
        try:        
            if self._source_address != None:
                _socket = socket.create_connection((self._ip, self._port), 3, (self._source_address[0], self._source_address[1] + 1));
            else:
                _socket = socket.create_connection((self._ip, self._port), 3);
            _socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 4096);
            
            print(fileName)
            if os.access(r"{0}".format(fileName), os.R_OK):
                with open(r"{0}".format(fileName), 'r') as fp:
                    print("start download {0} to device. {1}".format(fileName, self._log.getNowDateTime()));
                    
                    self._startSendCsv(_socket);
                    
                    header = fp.readline().split(",")[1:];
                    count = 0;
                    chMap = {};
                    for item in header:
                        #csv文件头必须以I:0 O:0开始，如果csv文件头以I:1 O:1开始，row，col均需要-1；
    #                     csv文件已I:1 O:1开头;
    #                     row = int(re.findall("\d+", item)[0]) - 1;
    #                     col = int(re.findall("\d+", item)[1]) - 1;
    #                     csv文件已I:0 O:0开头
                        row = int(item.split(" ")[0].split(":")[1]);
                        col = int(item.split(" ")[1].split(":")[1]);
                        if row >= self._row or col >= self._column:
                            continue;
                        ch = col * self._row + row + 1;
                        if ch in channelList:
                            chMap[header.index(item)] = ch;
                    for line in fp:
                        valueList = line.split(",")
                        
                        self._sendCsvRowTimeData(_socket, count, int(valueList[0]));
                        count += 1;
                        
                        valueList.pop(0)
                        channels = list()
                        tempList = list()
                        phaseList = list()
                        for i in range(len(valueList)):
                            if i not in chMap.keys():
                                continue;
                            value = valueList[i];
                            channels.append(chMap[i]);
                            if ":" in value:
                                tempList.append(float(value.split(":")[0]))
                                phaseList.append(float(value.split(":")[1]))
                            else:
                                tempList.append(float(value))
    #                   确保csv文件包含全部的待申请控制的通道；
                        if len(channels) != len(channelList):
                            print("Not all channels applying for control are in the CSV file.")
                            
                        self._sendCsvAttData(_socket, channels, tempList);
                        if self._isAttenuation == "AttenuationPhase" and self.cmp(0, len(phaseList)):
                            self._sendCsvPhaseData(_socket, channels, phaseList);
                                            
                    self._endSendCsv(_socket);
                    print("finish download csv. {0}".format(self._log.getNowDateTime()));
                    return True
            else:
                raise HbteException("The file does not exist.");
        except socket.error as e:
            raise HbteException("operate {0} error: {1}".format(fileName, e));
        except Exception as e:
            raise HbteException("operate {0} error: {1}.".format(fileName, e));
        finally:
            if (_socket != None):
                _socket.close();
                _socket = None;
        
    def _startSendCsv(self, _socket):
        self._sendCsvData(_socket, "$TA,c,000*\r\n");
        
    def _endSendCsv(self, _socket):
        self._sendCsvData(_socket, "$TA,s,000*\r\n");
        
    def _sendCsvRowTimeData(self, _socket, row, delayTime):
        self._sendCsvData(_socket, "$TA,T,{0}-{1}*\r\n".format(str(row).zfill(6), str(delayTime).zfill(5)))
        
    def _sendCsvAttData(self, _socket, channelList, valueList):
        data = list()
        for channel in range(self._channelRange):
            data.append("FF")
            
        tempList = list()
        for value in valueList:
            if value < 0:
                value = 0;
            if value > self._maxdB:
                if self._isAttenuation == "AttenuationSwitch":
                    tempList.append("FE")
                else:
                    value = self._maxdB;
                    tempList.append(hex(int(value * 2))[2:].zfill(2))
            else:
                tempList.append(hex(int(value * 2))[2:].zfill(2))
        
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = tempList[i]
        return self._sendCsvData(_socket, "$TA,FG,{0}*\r\n".format("".join(data).upper()));
        
    def _sendCsvPhaseData(self, _socket, channelList, phaseList):
        data = list()
        for index in range(self._channelRange):
            if int(self._phaseStep) > 1.0:
                data.append("FF");
            else:
                data.append("FFF");
        
        tempList = list()
        for value in phaseList:
            while value < 0:
                value += 360;
            while value > 360:
                value -= 360;                
            temp = float(value) / self._phaseStep;
            tmp = temp - int(temp) > 0.5 and int(temp + 1) or int(temp); 
            if tmp == int(360 / self._phaseStep):
                tmp = 0;
            if int(self._phaseStep) > 1.0: 
                tempList.append(hex(int(tmp))[2:].zfill(2))
            else:
                tempList.append(hex(int(tmp))[2:].zfill(3))        
        
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = tempList[i]
            
        return self._sendCsvData(_socket, "$TA,Fg,{0}*\r\n".format("".join(data).upper()));
    
    def _sendCsvData(self, _socket, data):
        _socket.sendall(data.encode("utf8"))
        print("send data: {0}".format(data));
        recvData = _socket.recv(1024);
        print("recvData: ", recvData);
        if "FF\r\n" == recvData.decode():
            print("send csv data: ", data, recvData);
            raise HbteException("This command is invalid.");
        
        if "01\r\n" != recvData.decode():
            print("send csv data: ", data, recvData);
            raise HbteException("send csv data failed.");
        
        return recvData.decode();
    
    def __sendCsvAttData(self, channelList, valueList):
        data = list()
        for channel in range(self._channelRange):
            data.append("FF")
            
        tempList = list()
        for value in valueList:
            if value < 0:
                value = 0;
            if value > self._maxdB:
                if self._isAttenuation == "AttenuationSwitch":
                    tempList.append("FE")
                else:
                    value = self._maxdB;
                    tempList.append(hex(int(value * 2))[2:].zfill(2))
            else:
                tempList.append(hex(int(value * 2))[2:].zfill(2))
        
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = tempList[i]
        return self.sendCsvAttData("".join(data));
    
    def __sendCsvPhaseData(self, channelList, phaseList):
        data = list()
        for index in range(self._channelRange):
            if int(self._phaseStep) > 1.0:
                data.append("FF");
            else:
                data.append("FFF");
        
        tempList = list()
        for value in phaseList:
            while value < 0:
                value += 360;
            while value > 360:
                value -= 360;                
            temp = float(value) / self._phaseStep;
            tmp = temp - int(temp) > 0.5 and int(temp + 1) or int(temp); 
            if tmp == int(360 / self._phaseStep):
                tmp = 0;
            if int(self._phaseStep) > 1.0: 
                tempList.append(hex(int(tmp))[2:].zfill(2))
            else:
                tempList.append(hex(int(tmp))[2:].zfill(3))        
        
        for i in range(len(channelList)):
            data[int(channelList[i]) - 1] = tempList[i]
        return self.sendCsvPhaseData("".join(data))

    def operateSweepOfDegree(self, horizontalAngleStart = -60.0, horizontalAngleEnd = 60.0, verticalAngleStart = 0.0, verticalAngleEnd = 96.0, inputChannelStart = 1, inputChannelEnd = 64, outputChannelStart = 1, outputChannelEnd = 4, hCoefficient = 0.5, vCoefficient = 1.4, runPath = "Two-way"):
        upStep = 1.0;
        downStep = 1.0;
        
        hAngles = [];
        vAngles = [];
        hStart = int(horizontalAngleStart * 10);
        hEnd = int(horizontalAngleEnd * 10);
        _upStep = int(upStep * 10);
        _downStep = int(downStep * 10);
        vStart = int(verticalAngleStart * 10);
        vEnd = int(verticalAngleEnd * 10);         
        
        for hAngle in range(hStart, hEnd, _upStep):
            hAngles.append(hAngle / 10.0);
        hAngles.append(horizontalAngleEnd);
        
        for vAngle in range(vStart, vEnd, _downStep):
            vAngles.append(vAngle / 10.0);
        vAngles.append(verticalAngleEnd);
        
        if runPath == "Two-way":
            hAngles.extend(reversed(hAngles[:-1]));
            vAngles.extend(reversed(vAngles[:-1]));
            
        for horizontalAngle in hAngles:
            for verticalAngle in vAngles:
                self.__operateDegree(horizontalAngle = horizontalAngle, verticalAngle = verticalAngle, inputChannelStart = inputChannelStart, inputChannelEnd = inputChannelEnd, outputChannelStart = outputChannelStart, outputChannelEnd = outputChannelEnd, hCoefficient = hCoefficient, vCoefficient = vCoefficient);
                time.sleep(1);
                
    def __operateDegree(self, horizontalAngle = 0.0, verticalAngle = 0.0, inputChannelStart = 1, inputChannelEnd = 1, outputChannelStart = 1, outputChannelEnd = 4, hCoefficient = 0.5, vCoefficient = 1.4):
        if inputChannelStart < 1 or inputChannelEnd > self._row:
            raise HbteException("operate degree error: The set channel over the maximum or lass than 1.");
        
        channelList = list();
        phaseList = list();
        
        group = 1 if int(self._row / 16) < 1 else int(self._row / 16);
        for i in range(group):
            for j in range(int(self._row / group / 2)):
                phiSum = self.__calcDegree(hAngle=horizontalAngle, vAngle=verticalAngle, hCoefficient=hCoefficient, vCoefficient=vCoefficient, m=i+1, n=j+1, formula = 3);
                _row = i * int(self._row / group) + j * 2 + 1;
                if _row < inputChannelStart or _row > inputChannelEnd:
                    continue;
                
                for _col in range(outputChannelStart, outputChannelEnd + 1, 1):
                    channelList.append(_row + (_col - 1) * self._row);
                    phaseList.append(phiSum);
                    channelList.append(_row + (_col - 1) * self._row + 1);
                    phaseList.append(phiSum);
               
        self.operateChannelPhase(channelList=channelList, phaseList=phaseList);            

    def operateDegree(self, horizontalAngle = 0.0, verticalAngle = 0.0, inputChannelStart = 1, inputChannelEnd = 1, outputChannel = 1, hCoefficient = 0.5, vCoefficient = 1.4):
        if inputChannelStart < 1 or inputChannelEnd > self._row:
            raise HbteException("operate degree error: The set channel over the maximum or lass than 1.");
        
        channelList = list();
        phaseList = list();
        
        group = 1 if int(self._row / 16) < 1 else int(self._row / 16);
        for i in range(group):
            for j in range(int(self._row / group / 2)):
                phiSum = self.__calcDegree(hAngle=horizontalAngle, vAngle=verticalAngle, hCoefficient=hCoefficient, vCoefficient=vCoefficient, m=i+1, n=j+1);
                _row = i * int(self._row / group) + j * 2 + 1;
                if _row < inputChannelStart or _row > inputChannelEnd:
                    continue;
                
                _col = outputChannel;
                channelList.append(_row + (_col - 1) * self._row);
                phaseList.append(phiSum);
                channelList.append(_row + (_col - 1) * self._row + 1);
                phaseList.append(phiSum);
                
        self.operateChannelPhase(channelList=channelList, phaseList=phaseList);
    
    def __calcDegree(self, hAngle = 0.0, vAngle = 0.0, hCoefficient = 0.5, vCoefficient = 1.4, m = 1, n = 1, formula = 1):
        phi1 = 0.0;
        phi2 = 0.0;
        if formula == 1:            
            phi1 = float(2 * 180 * (n - 1)) * sin(hAngle / 180.0 * PI) * hCoefficient;
            phi2 = float(2 * 180 * (m - 1)) * sin(vAngle / 180.0 * PI) * vCoefficient;
        elif formula == 3:
            phi1 = float(2 * 180 * (n - 1)) * sin(vAngle / 180.0 * PI) * sin(hAngle / 180.0 * PI) * hCoefficient;
            phi2 = float(2 * 180 * (m - 1)) * cos(vAngle / 180.0 * PI) * vCoefficient;
            
        phiSum = phi1 + phi2;
        while phiSum < 0:
            phiSum += 360;
        
        return int(phiSum) % 360 + phiSum - int(phiSum);
        
class PB(Logic):
    def __init__(self, ip = "127.0.0.1", port = 5000):
        Logic.__init__(self, ip, port)

    def openPort(self, channel, ip = None):
        """
        FunctionName:   openPort
        FunctionParam:  channel -as 1
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None
        if channel > self._channelRange or channel < 1:
            raise HbteException("open port error: The set channel over the maximum or lass than 1.")

        data = str(hex(channel)[2:].zfill(2))
        recvData = self.sendCDirective(data.join("01").upper())
        return recvData[2:] == "01"

    def closePort(self, channel, ip = None):
        """
        FunctionName:   closePort
        FunctionParam:  channel - as 1
                        ip - as None or "192.168.1.254"
        FunctionReturn: True ok
                        False fail
        """
        if not self.checkIPIsExist(ip):
            return None
        if channel > self._channelRange or channel < 1:
            raise HbteException("close port error: The set channel over the maximum or lass than 1.")

        data = str(hex(channel)[2:].zfill(2))
        recvData = self.sendCDirective(data.join("00").upper())
        return recvData[2:] == "00"

    def queryPort(self, channel, ip = None):
        """
        FunctionName:   queryPort
        FunctionParam:  channel - as 1
                        ip - as None or "192.168.1.254"
        FunctionReturn: 1 open
                        0 close
        """
        if not self.checkIPIsExist(ip):
            return None
        if channel > self._channelRange or channel < 1:
            raise HbteException("query port error: The set channel over the maximum or lass than 1.")

        data = str(hex(channel)[2:].zfill(2))
        recvData = self.sendCDirective(data.join("FF").upper())
        if recvData[2:] == "00":
            print("The port {0} is opened.".format(int(recvData[:2])))
        else:
            print("The port {0} is closed.".format(int(recvData[:2])))
        return int(recvData[2:])

    class RFBox(Logic):
        def __init__(self, ip = "127.0.0.1", port = 5000):
            Logic.__init__(ip, port)

        def openChannel(self, channel, ip = None):
            """
            FunctionName:   openChannel
            FunctionParam:  channel - as 1
                            ip - as None or "192.168.1.254"
            FunctionReturn: True ok
                            False fail
            """
            if not self.checkIPIsExist(ip):
                return None
            if channel > self._channelRange or channel < 1:
                raise HbteException("open channel error: The set channel over the maximum or lass than 1.")
                return None
            data = str(hex(channel)[2:].zfill(2))
            recvData = self.sendCDirective(data.join("01").upper())
            return recvData[2:] == "01"

        def closeChannel(self, channel, ip = None):
            """
            FunctionName:   closeChannel
            FunctionParam:  channel - as 1
                            ip - as None or "192.168.1.254"
            FunctionReturn: True ok
                            False fail
            """
            if not self.checkIPIsExist(ip):
                return None
            if channel > self._channelRange or channel < 1:
                raise HbteException("close channel error: The set channel over the maximum or lass than 1.")
                return None
            data = str(hex(channel)[2:].zfill(2))
            recvData = self.sendCDirective(data.join("00").upper())
            return recvData[2:0] == "00"

        def queryChannel(self, channel, ip = None):
            """
            FunctionName:   queryChannel
            FunctionParam:  channel - as 1
                            ip - as None or "192.168.1.254"
            FunctionReturn: 1 open
                            0 close
            """
            if not self.checkIPIsExist(ip):
                return None
            if channel > self._channelRange or channel < 1:
                raise HbteException("query channel error: The set channel over the maximum or lass than 1.")

            data = str(hex(channel)[2:].zfill(2))
            recvData = self.sendCDirective(data.join("FF").upper())
            if recvData[2:] == "00":
                print("The channel {0} is opened.".format(int(recvData[:2])))
            else:
                print("The channel {0} is closed.".format(int(recvData[:2])))
            return int(recvData[2:])

if __name__ == '__main__':
    try:
        pa = PA("192.168.2.51", 5000)
        pa.operateChannel([3,4],[2.5,3]);
        
        pb = PB("192.168.1.253", 5000)
        pb.openPort(1);
        
    except HbteException as e:
        print(e.error)
