# Silaty
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, GObject

class SideBar(Gtk.Grid):
	def __init__(self, stack = Gtk.Stack()):
		Gtk.Grid.__init__(self)
		self.set_orientation(Gtk.Orientation.VERTICAL)
		color = 70.0/256.0
		self.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA.from_color(Gdk.Color.from_floats(color,color,color)))
		self._childlength = 0
		self.stackchildnames = []
		self.stack = stack
		self.connect("window-shown", self.activate_button)

	@property
	def childlength(self):
		return self._childlength

	@childlength.setter
	def childlength(self, value):
		self._childlength = value

	def new_button(self, inact_icon, act_icon, on_press_callback = None):
		sidebaricon = SideBarButton(inact_icon, act_icon, on_press_callback)
		self.attach(sidebaricon, 0, self.childlength, 1, 1)

		sidebaricon.position = self.childlength
		if on_press_callback is None:
			sidebaricon.connect("sidebar-button-pressed", self.change_visible_stack, sidebaricon.position)

		self.childlength += 1

	def add_to_stack(self, widget, name):
		self.stack.add_named(widget, name)
		self.stackchildnames.append(name)

	def change_visible_stack(self, widget, position):
		self.stack.set_visible_child_name(self.stackchildnames[position])
		self.emit("stack-changed", self.stackchildnames[position])

	def activate_button(self, widget):
		visiblechild = self.stack.get_visible_child_name()
		index = self.stackchildnames.index(visiblechild)
		self.get_child(index).state = SideBarButtonState.ON
		self.get_child(index).iconstack.set_visible_child_name('active')
		self.emit("stack-changed", visiblechild)

	def get_child(self, index):
		return self.get_child_at(0, index)

class SideBarButton(Gtk.EventBox):	
	def __init__(self, inactive_icon, active_icon, on_press_callback = None):

		Gtk.EventBox.__init__(self)
		self.set_events(Gdk.EventMask.BUTTON_PRESS_MASK)
		if on_press_callback is None:
			self.connect("button-press-event", self.on_icon_pressed)
		else:
			self.connect("button-press-event", on_press_callback)

		self.inactive_icon = inactive_icon
		self.active_icon = active_icon
		self._position = 0
		self._state = SideBarButtonState.OFF

		self.iconstack = Gtk.Stack(margin_left=12, margin_right=12, margin_top=6, margin_bottom=6)
		self.iconstack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
		self.iconstack.set_transition_duration(300)

		icon = self.set_image_from_file(self.inactive_icon)
		self.iconstack.add_named(icon, 'inactive')

		icon = self.set_image_from_file(self.active_icon)
		self.iconstack.add_named(icon, 'active')

		self.add(self.iconstack)

	@property
	def position(self):
		return self._position

	@position.setter
	def position(self, value):
		self._position = value

	@property
	def state(self):
		return self._state

	@state.setter
	def state(self, value):
		if value == SideBarButtonState.ON:
			self.iconstack.set_visible_child_name('active')
		else:
			self.iconstack.set_visible_child_name('inactive')
		self._state = value	

	def on_icon_pressed(self, widget, data):
		parent = self.get_parent()
		for i in range(0, parent.childlength):
			if i == self.position:
				parent.get_child(i).state = SideBarButtonState.ON
				parent.get_child(i).emit("sidebar-button-pressed")
			else:
				parent.get_child(i).state = SideBarButtonState.OFF

	def set_image_from_file(self, iconpath):
		try:
			pixbuf = GdkPixbuf.Pixbuf.new_from_file(iconpath)
			icon = Gtk.Image.new_from_pixbuf(pixbuf)
		except GLib.GError:
			icon = Gtk.Image.new_from_stock(Gtk.STOCK_MISSING_IMAGE, 22)
		return icon

class SideBarButtonState(object):
	ON, OFF = True, False

GObject.type_register(SideBarButton)
GObject.signal_new("sidebar-button-pressed", SideBarButton, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())

GObject.type_register(SideBar)
GObject.signal_new("window-shown", SideBar, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ())
GObject.signal_new("stack-changed", SideBar, GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, [GObject.TYPE_STRING])