#gr-spacebase - UHF Band Spectrum Sensing for vehicular communications
##Software radio approach to cataloguing TV white space for enabling vehicular communications.

____

PREQUISITES: 

Python 2.7
GNU Radio : https://wiki.gnuradio.org/index.php/InstallingGR

Optional:

gpsd : http://www.catb.org/gpsd/installation.html (for GPS logging)

____

This project will be updated over the coming weeks as the modules are built.

Current testing rig is an Ettus Research N210 with WBX daughterboard.

Project Aim : Test different spectrum sensing techinques for UHF channel white space detection  whilst the sensing equipment is travelling in a vehicle at speed.

Data Output Info:

json files of each scan pass as well as the corresponding plotted bar charts can be found in the data folder, contained in files which are named after the specified session name.

If no session name is provided on start up, a 'TEST SESSION' will run and no data will be saved.

Antenna Info:

Please attached your antenna to the RX2 port. Currently this port is hardcoded in however there is scope to add an antenna choice (either TX/RX or RX2) in the near future.
