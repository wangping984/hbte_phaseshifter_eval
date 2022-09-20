from hbte import PA
import time
import pyvisa as visa

pa = PA("192.168.1.254")
ch_num = 1
pa.operateChannel(channelList=[ch_num], valueList=[0])
pa.operateChannelPhase(channelList=[ch_num], phaseList=[1])

rm = visa.ResourceManager()
N5244A = rm.open_resource('TCPIP0::192.168.1.2::inst0::INSTR')
N5244A.write(':SYSTem:PRESet')
N5244A.timeout = 5000
N5244A.write(':TRIGger:SEQuence:SOURce %s' % ('MANual'))
N5244A.write(':INITiate:CONTinuous %d' % (0))
# N5244A.write(':CALCulate:PARameter:DEFine:EXTended "%s","%s"' % ('meas1', 'S21'))
# N5244A.write(':DISPlay:WINDow1:STATe %d' % (1))
# N5244A.write(':DISPlay:WINDow1:TRACe2:FEED "%s"' % ('meas1'))
# N5244A.write(':SENSe:FREQuency:STARt %G' % (2000000000.0))
# N5244A.write(':SENSe:FREQuency:STOP %G' % (6000000000.0))
# N5244A.write(':SENSe:BANDwidth:RESolution %G' % (1000.0))
# N5244A.write(':SENSe:SWEep:POINts %d' % (401))
# N5244A.write(':SOURce:POWer:LEVel:IMMediate:AMPLitude %G' % (0.0))
# N5244A.write(':INITiate:IMMediate')
# N5244A.write('*WAI')
# N5244A.write(':CALCulate:PARameter:SELect "%s"' % ('meas1'))
# N5244A.write(':FORMat:BORDer %s' % ('SWAPped'))
# Mname = N5244A.query(':CALCulate:PARameter:SELect?')
# data = N5244A.query(':CALCulate:PARameter:CATalog:EXTended?')
# N5244A.write(':FORMat:DATA %s,%d' % ('REAL', 64))
# data1 = N5244A.query_binary_values(':CALCulate:DATA? %s' % ('SDATA'),'d',False)
# N5244A.write(':CALCulate:DATA:SNP:PORTs:SAVE "%s","%s"' % ('1,2', 'D:\\20220920\\123.s2p'))
# N5244A.write(':MMEMory:LOAD:CSARchive "%s"' % ('default.csa'))
# N5244A.write(':CALCulate:PARameter:SELect "%s"' % ('meas1'))
# Mname1 = N5244A.query(':CALCulate:PARameter:SELect?')
# data2 = N5244A.query(':CALCulate:PARameter:CATalog?')
# N5244A.write(':FORMat:DATA %s,%d' % ('ASCii', 0))
# temp_values = N5244A.query_ascii_values(':CALCulate1:DATA? %s' % ('SDATA'))
# data3 = temp_values[0]




N5244A.write(':MMEMory:LOAD:CSARchive "%s"' % ('hbte.csa'))


for deg in range(360):
    pa.operateChannelPhase(channelList=[ch_num], phaseList=[deg])
    time.sleep(0.1)
    N5244A.write(':INITiate:IMMediate')
    N5244A.write('*WAI')
    N5244A.write(':CALCulate:DATA:SNP:PORTs:SAVE "%s","%s"' % ('1,2', 'D:\\20220920\\A1B1_deg'+ str(deg) + '.s2p'))
    N5244A.write('*WAI')




N5244A.close()
rm.close()
