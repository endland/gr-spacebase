#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the class for the main controller
#The controller instances channel objects and stores
#them in a channel banks whilst continuously monitoring
#their status and last scan time.

from sensingTools.channel_list import uhfchanlist
from datafunnel import datafunnel as df
import uhf_channel
import os
import sys
import random
import pprint
import time

class controller(object):

    """Controller class which stores and monitors all channels.
    monitor : method that continously monitors the status of channels and runs
    update scans.
    Takes args - 
    pipeout : passed pipe for GUI communication
    named_session : name of session for data storage purposes  
    
    channel_bank : stored channels
    status_bank : stored channels' statuses
    time_bank : time of each stored channel's last scan
    gps_benk : gps location of each channel's last scan"""

    def __init__(self, options, pipeout=False, named_session='TEST SESSION'):
        #pipeout is passed pipe for output
        self.chan_list = uhfchanlist().full_list()#chan nums and frequencies
        self.channel_bank = {}#stores instanced channel classes
        self.status_bank = {}#stores channel occupied status
        self.time_bank = {}#stores channel lastscan times
        self.gps_bank = {}
        self.scan_number = 0 #stores the number of scan passes completed
        self.pipeout = pipeout
        self.session_name = named_session
        self.options = options
        #added explicitly for parsing simplicity to channel objects
        self.options.session = named_session
        self.__buildchannels()
        self.__initialscan()
        #store data funnel object
        self.datafunnel = df(self.channel_bank, named_session)
        self.__dataupdate() #pass inital scan results out
        self.monitor()

    def __postupdate(self, x):
        print 'in post update'
        """PRIVATE METHOD: Defines whether the postupdate function passes to a
        pipe or sys.stdout.write()"""
        x = x + '\n'
        os.write(self.pipeout, x) 


        
    def __buildchannels(self):
        """PRIVATE METHOD: instances channel classes using frequencies data
        taken from uhfchanlist.full_list. Stores instanced channels in
        self.channel_bank using the same keys provided by full_list."""
        for chan_num, frequencies in self.chan_list.iteritems():
            channel = uhf_channel.channel(chan_num, frequencies, self.options)
            self.channel_bank[chan_num] = channel
            
    def __initialscan(self):
        """PRIVATE METHOD: runs initial scan of all instances channels and
        saves both their status and lastscan time to self.status_bank and
        self.time_bank respectively."""
        for channel in self.channel_bank:
            if not self.channel_bank[channel].scan():
                self.__postupdate("""Inital Scan for channel {}
                                failed""".format(channel))
                continue #If channel scan fails, moves to next channel
            self.__postupdate("Initial Scan of channel {} complete, STATUS :\
            {}".format(
                                                self.channel_bank[channel].chan_id,
                                                self.channel_bank[channel].status))
            self.status_bank[channel] = self.channel_bank[channel].status
            self.time_bank[channel] = self.channel_bank[channel].lastscan
            if self.options.gps_flag:
                self.gps_bank[channel] = self.channel_bank[channel].lastgps

    def monitor(self):
        """monitor method: sorts channels into high and low priority lists
        based on their status. Iteratively scans all high priority channels as
        well as one low priority channel chosen at random. After each scan loop
        a child process is spawned using os.fork() which runs the private
        __dataupdate function to display the latest data to the operator."""
        high_priority = []
        low_priority = []
        for channel_num, channel in self.channel_bank.iteritems():
            if channel.status == 'PRIMARY_OCCUPIED': 
                #occupied channels are low scanning priority
                low_priority.append(channel)
                continue
            high_priority.append(channel)

        #if training scan, do not remove occupied channels from the scan.
        if self.options.training_scan:
            while True:
                print 'in training scan'
                for channel in high_priority: #scan all channels in high priority
                    if not channel.scan():
                        self.__postupdate("Routine scan of {} failed.".format(
                                                                    channel.chan_id))
                        continue #If channel scan fails, moves to next channel
                    if channel.status == 'PRIMARY_OCCUPIED':
                        #move to low priority and update status bank
                        high_priority.remove(channel)
                        low_priority.append(channel)
                        self.status_bank[channel.chan_id] = 'PRIMARY_OCCUPIED'
                    self.time_bank[channel.chan_id] = channel.lastscan
                    if self.options.gps_flag:
                        self.gps_bank[channel.chan_id] = channel.lastgps
                    self.__postupdate("High Priority Channel {} scanned. STATUS :\
                    {}".format(
                                                                   channel.chan_id,
                                                                   channel.status))
                if low_priority: #if low_priority list is not empty
                    for channel in low_priority:
                        #check a low priority channel at random
                        if not channel.scan():
                            self.__postupdate("Routine scan of {} failed.".format(
                                                                  channel.chan_id))
                            continue #If channel scan fails, move to next channel
                        if channel.status != 'PRIMARY_OCCUPIED':
                            #if channel status has changed, move to high priority queue
                            low_priority.remove(channel)
                            high_priority.append(channel)
                            self.status_bank[channel.chan_id] = channel.status
                        self.time_bank[channel.chan_id] = channel.lastscan
                        if self.options.gps_flag:
                            self.gps_bank[channel.chan_id] = channel.lastgps
                        self.__postupdate("Low Priority Channel {} scanned. STATUS :\
                            {}".format(
                                        channel.chan_id,
                                        channel.status))
                self.__postupdate("Monitor pass complete.")
                self.scan_number += 1
                self.__dataupdate() #transfer data to datafunnel


        while True:
            for channel in high_priority: #scan all channels in high priority
                if not channel.scan():
                    self.__postupdate("Routine scan of {} failed.".format(
                                                                channel.chan_id))
                    continue #If channel scan fails, moves to next channel
                if channel.status == 'PRIMARY_OCCUPIED':
                    #move to low priority and update status bank
                    high_priority.remove(channel)
                    low_priority.append(channel)
                    self.status_bank[channel.chan_id] = 'PRIMARY_OCCUPIED'
                self.time_bank[channel.chan_id] = channel.lastscan
                if self.options.gps_flag:
                    self.gps_bank[channel.chan_id] = channel.lastgps
                self.__postupdate("High Priority Channel {} scanned. STATUS :\
                {}".format(
                                                               channel.chan_id,
                                                               channel.status))
            if low_priority: #if low_priority list is not empty
                low_random = random.choice(low_priority)
                #check a low priority channel at random
                if not low_random.scan():
                    self.__postupdate("Routine scan of {} failed.".format(
                                                                low_random.chan_id))
                    continue #If channel scan fails, move to next channel
                if low_random.status != 'PRIMARY_OCCUPIED':
                    #if channel status has changed, move to high priority queue
                    low_priority.remove(low_random)
                    high_priority.append(low_random)
                    self.status_bank[low_random.chan_id] = low_random.status
                self.time_bank[low_random.chan_id] = low_random.lastscan
                if self.options.gps_flag:
                    self.gps_bank[low_random.chan_id] = low_random.lastgps
                self.__postupdate("Low Priority Channel {} scanned. STATUS :\
                    {}".format(
                                low_random.chan_id,
                                low_random.status))
            self.__postupdate("Monitor pass complete.")
            self.scan_number += 1
            self.__dataupdate() #transfer data to datafunnel


    def __dataupdate(self):

        """PRIVATE METHOD: Passes data to the instanced data funnel which plots
        and stores the data."""

        #plot the current status of monitored channels
        self.datafunnel.plot(self.status_bank)

        #store the data if this is not a TEST SESSION
        if self.session_name != 'TEST SESSION':
            if self.options.gps_flag:
                self.datafunnel.store(self.scan_number, self.status_bank,
                                      self.time_bank, self.gps_bank)
                return
            self.datafunnel.store(self.scan_number, self.status_bank,
                                  self.time_bank)



if __name__ == '__main__':
    print "controller.py : Running controller class test"
    print "use keyboard interupt 'ctrl-c' to exit."
    time.sleep(2)
    print "test starting"
    options = type('', (), {})() #creates empty object to mimic 'options'
    options.gps_flag = 1
    options.raw_store = 1
    test_controller = controller(options)
