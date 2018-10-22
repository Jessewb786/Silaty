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

class Location():

	def __init__(self, name, code, coordinates, country, city):
		self.name = name
		self.code = code
		self.coordinates = coordinates
		self.country = country
		self.city = city

	def get_full_name(self):
		if self.city and self.city not in self.name:
			return ('%s (%s), %s' % (self.city, self.name, self.country))
		else:
			return ('%s, %s' % (self.name, self.country))

	def get_latitude(self):
		if not self.coordinates:
			return None
		else:
			coordinates = self.coordinates.split(' ')
			parts = coordinates[0].split('-')
			parts_len = len(parts)
			index = parts_len - 1
			direction = parts[index][-1:]
			parts[index] = parts[index][:-1]
			if parts_len == 3:
				latitude = self.dms2dd(parts[0], parts[1], parts[2], direction)
			elif parts_len == 2:
				latitude = self.dms2dd(parts[0], parts[1], 0, direction)
			else:
				latitude = None
			return latitude

	def get_longitude(self):
		if not self.coordinates:
			return None
		else:
			coordinates = self.coordinates.split(' ')
			if len(coordinates) <= 1:
				return None
			else:
				parts = coordinates[1].split('-')
				parts_len = len(parts)
				index = parts_len - 1
				direction = parts[index][-1:]
				parts[index] = parts[index][:-1]
				if parts_len == 3:
					longitude = self.dms2dd(parts[0], parts[1], parts[2], direction)
				elif parts_len == 2:
					longitude = self.dms2dd(parts[0], parts[1], 0, direction)
				else:
					longitude = None
				return longitude

	def dms2dd(self, degrees, minutes, seconds, direction):
		dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
		if direction == 'W' or direction == 'S':
			dd *= -1
		return dd

class LocationDialog(Gtk.Dialog):

	def __init__(self, parent, title='Silaty'):
		Gtk.Dialog.__init__(self, modal=True, transient_for=parent, title=title)
		self.parent = parent
		self.set_border_width(10)
		self.set_resizable(False)
		self.locations = []
		# Location
		content_area = self.get_content_area()
		content_area.set_spacing(5)
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_size_request(150, 250)
		content_area.add(scrolledwindow)
		self.treestore = Gtk.TreeStore(str)
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

	def on_apply_button_clicked(self, widget):
		location_name = self.get_selected_location()
		location = self.get_location(location_name)
		if location is not None:
			self.parent.cityentry.set_text(location.get_full_name())
			latitude  = location.get_latitude()
			longitude = location.get_longitude()
			if latitude is not None:
				self.parent.latentry.set_value(latitude)
			if longitude is not None:
				self.parent.longentry.set_value(longitude)

	def on_cancel_button_clicked(self, widget):
		pass

	def on_search_entry_changed(self, widget):
		if not widget.get_text():
			self.apply_button.set_sensitive(False)

	def get_location(self, name):
		if name and name is not None:
			for location in self.locations:
				if location.name == name:
					return location

		return None

	def is_location(self, name):
		if self.get_location(name) is None:
			return False
		else:
			return True

	def get_selected_location(self, selection = None):
		if selection is None:
			selection = self.treeview.get_selection()
		model, tree_iter = selection.get_selected()
		if tree_iter and not model.iter_has_child(tree_iter): # a location should not have children
			value = model.get_value(tree_iter, 0)
			return value
		else:
			return None

	def on_selection_changed(self, selection):
		location_name = self.get_selected_location(selection)
		if self.is_location(location_name):
			self.apply_button.set_sensitive(True)
		else:
			self.apply_button.set_sensitive(False)

	# @see https://stackoverflow.com/questions/23355866/user-search-collapsed-rows-in-a-gtk-treeview
	def search_function(self, model, column, key, rowiter):
		row = model[rowiter]
		if key.lower() in list(row)[column-1].lower():
			return False # Search matches

		# Search in child rows. If one of the rows matches, expand the row so that it will be open in later checks.
		for level_1 in row.iterchildren():
			if key.lower() in list(level_1)[column-1].lower():
				self.treeview.expand_to_path(row.path)
				return True
			else:
				for level_2 in level_1.iterchildren():
					if key.lower() in list(level_2)[column-1].lower():
						self.treeview.expand_to_path(level_1.path)
						return True
					else:
						for level_3 in level_2.iterchildren():
							if key.lower() in list(level_3)[column-1].lower():
								self.treeview.expand_to_path(level_2.path)
								return True
							else:
								for level_4 in level_3.iterchildren():
									if key.lower() in list(level_4)[column-1].lower():
										self.treeview.expand_to_path(level_3.path)
										return True
									else:
										self.treeview.collapse_row(level_3.path)
								self.treeview.collapse_row(level_2.path)
						self.treeview.collapse_row(level_1.path)
				self.treeview.collapse_row(row.path)

		return True # Search does not match

	def add_location(self, location, country, city):
		name = location[0].text
		location_code = location.find('code')
		location_coordinates = location.find('coordinates')
		if location_code is not None:
			code = location_code.text
		else:
			print ('WARNING: %s > %s has no code.' % (country, name))
			code = ''
		if location_coordinates is not None:
			coordinates = location_coordinates.text
		else:
			print ('WARNING: %s > %s has no coordinates.' % (country, name))
			coordinates = ''
		self.locations.append(Location(name, code, coordinates, country, city))

	def parse_locations(self):
		# Parse XML file
		tree = ET.parse(os.path.dirname(os.path.realpath(__file__)) + '/data/Locations.xml')
		root = tree.getroot()
		for child in root:
			#print ('%s' % child[0].text)
			region = self.treestore.append(None, [child[0].text])
			for region_child in child:
				if region_child.tag == 'country':
					#print ('├── %s' % region_child[0].text)
					country = self.treestore.append(region, [region_child[0].text])
					for country_child in region_child:
						if country_child.tag == 'location':
							#print ('│   ├── %s' % country_child[0].text)
							self.treestore.append(country, [country_child[0].text])
							self.add_location(country_child, region_child[0].text, country_child[0].text)
						elif country_child.tag == 'city':
							#print ('│   ├── %s' % country_child[0].text)
							city = self.treestore.append(country, [country_child[0].text])
							for city_child in country_child:
								if city_child.tag == 'location':
									#print ('│   │   ├── %s' % city_child[0].text)
									self.treestore.append(city, [city_child[0].text])
									self.add_location(city_child, region_child[0].text, country_child[0].text)
						elif country_child.tag == 'state':
							#print ('│   ├── %s' % country_child[0].text)
							state = self.treestore.append(country, [country_child[0].text])
							for state_child in country_child:
								if state_child.tag == 'location':
									#print ('│   │   ├── %s' % state_child[0].text)
									self.treestore.append(state, [state_child[0].text])
									self.add_location(state_child, region_child[0].text, country_child[0].text)
								elif state_child.tag == 'city':
									#print ('│   │   ├── %s' % state_child[0].text)
									city = self.treestore.append(state, [state_child[0].text])
									for city_child in state_child:
										if city_child.tag == 'location':
											#print ('│   │   │   ├── %s' % city_child[0].text)
											self.treestore.append(city, [city_child[0].text])
											self.add_location(city_child, region_child[0].text, state_child[0].text)
