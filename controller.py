#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the class for the main controller
#The controller instances channel objects and stores
#them in a channel banks whilst continuously monitoring
#their status and last scan time.

from channel_list import uhfchanlist
import uhf_channel
import os
import random
import pprint
import time

class controller(object):

    """ADD CLASS DOC STRING HERE"""

    def __init__(self):
        self.chan_list = uhfchanlist().full_list()#chan nums and frequencies
        self.channel_bank = {}#stores instanced channel classes
        self.status_bank = {}#stores channel occupied status
        self.time_bank = {}#stores channel lastscan times
        self.__buildchannels()
        self.__initialscan()
        self.monitor()

        
    def __buildchannels(self):
        """PRIVATE METHOD: instances channel classes using frequencies data
        taken from uhfchanlist.full_list. Stores instanced channels in
        self.channel_bank using the same keys provided by full_list."""
        for chan_num, frequencies in self.chan_list.iteritems():
            channel = uhf_channel.channel(chan_num, frequencies)
            self.channel_bank[chan_num] = channel
            
    def __initialscan(self):
        """PRIVATE METHOD: runs initial scan of all instances channels and
        saves both their status and lastscan time to self.status_bank and
        self.time_bank respectively."""
        for channel in self.channel_bank:
            if not self.channel_bank[channel].scan():
                print "Inital Scan for channel {} failed".format(channel)
                continue #If channel scan fails, moves to next channel
            print "Initial Scan of channel {} complete, STATUS : {}".format(
                                                self.channel_bank[channel].chan_id,
                                                self.channel_bank[channel].status)
            self.status_bank[channel] = self.channel_bank[channel].status
            self.time_bank[channel] = self.channel_bank[channel].lastscan

    def monitor(self):
        """monitor method: sorts channels into high and low priority lists
        based on their status. Iteratively scans all high priority channels as
        well as one low priority channel chosen at random. After each scan loop
        a child process is spawned using os.fork() which runs the private
        __dataupdate function to display the latest data to the operator."""
        high_priority = []
        low_priority = []
        for channel_num, channel in self.channel_bank.iteritems():
            if channel.status == 'OCCUPIED': 
                #occupied channels are low scanning priority
                low_priority.append(channel)
                continue
            high_priority.append(channel)
        while True:
            for channel in high_priority: #scan all channels in high priority
                if not channel.scan():
                    print "Routine scan of {} failed.".format(channel.chan_id)
                    continue #If channel scan fails, moves to next channel
                if channel.status == 'OCCUPIED':
                    #move to low priority and update status bank
                    high_priority.remove(channel)
                    low_priority.append(channel)
                    self.status_bank[channel.chan_id] = 'OCCUPIED'
                    self.time_bank[channel.chan_id] = channel.lastscan
                print "High Priority Channel {} scanned. STATUS : {}".format(
                                                               channel.chan_id,
                                                               channel.status)
            low_random = random.choice(low_priority)
            #check a low priority channel at random
            if not occupied_random.scan():
                print "Routine scan of {} failed.".format(low_random.chan_id)
                continue #If channel scan fails, move to next channel
            if low_random.status != 'OCCUPIED':
                #if channel status has changed, move to high priority queue
                low_priority.remove(low_random)
                high_priority.append(low_random)
                self.status_bank[low_random.chan_id] = low_random.status
                self.time_bank[low_random.chan_id] = low_random.lastscan
                print "Low Priority Channel {} scanned. STATUS : {}".format(
                                                               channel.chan_id,
                                                               channel.status)
            print "monitor pass complete"
            print "printing priority lists"
            pprint.pprint(high_priority)
            pprint.pprint(low_priority)
            #spawn child process to display data to operator whilst
            #parent continues to monitor channels
            pid = os.fork()
            if not pid:
                #within child process
                self.__dataupdate()

    def __dataupdate(self):
        os._exit(0)
        #FIXME data plotting method to be written
        



if __name__ == '__main__':
    print "controller.py : Running controller class test"
    print "use keyboard interupt 'ctrl-c' to exit."
    time.sleep(2)
    print "test starting"
    test_controller = controller()
