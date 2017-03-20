#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the class used by the controller to represent channels
#Methods include self scan call as well as status report and return of raw date
#stored from the last self scan. See docstrings for details.

import usrp_spectrum_sense_mod as usrp_ss
import os
import time

class channel(object):

    """Channel object used to managed individual UHF channels. Requires a
    [centrefreq, visualfreq, soundfreq] array. Status displays 'OCCUPIED' or
    'UNOCCUPIED' and initialises as 'UNKNOWN'. lastscan stores the time of the
   last channel scan (in seconds since the epoch!) and scan_data stores the
   usrp output of said scan in an array of arrays structued [centerfreq,
   freq, power_db, noise_floor_db]."""
    
    def __init__(self, frequencies):
        self.centrefreq = frequencies[0]
        self.visualfreq = frequencies[1]
        self.soundfreq = frequencies[2]
        #use 7MHz channel bandwith - therfore min and max freq of:
        self.min_freq = self.centrefreq - 3500000
        self.max_freq = self.centrefreq + 3500000
        self.status = 'UNKNOWN' #used to establish if PU present on channel
        self.lastscan = '0' #time.time() string stored for last scan time
        self.scan_data = [] #stores scan data points
        #structured [center_freq, freq, power_db, noise_floor_db]

    def scan(self):
       """Channel calls a scan on itself by invoking the modified GNU RADIO
       example usrp_spectrum_sense module's top_block class and main loop."""
       #FIXME consider adding antenna option at top level ie TX/RX vs RX2
       #note: u is instanced uhd.usrp_source block from GNU Radio
       pid = os.fork()#creates child process to call scanner
       if not pid:
           #within child process
           scanner = usrp_ss.my_top_block(self.min_freq, self.max_freq)
           scanner.u.antenna = 'RX2' 
           scanner.start()
           usrp_ss.main_loop(scanner)
           os._exit(0)
       self.__getdata()
       
    def __getdata(self):
        """PRIVATE FUNCTION: reads from the fifo output of the
        usrp_spectrum_sense_mod file and store the data from the pass."""
        try:
            pipein = open('usrpout.fifo', 'r')
        except (OSError, IOError):
            print "ERROR: Could not locate usrpout.fifo in working directory."
            exit()
        while True:
            next_data = pipein.readline()
            if next_data == 'end':
                self.lastscan = time.time()
                print self.scan_data
                print self.lastscan
                break
            data_point = [float(x) for x in next_data.split()]
            self.scan_data.append(data_point)

            
            

if __name__ == '__main__':
    test_channel = [474000000, 417250000, 477250000]
    test = channel(test_channel)
    test.scan()
        
