from hbte import PA
import time
import pyvisa as visa

pa = PA("192.168.1.254")
ch_num = 1
pa.operateChannel(channelList=[ch_num], valueList=[0])

rm = visa.ResourceManager()
N5244A = rm.open_resource("TCPIP0::192.168.1.2::inst0::INSTR")
N5244A.write(":SYSTem:PRESet")
N5244A.write(':MMEMory:LOAD:CSARchive "%s"' % ("hbte.csa"))
N5244A.timeout = 5000
N5244A.write(":TRIGger:SEQuence:SOURce %s" % ("MANual"))
N5244A.write(":INITiate:CONTinuous %d" % (0))
N5244A.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude %G" % (10.0))

for deg in range(360):
    pa.operateChannelPhase(channelList=[ch_num], phaseList=[deg])
    time.sleep(0.1)
    N5244A.write(":INITiate:IMMediate")
    N5244A.write("*WAI")
    N5244A.write(
        ':CALCulate:DATA:SNP:PORTs:SAVE "%s","%s"'
        % ("1,2", "D:\\20220920\\A1B1_deg" + str(deg) + ".s2p")
    )
    N5244A.write("*WAI")


N5244A.close()
rm.close()