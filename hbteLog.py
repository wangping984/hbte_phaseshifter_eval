#-------------------------------------------------------------------------------
# -*- coding: UTF-8 -*-
# Name:        HBTE
# Purpose:
#
# Author:      yangyuexun
#
# Created:     26/10/2018
# Copyright:   (c) HBTE-YF-1 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import time
import datetime

class HbteLog(object):
    __instance = None;
    def __init__(self):
        pass;
    
    def __new__(cls, *args, **kwd):
        if not cls.__instance:
            cls.__instance = super(HbteLog, cls).__new__(cls, *args, **kwd)
        return cls.__instance;
    
    def mkdir(self, path):
        isExists = os.path.exists(path);
        if not isExists:
            os.makedirs(path);
            return True;
        
        return False;
    
    def writeFile(self, data):
        path = "./calibrationLog/{0}".format(self.getNowDate());
        if self.mkdir(path):
            return None;
        with open("{0}/{1}.txt".format(path, self.getNowHour()), "a") as fp:
            line = "{0}:\n{1}\n".format(self.getNowDateTime(), data);
            fp.write(line);
    
    def getNowDate(self):
        return time.strftime("%Y%m%d",time.localtime(time.time()));
    
    def getNowHour(self):
        return time.strftime("%H", time.localtime(time.time()));
    
    def getNowDateTime(self):
        return datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f");
    
    