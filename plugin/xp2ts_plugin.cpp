/* 
	XP2TS Project
	Released under GPLv3 Licence or later. (see below)
    
    Author: Enrico Gallesio
    XP2TS Plugin Ver. 0.5 Beta released on 24 Apr 2010
    
    --- Description:    
    XP2TS is a project aimed to allow voice automatic connection while
    flying online with X-Plane on IVAO network using a TeamSpeak client.
    
    Please do not be surprised for poor quality/elegance/performance of this
    project, since this is my first coding experience and I'm an absolute
    beginner. Please let me know your feedback and ideas to make it better.
    
    Please read README file for more details and installation info.
    For support or contacts pls refer to: http://xp2ts.sourceforge.net/

    
    --- GPL LICENCE NOTICE ---
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
 */

#include <stdio.h>
#include <string.h>
#include <iostream>
#include <fstream>
#include "XPLMDataAccess.h"
#include "XPLMProcessing.h"

using namespace std;

/*
 * glob vars
 * 
 */

static int				newfreq;
static int				oldfreq;
 
static XPLMDataRef		xDataRef = NULL;

/* Datarefs */
XPLMDataRef		xPlaneLat;
XPLMDataRef		xPlaneLon;
	

float	loopcallback(
                                   float                elapsedcall,    
                                   float                elapsedloop,    
                                   int                  counterin,    
                                   void *               refconin);

/*
 * XPluginStart
 */
PLUGIN_API int XPluginStart(
						char *		name,
						char *		sig,
						char *		desc)
{

	strcpy(name, "XP2TS");
	strcpy(sig, "xplanesdk.xp2ts");
	strcpy(desc, "The plugin-side of XP2TS project");


	xDataRef = XPLMFindDataRef("sim/cockpit/radios/com1_freq_hz");
	xPlaneLat = XPLMFindDataRef("sim/flightmodel/position/latitude");
	xPlaneLon = XPLMFindDataRef("sim/flightmodel/position/longitude");

	
	XPLMRegisterFlightLoopCallback(		
			loopcallback,	/* callback */
			1.0,		/* interval */
			NULL);		/* refcon is not used. */
			

 
	return 1;

}

/*
 * XPluginStop
 */
PLUGIN_API void	XPluginStop(void)
{
}

/*
 * XPluginDisable
 */
PLUGIN_API void XPluginDisable(void)
{
}

/*
 * XPluginEnable.
 */
PLUGIN_API int XPluginEnable(void)
{
	return 1;
}

/*
 * XPluginReceiveMessage
 */
PLUGIN_API void XPluginReceiveMessage(
					XPLMPluginID	in_fromwho,
					long			in_message,
					void *			in_param)
{
}

/*
 * callback in loop
 * 
 */

float	loopcallback(
                                   float                elapsedcall,    
                                   float                elapsedloop,    
                                   int                  counterin,    
                                   void *               refconin)
{
/* debug
cout << "oldfreq = " << oldfreq;
cout << "newfreq = " << newfreq;
*/
newfreq = XPLMGetDatai(xDataRef);
	if (oldfreq != newfreq)
	{
		ofstream SaveFile1("com1.txt");
		SaveFile1 << newfreq;
		SaveFile1.close();
		/*cout << "New com1 freq. selected: " << newfreq << " while old was: " << oldfreq << endl; */
		oldfreq = newfreq;

		xPlaneLat = XPLMFindDataRef("sim/flightmodel/position/latitude");
		xPlaneLon = XPLMFindDataRef("sim/flightmodel/position/longitude");
		float	lat = XPLMGetDataf(xPlaneLat);
		float	lon = XPLMGetDataf(xPlaneLon);
		
		ofstream SaveFile2("latlon.txt");
		SaveFile2 << lat << endl << lon;
		SaveFile2.close();
		/* cout << "Lat: " << lat << " Long: " << lon << endl;  */
		
	

	}
	else
	{
	/* cout << "check"; debug */
	}
return 1.0;	

}  

	


                 
