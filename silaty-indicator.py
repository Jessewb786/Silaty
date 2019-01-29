#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Silaty
#
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786
#
# TODO: Help document
# TODO: Good Code Documentation

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, GObject, Gio, GLib, Gdk, GdkPixbuf
from gi.repository import AppIndicator3 as AI
from datetime import date
from hijrical import *
from silaty import *
import locale
import sys

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

class SilatyIndicator():
	def __init__(self):
		# Setup Indicator Applet
		self.Indicator = AI.Indicator.new("silaty-indicator","silaty-indicator",
			AI.IndicatorCategory.APPLICATION_STATUS)
		self.Indicator.set_status(AI.IndicatorStatus.ACTIVE)
		self.Indicator.set_icon(self.icon())

		# Activate the Silaty Window
		self.silaty = Silaty(self)

		self.silaty.prayertimes.calculate()
		print ("DEBUG: Silaty started! @", (str(datetime.datetime.now())))
		print ("DEBUG: started prayer times report: @", (str(datetime.datetime.now())))
		self.silaty.prayertimes.report()
		print ("DEBUG: end of report @", (str(datetime.datetime.now())))

		# Setup the Menu
		print ("DEBUG: initialize the menu @", (str(datetime.datetime.now())))
		self.Menu = Gtk.Menu()

		# Add Hijri date
		print ("DEBUG: Adding hijri date to menu @", (str(datetime.datetime.now())))
		self.HijriDateItem = Gtk.MenuItem(self.get_hijri_date())
		self.HijriDateItem.connect("activate", self.show_home)
		self.Menu.append(self.HijriDateItem)
		self.Menu.append(Gtk.SeparatorMenuItem())

		# Add City
		print ("DEBUG: Adding city to menu @", (str(datetime.datetime.now())))
		self.CityItem = Gtk.MenuItem("Location: %s" % self.silaty.prayertimes.options.city, sensitive=False)
		self.Menu.append(self.CityItem)

		# Add Qibla Direction
		print ("DEBUG: Adding qibla direction to menu @", (str(datetime.datetime.now())))
		self.QiblaItem = Gtk.MenuItem("Qibla is %.2f° from True North" % self.silaty.prayertimes.get_qibla())
		self.QiblaItem.connect("activate", self.show_qibla)
		self.Menu.append(self.QiblaItem)
		self.Menu.append(Gtk.SeparatorMenuItem())

		# Add Prayer Times
		print ("DEBUG: Adding the prayer times to menu @", (str(datetime.datetime.now())))
		self.FajrItem     = Gtk.MenuItem("Fajr\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.fajr_time()), sensitive=False)
		#self.ShurukItem   = Gtk.MenuItem("Shuruk\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.shrouk_time()), sensitive=False)
		self.DhuhrItem    = Gtk.MenuItem("Dhuhr\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.zuhr_time()), sensitive=False)
		self.AsrItem      = Gtk.MenuItem("Asr\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.asr_time()), sensitive=False)
		self.MaghribItem  = Gtk.MenuItem("Maghrib\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.maghrib_time()), sensitive=False)
		self.IshaItem     = Gtk.MenuItem("Isha\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.isha_time()), sensitive=False)
		self.Menu.append(self.FajrItem)
		#self.Menu.append(self.ShurukItem)
		self.Menu.append(self.DhuhrItem)
		self.Menu.append(self.AsrItem)
		self.Menu.append(self.MaghribItem)
		self.Menu.append(self.IshaItem)
		self.Menu.append(Gtk.SeparatorMenuItem())

		print ("DEBUG: Adding Next prayer to menu @", (str(datetime.datetime.now())))
		self.NextPrayerItem = Gtk.MenuItem('Next Prayer', sensitive=False)# Next PrayerTime's Item, it shows you information about the next prayer
		self.Menu.append(self.NextPrayerItem)
		self.Menu.append(Gtk.SeparatorMenuItem())

		print ("DEBUG: Adding About, Settings and Quit to menu @", (str(datetime.datetime.now())))
		# The Last 3 menu items never change and don't need to be updated
		AboutItem = Gtk.MenuItem('About')
		self.Menu.append(AboutItem)
		AboutItem.connect('activate',self.about_dialog, None)

		SettingsItem = Gtk.MenuItem('Settings')
		self.Menu.append(SettingsItem)
		SettingsItem.connect('activate', self.show_settings, None)

		ExitItem = Gtk.MenuItem('Quit')
		self.Menu.append(ExitItem)
		ExitItem.connect('activate', self.quit)

		print ("DEBUG: starting mainloop @", (str(datetime.datetime.now())))
		self.currentprayer = self.silaty.prayertimes.next_prayer()
		self.loop()# Run Application's loop
		self.Menu.show_all()# Show All Items
		self.Indicator.set_menu(self.Menu)# Assign Menu To Indicator
		self.Gobjectloop = GLib.timeout_add_seconds(1, self.loop)# Run loop

	def loop(self):
		global NextPrayerDT
		self.silaty.prayertimes.calculate()# Calculate PrayerTimes

		# Update City menu item
		self.CityItem.set_label("Location: %s" % self.silaty.prayertimes.options.city)

		# Update Hijri Date Menu item
		self.HijriDateItem.set_label(self.get_hijri_date())

		# Update Qibla Menu item
		self.QiblaItem.set_label("Qibla is %.2f° from True North" % self.silaty.prayertimes.get_qibla())

		# Update Prayer Times items
		self.FajrItem.set_label("Fajr\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.fajr_time()))
		#self.ShurukItem.set_label("Shuruk\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.shrouk_time()))
		self.DhuhrItem.set_label("Dhuhr\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.zuhr_time()))
		self.AsrItem.set_label("Asr\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.asr_time()))
		self.MaghribItem.set_label("Maghrib\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.maghrib_time()))
		self.IshaItem.set_label("Isha\t\t\t\t\t%s" % self.silaty.get_times(self.silaty.prayertimes.isha_time()))

		nextprayer = self.silaty.prayertimes.next_prayer()
		tonextprayer = self.silaty.prayertimes.time_to_next_prayer()

		# Update displayed prayer
		if (nextprayer != self.currentprayer) and self.silaty.is_visible():
			self.silaty.homebox.emit("prayers-updated", nextprayer)
			self.currentprayer = nextprayer

		self.NextPrayerItem.set_label("%s until %s" % (self.secs_to_hrtime(tonextprayer.seconds), nextprayer))
		self.silaty.headerbar.set_title("%s until %s" % (self.secs_to_hrtime(tonextprayer.seconds), nextprayer))
		self.Indicator.set_title("%s in %s" % (nextprayer, (self.secs_to_nrtime(tonextprayer.seconds))))

		if self.silaty.prayertimes.options.iconlabel == True:
			self.Indicator.set_label("%s in %s" % (nextprayer, (self.secs_to_nrtime(tonextprayer.seconds))),"")
		else:
			self.Indicator.set_label("","")
		return True

	def secs_to_hrtime(self, secs):
		# Transform Seconds into Hours and Minutes
		hours = secs//3600
		minutes = (secs//60)%60
		minutes += 1 # correct minutes (to avoid values like "0min")
		if minutes == 60:
			hours += 1
			return str(hours)+" Hours"
		elif hours == 0:
			return str(minutes)+" Minutes"
		else:
			return str(hours)+" Hours and "+str(minutes)+" Minutes"

	def secs_to_nrtime(self, secs):
		# Transform Seconds into Hours and Minutes
		# Using the same standard in iPray
		hours = secs//3600
		minutes = (secs//60)%60
		minutes += 1 # correct minutes (to avoid values like "0min")
		if minutes == 60:
			hours += 1
			return str(hours)+"hr"
		elif hours == 0:
			return str(minutes)+"min"
		else:
			return str(hours)+"hr "+str(minutes)+"min"

	def icon(self):
		# Get Icon
		print ("DEBUG: getting Icons @", (str(datetime.datetime.now())))
		PathDir = os.path.dirname(os.path.realpath(__file__)) + "/icons/hicolor/scalable/silaty-indicator.svg"
		#print (PathDir)

		if os.path.exists(PathDir):
			print ("DEBUG: icon found in the OS @", (str(datetime.datetime.now())))
			return PathDir

		else:
			print ("ERROR: Cannot find icon : silaty-indicator.svg @ %s" % (str(datetime.datetime.now())), file=sys.stderr)
			print ("DEBUG: silaty-indicator QUITING @", (str(datetime.datetime.now())))
			sys.exit(1)

	def get_hijri_date(self):
		wd = datetime.datetime.now().strftime("%A")
		calc = HijriCal(self.silaty.prayertimes.options.hijrical_adjustment)
		h_months = ['Muharram ', 'Safar', 'Rabi al Awwal', 'Rabi al Akhira', 'Jumada al Ula', 'Jumada al Akhira', 'Rajab', "Sha'ban", 'Ramadan', 'Shawwal', "Dhu al Qa'da", 'Dhu al Hijja']
		h_year,  h_month,  h_day,  h_week_day = calc.today
		h_date = '%i %s %i' % ( h_day,  h_months[int(h_month-1)],  h_year)
		return (str(wd)+", "+str(h_date))

	def show_home(self, widget):
		self.show_window("home")

	def show_qibla(self, widget):
		self.show_window("qibla")

	def show_settings(self, widget, data):
		self.show_window("options")

	def show_window(self, active_tab_name):
		# Show main window
		#print ('DEBUG: window is visible: %s, active: %s' % (self.silaty.is_visible(), self.silaty.is_active()))
		if not self.silaty.is_visible():
			self.silaty.show_all()
		elif not self.silaty.is_active():
			self.silaty.present()
		# Set active tab
		current_tab_name = self.silaty.sidebar.stack.get_visible_child_name()
		if (current_tab_name != active_tab_name):
			# If another tab was activated before, set its state to OFF
			index = self.silaty.sidebar.stackchildnames.index(current_tab_name)
			self.silaty.sidebar.get_child(index).state = SideBarButtonState.OFF
		# Activate/show new tab
		self.silaty.sidebar.stack.set_visible_child_name(active_tab_name)
		self.silaty.sidebar.emit("window-shown")

	def about_dialog(self, widget, data=None):# The About Dialog
		print ("DEBUG: opening about dialog @", (str(datetime.datetime.now())))
		about_dialog = Gtk.AboutDialog()
		if self.silaty.is_visible():
			about_dialog.set_transient_for(self.silaty)
		else:
			about_dialog.set_position(Gtk.WindowPosition.CENTER)
		logo = GdkPixbuf.Pixbuf.new_from_file(os.path.dirname(os.path.realpath(__file__)) + "/icons/hicolor/48x48/apps/silaty.svg")
		about_dialog.set_logo(logo)
		about_dialog.set_program_name("Silaty")
		about_dialog.set_website("https://github.com/AXeL-dev/Silaty")
		about_dialog.set_website_label("GitHub Project Page")
		about_dialog.set_authors(["AXeL-dev <anass_denna@hotmail.fr> (Maintainer)", "Jesse Wayde Brandão <www.jwb@gmail.com> (Lead Developer)",\
		 "Mohamed Alaa <m.alaa8@gmail.com> (Developer)","Eslam Mostafa <CsEslam@gmail.com> (Developer)",\
		 "Ahmed Youssef <xmonader(at)gmail.com> (Developer)"])
		about_dialog.set_artists(["Mustapha Asbbar <abobakrsalafi@gmail.com> (Designer)"])
		about_dialog.set_license('''Silaty, A Prayer Times Reminder Application.
Copyright © 2018 Silaty Team

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.''')
		about_dialog.set_version("1.2")
		about_dialog.set_comments("A neat Prayer Time Reminder App.\n Simple and complete so no prayer is missed")
		about_dialog.set_copyright("Copyright © 2018 Silaty Team")
		about_dialog.run()
		about_dialog.destroy()

	def quit(self, widget):
		self.silaty.prayertimes.options.save_options()
		self.silaty.destroy()
		Gtk.main_quit()

	def main(self):
		Gtk.main()
		print ("DEBUG: starting/stopping GTK @", (str(datetime.datetime.now())))

if __name__ == '__main__':
	ipm = SilatyIndicator()
	ipm.main()
