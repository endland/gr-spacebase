#Class that reads from channel_list.txt in this director to read all channel
#numbers and frequencies into an internal dict. Methods to call channel
#frequency details include as well as an iterative return next channel
import pprint

class uhfchanlist:
    """class uhfchanlist: Returns channel frequencies upon request.
    Frequencies stored in form dict(chan no.) = [centrefreq, visfreq, soundfreq]
    chan_freq(chan no.) return a specific array of frequencies
    full_list() returns the complete dict of channels and frequencies."""
    def __init__(self):
       self.chanlist = self.get_channels()
       pprint.pprint(self.chanlist)

    def get_channels(self):
        """Returns a dict of the form dict(chan no.) = [centrefreq, visfreq,
        soundfreq]."""
        chanlist = {}
        with open('channel_list.txt') as clist:
            for line in clist:
                cnum, visf, soundf, centref = line.split()#values in MHz
                chanlist[cnum] = [float(centref*1000000), float(visf*1000000),
                                  float(soundf*1000000)]#convert to Hz to avoid
                #having to import engineering notation modules
        return chanlist

    def chan_freq(self, chan):
        """Returns an array of the form [centrefrew, visfreq, soundfreq]."""
        chan = str(chan)
        return self.chanlist[chan]

    def full_list(self):
        """Returns full channel list."""
        return self.chanlist


if __name__ == "__main__":
    x = uhfchanlist()
    x.full_list()
    print x.__doc__
