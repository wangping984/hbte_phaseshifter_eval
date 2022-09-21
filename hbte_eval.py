from hbte import PA
import time
import pyvisa as visa
import sys


def hbte_eval_deg():
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
    # hbte.csa has a meas named meas1
    N5244A.write(':CALCulate:PARameter:SELect "%s"' % ("meas1"))

    for deg in range(360):
        pa.operateChannelPhase(channelList=[ch_num], phaseList=[deg])
        time.sleep(0.1)
        N5244A.write(":INITiate:IMMediate")
        # 401 points, 1khz ifbw, 0.4s*2 =0.8s at least to sweep
        time.sleep(1.2)
        N5244A.write("*WAI")
        N5244A.write(
            ':CALCulate:DATA:SNP:PORTs:SAVE "%s","%s"'
            % ("1,2", "D:\\20220921\\A1B1_r7_deg" + str(deg) + ".s2p")
        )
        N5244A.write("*WAI")
        sys.stdout.write("Test progress: %d  of 359 deg \r" % (deg))
        sys.stdout.flush()

    N5244A.close()
    rm.close()


def hbte_eval_mag():
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
    N5244A.write(':CALCulate:PARameter:SELect "%s"' % ("meas1"))

    for mag in range(180):
        pa.operateChannel(channelList=[ch_num], valueList=[mag / 2])
        time.sleep(0.1)
        N5244A.write(":INITiate:IMMediate")
        # 401 points, 1khz ifbw, 0.4s*2 =0.8s at least to sweep
        time.sleep(1.2)
        N5244A.write("*WAI")
        N5244A.write(
            ':CALCulate:DATA:SNP:PORTs:SAVE "%s","%s"'
            % ("1,2", "D:\\20220921\\A1B1_r6_mag" + str(mag / 2) + ".s2p")
        )
        N5244A.write("*WAI")
        sys.stdout.write("Test progress: %.1f  of 90 dB \r" % (mag/2))
        sys.stdout.flush()

    N5244A.close()
    rm.close()


if __name__ == "__main__":
    # hbte_eval_mag()
    hbte_eval_deg()
