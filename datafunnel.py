#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the datafunnel object which handles
#plotting functions that plot the status of
#TV whitespace channels as bar charts to display to the operator

import numpy as np
import matplotlib.pyplot as plt
import json
import time
import os

class datafunnel(object):

    """Plots the status of channels sent by the controller.
    Required args:
        channel_bank : should be a
    dictionary of the form {'channel_num' : uhf_channel}

    Optional args :
        named_session : provide a name for the session.
        named sessions have their data stored in the data folder.

    plot(status_data) : Called to initially plot the first data sent
    through."""

    

    def __init__(self, channel_bank, named_session='TEST SESSION'):
        self.channel_list = self.__ordered(channel_bank)
        self.T_plot, self.B_plot = self.__datasort()
        self.session_name = named_session
        self.current_fig = False



    def __ordered(self, input_dict, want_data=False):
        
        """PRIVATE METHOD: Sorts dictionary keys that are sent to channelplot.
        Structured so that unordered dictionaries used for convenience handling
        of uhf channels 21 through 68 in the controller can be sorted into
        numerical order for data plotting. want_data flag used if dictionary
        data is required in order of channel number."""

        int_list = [int(x) for x in input_dict.keys()]
        int_list = sorted(int_list)
        if not want_data:#want_data false for sorting keys
            return [str(x) for x in int_list]
        ordered_data = []
        for k in [str(x) for x in int_list]:#iterate through ordered dict key
        #for corresponding values
            if input_dict[k] == 'OCCUPIED':
                ordered_data.append(1)
                continue
            if input_dict[k] == 'UNOCCUPIED':
                ordered_data.append(0)
                continue
            ordered_data.append(0.5)#default case unknown to prevent false
            #positives or negatives
        return ordered_data

    def __datasort(self):

        """PRIVATE METHOD: Returns the sorted channel values. If more than 20
        channels have been sent to be plotted, __datasort() splits them into
        two sets."""

        N = len(self.channel_list)
        #if more than 20 channels to be plotted, split into two sets
        if N > 20:
            T_plot = self.channel_list[:(N//2)]
            B_plot = self.channel_list[(N//2):]
            return T_plot, B_plot
        return self.channel_list, None

    def plot(self, input_data):

        """Plots the status data passed in by the controller. If more
        than 20 points are present, two figures are plotted."""
        
        plt.ion()#interactive mode for persistent graphs whilst func continues
        #orders status data and converts string tags to binary values
        status_data = self.__ordered(input_data, True)#'OCCUPIED' becomes 1 etc
        ylabels = (('UNOCCUPIED', '', 'UNKNOWN', '', '', 'OCCUPIED'))#y axis labels
        
        #Arrange top plot data
        T_pos = np.arange(len(self.T_plot))
        T_sdata = np.array(status_data[:len(self.T_plot)])
        fig = plt.figure()#initialise figure plot
        subT = fig.add_subplot(211) #enter first subfigure
        dataT = subT.bar(T_pos, T_sdata, align='center', tick_label=self.T_plot)
        #format figure layout
        subT.set_yticklabels(ylabels) 
        plt.axis('tight') #required to ensure bars plot flush to figure

        if self.B_plot:
            #if two sets have been created
            #Arrange bottom plot data
            B_pos = np.arange(len(self.B_plot))
            B_sdata = np.array(status_data[len(self.T_plot):])
            subB = fig.add_subplot(212) #initialise new subplot
            dataB = subB.bar(B_pos, B_sdata, align='center', tick_label=self.B_plot)
            #format figure layout
            subB.set_yticklabels(ylabels)#label y-axis

        #format window layout
        fig.canvas.set_window_title('Channel Status Plot @' \
                                    ' {}'.format(time.strftime('%X %x %Z')))
        plt.axis('tight')
        fig.tight_layout() #required to prevent y-labels from being cut off
        fig.canvas.draw()
        self.current_fig = fig

    def store(self, scan_number, input_status, input_time, input_gps=False):

        """Stores the passed data in .json format. Data is stored in the local
        directory ~/data/(session_name). Data is stored in the format 
        [scan_pass_number, time_stored, [chan_num, status, time_scanned, gps
        coordinates(optional)]"""
        #if test session, pass on all storage

        if self.session_name == 'TEST SESSION':
            return

        #data structure for stored data
        #[scan pass nummber, time stored, data bank]
        output = [scan_number, time.strftime('%X %x %Z')]
        data_bank = []

        for key in self.__ordered(input_status):
            #data bank entries of the form
            #[channel status, time scanned, gps coordinates]
            entry = [key, input_status[key], input_time[key]]
            if input_gps:
                entry.append(input_gps[key])
            data_bank.append(entry)
        output.append(data_bank)

        storage = 'data/{}'.format(self.session_name)
        #check if a directory for the current session exists
        if not os.path.exists(storage):
            os.makedirs(storage)
            
        #store the data in json format
        file_name = storage + '/' + str(scan_number) + '.json'
        with open(file_name, 'w+') as fp:
            json.dump(output, fp, indent=4)
        
        #save current channel plot
        fig_name = storage + '/{}.png'.format(scan_number)
        self.current_fig.savefig(fig_name)


        


            



if __name__ == '__main__':
    dummy_channel_bank = {}
    choice = ['OCCUPIED', 'UNOCCUPIED', 'UNKNOWN']
    for i in range(1,40):
        dummy_channel_bank[str(i)] = 'dummy'
    plotter = datafunnel(dummy_channel_bank, named_session ='unittest')
    dummy_status_data = {}
    for i in range(1,40):
        dummy_status_data[str(i)] = choice[np.random.randint(3)]
    plotter.plot(dummy_status_data)
    raw_input('Press enter to test store() method.') 
    dummy_scan_number = 0
    dummy_time_bank = {}
    for i in range(1,40):
        dummy_time_bank[str(i)] = time.strftime('%X %x %Z')
    dummy_gps_bank = {}
    for i in range(1,40):
        dummy_gps_bank[str(i)] = [100.00, 100.00]
    plotter.store(dummy_scan_number, dummy_status_data, dummy_time_bank,
                  dummy_gps_bank)

    raw_input('Enter to exit')

    

