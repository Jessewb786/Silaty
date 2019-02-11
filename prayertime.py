#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#       prayertime.py
#       
#       Copyright 2010 ahmed youssef <xmonader@gmail.com>
#       Copyright 2014 Jesse Brandao <www.jwb@gmail.com>
#       Copyright 2018 AXeL-dev      <anass_denna@hotmail.fr>
#       
#       This program is free software you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

__author__ = "Jesse Wayde Brandão (Abdul Hakim)"
__all__ = ['Calendar', 'Prayertime', 'Madhab', 'as_pytime', 'as_pydatetime']

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk, Gst, GObject, Gio, GLib, GdkPixbuf, Notify
from math import degrees, radians, atan, atan2, asin, acos, cos, sin, tan, fabs 
from datetime import date, timedelta
from time import strptime
from options import *
from translate import translate_text as _
import datetime
import time
import os

class Prayertime(object):

    def __init__(self):
        GLib.threads_init()
        Gst.init(None)

        self.options = Options()

        year  = datetime.datetime.now().year
        month = datetime.datetime.now().month
        day   = datetime.datetime.now().day
        self.date = date(year, month, day)

        self._shrouk = None
        self._fajr = None
        self._zuhr = None
        self._asr = None
        self._maghrib = None
        self._isha = None
        self._nextprayer = ""
        self._tnprayer = 0
        self.dec = 0

    def shrouk_time(self):
        """Gets the time of shrouk."""
        fmt = to_hrtime(self._shrouk)
        if "00" in fmt:
            fmt = fmt.replace('00','12')
        return fmt

    def fajr_time(self):
        """Gets the time of fajr."""
        fmt = to_hrtime(self._fajr)
        if "00" in fmt:
            fmt = fmt.replace('00','12')
        return fmt

    def zuhr_time(self):
        """Gets the time of zuhr."""
        fmt = to_hrtime(self._zuhr)
        if "00" in fmt:
            fmt = fmt.replace('00','12')
        return fmt

    def asr_time(self):
        """Gets the time of asr."""
        fmt = to_hrtime(self._asr)
        if "00" in fmt:
            fmt = fmt.replace('00','12')
        return fmt

    def maghrib_time(self):
        """Gets the time of maghrib"""
        fmt = to_hrtime(self._maghrib)
        if "00" in fmt:
            fmt = fmt.replace('00','12')
        return fmt

    def isha_time(self):
        """Gets the time of isha"""
        fmt = to_hrtime(self._isha)
        if "00" in fmt:
            fmt = fmt.replace('00','12')
        return fmt

    def next_prayer(self):
        return self._nextprayer

    def time_to_next_prayer(self):
        return self._tnprayer

    def calculate(self, notify_also = True):
        """Calculations of prayertimes."""
        year = self.date.year
        month = self.date.month
        day = self.date.day
        longitude = self.options.longitude
        latitude = self.options.latitude
        zone = self.options.timezone
        julian_day = (367*year)-int(((year+int((month+9)/12))*7)/4)+int(275*month/9)+day-730531.5
        sun_length = (280.461+0.9856474*julian_day)%360
        middle_sun = (357.528+0.9856003*julian_day)%360

        lamda = (sun_length+1.915*sin(radians(middle_sun))+0.02*sin(radians(2*middle_sun)))%360

        obliquity = 23.439-0.0000004*julian_day

        alpha = degrees(atan(cos(radians(obliquity))*tan(radians(lamda))))

        if 90 < lamda < 180:
            alpha += 180
        elif 179 < lamda < 360:
            alpha += 360

        ST = (100.46+0.985647352*julian_day)%360

        self.dec = degrees(asin(sin(radians(obliquity))*sin(radians(lamda))))

        noon = alpha-ST

        if noon < 0:
            noon += 360

        UTNoon = noon-longitude
        zuhr = (UTNoon/15)+zone                       # Zuhr Time.
        maghrib = zuhr+self._equation(-0.8333)/15     # Maghrib Time
        shrouk = zuhr-self._equation(-0.8333)/15      # Shrouk Time

        fajr_alt = 0
        isha_alt = 0

        if  self.options.calculation_method == Calendar.UmmAlQuraUniv:
            fajr_alt = -19
        elif self.options.calculation_method == Calendar.EgyptianGeneralAuthorityOfSurvey:
            fajr_alt = -19.5
            isha_alt = -17.5
        elif self.options.calculation_method == Calendar.MuslimWorldLeague:
            fajr_alt = -18
            isha_alt = -17
        elif self.options.calculation_method == Calendar.IslamicSocietyOfNorthAmerica:
            fajr_alt = isha_alt = -15
        elif self.options.calculation_method == Calendar.UnivOfIslamicSciencesKarachi:
            fajr_alt = isha_alt = -18

        fajr = zuhr-self._equation(fajr_alt)/15  # Fajr Time
        isha = zuhr+self._equation(isha_alt)/15  # Isha Time

        if self.options.calculation_method == Calendar.UmmAlQuraUniv :
            isha = maghrib+1.5

        asr_alt = 0

        if self.options.madhab == Madhab.Hanafi :
            asr_alt = 90 - degrees(atan(2+tan(radians(abs(latitude - self.dec)))))
        else:
            asr_alt = 90 - degrees(atan(1 + tan(radians(abs(latitude - self.dec)))))

        asr = zuhr+self._equation(asr_alt)/15  # Asr Time.

        # Add one hour to all times if the season is Summmer.
        if self.options.daylight_saving_time and is_dst() :
            fajr += 1
            shrouk += 1
            zuhr += 1
            asr += 1
            maghrib += 1
            isha += 1

        self._shrouk = shrouk
        self._fajr = fajr
        self._zuhr = zuhr
        self._asr = asr
        self._maghrib = maghrib
        self._isha = isha

        # Transform Times To DateTimes ,so We Can Make Calculations on it
        Fajr    = datetime.datetime.strptime(self.fajr_time(),"%I:%M:%S %p")
        Dhuhr   = datetime.datetime.strptime(self.zuhr_time(),"%I:%M:%S %p")
        Asr     = datetime.datetime.strptime(self.asr_time(),"%I:%M:%S %p")
        Maghrib = datetime.datetime.strptime(self.maghrib_time(),"%I:%M:%S %p")
        Isha    = datetime.datetime.strptime(self.isha_time(),"%I:%M:%S %p")

        # Assign Times to A List
        PrayerTimes = [Fajr, Dhuhr, Asr, Maghrib, Isha]
        Time = datetime.datetime.now()# Time Now
        Time = Time.replace(microsecond=0, year=1900, month=1, day=1)# Replace year,month and day to be the same on PrayerTimes

        NotifTime = Time+datetime.timedelta(minutes=self.options.notification_time)# Ten Minutes Before Next Prayer
        ClosestPrayer = self.closest(Time, PrayerTimes)# Get The Closest Prayer Time
        PrayerIndex = PrayerTimes.index(ClosestPrayer)# Get Index From List

        if PrayerIndex == 0:
            CurrentPrayer='Fajr'
            if Time < Fajr:
                PrevPrayer = 'Isha'
                NextPrayer = 'Fajr'
                NextPrayerDT = Fajr
            else:
                PrevPrayer = 'Fajr'
                NextPrayer = 'Dhuhr'
                NextPrayerDT = Dhuhr

        if PrayerIndex == 1:
            CurrentPrayer = 'Dhuhr'
            if Time < Dhuhr:
                PrevPrayer = 'Fajr'
                NextPrayer = 'Dhuhr'
                NextPrayerDT = Dhuhr
            else:
                PrevPrayer = 'Dhuhr'
                NextPrayer = 'Asr'
                NextPrayerDT = Asr

        elif PrayerIndex == 2:
            CurrentPrayer = 'Asr'
            if Time < Asr:
                PrevPrayer = 'Dhuhr'
                NextPrayer = 'Asr'
                NextPrayerDT = Asr
            else:
                PrevPrayer = 'Asr'
                NextPrayer = 'Maghrib'
                NextPrayerDT = Maghrib

        elif PrayerIndex == 3:
            CurrentPrayer = 'Maghrib'
            if Time < Maghrib:
                PrevPrayer = 'Asr'
                NextPrayer = 'Maghrib'
                NextPrayerDT = Maghrib
            else:
                PrevPrayer = 'Maghrib'
                NextPrayer = 'Isha'
                NextPrayerDT = Isha

        elif PrayerIndex == 4:
            CurrentPrayer = 'Isha'
            if Time < Isha:
                PrevPrayer = 'Maghrib'
                NextPrayer = 'Isha'
                NextPrayerDT = Isha
            else:
                PrevPrayer = 'Isha'
                NextPrayer = 'Fajr'
                NextPrayerDT = Fajr

        # Calculate Time to The Next Prayer
        TimeToNextPrayer = NextPrayerDT-Time
        if TimeToNextPrayer.total_seconds() < 0:
            # Add a day to fix the timining
            TimeToNextPrayer = TimeToNextPrayer + timedelta(days=1)

        self._nextprayer = NextPrayer
        self._tnprayer = TimeToNextPrayer

        # Notification
        if notify_also:
            for time in PrayerTimes:
                if time == NotifTime:
                    self.notify(_('Get Ready'), _('%s minutes left until the %s prayer.') % (str(int(self.options.notification_time)), _(NextPrayer)))
                elif time == Time:
                    self.notify(_('Prayer time for %s') % _(CurrentPrayer), _("It's time for the %s prayer.") % _(CurrentPrayer), self.options.audio_notifications, CurrentPrayer)

    def notify(self, title, message, play_audio = False, current_prayer = ''):
        Notify.init("Silaty")
        notif = Notify.Notification.new(title, message)
        icon = GdkPixbuf.Pixbuf.new_from_file(os.path.dirname(os.path.realpath(__file__)) + "/icons/hicolor/128x128/apps/silaty.svg")
        notif.set_icon_from_pixbuf(icon)

        if play_audio:
            if current_prayer == 'Fajr':
                uri = "file://" + os.path.dirname(os.path.realpath(__file__)) + "/audio/Fajr/" + self.options.fajr_adhan + ".ogg"
                self.fajrplayer = Gst.ElementFactory.make("playbin", "player")
                fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
                self.fajrplayer.set_property('uri', uri)
                self.fajrplayer.set_property("video-sink", fakesink)
                self.fajrplayer.set_state(Gst.State.PLAYING)
            else:
                uri = "file://" + os.path.dirname(os.path.realpath(__file__)) + "/audio/Normal/" + self.options.normal_adhan + ".ogg"
                self.normalplayer = Gst.ElementFactory.make("playbin", "player")
                fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
                self.normalplayer.set_property('uri', uri)
                self.normalplayer.set_property("video-sink", fakesink)
                self.normalplayer.set_state(Gst.State.PLAYING)

        notif.set_app_name('Silaty')
        notif.show()

    def closest(self, target, collection) :# Returns the closest Adhan
        return min((abs(target - i), i) for i in collection)[1]

    def _equation(self, alt):
        return degrees( acos( (sin(radians(alt)) - sin(radians(self.dec)) * sin(radians(self.options.latitude)))/(cos(radians(self.dec))*cos(radians(self.options.latitude)))))

    def report(self):
        """Simple report of all prayertimes."""
        print ('Fajr Time is    %s' % self.fajr_time())
        print ('Shrouk Time is  %s' % self.shrouk_time())
        print ('Zuhr  Time is   %s' % self.zuhr_time())
        print ('Asr Time is     %s' % self.asr_time())
        print ('Maghrib Time is %s' % self.maghrib_time())
        print ('Ishaa Time is   %s' % self.isha_time())

    def get_qibla(self):
        k_lat = radians(21.423333);
        k_lon = radians(39.823333);

        longitude = radians(self.options.longitude)
        latitude  = radians(self.options.latitude)

        numerator = sin(k_lon - longitude)
        denominator = (cos(latitude) * tan(k_lat)) - (sin(latitude) * cos(k_lon - longitude))

        q = atan2(numerator,denominator)
        q = degrees(q)
        if q < 0 : q += 360

        return q

    def qibla_distance(self):
        k_lat = radians(21.423333);
        k_lon = radians(39.823333);

        longitude = radians(self.options.longitude)
        latitude =  radians(self.options.latitude)

        r = 6378.7 # kilometers

        return acos(sin(k_lat) * sin(latitude) + cos(k_lat) * cos(latitude) * cos(longitude-k_lon)) * r

if __name__=="__main__":
    pt = Prayertime()
    print ("%s" % pt.get_qibla())
    print ("%s" % pt.qibla_distance())
    pt.calculate()
    pt.report()

def is_dst():
    # Find out whether or not daylight savings is in effect
    return bool(time.localtime().tm_isdst)

def fill_zeros(time):
    fill = lambda var: [var, '0'+var] [len(var) <2]
    return ':'.join(map(fill, time.split(':')))

def to_hrtime(var):
    """var: double -> human readable string of format "%I:%M:%S %p" """
    time = ''
    hours = int(var) # cast var (initially a double) as an int

    # If 12 <= hours < 24 or 24 <= hours < 36, it's afternoon, else morning
    #print ('%s' % hours)
    if (hours >= 12 and hours < 24) or (hours >= 24 and hours < 36):
        zone = "PM"
    else:
        zone = "AM"

    # This will give us the time from 0 to 12
    time += str(hours%12)
    time += ":"
    var -= hours

    # Get the minutes from the left over time
    minutes = int(var*60)
    time += str(abs(minutes))
    time += ":"
    var -= minutes/100

    # And get the seconds from what's left over of that
    sec = int(fabs(60*var))

    time += str(sec)
    time = fill_zeros(time)
    time += " "

    # Add the AM or PM
    time += zone

    #print ('%s' % time)
    return time

def as_pytime(string_to_parse, fmt="%I:%M:%SS %p"):
    """returns time.tm_struct by parsing string_to_parse."""
    return strptime(string_to_parse, fmt)

def as_pydatetime(d, ts):
    """returns a datetime object.
            d: date object
            ts: tm_struct
    """
    return datetime(year=d.year, month=d.month, day=d.day, \
                    hour=ts.tm_hour, minute=ts.tm_min, second=ts.tm_sec)