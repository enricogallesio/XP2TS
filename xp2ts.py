"""
	XP2TS Project
	Released under GPLv3 Licence or later. (see below)
	
	Author: Enrico Gallesio
	XP2TS Ver. 0.65 Beta released on 26 jun 2010
	http://xp2ts.sourceforge.net/
	
	--- Description:    
	XP2TS is a project aimed to allow voice automatic connection while
	flying online with X-Plane on IVAO network using a TeamSpeak client on linux.    
	Do not be surprised for poor quality/elegance/performance of this
	project, since this is my first coding experience and I'm an absolute
	beginner. Please let me know your feedback and ideas to make it better.
	
	Please read this file for more details and installation infos.
	
	--- GPL LICENCE NOTICE
	This file is part of XP2TS project

	XP2TS is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	XP2TS is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with XP2TS.  If not, see <http://www.gnu.org/licenses/>.
	---
	

"""

#import sys
#sys.setdefaultencoding('iso-8859-1')

### includes and modules
import subprocess       # needed for executing console commands
import re               # regular expressions to manage strings
import time             
import sys
import os
import os.path
import math             # needed to calculate geog. distances

### definitions
ts_path = ""
ts_usr = ""
ts_pwd = ""
ts_nick = ""
whazz_url = "http://nl1.www.ivao.aero/whazzup.txt" # TODO more URLs to be choosen randomly
com1_freq =0

### functions
def get_config():       # takes TS useful variables and fixes paths to call TS instance
	
	if not os.path.exists("./config.ini"):
		print "ERROR: I cannot find a config.ini in the current directory."
		print "Please follow README instructions to create a properly filled config.ini file."
		print "Crashing here"
		sys.exit()

	try:
		config = open("config.ini", "r")
	except: print "ERROR while opening config.ini file."
	
	global ts_prefix_complete,ts_login,ts_control_cmd
	try:
		str_usr = config.readline()     #read from config.ini
		str_pwd = config.readline()
		str_nick = config.readline()
		str_path = config.readline()
	except: print "ERROR while catching config.ini content"
	
	ts_usr = str_usr.strip()        #delete newline characters
	ts_pwd = str_pwd.strip()
	ts_nick = str_nick.strip()
	ts_path = str_path.strip()+"client_sdk/"    # I preferred to split TS paths for more customizable commands later
	ts_control_cmd = ts_path + "tsControl "                    
	ts_prefix_complete = ts_control_cmd + "CONNECT TeamSpeak://"
	ts_disconnect = ts_control_cmd + "DISCONNECT"
	ts_login = "?nickname=\""+ts_nick+"\"?loginname=\"" + ts_usr + "\"?password=\""+ ts_pwd + "\"?channel="
	return 0

def consolecmd(cmd,logfile,iomode):         #excute custom commands and logs output for debug if needed
	try:                                    #i/o modes: r,w,a,r+, default=r              
		#subprocess.Popen(cmd, shell=True, stdout=logfile, stderr=logfile)
		p=subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stout=p.stdout.read()
		filetolog = open(logfile, iomode)    
		filetolog.write(time.ctime()+ ": "+stout)
		return stout
	except:
		print "ERROR while executing command: "+ cmd
		return 0
	

def ts_disconnect():                        # used to disconnect from any TS server if needed
	global ts_control_cmd
	ts_disc_cmd = ts_control_cmd + " DISCONNECT"
	stout=consolecmd(ts_disc_cmd,"ts.log","a") #receives subprocess.PIPE stdout for checking cmd results
	if re.search("-1001", stout):
		print "ERROR: Teamspeak is not running. No changes done."
	else:
		print "Ok! DISCONNECTED"
	return 0

def freq_conn(ts_server,freq_chan,retry):   # connects TS to any server/freq.channel given
											# returns 0 if ok, 1 if a retry is needed
											# TODO exception detection
	
	global ts_prefix_complete,ts_login
	retry =0
	#try:
	ts_conn_cmd = ts_prefix_complete + ts_server + ts_login + freq_chan
	consolecmd(ts_conn_cmd,"ts.log","a") # pass command to console and log output
	print " "
	print "Connecting to " + ts_server + "...\n" #+ "with command: " + ts_conn_cmd   # debug
	time.sleep(3)
										# now let's check we're connected correctly
										
	ts_check_cmd = ts_control_cmd + " GET_USER_INFO" 
	p=subprocess.Popen(ts_check_cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stout=p.stdout.read()   #this gets standard output answer
	filetolog = open("ts.log", "a")    
	filetolog.write(time.ctime()+ ": "+stout)  #this is to log even connections
#    print stout
	if re.search(freq_chan, stout):
		print "OK! Connection should be established"
	elif re.search("NOT CONNECTED", stout):
		print stout+"Maybe we reconnected too fast. I'll wait 5 secs now before trying again..."
		time.sleep(5)
		return 1    
	elif re.search("-1001", stout):
		print "ERROR: Teamspeak appears to be quit. No changes done. Please tune unicom and run TS again!"  #TODO auto-select unicom?
		# sys.exit()
	else:
		print "WARNING: Must have failed somewhere, let's try again"
		retry=retry+1
		return retry
#except:
	#    print "ERROR passing console command to TS"
	return 0

def extract_atc(com1_freq):     #parses data got from internet and chooses the proper online ATC station
								#returns a tuple with all data to connect to the choosen online ATC
								#returns -1 if no (valid) online atc is found on the selected freq
	
	#definitions
	lat_xplane=0
	lon_xplane=0
	atc_on_freq = 0 #atc counter
	atc_list = []
	distances_list = []
	lower_distance = 0

	try:
		latlon_obj = open("./latlon.txt", "r")
	except: 
		print "WARNING: Location data file not found. This is normal for the first run"
		print "Creating a default location file, then waiting for changes from xplane."
		latlon_obj = open("latlon.txt", "w")    #now we create even latlon.txt to fix the first time launch
		latlon_obj.write("0\n0")
		latlon_obj = open("latlon.txt", "r")
	
	for line in latlon_obj:                     #TODO use latlong_readline() ----------!!!!
		if lat_xplane==0:lat_xplane=float(line)
		else: lon_xplane=float(line)
	
	print " "
	# debug # print "Your geographic position in X-Plane is lat: "+str(lat_xplane)+" lon: "+str(lon_xplane)
	
	try:
		whazzup = open("whazzup.txt", "r")
	except: 
		print "ERROR while opening whazzup.txt file. Is this file there?"
	#print ":"+com1_freq+":" #debug
	print "Now listing ATC found on the same freq (even .xx5 freqs are considered due to 25 KHz and 8.33Hz spacing):"
	
	for line in whazzup:                            #FOR cycle begin to parse whazzup lines
		if (re.search(":"+com1_freq+":", line) or re.search(":"+com1_freq2+":", line)):  #because of 8.33Hz bug
			
			# Parsing whazzup.txt per line using string slices
			
			icao_id = line[:line.find(":")]
			if re.search("OBS", icao_id):
				continue       #avoid observers, go to next for cycle
			
			trim1_left = line[line.find(":ATC:")+5:]
			freq = trim1_left[:trim1_left.find(":")]
			
			trim2_left = trim1_left[8:]
			lat = trim2_left[:trim2_left.find(":")]
			lat = float(lat) # we need float data to calculate distance. TODO trunk decimals
			
			trim3_left = trim2_left[trim2_left.find(":")+1:]
			lon = trim3_left[:trim3_left.find(":")]
			lon = float(lon) # we need float data to calculate distance. TODO trunk decimals
			
			trim4_left = line[line.find("::::::::::::::::")+16:]
			ts_serv = trim4_left[:trim4_left.find("/")]
			if re.search("No Voice", ts_serv):
				#print "ERROR No Voice station" TODO No Voice station selected? ------------!!!!!
				continue       #avoid no voice - continue to next for cycle
			
			#whazzup parsing done
			
			#now calculating distances
			
			distance = calculate_distance(lat_xplane,lon_xplane,lat,lon)    #computing stations distance
			distances_list.append(distance)             #creating distances list to use out of loop
			
			tuple_atc = icao_id,lat,lon,ts_serv,distance #create a new tuple with these atc data
			
			#Creating a list to display all valid online ATCs found on the selected freq.
			#and append to atc list for further use
			
			atc_list.append(tuple_atc)
			print str(atc_on_freq)+": \t"+icao_id + " \t" + freq + " \t" + str(lat) + " \t" + str(lon) + " \t\t" + ts_serv + "\t - Distance (nm): \t" + str(distance)
			atc_on_freq = atc_on_freq +1    #counting one more valid station with com1 freq
			#print atc_on_freq
			# end for cyce
			
	# Now deciding what online ATC is the nearest to return
	print " "
	if atc_on_freq != 0:
		lower_distance=min(distances_list)                      #gets the lower distances atc in the list
		nearest_station=distances_list.index(lower_distance)    #and tell us which nearest atc index number is
		print "The nearest valid station is: "+ atc_list[nearest_station][0]+", ("+ str(atc_list[nearest_station][4])+" nm)"
	else: 
		print "WARNING: No valid ATC found in whazzup" #TODO reload whzzup or manual connect?... ---------------- !
		return -1 # this means no atc found at all
	
	nearest_atc_tuple = atc_list[nearest_station][0], atc_list[nearest_station][3] #preparing ATC data to return
	
	return nearest_atc_tuple
		
def calculate_distance(lat1, lon1, lat2, lon2): #self explicative returns geographic distances
	#maths stuff
	deg_to_rad = math.pi/180.0
	phi1 = (90.0 - lat1)*deg_to_rad
	phi2 = (90.0 - lat2)*deg_to_rad
	theta1 = lon1*deg_to_rad
	theta2 = lon2*deg_to_rad
	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + math.cos(phi1)*math.cos(phi2))
	arc = math.acos( cos )
	distance = arc*3960 # nautical miles
	#distance = arc*6373 # if kilometers needed
	return distance

def getwhazzup():   # Connects to the internet and downloads the data file whazzup.txt from IVAO server only if needed
					# which means not more than once every 5 mins. 
					# TODO Add an option to force immediate download ----!!!!
					# TODO we should use another data file provided from IVAO and use a geo-loc ICAO codes list ----!!!!
	if not os.path.exists("./whazzup.txt"):  
		print "Downloading network data"
		os.system("wget -N "+whazz_url)
		if not os.path.exists("./whazzup.txt"):
			print "ERROR while downloading network data (whazzup.txt)"
			print "Please check your network. Crashing here"
			sys.exit()
	else:
		try:
			time_whazzup = os.path.getmtime("whazzup.txt")
			age_whazzup = time.time()-time_whazzup
			if age_whazzup > 300:  # 3000 is for debug 300 is ok
				#print age_whazzup
				os.remove("whazzup.txt")
				os.system("wget -N "+whazz_url)
				print "Yes, updated network data are needed. Downloading now..."
				time.sleep(5)
			else: 
				print "Old network data are too young do die. I'll keep the previous by now..."
				return 0
			print "OK we caught the data!"  # TODO check stout if the file is actually got  ---------!!!!!
		except:
			print "ERROR retrieving whazzup file from internet. Will try with older one if present."
	return 0;
pass

def scan_com1():    # scans com1.txt file and gets the X-Plane Com1 dataref obtained via XP2TS_plugin
	try:
		com1_obj = open("com1.txt", "r") 
		freq_str = com1_obj.readline()
		freq_str = freq_str.strip() #erase newline character
		freq_left = freq_str[:3]
		freq_right = freq_str[3:]+"0" # adds "0" because missing from dateref. 25KHz and 8.33KHz spacing are managed later
		freq = freq_left+"."+freq_right
	except: 
		print "WARNING: No Com1 data found. This is normal at the first run."
		print "We will pre-select UNICOM awating for changes from xplane"
		com1_obj = open("com1.txt", "w")
		com1_obj.write("12280\n")
		freq = "122.800"

	return freq

def activate_me():              # --script activation function--
								# gets com1_freq, IVAO data, online choosen ATC connection data,
								# launches TS connection and returns 0 if everything is ok
	global com1_freq, com1_freq2 # this last one is needed to manage 25KHz which is not supported by X-Plane datarefs.
	
	print "...ACTIVATING at: "+ time.ctime()
	print "New Com1 freq. received: "+com1_freq+ " (or "+com1_freq2+" due to 25KHz spacing) !"
	time.sleep(1)
	print "Now deciding if we have to get a new ivao data file..."
	getwhazzup()
	time.sleep(1)
	print " "
	print "Now finding the correct ATC channel for your freq and position..."
	ts_atc_data= extract_atc(com1_freq) #returns a tuple with 2 str with ts srver/channel data
	if ts_atc_data == -1:
		print "NO ATC FOUND, Disconnecting voice" # this can be changed if users prefer ivap behaviour commenting next line
		ts_disconnect()
	else:
		print "Ok nearest ATC found!"
		print " "
		print "Now let's go on TeamSpeak!!"
		if freq_conn(ts_atc_data[1],ts_atc_data[0],0) == 0: print "" # this is to control if we have to try again, max 3 chances
		elif freq_conn(ts_atc_data[1],ts_atc_data[0],0) < 3: freq_conn(ts_atc_data[1],ts_atc_data[0],1) # not yet got?
		else: print "Multiple TS connection errors, sorry." #TODO WTF why this doesn't work!? ------to be fixed ------!!!!
	return 0

### MAIN sequence
# TODO by now managed this way but a new funcion should be made for this

print " "
print "XP2TS for Linux ver. 0.65beta by Enrico Gallesio released under GPLv3 (attached) or later"
print " "
print "This scripts gets Com1 and geographic location from x-plane using the attached plugin and automatically connects to the proper teamspeak channel while flying online on the IVAO network"
print "Make sure you have followed installation and configuration instructions placed in the README file."
print "Remember: 1st run Teamspeak and keep it opened, 2nd run this script, 3rd run xplane."
print "If you're happy with this software then, please, let me know! Whistles, comments, bugs reports and features requests must be sent to:"
print "http://xp2ts.sourceforge.net in the Support area. Thank you very much in advance"
print " "
os.chdir(sys.path[0]) #change CWD to script directory
time.sleep(1)
a = raw_input("Press ENTER to continue")
print " "

com1_old = 0
#let's go

get_config()    #this gets alla datas from configure.ini and fixes all paths to call TS. Done just 1 time

while(1):                               #infinite cycle TODO add options while looping

	time.sleep(2) #to not overload cpu, cycles only once every 2 secs
	com1_freq = scan_com1() #returns string frequency in format xxx.xxx (25KHz / 8.33KHz not compliance)
	com1_freq2 = com1_freq[:6]+"5" #workaround needed to manage 25KHz spacing.
	
	if com1_old != com1_freq:           # TODO UNICOM and GUARD freqs should be managed somewhere else
		print time.ctime()
		if com1_freq == "122.800":
			print "UNICOM Selected, disconnecting voice" # if you prefer IVAP behaviour comment next line
			ts_disconnect()
		elif com1_freq == "121.500": 
			print "GUARD Freq. selected. No voice changes" #no changes if GUARD selected
		else: activate_me()
		print " "
		print "Waiting for a new COM1 frequency... (press CTRL+C to quit)"
		print "..."
	com1_old = com1_freq
