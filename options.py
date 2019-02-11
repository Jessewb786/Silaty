# Silaty
# Copyright (c) 2018 - 2019 AXeL
# Copyright (c) 2014 - 2015 Jessewb786

import configparser
import os
import datetime

class Calendar(object):
	UmmAlQuraUniv, \
	EgyptianGeneralAuthorityOfSurvey,\
	UnivOfIslamicSciencesKarachi,\
	IslamicSocietyOfNorthAmerica,\
	MuslimWorldLeague = range(5)

class Madhab(object):
	Default, Hanafi = 0, 1

class Options:
	def __init__(self):
		print ("DEBUG: Initializing the Options module @", (str(datetime.datetime.now())))

		cparse = configparser.ConfigParser()
		cparse.read([os.path.expanduser('~/.silaty')])

		try:
			self._city               = cparse.get('DEFAULT', 'city')
			self._country            = cparse.get('DEFAULT', 'country')
			self._calcmethodname     = cparse.get('DEFAULT', 'calculation-method')
			self._madhab             = cparse.get('DEFAULT', 'madhab')
			self._clockformat        = cparse.get('DEFAULT', 'clock-format')
			self._latitude           = cparse.get('DEFAULT', 'latitude')
			self._longitude          = cparse.get('DEFAULT', 'longitude')
			self._timezone           = cparse.get('DEFAULT', 'timezone')
			self._notif              = cparse.get('DEFAULT', 'notif')
			self._iconlabel          = cparse.get('DEFAULT', 'iconlabel')
			self._startminimized     = cparse.get('DEFAULT', 'minimized')
			self._fajradhan          = cparse.get('DEFAULT', 'fajr-adhan')
			self._normaladhan        = cparse.get('DEFAULT', 'normal-adhan')
			self._audionotifications = cparse.get('DEFAULT', 'audio-notifications')
			self._daylightsavingtime = cparse.get('DEFAULT', 'daylight-saving-time')
			self._hijricaladjustment = cparse.get('DEFAULT', 'hijrical-adjustment')
			self._language           = cparse.get('DEFAULT', 'language')

		except configparser.NoOptionError:
			print ("DEBUG: No configration file using default settings")
			self._city               = 'Makkah'
			self._country            = 'Saudi Arabia'
			self._latitude           = '21.25'
			self._longitude          = '39.49'
			self._timezone           = '3'
			self._calcmethodname     = 'Makkah'
			self._madhab             = 'Default'
			self._clockformat        = '24h'
			self._notif              = '10'
			self._iconlabel          = '1'
			self._startminimized     = '1'
			self._fajradhan          = (self.get_fajr_adhans())[0]
			self._normaladhan        = (self.get_normal_adhans())[0]
			self._audionotifications = '1'
			self._daylightsavingtime = '1'
			self._hijricaladjustment = '0'
			self._language           = 'English'
			self.save_options()

		except ValueError:
			print ("DEBUG: Problem while reading setting file, using the default settings")
			os.system("rm ~/.silaty")
			self._city               = 'Makkah'
			self._country            = 'Saudi Arabia'
			self._latitude           = '21.25'
			self._longitude          = '39.49'
			self._timezone           = '3'
			self._calcmethodname     = 'Makkah'
			self._madhab             = 'Default'
			self._clockformat        = '24h'
			self._notif              = '10'
			self._iconlabel          = '1'
			self._startminimized     = '1'
			self._fajradhan          = (self.get_fajr_adhans())[0]
			self._normaladhan        = (self.get_normal_adhans())[0]
			self._audionotifications = '1'
			self._daylightsavingtime = '1'
			self._hijricaladjustment = '0'
			self._language           = 'English'
			self.save_options()

	## Functions with lists for the Buttons
	def get_cal_methods(self):
		return ['Makkah', 'Egypt', 'Karachi', 'ISNA', 'MWL']

	def get_madhahed(self):
		return ['Hanafi', 'Default']

	def get_clock_formats(self):
		return ['12h', '24h']

	def get_languages(self):
		return ['English', 'Arabic']#, 'French']

	def get_fajr_adhans(self):
		dirfiles = os.listdir( os.path.dirname(os.path.realpath(__file__))+"/audio/Fajr/")
		wavfiles = filter(lambda song: song.endswith(".ogg"), dirfiles)
		adhans = list(map(lambda x: os.path.splitext(x)[0], wavfiles))
		return adhans

	def get_normal_adhans(self):
		dirfiles = os.listdir( os.path.dirname(os.path.realpath(__file__))+"/audio/Normal/")
		wavfiles = filter(lambda song: song.endswith(".ogg"), dirfiles)
		adhans = list(map(lambda x: os.path.splitext(x)[0], wavfiles))
		return adhans

	## Functions to get and set settings
	@property
	def audio_notifications_num(self):
		return self._audionotifications

	@audio_notifications_num.setter
	def audio_notifications_num(self, value):
		self._audionotifications = value

	@property
	def audio_notifications(self):
		#print ("DEBUG: getting audio notifications settings @", (str(datetime.datetime.now())))
		if self.audio_notifications_num == '1':
			return True
		else:
			return False

	@audio_notifications.setter
	def audio_notifications(self, data):
		#print ("DEBUG: setting audio notifications settings @", (str(datetime.datetime.now())))
		if data == True:
			self.audio_notifications_num = '1'
		else:
			self.audio_notifications_num = '0'

	@property
	def fajr_adhan(self):
		return self._fajradhan

	@fajr_adhan.setter
	def fajr_adhan(self, value):
		self._fajradhan = value

	@property
	def normal_adhan(self):
		return self._normaladhan

	@normal_adhan.setter
	def normal_adhan(self, value):
		self._normaladhan = value

	@property
	def city(self):
		#print ("DEBUG: getting city settings @", (str(datetime.datetime.now())))
		return self._city

	@city.setter
	def city(self, data):
		#print ("DEBUG: setting city settings @", (str(datetime.datetime.now())))
		self._city = data

	@property
	def country(self):
		#print ("DEBUG: getting country settings @", (str(datetime.datetime.now())))
		return self._country
	@country.setter
	def country(self, value):
		#print ("DEBUG: setting country settings @", (str(datetime.datetime.now())))
		self._country = value

	@property
	def calculation_method_name(self):
		return self._calcmethodname

	@calculation_method_name.setter
	def calculation_method_name(self, value):
		self._calcmethodname = value

	@property
	def calculation_method(self):
		#print ("DEBUG: getting calculation method settings @", (str(datetime.datetime.now())))
		if self.calculation_method_name == 'Makkah':
			return Calendar.UmmAlQuraUniv
		elif self.calculation_method_name == 'Egypt':
			return Calendar.EgyptianGeneralAuthorityOfSurvey
		elif self.calculation_method_name == 'Karachi':
			return Calendar.UnivOfIslamicSciencesKarachi
		elif self.calculation_method_name == 'ISNA':
			return Calendar.IslamicSocietyOfNorthAmerica
		elif self.calculation_method_name == 'MWL':
			return Calendar.MuslimWorldLeague

	@calculation_method.setter
	def calculation_method(self, data):
		#print ("DEBUG: setting calculation method settings @", (str(datetime.datetime.now())))
		self.calculation_method_name = data

	@property
	def madhab_name(self):
		return self._madhab

	@madhab_name.setter
	def madhab_name(self, value):
		self._madhab = value

	@property
	def madhab(self):
		#print ("DEBUG: getting madhab settings @", (str(datetime.datetime.now())))
		if self.madhab_name == 'Default':
			return Madhab.Default
		if self.madhab_name == 'Hanafi':
			return Madhab.Hanafi

	@madhab.setter
	def madhab(self, data):
		#print ("DEBUG: setting madhab settings @", (str(datetime.datetime.now())))
		self._madhab = data

	@property
	def latitude(self):
		#print ("DEBUG: getting latitude settings @", (str(datetime.datetime.now())))
		return float(self._latitude)

	@latitude.setter
	def latitude(self, data):
		#print ("DEBUG: setting latitude settings @", (str(datetime.datetime.now())))
		self._latitude = str(data)

	@property
	def longitude(self):
		#print ("DEBUG: getting longitude settings @", (str(datetime.datetime.now())))
		return float(self._longitude)

	@longitude.setter
	def longitude(self, data):
		#print ("DEBUG: setting longitude settings @", (str(datetime.datetime.now())))
		self._longitude = str(data)

	@property
	def timezone(self):
		#print ("DEBUG: getting timezone settings @", (str(datetime.datetime.now())))
		return float(self._timezone)

	@timezone.setter
	def timezone(self, data):
		#print ("DEBUG: setting timezone settings @", (str(datetime.datetime.now())))
		self._timezone = str(data)

	@property
	def notification_time(self):
		#print ("DEBUG: getting notification time settings @", (str(datetime.datetime.now())))
		return float(self._notif)

	@notification_time.setter
	def notification_time(self, data):
		#print ("DEBUG: setting notification time settings @", (str(datetime.datetime.now())))
		self._notif = str(data)

	@property
	def hijrical_adjustment(self):
		#print ("DEBUG: getting hijri cal adjustment settings @", (str(datetime.datetime.now())))
		return float(self._hijricaladjustment)

	@hijrical_adjustment.setter
	def hijrical_adjustment(self, data):
		#print ("DEBUG: setting hijri cal adjustment settings @", (str(datetime.datetime.now())))
		self._hijricaladjustment = str(data)

	@property
	def language(self):
		return self._language

	@language.setter
	def language(self, value):
		self._language = value

	@property
	def iconlabel_num(self):
		return self._iconlabel

	@iconlabel_num.setter
	def iconlabel_num(self, value):
		self._iconlabel = value

	@property
	def iconlabel(self):
		#print ("DEBUG: getting icon label settings @", (str(datetime.datetime.now())))
		if self.iconlabel_num == '1':
			return True
		else:
			return False

	@iconlabel.setter
	def iconlabel(self, data):
		#print ("DEBUG: setting icon label settings @", (str(datetime.datetime.now())))
		if data == True:
			self.iconlabel_num = '1'
		else:
			self.iconlabel_num = '0'

	@property
	def start_minimized_num(self):
		return self._startminimized

	@start_minimized_num.setter
	def start_minimized_num(self, value):
		self._startminimized = value

	@property
	def start_minimized(self):
		#print ("DEBUG: getting start minimized settings @", (str(datetime.datetime.now())))
		if self.start_minimized_num == '1':
			return True
		else:
			return False

	@start_minimized.setter
	def start_minimized(self, data):
		#print ("DEBUG: setting start minimized settings @", (str(datetime.datetime.now())))
		if data == True:
			self.start_minimized_num = '1'
		else:
			self.start_minimized_num = '0'

	@property
	def daylight_saving_time_num(self):
		return self._daylightsavingtime

	@daylight_saving_time_num.setter
	def daylight_saving_time_num(self, value):
		self._daylightsavingtime = value

	@property
	def daylight_saving_time(self):
		#print ("DEBUG: getting daylight saving time settings @", (str(datetime.datetime.now())))
		if self.daylight_saving_time_num == '1':
			return True
		else:
			return False

	@daylight_saving_time.setter
	def daylight_saving_time(self, data):
		#print ("DEBUG: setting daylight saving time settings @", (str(datetime.datetime.now())))
		if data == True:
			self.daylight_saving_time_num = '1'
		else:
			self.daylight_saving_time_num = '0'

	@property
	def clock_format(self):
		#print ("DEBUG: getting clock format settings @", (str(datetime.datetime.now())))
		return self._clockformat

	@clock_format.setter
	def clock_format(self, data):
		#print ("DEBUG: setting clock format settings @", (str(datetime.datetime.now())))
		self._clockformat = data

	## Function to save the options
	def save_options(self):
		print ("DEBUG: saving settings file @", (str(datetime.datetime.now())))
		config = open(os.path.expanduser('~/.silaty'), 'w')
		Text='''# Silaty Settings File

[DEFAULT]
# Location Information
city = %s
country = %s
latitude = %s
longitude = %s
timezone = %s
language = %s

# Possible Values for Calculation Methods
# Makkah
# Egypt
# Karachi
# ISNA
# MWL
calculation-method = %s

# Possible Values for Madhaheb
# Default
# Hanafi
madhab = %s

# Possible Values for Clock Format
# 24h
# 12h
clock-format = %s

# Time before prayer for notification
notif = %s

# Display Time by the indicator icon
iconlabel = %s

# Should audio notifications be enabled
audio-notifications = %s

# Should the application start minimized
minimized = %s

# Should the application use daylight saving time
daylight-saving-time = %s

# Adjust Hijri Calendar
hijrical-adjustment = %s

# Paths to the audio files
fajr-adhan = %s
normal-adhan = %s

''' %  (self.city, self.country, self.latitude, self.longitude, self.timezone, self.language, \
        self.calculation_method_name, self.madhab_name, self.clock_format, \
        self.notification_time, self.iconlabel_num, self.audio_notifications_num, self.start_minimized_num, \
        self.daylight_saving_time_num, self.hijrical_adjustment, self.fajr_adhan, self.normal_adhan)
		config.write(Text)
		config.close()
