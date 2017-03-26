#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the class used by the controller to represent channels
#Methods include self scan call as well as status report and return of raw date
#stored from the last self scan. See docstrings for details.

import usrp_spectrum_sense_mod as usrp_ss
import os
import time

class channel(object):

    """Channel object used to managed individual UHF channels.
    Required:
        chan_id : channel id string (usually the UHF channel number)
        frequnecies:  a [centrefreq, visualfreq, soundfreq] array.
    Optional: 
        antenna: Antenna string to pass to gnuradio block
        
    status:  displays 'OCCUPIED' or 'UNOCCUPIED' and initialises as 'UNKNOWN'
    lastscan: stores the time of the last channel scan (in seconds since the epoch!)
    scan_data:  stores the usrp output of said scan in an array of arrays 
                structued [centerfreq, freq, power_db, noise_floor_db]."""
    
    def __init__(self, chan_id, frequencies, antenna='RX2'):
        self.chan_id = chan_id
        self.centrefreq = frequencies[0]
        self.visualfreq = frequencies[1]
        self.soundfreq = frequencies[2]
        self.antenna = antenna#Default is 'RX2'
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
       #note: u is instanced uhd.usrp_source block from GNU Radio
       pid = os.fork()#creates child process to call scanner
       if not pid:
           #within child process
           scanner = usrp_ss.my_top_block(self.min_freq, self.max_freq)
           scanner.u.antenna = self.antenna
           scanner.start()
           usrp_ss.main_loop(scanner)
           os._exit(0)
       self.__getdata()
       self.__statustest()
       return True #reports back to controller that scan is complete
       
    def __getdata(self):
        """PRIVATE METHOD: reads from the fifo output of the
        usrp_spectrum_sense_mod file and store the data from the pass."""
        #FIXME wiping data here so that each store is a fresh scan
        #FIXME need a pass to long term storage function so we can analyse
        #FIXME scan history for a whole session
        self.scan_data = []
        try:
            pipein = open('usrpout.fifo', 'r')
        except (OSError, IOError):
            print "ERROR: Could not locate usrpout.fifo in working directory."
            exit()
        while True:
            next_data = pipein.readline()
            if next_data == 'end':
                self.lastscan = time.time()
                break
            data_point = [float(x) for x in next_data.split()]
            self.scan_data.append(data_point)
    
    def __statustest(self):
        """Primitive test function implemented that declares the channel
        'OCCUPIED' if energy > -85dBm(ref: Implementation Issues in Spectrum
        Sensing for Cognitive Radios - Cabric et al) is detected on the
        channel. Currenlty using >-80dBm for OCCUPIED and -80 > UNKNOWN >- 85"""
        max_power = -1000
        

        #find max power recorded in the scan data
        for datapoint in self.scan_data:
            if (datapoint[2] + datapoint[3]) > max_power:
                max_power = (datapoint[2] + datapoint[3])


        if max_power > -80:
            #if noise floor plus power >-85bd declare channel occupied
            self.status = 'OCCUPIED'
            return
        if -85 < max_power <= -80:
            self.status = 'UNKNOWN'
            return
        self.status = 'UNOCCUPIED'
            

            
            

if __name__ == '__main__':
    print "uhf_channel.py : Running channel class test"
    time.sleep(2)
    print "test starting"
    test_channel = [474000000, 417250000, 477250000]
    test_id = '1'
    test = channel(test_id, test_channel)
    test.scan()
    print test.scan_data
    print test.lastscan
        
