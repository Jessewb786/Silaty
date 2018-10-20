# Silaty
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject, Gtk, Gdk
from hijrical import *
import datetime

class Home(Gtk.Box):
	def __init__(self):
		Gtk.Box.__init__(self)
		self.set_orientation(Gtk.Orientation.VERTICAL)
		self.set_margin_bottom(6)
		# Set the Date in the Title
		now_wd = datetime.datetime.now().strftime("%H:%M - %A")
		g_date = datetime.datetime.now().strftime("%d %B %Y")
		calc = HijriCal()
		h_months = ['Muharram', 'Safar', 'Rabi al Awwal', 'Rabi al Akhira', 'Jumada al Ula', 'Jumada al Akhira', 'Rajab',  "Sha'ban",  'Ramadan',  'Shawwal',  "Dhu al Qa'da", 'Dhu al Hijja']
		h_year,  h_month,  h_day,  h_week_day = calc.today
		h_date = '%i %s %i' % ( h_day,  h_months[int(h_month-1)],  h_year)

		titlelabel = Gtk.Label(label=(now_wd+", "+h_date+" / "+g_date), margin_bottom=12, margin_top=12)
		titlelabel.props.halign = Gtk.Align.FILL
		self.pack_start(titlelabel, False, True, 0)
		self.prayers = []
		self.nprayers = 0
		self.connect("prayers-updated", self.update_prayers_highlight)

	def add_prayer(self, prayer, prayertime, colored):
		# Prayer Listbox
		prayercontainer = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		prayercontainer.set_size_request(380,0)
		prayerbox = Prayer(prayer, prayertime, colored)
		prayerbox.set_halign(Gtk.Align.FILL)
		prayerbox.set_valign(Gtk.Align.CENTER)

		if self.nprayers % 2 == 0:
			color = 235.0/256.0
			prayerbox.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA.from_color(Gdk.Color.from_floats(color,color,color)))
			color = 204.0/256.0
			prayercontainer.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA.from_color(Gdk.Color.from_floats(color,color,color)))
			prayerbox.props.margin_top = 1
			prayerbox.props.margin_bottom = 1

		self.nprayers += 1
		self.prayers.append(prayerbox)
		prayercontainer.pack_start(prayerbox, True, False, 0)
		self.pack_start(prayercontainer, False, True, 0)

	def update_prayers_highlight(self, widget, prayername):
		print ("DEBUG: received update prayers signal")
		for prayer in self.prayers:
			if prayer.name == prayername:
				prayer.prayerlabel.set_markup("<span color=\"#55c1ec\">"+prayer.name+"</span>")
				prayer.timelabel.set_markup("<span color=\"#55c1ec\">"+prayer.time+"</span>")
			else:
				prayer.prayerlabel.set_markup(prayer.name)
				prayer.timelabel.set_markup(prayer.time)

class Prayer(Gtk.Box):
	def __init__(self, prayer, prayertime, state):
		Gtk.Box.__init__(self)
		self.set_orientation(Gtk.Orientation.HORIZONTAL)
		self.set_halign(Gtk.Align.FILL)
		self.set_valign(Gtk.Align.CENTER)
		self._state = state
		self._name = prayer
		self._time = prayertime

		self.prayerlabel = Gtk.Label(halign=Gtk.Align.START, margin_bottom=6, margin_top=6, margin_left=12)
		self.prayerlabel.set_use_markup(True)

		if state == True:
			self.prayerlabel.set_markup("<span color=\"#55c1ec\">"+prayer+"</span>")
		else:
			self.prayerlabel.set_label(prayer)

		self.pack_start(self.prayerlabel, True, True, 0)

		self.timelabel = Gtk.Label(label=prayertime, halign=Gtk.Align.END, margin_bottom=6, margin_top=6, margin_right=12)
		self.timelabel.set_use_markup(True)

		if state == True:
			self.timelabel.set_markup("<span color=\"#55c1ec\">"+prayertime+"</span>")
		else:
			self.timelabel.set_label(prayertime)

		self.pack_end(self.timelabel, True, True, 0)

	@property
	def time(self):
		return self._time
	@time.setter
	def time(self, value):
		self._time = value

	@property
	def name(self):
		return self._name

	@name.setter
	def name(self, value):
		self._name = value

GObject.type_register(Home)
GObject.signal_new("prayers-updated", Home, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [GObject.TYPE_STRING])
