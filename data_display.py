#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the plotting functions to live plot the status of
#TV whitespace channels as bar charts to display to the operator

import numpy as np
import matplotlib.pyplot as plt

class channelplot(object):

    """Plots the status of channels sent by the controller.
    Required args:
        channel_bank : should be a
    dictionary of the form {'channel_num' : uhf_channel}

    plot(status_data) : Called to initially plot the first data sent through.

    update(status_data) : Updates the plots with new status data about the
    provided channels."""
    

    def __init__(self, channel_bank):
        self.channel_list = self.__ordered(channel_bank)
        self.T_plot, self.B_plot = self.__datasort()
        print self.T_plot
        print self.B_plot
        #initialise global plotting placeholders for easy updating
        self.fig = None
        self.subT = None
        self.dataT = None
        self.subB = None
        self.dataB = None



    def __ordered(self, input_dict, want_data=False):
        
        """PRIVATE METHOD: Sorts dictionary keys that are sent to channelplot.
        Structured so that unordered dictionaries used for convenience handling
        of uhf channels 21 through 68 in the controller can be sorted into
        numerical order for data plotting. want_data flag used if dictionary
        data is required in order of channel number."""

        int_list = [int(x) for x in input_dict.keys()]
        int_list = sorted(int_list)
        if not want_data:
            return [str(x) for x in int_list]
        ordered_data = []
        for k in [str(x) for x in int_list]:
            ordered_data.append(input_dict[k])
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

        """Initially plots the status data passed in by the controller. If more
        than 20 points are present, two figures are plotted."""
        
        plt.ion()
        status_data = self.__ordered(input_data, True) #order status data
        T_pos = np.arange(len(self.T_plot))
        print T_pos
        print len(T_pos)
        T_sdata = np.array(status_data[:len(self.T_plot)])
        print T_sdata
        print len(T_pos)
        self.fig = plt.figure() #plot first figure
        self.subT = self.fig.add_subplot(211)
        self.dataT = self.subT.bar(T_pos, T_sdata)
        #subT.xticks(T_pos, self.T_plot)
        if self.B_plot:
            #if two sets have been created
            B_pos = np.arange(len(self.B_plot))
            B_sdata = np.array(status_data[len(self.T_plot):])
            self.subB = self.fig.add_subplot(212) #swith to second figure
            self.dataB = self.subB.bar(B_pos, B_sdata)
            #subB.xticks(B_pos, self.B_plot)
        self.fig.canvas.draw()

    def update(self, input_data):

        """Updates the status data for the plotted graphs."""

        status_data = self.__ordered(input_data, True) #order status data
        #clear the subplots and replot with updated data
        T_sdata = np.array(status_data[:len(self.T_plot)])
        for bar, h in zip(self.dataT, T_sdata):
            bar.set_height(h)
        #if two data sets, do for second subplot
        if self.B_plot:
            B_sdata = np.array(status_data[len(self.T_plot):])
            for bar, h in zip(self.dataB, B_sdata):
                bar.set_height(h)
        self.fig.canvas.draw()

if __name__ == '__main__':
    dummy_channel_bank = {}
    for i in range(1,40):
        dummy_channel_bank['{}'.format(i)] = 'dummy'
    plotter = channelplot(dummy_channel_bank)
    dummy_status_data = {}
    for i in range(1,40):
        dummy_status_data['{}'.format(i)] = (np.random.randint(0,2))
    plotter.plot(dummy_status_data)
    dummy_status_data_2 = {}
    for i in range(1,40):
        dummy_status_data_2['{}'.format(i)] = (np.random.randint(0,2))
    print 'Press enter to test update function.'
    resume = raw_input()
    plotter.update(dummy_status_data_2)


    

