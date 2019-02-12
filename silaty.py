# Silaty
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gst', '1.0')
from gi.repository import Gtk, Gst, Gio, GLib, Gdk, GdkPixbuf
from qiblacompass import *
from settingspane import *
from prayertime import *
from silatycal import *
from sidebar import *
from home import *
from location import *
from translate import set_language, translate_text as _
import urllib.request
import datetime
import time
import json
import sys
import os

class Silaty(Gtk.Window):

    def __init__(self, parent):
        Gtk.Window.__init__(self)
        GLib.threads_init()
        Gst.init(None)

        # Set parent widget
        self.parent = parent
        self.lock_location_updates = False

        # Init dialog
        self.dialog = None

        # Tweak window
        self.set_decorated(True)
        self.set_icon_name('silaty')
        self.set_modal(True)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('delete-event', self.hide_window)
        #self.set_default_size(429, 440)
        self.headerbar = Gtk.HeaderBar()

        # Set up mainbox
        self.mainbox = Gtk.Box()
        self.mainbox.set_orientation(Gtk.Orientation.HORIZONTAL)

        self.prayertimes = Prayertime()
        self.prayertimes.calculate()
        #self.prayertimes.notify('Title', 'This is a test.')

        # Set language
        set_language(self.prayertimes.options.language)
        if self.prayertimes.options.language == 'Arabic':
            #self.set_gravity(Gdk.Gravity.NORTH_EAST)
            #self.set_direction(Gtk.TextDirection.RTL)
            Gtk.Widget.set_default_direction(Gtk.TextDirection.RTL)

        # Set layout
        self.set_layout()

        if self.prayertimes.options.start_minimized == False:
            self.show_all()
            self.sidebar.emit("window-shown")

    def set_layout(self):
        # Set up Titlebar
        self.headerbar.set_show_close_button(True)
        self.set_titlebar(self.headerbar)

        # Set up the Stack
        stack = Gtk.Stack()
        stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        stack.set_transition_duration(300)
        stack.set_homogeneous(False)

        # Set up sidebar and give it the stack to manage
        self.sidebar = SideBar(stack)

        # Set up the home pane
        self.set_home()

        # Set up the qibla pane
        compdirection = self.prayertimes.get_qibla()
        country = self.prayertimes.options.country
        city = self.prayertimes.options.city
        self.qiblacompass = QiblaCompass(compdirection, country, city)
        self.sidebar.add_to_stack(self.qiblacompass, 'qibla')

        # Set up calendar panel
        self.calendar = SilatyCal()
        self.sidebar.add_to_stack(self.calendar, "calendar")

        # Set up the options pane
        self.set_options()

        # Set up the sidebar buttons
        self.set_sidebar_buttons()

        # Add the stack and menu to the list
        self.mainbox.set_size_request(429, 200)
        self.mainbox.pack_start(self.sidebar, False, True, 0)
        self.mainbox.pack_start(self.sidebar.stack, True, True, 0)

        self.add(self.mainbox)

    def set_home(self):
        ## Home - Prayers
        self.homebox = Home(self)

        nextprayer = self.prayertimes.next_prayer()
        if nextprayer == 'Fajr':
            self.homebox.add_prayer(_('Fajr'), self.get_times(self.prayertimes.fajr_time()), True)
        else:
            self.homebox.add_prayer(_('Fajr'), self.get_times(self.prayertimes.fajr_time()), False)

        self.homebox.add_prayer(_('Shuruk'), self.get_times(self.prayertimes.shrouk_time()), False)

        if nextprayer == 'Dhuhr':
            self.homebox.add_prayer(_('Dhuhr'), self.get_times(self.prayertimes.zuhr_time()), True)
        else:
            self.homebox.add_prayer(_('Dhuhr'), self.get_times(self.prayertimes.zuhr_time()), False)

        if nextprayer == 'Asr':
            self.homebox.add_prayer(_('Asr'), self.get_times(self.prayertimes.asr_time()), True)
        else:
            self.homebox.add_prayer(_('Asr'), self.get_times(self.prayertimes.asr_time()), False)

        if nextprayer == 'Maghrib':
            self.homebox.add_prayer(_('Maghrib'), self.get_times(self.prayertimes.maghrib_time()), True)
        else:
            self.homebox.add_prayer(_('Maghrib'), self.get_times(self.prayertimes.maghrib_time()), False)

        if nextprayer == 'Isha':
            self.homebox.add_prayer(_('Isha'), self.get_times(self.prayertimes.isha_time()), True)
        else:
            self.homebox.add_prayer(_('Isha'), self.get_times(self.prayertimes.isha_time()), False)

        self.sidebar.add_to_stack(self.homebox, 'home')
        self.sidebar.connect('stack-changed', self.on_stack_changed)

    def on_stack_changed(self, widget, visiblechild):
        print ("DEBUG: stack changed @", (visiblechild))
        if visiblechild == 'home':
            self.homebox.set_title()

    def set_options(self):
        ## Options
        settings = SettingsPane()

        settings.add_category(_("System"))

        # Start minimized
        startmin     = self.prayertimes.options.start_minimized
        smlabel      = Gtk.Label(_('Start Minimized:'))
        self.smvalue = Gtk.Switch(halign=Gtk.Align.START)
        self.smvalue.set_active(startmin)
        self.smvalue.connect('button-press-event', self.on_entered_start_minimized)
        settings.add_setting(self.smvalue, smlabel)

        # Daylight saving time
        defaultdst    = self.prayertimes.options.daylight_saving_time
        dstlabel      = Gtk.Label(_('Daylight Saving Time:'))
        self.dstvalue = Gtk.Switch(halign=Gtk.Align.START)
        self.dstvalue.set_active(defaultdst)
        self.dstvalue.connect('button-press-event', self.on_entered_daylight_saving_time)
        settings.add_setting(self.dstvalue, dstlabel)

        # Clock Format
        defaultcf   = self.prayertimes.options.clock_format
        cflabel     = Gtk.Label(_('Clock Format:'))
        self.cfmenu = Gtk.ComboBoxText(halign=Gtk.Align.FILL)
        self.clockformats = self.prayertimes.options.get_clock_formats()
        for cf in self.clockformats:
            self.cfmenu.append(cf, _(cf))
        self.cfmenu.set_active(self.clockformats.index(defaultcf))
        self.cfmenu.connect("changed", self.on_entered_clock_format)
        settings.add_setting(self.cfmenu, cflabel)

        # Adjust Hijri Calendar
        defaultvalue = self.prayertimes.options.hijrical_adjustment
        hijrilabel   = Gtk.Label(_('Adjust Hijri Calendar:'), halign=Gtk.Align.START)
        hijriadj     = Gtk.Adjustment(value=0, lower=-1, upper=1, step_incr=1, page_incr=1, page_size=0)
        self.hijrivalue = Gtk.SpinButton(adjustment=hijriadj, halign=Gtk.Align.FILL)
        self.hijrivalue.set_value(float(defaultvalue))
        self.hijrivalue.connect("value-changed",self.on_entered_hijrical_adjustment)
        settings.add_setting(self.hijrivalue, hijrilabel)

        # Language
        defaultlang   = self.prayertimes.options.language
        langlabel     = Gtk.Label(_('Language:'))
        self.langmenu = Gtk.ComboBoxText(halign=Gtk.Align.FILL)
        self.langlist = self.prayertimes.options.get_languages()
        for lang in self.langlist:
            self.langmenu.append(lang, _(lang))
        self.langmenu.set_active(self.langlist.index(defaultlang))
        self.langmenu.connect("changed", self.on_entered_language)
        settings.add_setting(self.langmenu, langlabel)

        settings.add_category(_("Notifications"))

        # Show Icon with label
        showstat     = self.prayertimes.options.iconlabel
        silabel      = Gtk.Label(_('Show Time left with Icon:'))
        self.sivalue = Gtk.Switch(halign=Gtk.Align.START)
        self.sivalue.set_active(showstat)
        self.sivalue.connect('button-press-event', self.on_entered_iconlabel)
        settings.add_setting(self.sivalue, silabel)

        # Enable Audio
        enableaudio     = self.prayertimes.options.audio_notifications
        audiolabel      = Gtk.Label(_('Enable audio notifications:'))
        self.audiovalue = Gtk.Switch(halign=Gtk.Align.START)
        self.audiovalue.set_active(enableaudio)
        self.audiovalue.connect('button-press-event', self.on_entered_audio_notifications)
        settings.add_setting(self.audiovalue, audiolabel)

        # Notification Time
        defaultvalue = self.prayertimes.options.notification_time
        ntlabel      = Gtk.Label(_('Time before notification:'), halign=Gtk.Align.START)
        notifadj     = Gtk.Adjustment(value=0, lower=5, upper=60, step_incr=1, page_incr=1, page_size=0)
        self.ntvalue = Gtk.SpinButton(adjustment=notifadj, halign=Gtk.Align.FILL)
        self.ntvalue.set_value(float(defaultvalue))
        self.ntvalue.connect("value-changed",self.on_entered_notification_time)
        settings.add_setting(self.ntvalue, ntlabel)

        # Adhan choices
        adhanbox      = Gtk.Box(halign=Gtk.Align.FILL, spacing=3)
        self.fajradhanplay = Gtk.Button.new_from_icon_name("media-playback-start", Gtk.IconSize.BUTTON)
        self.fajradhanplay.set_relief(Gtk.ReliefStyle.HALF)
        self.fajradhanplay.connect("button-press-event", self.on_fajr_play_pressed)
        adhanbox.pack_start(self.fajradhanplay, False, False, 0)

        defaultadhan   = self.prayertimes.options.fajr_adhan
        adhans         = self.prayertimes.options.get_fajr_adhans()
        fajrlabel      = Gtk.Label(_('Fajr Adhan:'), halign=Gtk.Align.START)
        self.fajradhan = Gtk.ComboBoxText(halign=Gtk.Align.FILL)
        for adhan in adhans:
            self.fajradhan.append(adhan, adhan)
        active_text = adhans.index(defaultadhan)
        self.fajradhan.set_active(active_text)
        self.fajradhan.connect("changed", self.on_entered_fajr_adhan)
        adhanbox.pack_start(self.fajradhan, True, True, 0)
        self.fajrplaying = False;

        settings.add_setting(adhanbox, fajrlabel)

        adhanbox = Gtk.Box(halign=Gtk.Align.FILL, spacing=3)
        self.normaladhanplay = Gtk.Button.new_from_icon_name("media-playback-start",  Gtk.IconSize.BUTTON)
        self.normaladhanplay.set_relief(Gtk.ReliefStyle.HALF)
        self.normaladhanplay.connect("button-press-event", self.on_normal_play_pressed)
        adhanbox.pack_start(self.normaladhanplay, False, False, 0)

        defaultadhan     = self.prayertimes.options.normal_adhan
        adhans           = self.prayertimes.options.get_normal_adhans()
        normallabel      = Gtk.Label(_('Normal Adhan:'), halign=Gtk.Align.START)
        self.normaladhan = Gtk.ComboBoxText(halign=Gtk.Align.FILL)
        for adhan in adhans:
            self.normaladhan.append(adhan, adhan)
        active_text = adhans.index(defaultadhan)
        self.normaladhan.set_active(active_text)
        self.normaladhan.connect("changed", self.on_entered_normal_adhan)
        adhanbox.pack_start(self.normaladhan, True, True, 0)
        self.normalplaying = False;

        settings.add_setting(adhanbox, normallabel)

        settings.add_category(_("Jurisprudence"))

        # Calculation Method
        defaultmethod    = self.prayertimes.options.calculation_method_name
        self.methods     = self.prayertimes.options.get_cal_methods()
        calmethodlabel   = Gtk.Label(_('Calculation Method:'), halign=Gtk.Align.START)
        self.methodsmenu = Gtk.ComboBoxText(halign=Gtk.Align.FILL)
        for method in self.methods:
            self.methodsmenu.append(method, _(method))
        active_text      = self.methods.index(defaultmethod)
        self.methodsmenu.set_active(active_text)
        self.methodsmenu.connect("changed", self.on_entered_calculation_method_name)
        settings.add_setting(self.methodsmenu, calmethodlabel)

        # Madhab
        defaultmadhab    = self.prayertimes.options.madhab_name
        self.madaheb     = self.prayertimes.options.get_madhahed()
        madhablabel      = Gtk.Label(_('Madhab:'), halign=Gtk.Align.START)
        self.madahebmenu = Gtk.ComboBoxText(halign=Gtk.Align.FILL)
        for madhab in self.madaheb:
            self.madahebmenu.append(madhab, _(madhab))
        self.madahebmenu.set_active(self.madaheb.index(defaultmadhab))
        self.madahebmenu.connect("changed", self.on_entered_madhab_name)
        settings.add_setting(self.madahebmenu, madhablabel)

        settings.add_category(_("Location"))

        # City name
        citybox        = Gtk.Box(halign=Gtk.Align.FILL, spacing=3)
        defaultcity    = self.prayertimes.options.city
        defaultcountry = self.prayertimes.options.country
        citylabel      = Gtk.Label(_('City:'), halign=Gtk.Align.START)
        self.cityentry = Gtk.Entry(halign=Gtk.Align.FILL)
        self.cityentry.set_text('%s' % defaultcity)
        #self.cityentry.connect("activate", self.on_entered_city_activate)
        self.cityentry.connect("focus-out-event", self.on_entered_city_focus_out)
        citybox.pack_start(self.cityentry, True, True, 0)

        self.citysearch = Gtk.Button.new_from_icon_name("system-search-symbolic", Gtk.IconSize.BUTTON)
        self.citysearch.set_relief(Gtk.ReliefStyle.HALF)
        self.citysearch.connect("button-press-event", self.on_city_search_pressed)
        citybox.pack_start(self.citysearch, False, False, 0)

        settings.add_setting(citybox, citylabel)

        # Latitude
        defaultlatitude = self.prayertimes.options.latitude
        latlabel        = Gtk.Label(_('Latitude:'), halign=Gtk.Align.START)
        latadj          = Gtk.Adjustment(value=0, lower=-90, upper=90, step_incr=0.01, page_incr=1, page_size=1)
        self.latentry   = Gtk.SpinButton(adjustment=latadj, digits=3, halign=Gtk.Align.FILL)
        self.latentry.set_value(float(defaultlatitude))
        self.latentry.connect("value-changed", self.on_entered_latitude)
        settings.add_setting(self.latentry, latlabel)

        # Longitude
        defaultlong    = self.prayertimes.options.longitude
        longlabel      = Gtk.Label(_("Longitude:"), halign=Gtk.Align.START)
        lngadj         = Gtk.Adjustment(value=0, lower=-180, upper=180, step_incr=0.01, page_incr=1, page_size=1)
        self.longentry = Gtk.SpinButton(adjustment=lngadj, digits=3, halign=Gtk.Align.FILL)
        self.longentry.set_value(float(defaultlong))
        self.longentry.connect("value-changed", self.on_entered_longitude)
        settings.add_setting(self.longentry, longlabel)

        # Time zone
        defaulttz    = self.prayertimes.options.timezone
        tzlabel      = Gtk.Label(_("Time Zone:"), halign=Gtk.Align.START)
        tzadj        = Gtk.Adjustment(value=0, lower=-12, upper=14, step_incr=1, page_incr=1, page_size=1)
        self.tzentry = Gtk.SpinButton(adjustment=tzadj, digits=1, halign=Gtk.Align.FILL)
        self.tzentry.set_value(float(defaulttz))
        self.tzentry.connect("value-changed", self.on_entered_timezone)
        settings.add_setting(self.tzentry, tzlabel)

        # Add settings to the Stack
        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_min_content_height(420)
        scrolledwindow.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.add_with_viewport(settings)
        scrolledwindow.set_kinetic_scrolling(True)
        self.sidebar.add_to_stack(scrolledwindow, 'options')

    def set_sidebar_buttons(self):
        # Set up the home icon
        act_icon   =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/homeA.svg"
        inact_icon =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/homeN.svg"
        self.sidebar.new_button(inact_icon, act_icon)

        # Set up the qibla icon
        act_icon   =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/qiblaA.svg"
        inact_icon =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/qiblaN.svg"
        self.sidebar.new_button(inact_icon, act_icon)

        # Set up the calendar icon
        act_icon   =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/calendarA.svg"
        inact_icon =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/calendarN.svg"
        self.sidebar.new_button(inact_icon, act_icon)

        # Set up the settings icon
        act_icon   =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/settingsA.svg"
        inact_icon =  os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/settingsN.svg"
        self.sidebar.new_button(inact_icon, act_icon)

        # Set up the about icon
        act_icon   = os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/aboutA.svg"
        inact_icon = os.path.dirname(os.path.realpath(__file__)) + "/icons/sidebar/aboutN.svg"
        self.sidebar.new_button(inact_icon, act_icon, self.parent.about_dialog)

    def on_city_search_pressed(self, widget, event):
        if self.dialog is None:
            self.dialog = LocationDialog(self)
            self.dialog.run()
        else:
            self.dialog.show()

    def on_entered_audio_notifications(self, widget, event):
        self.prayertimes.options.audio_notifications = (not widget.get_active())

    def on_entered_fajr_adhan(self, widget):
        self.prayertimes.options.fajr_adhan = widget.get_active_text()

    def on_fajr_play_pressed(self, widget, event):
        if self.fajrplaying == False:
            uri = "file://"+ os.path.dirname(os.path.realpath(__file__))+"/audio/Fajr/"+self.fajradhan.get_active_text()+".ogg"
            self.fajrplayer = Gst.ElementFactory.make("playbin", "player")
            fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
            bus = self.fajrplayer.get_bus()
            bus.add_signal_watch()
            bus.connect('message', self.on_fajr_adhan_termination)
            self.fajrplayer.set_property('uri', uri)
            self.fajrplayer.set_property("video-sink", fakesink)
            self.fajrplayer.set_state(Gst.State.PLAYING)

            self.fajradhanplay.set_image(Gtk.Image.new_from_icon_name("media-playback-pause",  Gtk.IconSize.BUTTON))
            self.fajrplaying = True     
        else:
            self.fajrplayer.set_state(Gst.State.NULL)
            self.fajradhanplay.set_image(Gtk.Image.new_from_icon_name("media-playback-start",  Gtk.IconSize.BUTTON))
            self.fajrplaying = False

    def on_entered_normal_adhan(self, widget):
        self.prayertimes.options.normal_adhan = widget.get_active_text()

    def on_normal_play_pressed(self, widget, event):
        if self.normalplaying == False:
            uri = "file://"+ os.path.dirname(os.path.realpath(__file__))+"/audio/Normal/"+self.normaladhan.get_active_text()+".ogg"
            self.normalplayer = Gst.ElementFactory.make("playbin", "player")
            fakesink = Gst.ElementFactory.make("fakesink", "fakesink")
            bus = self.normalplayer.get_bus()
            bus.add_signal_watch()
            bus.connect('message', self.on_normal_adhan_termination)
            self.normalplayer.set_property('uri', uri)
            self.normalplayer.set_property("video-sink", fakesink)
            self.normalplayer.set_state(Gst.State.PLAYING)
            self.normaladhanplay.set_image(Gtk.Image.new_from_icon_name("media-playback-pause",  Gtk.IconSize.BUTTON))
            self.normalplaying = True
        else:
            self.normalplayer.set_state(Gst.State.NULL)
            self.normaladhanplay.set_image(Gtk.Image.new_from_icon_name("media-playback-start",  Gtk.IconSize.BUTTON))
            self.normalplaying = False

    def on_normal_adhan_termination(self, bus, message): 
        t = message.type
        if t == Gst.MessageType.EOS: # track is finished
            self.normalplayer.set_state(Gst.State.NULL)
            self.normaladhanplay.set_image(Gtk.Image.new_from_icon_name("media-playback-start",  Gtk.IconSize.BUTTON))
            self.normalplaying = False
        elif t == Gst.MessageType.ERROR:
            self.normalplayer.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)

    def on_fajr_adhan_termination(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS: # track is finished
            self.fajrplayer.set_state(Gst.State.NULL)
            self.fajradhanplay.set_image(Gtk.Image.new_from_icon_name("media-playback-start",  Gtk.IconSize.BUTTON))
            self.fajrplaying = False
        elif t == Gst.MessageType.ERROR:
            self.normalplayer.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print ("Error: %s" % err, debug)

    def on_entered_iconlabel(self, widget, event):
        self.prayertimes.options.iconlabel = (not widget.get_active())

    def on_entered_start_minimized(self, widget, event):
        self.prayertimes.options.start_minimized = (not widget.get_active())

    def on_entered_daylight_saving_time(self, widget, event):
        self.prayertimes.options.daylight_saving_time = (not widget.get_active())
        self.update_prayers()

    def update_location(self):
        self.update_prayers()
        self.update_qibla()

    def on_entered_latitude(self, widget):
        self.prayertimes.options.latitude = widget.get_value()
        if not self.lock_location_updates:
            self.update_location()

    def on_entered_longitude(self, widget):
        self.prayertimes.options.longitude = widget.get_value()
        if not self.lock_location_updates:
            self.update_location()

    def on_entered_timezone(self, widget):
        self.prayertimes.options.timezone = widget.get_value()
        if not self.lock_location_updates:
            self.update_prayers()

    def on_entered_notification_time(self, widget):
        self.prayertimes.options.notification_time = widget.get_value()

    def on_entered_hijrical_adjustment(self, widget):
        self.prayertimes.options.hijrical_adjustment = widget.get_value()
        self.calendar.cal.hijrical.adjustment = widget.get_value()
        self.calendar.cal.refresh()

    def on_entered_clock_format(self, widget):
        index = widget.get_active()
        self.prayertimes.options.clock_format = self.clockformats[index]
        self.update_prayers(False)

    def on_entered_language(self, widget):
        index = widget.get_active()
        self.prayertimes.options.language = self.langlist[index]
        # Show our message dialog
        dialog = Gtk.MessageDialog(text=_('Silaty needs to be restarted, restart now?'), transient_for=self, buttons=Gtk.ButtonsType.OK_CANCEL, message_type=Gtk.MessageType.QUESTION)
        response = dialog.run()
        dialog.destroy()
        # We only restart when the user presses the OK button
        if response == Gtk.ResponseType.OK:
            self.prayertimes.options.save_options()
            os.execl(sys.executable, sys.executable, *sys.argv)

    def on_entered_calculation_method_name(self, widget):
        index = widget.get_active()
        self.prayertimes.options.calculation_method_name = self.methods[index]
        self.update_prayers()

    def on_entered_madhab_name(self, widget):
        index = widget.get_active()
        self.prayertimes.options.madhab_name = self.madaheb[index]
        self.update_prayers()

    def fetch_location(self, city):
        entry = self.cityentry.get_text()
        print ("DEBUG: fetching city '%s' from internet @", (city, str(datetime.datetime.now())))
        try:
            entry = self.cityentry.get_text()
            url = 'http://maps.googleapis.com/maps/api/geocode/json?address=%s&sensor=false' % city
            data = json.loads(urllib.request.urlopen(url).read().decode())
            return data
        except IOError:
            print ("DEBUG: Error fetching city '%s' from internet IOError: timeout @", (city, str(datetime.datetime.now())))

        return None

    def on_entered_city_activate(self, widget):
        entry = self.cityentry.get_text()
        data = self.fetch_location(entry)
        success = False
        if data != None:
            if data["status"] == "ZERO_RESULTS":
                self.cityentry.set_text("Invalid City")
            elif data["status"] == "OVER_QUERY_LIMIT" or not data["results"]:
                self.cityentry.set_text("Error")
                print ("Debug: %s" % data["error_message"])
            else:
                self.cityentry.set_text('%s' % data["results"][0]["address_components"][1]["long_name"])
                self.latentry.set_value(float(data["results"][0]['geometry']['location']['lat']))
                self.longentry.set_value(float(data["results"][0]['geometry']['location']['lng']))
                success = True

        if success:

            for addcom in data["results"][0]["address_components"]:
                for item in addcom["types"]:
                    if item == "locality":
                        self.prayertimes.options.city = '%s' % addcom["long_name"]
                    if item  == "country":
                        self.prayertimes.options.country = '%s' % addcom["long_name"]

            self.prayertimes.options.latitude = float(data["results"][0]['geometry']['location']['lat'])
            self.prayertimes.options.longitude = float(data["results"][0]['geometry']['location']['lng'])
            self.prayertimes.options.timezone = float(time.timezone / 60 / 60 * -1)

            # Update qibla
            self.update_qibla()

            # Update home prayers
            self.update_prayers()

    def on_entered_city_focus_out(self, widget, event):
        self.prayertimes.options.city = widget.get_text()
        self.update_qibla()

    def update_qibla(self):
        print ("DEBUG: updating qibla @", (str(datetime.datetime.now())))
        # Update the Compass direction
        new_qibla = self.prayertimes.get_qibla()
        new_country = self.prayertimes.options.country
        new_city = self.prayertimes.options.city
        self.qiblacompass.update_compass(new_qibla, new_country, new_city)

    def update_prayers(self, recalculate_prayer_times = True):
        print ("DEBUG: updating prayer times @", (str(datetime.datetime.now())))
        # Re-calculate prayer times first
        if recalculate_prayer_times:
            self.prayertimes.calculate(False)
        # Update prayer times
        i = 0
        for prayer in self.homebox.prayers:
            if prayer.name == _('Fajr'):
                self.homebox.prayers[i].time = self.get_times(self.prayertimes.fajr_time())
            elif prayer.name == _('Shuruk'):
                self.homebox.prayers[i].time = self.get_times(self.prayertimes.shrouk_time())
            elif prayer.name == _('Dhuhr'):
                self.homebox.prayers[i].time = self.get_times(self.prayertimes.zuhr_time())
            elif prayer.name == _('Asr'):
                self.homebox.prayers[i].time = self.get_times(self.prayertimes.asr_time())
            elif prayer.name == _('Maghrib'):
                self.homebox.prayers[i].time = self.get_times(self.prayertimes.maghrib_time())
            elif prayer.name == _('Isha'):
                self.homebox.prayers[i].time = self.get_times(self.prayertimes.isha_time())
            i += 1
        nextprayer = self.prayertimes.next_prayer()
        self.homebox.emit("prayers-updated", nextprayer)

    def hide_window(self, widget, data):
        self.prayertimes.options.save_options()
        return self.hide_on_delete()

    def get_times(self, prayer):# If User Sets Clock Format 12hr or 24hr Return It As He Likes!
        if self.prayertimes.options.clock_format == '12h':
            #print ("DEBUG: using 12h format @", (str(datetime.datetime.now())))
            return self.timeto12(prayer).replace('AM', _('AM')).replace('PM', _('PM'))
        if self.prayertimes.options.clock_format == '24h':
            #print ("DEBUG: using 24h format @", (str(datetime.datetime.now())))
            return self.timeto24(prayer)

    def timeto24(self, timeto24):# Transform 12hr clock into 24hr Clock
        #print ("DEBUG: transforming 24h to 12h @", (str(datetime.datetime.now())))
        tts = datetime.datetime.strptime(timeto24, "%I:%M:%S %p")
        tfs = datetime.datetime.strftime(tts,"%H:%M")
        return str(tfs)

    def timeto12(self, timeto12):# Transform 12hr clock into 12hr Clock Without second and Remove The Zero before hour
        #print ("DEBUG: analysing times @", (str(datetime.datetime.now())))
        tts = datetime.datetime.strptime(timeto12, "%I:%M:%S %p")
        tfs = datetime.datetime.strftime(tts,"%l:%M %p")
        return str(tfs)
