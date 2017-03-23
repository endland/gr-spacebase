#gr-spacebase project github.com/wirrell/gr-spacebase
#This file contains the top level output GUI for the main controller
#The controller is called from this class via a child process
#and updated from the controller are piped through to the GUI

from Tkinter import *
from controller import controller
import os




def run():
    """Top level run method which initiates program."""

    def updateInput():
        """Update the textbox with controller output."""
        print 'in update input'
        line = os.read(pipein, 100)
        print line
        text.insert(END, line)
        text.after(1000, updateInput)


    pipein, pipeout = os.pipe() #pipe for comms between tkinter and controller
    pid = os.fork()
    if not pid:
        #within child process, launch controller with passed pipe
        os.close(pipein)
        mainController = controller(pipeout)
    os.close(pipeout)
    root = Tk()
    text = Text(root)
    text.pack()
    text.after(1000, updateInput) #update text box each second
    root.mainloop()



if __name__ == "__main__":
    run()
