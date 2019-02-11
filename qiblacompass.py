# Silaty
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio, Gdk, GdkPixbuf
from translate import translate_text as _

class QiblaCompass(Gtk.Box):
	def __init__(self, qibladirection, country, city):
		Gtk.Box.__init__(self)

		self.mainbox = Gtk.Box()
		self.mainbox.set_orientation(Gtk.Orientation.VERTICAL)

		qibla = self.set_compass(qibladirection)
		qibla.props.valign = Gtk.Align.START

		## Make the top label
		qiblatitle = Gtk.Label(label=_("Qibla direction :"), margin_left=20, margin_right=20)
		qiblatitle.props.halign = Gtk.Align.START
		self.mainbox.pack_start(qiblatitle, False, False, 12)

		## Set the compass image
		self.mainbox.pack_start(qibla, False, True, 0)

		## Set the country and city
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
		qiblalabel = Gtk.Label(label=_("Country : %s") % country)
		qiblalabel.props.halign = Gtk.Align.CENTER
		qiblalabel.props.valign = Gtk.Align.CENTER
		vbox.pack_start(qiblalabel, True,True, 0)

		qiblalabel = Gtk.Label(label=_("City : %s") % city)
		qiblalabel.props.halign = Gtk.Align.CENTER
		qiblalabel.props.valign = Gtk.Align.CENTER
		vbox.pack_start(qiblalabel, True, True, 0)

		## Add it all in the end
		self.mainbox.pack_start(vbox, False, False, 12)
		self.pack_start(self.mainbox, True, True, 0)

	def set_compass(self, qibladirection):
		print ("DEBUG: Showing Qibla window")
		img='''<?xml version="1.0"?>
<svg width="380" height="220"  xmlns="http://www.w3.org/2000/svg">
	<!-- center of rotation -->

	<!-- rotated arrow -->
	<g>
		<rect fill="#ebebeb" width="380" height="220"/>
		<line stroke="#cccccc" fill="#cccccc" id="top-border" stroke-width="1" y2="0" x2="380" y1="0" x1="0"/>
		<line stroke="#cccccc" fill="#cccccc" id="bottom-border" stroke-width="1" y2="220" x2="380" y1="220" x1="0"/>

		<title>Layer 1</title>
		<circle fill="#ffffff" id="svg_1" stroke="#ebebeb" stroke-width="1" r="86" cy="110" cx="190"/>
		<circle fill="#ffffff" id="svg_2" stroke="#ebebeb" stroke-width="1" r="80" cy="110" cx="190"/>
		<g transform="rotate(%s, 190, 110)" stroke=" black" id="arrow">
			<line stroke="#51acff" fill="#51acff" id="svg_3" stroke-width="2" y2="110" x2="114" y1="110" x1="190"/>
			<line stroke="#51acff" fill="#51acff" id="svg_4" stroke-width="2" y2="110" x2="266" y1="110" x1="190"/>
			<line stroke="#51acff" fill="#51acff" id="svg_5" stroke-width="2" y2="110" x2="266" y1="97" x1="252"/>
			<line stroke="#51acff" fill="#51acff" id="svg_5" stroke-width="2" y2="110" x2="266" y1="123" x1="252"/>
		</g>
		<circle id="svg_34" r="11" cy="110" cx="190" stroke-width="2" stroke="#51acff" fill="#ffffff"/>
		<text stroke="#6e6e6e" fill="#6e6e6e" id="svg_7" font-family="Raleway" font-weight="300" font-size="30" y="35" x="260">%.2f&#176;</text>
	</g>

</svg>''' % (qibladirection-90, qibladirection)
		stream = Gio.MemoryInputStream.new_from_bytes(GLib.Bytes.new(img.encode('utf-8')))
		pixbuf = GdkPixbuf.Pixbuf.new_from_stream(stream, None)
		svgwidget = Gtk.Image.new_from_pixbuf(pixbuf)
		return svgwidget

	def update_compass(self, qibladirection, country, city):
		## The only way to update so far is to remove the whole thing and create it again
		self.remove(self.mainbox)

		self.mainbox = Gtk.Box()
		self.mainbox.set_orientation(Gtk.Orientation.VERTICAL)

		qibla = self.set_compass(qibladirection)
		qibla.props.valign = Gtk.Align.START

		## Make the top label
		qiblatitle = Gtk.Label(label=_("Qibla direction :"), margin_left=20, margin_right=20)
		qiblatitle.props.halign = Gtk.Align.START
		self.mainbox.pack_start(qiblatitle, False, False, 12)

		## Set the compass image
		self.mainbox.pack_start(qibla, False, True, 0)

		## Set the country and city
		vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
		qiblalabel = Gtk.Label(label=_("Country : %s") % country)
		qiblalabel.props.halign = Gtk.Align.CENTER
		qiblalabel.props.valign = Gtk.Align.CENTER
		vbox.pack_start(qiblalabel, True,True, 0)

		qiblalabel = Gtk.Label(label=_("City : %s") % city)
		qiblalabel.props.halign = Gtk.Align.CENTER
		qiblalabel.props.valign = Gtk.Align.CENTER
		vbox.pack_start(qiblalabel, True, True, 0)

		## Add it all in the end
		self.mainbox.pack_start(vbox, False, False, 12)
		self.pack_start(self.mainbox, True, True, 0)
		self.show_all()