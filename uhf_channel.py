#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the class used by the controller to represent channels
#Methods include self scan call as well as status report and return of raw date
#stored from the last self scan. See docstrings for details.

import usrp_spectrum_sense_mod as usrp_ss
import sensingTools.SPmethods as SPmethods
import predictionModel.SignalClassifier as SignalClassifier
import os
import time
import json
import matplotlib.pyplot as plt
import numpy as np
try:
    #import gps module from gpsd if installed
    import gps
except:
    pass

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
                structued [centerfreq, freq, power_db, noise_floor_db]
    lastgps: gps co-ordinates of last scan if options.gps_flag =1 """
    
    def __init__(self, chan_id, frequencies, options):
        self.chan_id = chan_id
        self.centrefreq = frequencies[0]
        self.visualfreq = frequencies[1]
        self.soundfreq = frequencies[2]
        self.options = options
        self.antenna = options.antenna#Default is 'RX2'
        #use 7MHz channel bandwith - therfore min and max freq of:
        self.min_freq = self.centrefreq - 3500000
        self.max_freq = self.centrefreq + 3500000
        self.status = 'UNKNOWN' #used to establish if PU present on channel
        self.lastscan = '0' #time.time() string stored for last scan time
        self.lastgps = None
        self.scan_data = [] #stores scan data points
        #structured [center_freq, freq, power_db, noise_floor_db]
        self.scan_count = 0 #tracks the scan count for the channel
        self.scan_SP = [] #stores returned signal properties from SPmethods
        #load prediction model
        store = 'predictionModel/training_data/cleaned_data'
        print store
        self.classifier, self.scaler = SignalClassifier.loadmodel(store)

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
        if self.options.gps_flag:
           self.__getlocation()
        self.__getSP()
        self.__statustest()
        #store raw data with classification if raw_store
        if self.options.raw_store:
           self.__rawstore('9001')
        #increment scan_count by 1
        self.scan_count += 1
        return True #reports back to controller that scan is complete
       
    def __getdata(self):

        """PRIVATE METHOD: reads from the fifo output of the
        usrp_spectrum_sense_mod file and store the data from the pass."""

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

        """PRIVATE METHOD: Predicts the status of the channel using the kNN
        model from predictionModel.SignalClassifier."""

        data = self.scaler.transform(self.scan_SP)
        status = self.classifier.predict(data)
        if status == 2:
            self.status = 'PRIMARY_OCCUPIED'
        if status == 1:
            self.status = 'SECONDARY_OCCUPIED'
        if status == 0:
            self.status = 'UNOCCUPIED'

            
    def __getlocation(self):

        """PRIVATE METHOD: Calls the gps module from gpsd and establishes the
        location from which the scan is being made. This is stored in
        self.lastgps."""

        session = gps.gps()
        latitude = session.fix.latitude
        longitude = session.fix.longitude

        self.lastgps = [float(latitude), float(longitude)]

        #CONSIDER: including session.fix.altitude in this

    def __rawstore(self, max_power):

        """PRIVATE METHOD: Stores raw FFT data from last scan for use in
        analytics such as model training."""

        #data dump of [status, max power, noise floor, raw data]
        data_dump = [self.status, max_power, self.scan_data[0][3], self.scan_data]
        store = 'data/{}/raw_store'.format(self.options.session)
        #make directory for session and channel
        if not os.path.exists(store):
            os.makedirs(store)
        #make json directory
        if not os.path.exists(store + '/json'):
            os.makedirs(store +'/json')
        
        #store the data in json format
        file_name = store + '/json/{}_{}_{}.json'.format(self.chan_id,
                                                  str(self.scan_count),
                                                     self.options.session)
        with open(file_name, 'w+') as fp:
           json.dump(data_dump, fp, indent=4)
           
        #save line plot of raw data for visual inspection purposes
        fig = plt.figure()
        sub = fig.add_subplot(211)
        sub.set_title('channel_id : {} | noise_floor(dBm) : {}'.format(
            self.chan_id,
            self.scan_data[0][3]))#noise floor is same for all values in a scan
        x_data = [j[1] for j in self.scan_data]
        y_data = [k[2] for k in self.scan_data]
        sub.plot(x_data, y_data)

        fig_name = store + '/{}_{}_{}.png'.format(self.chan_id,
                                                  str(self.scan_count),
                                                     self.options.session)
        fig.tight_layout()
        fig.savefig(fig_name, bbox_inches='tight')

    def __storeSP(self):

        """Stores signal properties, sorted by environement data,
        in json format for use in analytics."""


        store = 'data/{}/SPdump'.format(self.options.session)
        #make directory for store
        if not os.path.exists(store):
            os.makedirs(store)
        try:
            if self.chan_id in self.options.environment[0]:
                #primary chan for environment
                category = 2
            if self.chan_id in self.options.environment[1]:
                #secondary chan for environment
                category = 1
            if self.chan_id in self.options.environment[2]:
                #unoccupied chan
                category = 0
        except:
            #uncategorised
            category = None

        file_name = store + '/{}_{}_SP_{}.json'.format(self.chan_id,
                                                  str(self.scan_count),
                                                     self.options.session)
        data_dump = [category, self.scan_SP]

        with open(file_name, 'w+') as fp:
           json.dump(data_dump, fp, indent=4)


    def __getSP(self):
        #calls the SPmethods function and returns signal properties as a list
        #[max_power, max_power_relative, mean_power, mean_power_relative,
        #   stddev_power, ratio_vpp_std, noise_floor]
        self.scan_SP = SPmethods.getproperties(self.scan_data)
        print self.scan_SP

        #dump SP data to json if flagged
        if self.options.SPstore:
            self.__storeSP()


            
            

if __name__ == '__main__':
    print "uhf_channel.py : Running channel class test"
    print "test starting"
    test_channel = [770000000, 767250000, 773250000]
    test_id = '58'
    options = type('', (), {})() #creates empty object to mimic 'options'
    options.gps_flag = 0
    options.session = 'Testing'
    options.raw_store = 1
    options.antenna = 'RX2'
    options.SPstore = 1
    test = channel(test_id, test_channel, options)
    test.scan()
    print test.scan_SP

    test_channel = [578000000, 575250000, 581250000]
    test_id = '34'
    options = type('', (), {})() #creates empty object to mimic 'options'
    options.gps_flag = 0
    options.session = 'Testing'
    options.raw_store = 1
    options.antenna = 'RX2'
    options.SPstore = 1
    test = channel(test_id, test_channel, options)
    test.scan()
    print test.scan_SP

    test_channel = [786000000, 783250000, 789250000]
    test_id = '60'
    options = type('', (), {})() #creates empty object to mimic 'options'
    options.gps_flag = 0
    options.session = 'Testing'
    options.raw_store = 1
    options.antenna = 'RX2'
    options.SPstore = 1
    test = channel(test_id, test_channel, options)
    test.scan()
    print test.scan_SP
