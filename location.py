# Silaty
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import os
try:
	import xml.etree.cElementTree as ET # C implementation is much faster
except ImportError:
	import xml.etree.ElementTree as ET

class TimeZone():

	def __init__(self, zone_name, value):
		self.zone_name = zone_name
		self.value = value

class Country():

	def __init__(self, name, timezone):
		self.name = name
		self.timezone = timezone

class Location():

	def __init__(self, num, name, coordinates, country, is_city):
		self.num = num
		self.name = name
		self.coordinates = coordinates
		self.country = country
		self.is_city = is_city

	def get_latitude(self):
		if self.coordinates is None:
			return None
		else:
			coordinates = self.coordinates.split(' ')
			return float(coordinates[0])

	def get_longitude(self):
		if self.coordinates is None:
			return None
		else:
			coordinates = self.coordinates.split(' ')
			if len(coordinates) <= 1:
				return None
			else:
				return float(coordinates[1])

class LocationDialog(Gtk.Dialog):

	def __init__(self, parent, title='Silaty'):
		Gtk.Dialog.__init__(self, modal=True, transient_for=parent, title=title, flags=Gtk.DialogFlags.DESTROY_WITH_PARENT)
		self.parent = parent
		self.set_border_width(10)
		self.set_resizable(False)
		self.connect('delete-event', self.hide_dialog)
		self.connect('response', self.hide_dialog)
		self.locations = []
		self.locations_count = 0
		# Location
		content_area = self.get_content_area()
		content_area.set_spacing(5)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_size_request(150, 250)
		content_area.add(scrolledwindow)
		self.treestore = Gtk.TreeStore(str, int)
		self.parse_locations()
		treemodelsort = Gtk.TreeModelSort(self.treestore)
		treemodelsort.set_sort_column_id(0, Gtk.SortType.ASCENDING)
		self.treeview = Gtk.TreeView()
		self.treeview.set_model(treemodelsort)
		scrolledwindow.add(self.treeview)
		cellrenderertext = Gtk.CellRendererText()
		treeviewcolumn = Gtk.TreeViewColumn('Location', cellrenderertext, text=0)
		self.treeview.append_column(treeviewcolumn)
		#self.treeview.set_headers_visible(False)
		treeselection = self.treeview.get_selection()
		treeselection.set_mode(Gtk.SelectionMode.SINGLE)
		treeselection.connect('changed', self.on_selection_changed)
		# Search
		searchbox   = Gtk.Box(halign=Gtk.Align.FILL, spacing=10)
		searchlabel = Gtk.Label('Search:', halign=Gtk.Align.START)
		searchbox.pack_start(searchlabel, False, False, 0)
		searchentry = Gtk.Entry(halign=Gtk.Align.FILL)
		searchentry.connect('changed', self.on_search_entry_changed)
		self.treeview.set_search_entry(searchentry)
		self.treeview.set_search_equal_func(self.search_function)
		self.treeview.set_search_column(0)
		searchbox.pack_start(searchentry, True, True, 0)
		content_area.add(searchbox)
		# Help
		helpbox   = Gtk.Box(halign=Gtk.Align.FILL, spacing=3, margin=10)
		helpimage = Gtk.Image(icon_name='system-help')
		helpbox.pack_start(helpimage, False, False, 0)
		helplabel = Gtk.Label('Check your location on <a href="https://www.islamicfinder.org/">www.islamicfinder.org</a>', use_markup=True)
		helpbox.pack_start(helplabel, True, True, 0)
		content_area.add(helpbox)
		# Buttons
		self.action_area.set_layout(Gtk.ButtonBoxStyle.END)
		self.apply_button = Gtk.Button('Apply')
		self.apply_button.set_sensitive(False)
		self.apply_button.connect('clicked', self.on_apply_button_clicked)
		cancel_button = Gtk.Button('Cancel')
		cancel_button.connect('clicked', self.on_cancel_button_clicked)
		self.add_action_widget(self.apply_button, Gtk.ResponseType.OK)
		self.add_action_widget(cancel_button, Gtk.ResponseType.CANCEL)
		self.show_all()

	def hide_dialog(self, widget, response):
		self.hide()
		return True

	def on_apply_button_clicked(self, widget):
		location_num = self.get_selected_location()
		location = self.get_location(location_num)
		if location is not None:
			self.parent.lock_location_updates = True
			self.parent.prayertimes.options.country = location.country.name
			self.parent.prayertimes.options.city = location.name
			self.parent.cityentry.set_text(location.name)
			latitude  = location.get_latitude()
			longitude = location.get_longitude()
			timezone  = location.country.timezone
			if latitude is not None:
				self.parent.latentry.set_value(latitude)
			if longitude is not None:
				self.parent.longentry.set_value(longitude)
			if timezone is not None:
				self.parent.tzentry.set_value(timezone.value)
			self.parent.update_location()
			self.parent.lock_location_updates = False

	def on_cancel_button_clicked(self, widget):
		pass

	def on_search_entry_changed(self, widget):
		if not widget.get_text():
			self.apply_button.set_sensitive(False)

	def get_location(self, location_num):
		if location_num is not None:
			for location in self.locations:
				if location.num == location_num:
					return location

		return None

	def is_location(self, location_num):
		if self.get_location(location_num) is None:
			return False
		else:
			return True

	def get_selected_location(self, selection = None):
		if selection is None:
			selection = self.treeview.get_selection()
		model, tree_iter = selection.get_selected()
		if tree_iter and not model.iter_has_child(tree_iter): # a location should not have children
			value = model.get_value(tree_iter, 1) # 0 => location name, 1 => location num
			return value
		else:
			return None

	def on_selection_changed(self, selection):
		location_num = self.get_selected_location(selection)
		if self.is_location(location_num):
			self.apply_button.set_sensitive(True)
		else:
			self.apply_button.set_sensitive(False)

	def toggle_rows(self, row, key, column):
		for child in row.iterchildren():
			if key.lower() in list(child)[column].lower():
				self.treeview.expand_to_path(row.path)
				return True
			else:
				if self.toggle_rows(child, key, column):
					return True
				self.treeview.collapse_row(row.path)

		return False

	# @see https://stackoverflow.com/questions/23355866/user-search-collapsed-rows-in-a-gtk-treeview
	def search_function(self, model, column, key, rowiter):
		row = model[rowiter]
		if key.lower() in list(row)[column-2].lower():
			return False # Search matches

		# Search in child rows. If one of the rows matches, expand the row so that it will be open in later checks.
		self.toggle_rows(row, key, column-2)

		return True # Search does not match

	def add_location(self, location, country, is_city = False):
		name = location[0].text
		location_coordinates = location.find('coordinates')
		if location_coordinates is not None:
			coordinates = location_coordinates.text
		else:
			print ('WARNING: %s > %s has no coordinates.' % (country.name, name))
			coordinates = None
		self.locations_count += 1
		new_location = Location(self.locations_count, name, coordinates, country, is_city)
		# add new location
		self.locations.append(new_location)

	def parse_locations(self):
		# Parse XML file
		tree = ET.parse(os.path.dirname(os.path.realpath(__file__)) + '/data/Locations.xml')
		root = tree.getroot()
		for child in root:
			if child.tag == 'region':
				region_name = child.find('name').text
				#print ('%s' % region_name)
				region_node = self.treestore.append(None, [region_name, 0])
				for region_child in child:
					if region_child.tag == 'country':
						country_name = region_child.find('name').text
						#print ('├── %s' % country_name)
						timezones = region_child.find('timezones')
						if timezones is not None:
							zone = timezones[0].attrib['id']
							value = float(timezones[0].attrib['value'])
							timezone = TimeZone(zone, value)
						else:
							print ('WARNING: %s has no timezone.' % (country_name))
							timezone = None
						country = Country(country_name, timezone)
						country_node = self.treestore.append(region_node, [country_name, 0])
						for country_child in region_child:
							if country_child.tag == 'location':
								location_name = country_child.find('name').text
								#print ('│   ├── %s' % location_name)
								self.add_location(country_child, country)
								self.treestore.append(country_node, [location_name, self.locations_count])
							elif country_child.tag == 'city':
								city_name = country_child.find('name').text
								#print ('│   ├── %s' % city_name)
								self.add_location(country_child, country, True)
								self.treestore.append(country_node, [city_name, self.locations_count])
							elif country_child.tag == 'state':
								state_name = country_child.find('name').text
								#print ('│   ├── %s' % state_name)
								state_node = self.treestore.append(country_node, [state_name, 0])
								for state_child in country_child:
									if state_child.tag == 'location':
										location_name = state_child.find('name').text
										#print ('│   │   ├── %s' % location_name)
										self.add_location(state_child, country)
										self.treestore.append(state_node, [location_name, self.locations_count])
									elif state_child.tag == 'city':
										city_name = state_child.find('name').text
										#print ('│   │   ├── %s' % city_name)
										self.add_location(state_child, country, True)
										self.treestore.append(state_node, [city_name, self.locations_count])
