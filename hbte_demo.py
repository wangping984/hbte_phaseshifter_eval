# -*- coding:UTF-8 -*-
#-------------------------------------------------------------------------------
#! /usr/bin/env python
# -*- coding: UTF-8 -*-
# Name:        hbte_demo.py
# Purpose:
#
# Author:      yangyuexun
#
# Created:     10/07/2017
# Copyright:   (c) HBTE-YF-1 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from hbte import PA
from base_logic import HbteException
import time
import csv
import random;
import re;
import os;

N = 1

def getNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

def main():
    try:
        pa = PA(ip = "192.168.1.254", errCount = 10);
        with open("{0}.csv".format("pa._type"), "w") as fp:
            write = csv.writer(fp)
            write.writerow(["start time", getNowTime()]);
            channelList = list();
            valueList = list();
            phaseList = list();
            
            #             pa.operateCSV(fileName = "D:\\Fachen\\pack\\pack5.7\\8X8PAP.csv", channelList=[1,2,3]);
            #pa.operateDegree(horizontalAngle = 0.0, verticalAngle = 0.0, inputChannelStart = 1, inputChannelEnd = 64, outputChannel = 1, hCoefficient = 0.5, vCoefficient = 3.2);
            for i in range(1, random.randint(1,  pa._channelRange)):
                channelList.append(i);
                valueList.append(float(random.randint(1, 900) / 10.0));
                phaseList.append(float(random.randint(0, 3600) / 10.0));
                
            try:
                #pa.exportAtt(fileName = "att_test.csv");
                #pa.loadCSV(fileName = "att_test.csv", channelList = channelList);
#                 载入相位csv文件
#                 print(pa.loadPhaseCSV(fileName="D:\\Fachen\\pack\\pack5.7\\64X16PAP.csv", channelList=channelList));
#                 载入衰减csv文件
#                 print(pa.loadCSV(fileName="D:\\Fachen\\pack\\pack5.7\\64X16.csv", channelList=channelList));
#                 pa.operateDegree(horizontalAngle=10.0, verticalAngle=11.0, inputChannelStart=1, inputChannelEnd=32, outputChannel=1);
                #if pa.operateChannel(channelList = channelList, valueList = valueList):
                 #   print("operate channel att ok")
                #else:
                 #   print("operate channel att failed")
                  #  write.writerow(["operate channel att failed", channelList, getNowTime()]);
                pa.operateChannel([1,2,3,4], [10,10,10,10]);
                print(pa.queryChannel(channelList=[1, 3, 4, 5, 7, 16]))

                #pa.operateSweepOfDegree(horizontalAngleStart = -60, horizontalAngleEnd = 60, verticalAngleStart = 96, verticalAngleEnd = 96, inputChannelStart = 1, inputChannelEnd = 64,
                #                     outputChannelStart = 1, outputChannelEnd = 4, hCoefficient = 0.5, vCoefficient = 3.2);

                
#                 if pa.operateChannelPhase(channelList = channelList, phaseList = phaseList):
#                     print("operate channel phase ok");
#                 else:
#                     print("operate channel phase failed");
                
#                 print(pa.queryCurrentFrePoint());
#                 print(pa.queryFrePoints());
#                 print(pa.setCurrentFrePoints(fre = 3500))
#                 pa.operatePreChannel(channelList = channelList, valueList = valueList);
#                 print(pa.queryPreChannel(channelList = channelList));
#                 time.sleep(0.5);
#                  
#                 if pa.operateChannel(channelList = channelList, valueList = valueList):
#                     print("operate channel att ok")
#                 else:
#                     print("operate channel att failed")
#                     write.writerow(["operate cahnnel att failed", channelList, getNowTime()]);
#                 pa.stopCsv();
#                 pa.stopCsv();
# 
#                 pa.downloadCSVToDevice(fileName = "C:\\Users\\Young\\Desktop\\PPSM_64x08.csv", channelList = channelList);
# #                 pa.runExternalCSv(loopCount = 2);
#                 #启动内部触发；
#                 pa.runCsv(loopCount = 1);
#                 count = 0;
#                 while(True):
#                     print(pa.queryCsvState());
#                     time.sleep(1)
#                     count = count + 1;
#                     if count > 60:
#                         break;
#                 pa.pauseCsv();
#                 time.sleep(10);
#                 pa.continueCsv();
#                 time.sleep(1 * 60);
#                 pa.stopCsv();
#                 time.sleep(20);
#                 
#                 print(pa.queryChannel(channelList=[1, 3, 4, 5, 7, 16]))
#                 if pa.operateChannelPhase(channelList = channelList, phaseList = phaseList):
#                     print("operate channel phase ok");
#                 else:
#                     print("operate channel phase failed");
#                     write.writerow(["operate channel phase failed", channelList, getNowTime()]);
#                     exit(0);
#                 
#                 print(pa.queryChannelPhase(channelList = channelList));
                
#             print(pa.queryFrePoints())
#             
#             
#             print(pa.setCurrentFrePoints(fre = 3700));
#             
#             print(pa.queryChannel(channelList = [1, 2, 3]));
                
#                 if pa.operateColumnPhase(columnList = [1, 3, 9, 12, 16], value = 210):
#                     print("operate channel phase ok")
#                 else:
#                     print("operate channel phase failed")
#                 if pa.operateChannelPhase(channelList = [1, 500, 10], phaseList = [30, 359, 20]):
#                     print("operate channel phase ok {0} {1} {2}".format(1, 20, getNowTime()));
#                 else:
#                     print("operate channel failed {0} {1} {2}".format(1, 20, getNowTime()));
#                 print(pa.queryChannelPhase(channelList = [1, 10, 500]));
#                 if pa.operateMulChannelPhase(startChannel = 129, endChannel=200, phaseValue = -90):
#                     print("operate channel phase ok {0} {1} {2}".format(129, 200, getNowTime()));
#                 else:
#                     print("operate channel failed {0} {1} {2}".format(129, 200, getNowTime()));
#                 time.sleep(1);
#                 if pa.operateChannel(channelList = [9], valueList = [30]):
#                     print("operate channel ok {0} {1} {2}".format(1, 15.5, getNowTime()));
#                 else:
#                      print("operate channel failed {0} {1} {2}".format(1, 15.5, getNowTime()));
            except HbteException as e:
                print(e.error)
                write.writerow([e.error, getNowTime()])
#             for m in range(N):
#                 for i in range(20, 50):
#                     for j in range(-180, 360, 2):
#                         try:
#                             if pa.operateChannelPhase(channelList=[i + 1, i+2], phaseList=[j, j+2]):
#                                 print "operate channel ok", i+1, j, getNowTime()
#                             else:
#                                 print "operate channel failed", i + 1, j, getNowTime()
#                         except HbteException, e:
#                             write.writerow([e.error, i+1, j, getNowTime()])
#                             break;'
#                         time.sleep(0.2)
#             for m in range(10):
#                 try:
#                     if pa.operateMulChannel(startChannel=1, endChannel=5, value=2.5):
#                         print "operate channel ok", 1, 2.5, getNowTime()
#                     else:
#                         print "operate channel failed", 1, 2.5, getNowTime()
#                 except HbteException, e:
#                     write.writerow([e.error, 1, 2.5, getNowTime()])
#                     break;
            write.writerow(["End time:", getNowTime()])
    except HbteException as e:
        print(e.error)
        
def testDeviceConsistency(deviceIP1, fileName1, deviceIP2, fileName2):
    try:        
        dataList1 = readCsv(fileName1, deviceIP1);
        dataList2 = readCsv(fileName2, deviceIP2);
        
        if len(dataList1) != len(dataList2):
            raise HbteException("test device consistency failed: The length of the CSV file read is inconsistent");
                
        pa1 = PA(deviceIP1);
        pa2 = PA(deviceIP2);
        
        for i in range(len(dataList1)):
            data1 = dataList1[i];
            data2 = dataList2[i];
            
            pa1.operateChannel(channelList = data1["channels"], valueList = data1["values"]);
            if len(data1["phases"]) != 0:
                pa1.operateChannelPhase(channelList = data1["channels"], phaseList = data1["phases"]);
                
            pa2.operateChannel(channelList = data2["channels"], valueList = data2["values"]);
            if len(data2["phases"]) != 0:
                pa2.operateChannelPhase(channelList = data2["channels"], phaseList = data2["phases"]);
            
            time.sleep(data1["delay"]);
        
    except HbteException as e:
        print(e.error);
    
def readCsv(fileName, deviceIP):
    try:
        pa = PA(deviceIP);
        if os.access(r"{0}".format(fileName), os.R_OK):
            with open(r"{0}".format(fileName), 'r') as fp:
                header = fp.readline().split(",")[1:];
                chMap = {};
                #csv文件以I:0 O:0开始，csvFlag = 0；
                #csv文件以I:1 O:1开始，csvFlag = 1；
                #矩阵（8*8）表头以I:0 O:0或者I:1 O:1开始，非矩阵（8-8）以I:0或者O:1开始。
                csvFlag = 0;
                dataList = list();
                for item in header:
                    #csv文件头必须以I:0 O:0开始，如果csv文件头以I:1 O:1开始，row，col均需要-1；
                    if len(re.findall("\d+", item)) > 1:
                        row = int(re.findall("\d+", item)[0]) - csvFlag;
                        col = int(re.findall("\d+", item)[1]) - csvFlag;
                        
                        ch = col * pa._row + row + 1;
                    else:
                        row = int(re.findall("\d+", item)[0]) - csvFlag; 
                        ch = row + 1;
                    if ch > pa._channelRange:
                        continue;
                    chMap[header.index(item)] = ch;
                for line in fp:
                    valueList = line.split(",")
                    delay = float(valueList[0]) / 1000
                    valueList.pop(0)
                    channels = list()
                    tempList = list()
                    phaseList = list()
                    map = {};
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
                    map["delay"] = delay;
                    map["channels"] = channels;
                    map["values"] = tempList;
                    map["phases"] = phaseList;
                    
                    dataList.append(map);
                return dataList;
                
    except HbteException as e:
        print(e.error); 

if __name__ == '__main__':
#     row = int(re.findall("\d+", "A12B21")[0]);
#     col = int(re.findall("\d+", "A12B21")[1]);
#         
#     print(row, col, type(row));
    while True:
        main();
#         testDeviceConsistency("192.168.1.123", "D:\\FacheApplication\\HBTE Power Creator\\PAM_16x16.csv", 
#                               "192.168.1.254", "D:\\FacheApplication\\HBTE Power Creator\\PAM_16x16.csv");
