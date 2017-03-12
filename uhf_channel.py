#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the class used by the controller to represent channels
#Methods include self scan call as well as status report and return of raw date
#stored from the last self scan. See docstrings for details.

import usrp_spectrum_sense_mod as usrp_ss

class channel(object):
    
    def __init__(self, frequencies):
        self.centrefreq = frequencies[0]
        self.visualfreq = frequencies[1]
        self.soundfreq = frequencies[2]
        #use 7MHz channel bandwith - therfore min and max freq of:
        self.min_freq = self.centrefreq - 3500000
        self.max_freq = self.centrefreq + 3500000
        self.status = 'UNKNOWN' #used to establish if PU present on channel

    def scan(self):
       """Channel calls a scan on itself by invoking the modified GNU RADIO
       example usrp_spectrum_sense module's top_block class and main loop."""
       t = usrp_ss.ThreadClass()
       t.start()
       scanner = usrp_ss.my_top_block(self.min_freq, self.max_freq)
       #FIXME consider adding antenna option at top level ie TX/RX vs RX2
       #note: u is instanced uhd.usrp_source block from GNU Radio
       scanner.u.antenna = 'RX2' 
       scanner.start()
       usrp_ss.main_loop(scanner)

if __name__ == '__main__':
    test_channel = [474000000, 417250000, 477250000]
    test = channel(test_channel)
    test.scan()
        
