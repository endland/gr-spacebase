#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the top level output GUI for the main controller
#The controller is called from this class via a child process
#and updated from the controller are piped through to the GUI

from Tkinter import *
import ScrolledText
from controller import controller
import os
import time
from optparse import OptionParser
import sensingTools.UHFenvironments as UHFenvironments




def run():
    """Top level run method which initiates program."""

    #build options parser for the gps flag
    parser = OptionParser()
    parser.add_option("-G", "--gps", type='int', dest="gps_flag", default=0,
                      help="toggle gps recording : 1 or 0")
    parser.add_option("-r", "--rawstore", type='int',  dest="raw_store", default=0,
                      help="store raw data from channel FFT bins : 1 or 0")
    parser.add_option("-A", "--antenna", type="string", default='RX2',
                      help="select Rx Antenna where appropriate : 'TX/RX' or"
                      "'RX2'")
    parser.add_option("-S", "--spstore", type="int", dest= "SPstore", default='0',
                      help="store signal properties in JSON format: 1 or 0")
    parser.add_option("-T", "--training", type="int", dest= "training_scan",
                      default='0',
                      help="set as training scan for data collection: 1 or 0")
    (options, args) = parser.parse_args()

    print options.gps_flag
    print options.raw_store
    print options.SPstore

    def enviroset():
        while True:
            enviro = raw_input('Choose scanning environment "D" (Durham), "M" \
    (MetroCentre) or "C" (Consett) : ')
            if enviro == 'D':
                options.environment = UHFenvironments.Durham()
                return
            if enviro == 'M':
                options.environment = UHFenvironments.MetroCentre()
                return
            if enviro == 'C':
                options.environment = UHFenvironments.Consett()
                return
            print "Invalid input. Enter 'D', 'M' or 'C'.\n"

    if options.training_scan:
        enviroset()
        
    def updateInput():
        """Update the textbox with controller output."""
        line = os.read(pipein, 100)
        print line
        text.insert(END, line)
        text.after(1000, updateInput)
        text.see(END)

    #if gps_flag, import gps module
    if options.gps_flag:
        try:
            import gps
        except:
            print 'gpsd package not installed, cannot run gps_recording.'
            raw_input('Press enter to continue without gps recording.')
            options.gps_flag = 0

    pipein, pipeout = os.pipe() #pipe for comms between tkinter and controller
    pid = os.fork()
    if not pid:
        #within child process, launch controller with passed pipe
        os.close(pipein)
        mainController = controller(options, pipeout,
                                    named_session=session_name)
    os.close(pipeout)

    root = Tk()
    root.wm_title('gr-spacebase UHF Scanner CONTROLLER OUTPUT CONSOLE')
    name_label = Label(root, text="Session Name : {} || Start Time :\
 {}".format(session_name, time.strftime('%X %x %Z')))
    name_label.pack(side = 'top')
    text = ScrolledText.ScrolledText(root)
    text.pack(side = 'bottom', expand=1)
    text.after(1000, updateInput) #update text box each second
    root.mainloop()

    #FIXME program giving XIO error. could require restart. try to fix.
    #FIXME also cannot enter text in entry widget, try to fix.


if __name__ == "__main__":
    print
    print 'Starting UHF Scanner'
    print
    print
    name_input = raw_input('Enter a session name or press enter to run a TEST \
SESSION : \n')
    session_name = 'TEST SESSION'
    if name_input:
        session_name = name_input

    run()
