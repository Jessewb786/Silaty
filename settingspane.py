# Silaty
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SettingsPane(Gtk.Box):
	def __init__(self):
		Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, margin_top=12, margin_bottom=6, margin_left=12, margin_right=6)		
		self.nrows = 0
		self.ngrids = -1
		self.grids = []

	def add_grid(self):
		grid = Gtk.Grid(column_spacing=3, row_spacing=6, margin_left=12, margin_top=6, margin_bottom=6)
		#grid.set_row_homogeneous(True)
		grid.set_column_homogeneous(True)
		grid.set_halign(Gtk.Align.FILL)
		grid.set_valign(Gtk.Align.START)
		self.pack_start(grid, True, True, 0)
		self.grids.append(grid)

	def add_setting(self, setting, label):
		label.set_halign(Gtk.Align.START)
		self.grids[self.ngrids].attach(label, 0, self.nrows, 1, 1)
		self.grids[self.ngrids].attach_next_to(setting, label, Gtk.PositionType.RIGHT, 1, 1)
		self.nrows += 1

	def add_category(self, category):
		label = Gtk.Label(label="<b>"+category+"</b>")
		label.set_use_markup(True)
		label.set_halign(Gtk.Align.START)
		self.pack_start(label, True, True, 0)
		self.add_grid()
		self.nrows = 0
		self.ngrids += 1
