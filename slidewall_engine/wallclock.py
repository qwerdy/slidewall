# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2012 fioan89@gmail.com <fioan89@gmail.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE


#Credit goes to Natan Yellin from  WallpaperClockScreenlet.This module is based almost entirely on his work

from gi.repository import Gtk
import decimal
import math
import os
import random
import time
import ConfigParser

from slidewall_engine import ConfEngine
from slidewall_engine import NotifyEngine

from commands import getoutput
from datetime import datetime
from sys import path

from gi.repository import Gio

try:
	import Image
except:
	import sys
	print "Please make sure you have installed python image module"
	sys.exit()

class WallClock:
	clock_settings = 'com.canonical.indicator.datetime'
	def __init__(self,parent):
		self.parent = parent
		self.time = datetime.now()
		self.timeout = None
		self.dec = decimal.Decimal
		self.image = None
		self.image1 = None	
		self.current_file_index = 0
		
		self.month = ''
		self.day = ''
		self.hour = ''
		self.minute = ''
		self.weekday = ''

		self.settings = Gio.Settings.new(self.clock_settings)
		self.hour_format = '12'
		if(self.isFormat24()):
			self.hour_format = '24'

		


	def import_wallclock_dialog(self, parent = None):
		''' Show a dialog wich let you choose a .wcz file and install
		it in /home/user/.local/share/slidewall/live/<name_of_the_wcz>'''

		filter = Gtk.FileFilter()
		filter.add_pattern('*.wcz')

		dlg = Gtk.FileChooserDialog(buttons=(Gtk.STOCK_CANCEL, 
			Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		dlg.set_current_folder(os.environ['HOME'])
		dlg.set_title('Import Wallpaper Clock (.wcz package)')
		dlg.set_filter(filter)
		
		resp		= dlg.run()
		filename	= dlg.get_filename()
		dlg.destroy()
		if resp == Gtk.ResponseType.OK:
			self.install (filename)
			#update livemode
			self.clear_icon_view(parent.live_view, parent.live_engine)
			parent.live_engine.load_livemode_wall()

	def install(self,path):
		"""Extract the .wcz archive"""
		filename = path
		basename	= os.path.basename(filename)
		extension	= str(filename)[-3:]

		unzip_command = 'unzip -o %s -d %s'
		config_engine = ConfEngine.ConfigEngine()
        notify_engine = NotifyEngine.NotifyServer('Slidewall')
		if extension.lower() == 'wcz':
			if not os.path.isdir(self.parent.config_engine.slidewall_live_dir + '/' + basename):
				os.mkdir(self.parent.config_engine.slidewall_live_dir + '/' + basename)
			os.system(unzip_command % (chr(34) + filename + chr(34),
				self.parent.config_engine.slidewall_live_dir + '/' + basename))
			notify_engine.wall_notify('Slidewall','Wallpaper clock imported!',config_engine.slidewall_data+'/media/slidewall.png')
			return True
		else:
			notify_engine.wall_notify('Slidewall','Wallpaper clock could not be imported!File must be invalid',config_engine.slidewall_data+'/media/slidewall.png')
			return False

	def clear_icon_view(self, iconview, live_engine):
		'''Clear all the widgets from iconview '''
		live_engine.remove_bin(widget = None, data = None)


	def isFormat24(self):
		'''Check if ubuntu time format is 24 hour'''
		value = self.settings.get_string("time-format")
		if value == '24-hour':
			return True
		return False
	def position(self, now=None): 
		dec = decimal.Decimal
		if now is None: 
			now = datetime.now()

		diff = now - datetime(2001, 1, 1)
		days = dec(diff.days) + (dec(diff.seconds) / dec(86400))
		lunations = dec("0.20439731") + (days * dec("0.03386319269"))

		return lunations % dec(1)

	def phase(self, pos): 
		dec = decimal.Decimal
		index = (pos * dec(8)) + dec("0.5")
		index = math.floor(index)
		return [("New Moon"),("Waxing Crescent"),("First Quarter"),("Waxing Gibbous"),("Full Moon"),("Waning Gibbous"),("Last Quarter"),("Waning Crescent")][int(index) & 7]

	def get_zodiac(self, day, month):
		"""Finds the zodiac and returns it."""
		# all zodiacs in order of the monthss
		zodiac = [('Capricorn'), ('Aquarius'),
			('Pisces'), ('Aries'), ('Taurus'),
			('Gemini'), ('Cancer'), ('Leo'),
			('Virgo'), ('Libra'), ('Scorpio'),
			('Sagittarius')]
		
		# the midpoints each month where one zodiac
		# ends and the next begins, in month order
		midpoint = [19, 18, 20, 19, 20,
			20, 22, 22, 22, 22, 21, 21]
				
		# deal with december where we need to wrap
		# around to the first zodiac
		if month == 12 and day > midpoint[month-1]:
			return zodiac[0]
		
		# if it's the first half of the month,
		# return the appropriate zodiac
		elif day <= midpoint[month-1]:
			return zodiac[month-1]
		
		# if it's the second half of the month,
		# return the next zodiac in the list
		else:
			return zodiac[month]

	def get_day (self):
		"""Only needed for the service."""
		return self.time.strftime("%d")
		
	def get_month (self):
		"""Only needed for the service."""
		return self.time.strftime("%m")
		
	def get_hour24 (self):
		"""Only needed for the service."""
		return self.time.strftime("%H")
		
	def get_hour (self):
		"""Only needed for the service."""
		if self.hour_format == '24' :
			return self.time.strftime("%H")
		elif self.hour_format == '12' :
			return self.time.strftime("%I")
			
	def get_minute (self):
		"""Only needed for the service."""
		return self.time.strftime("%M")
		
	def get_weekday (self):
		"""Only needed for the service."""
		return self.time.strftime("%w")
		
	def get_year (self):
		"""Only needed for the service."""
		return self.time.strftime("%y")

	def set_image(self,basename):
		'''Build image and save it in /home/<user>/.local/share/slidewall/live/slidewall.png'''
		#print "Point 1: " +str(time.localtime())
		#print "Point 1: " +str(datetime.now())
		if basename!= '':
			# load the background image and determine the path
			try:
				self.image = Image.open( basename+'/bg.jpg')
				path = basename
			except:
				self.parent.parent.notify_engine.wall_notify('WallClock cant find' + basename ,self.parent.config_engine.slidewall_data+'/media/slidewall.png')
				path = ''
			
			# load the am/pm image and paste it onto the background
			if self.hour_format == '12' and os.path.isfile(path + '/am.png'):
				print 'is 12 hour format and there is a am.png file'
				try:
					if int(self.get_hour24())> 12:
						print 'setting pm'
						self.image1 = Image.open(path + '/pm.png')
						self.image.paste(self.image1, (0,0), self.image1)
					else:
						print 'setting am'
						self.image1 = Image.open(path + '/am.png')
						self.image.paste(self.image1, (0,0), self.image1)
						#self.hour = str(int(self.hour)/2)
				except:
					try:
						self.image1 = self.image1.convert('RGBA')
						self.image.paste(self.image1, (0,0), self.image1)
					except:
						pass
					

			# load the other images and paste them onto the background
			for img in ("minute", "hour", "day", "month", "weekday"):
				try:
					self.image1 = Image.open(path + '/' + img + getattr(self, img) + '.png')
					print('image::' + img)
					self.image.paste(self.image1, (0,0), self.image1)
				except:
					try:
						self.image1 = self.image1.convert('RGBA')
						self.image.paste(self.image1, (0,0), self.image1)
					except:
						pass
			
			# save the file to the location we just selected. this is a slow operation
			self.image.save(self.parent.config_engine.slidewall_live_dir + '/slidewall.png')
			
	def update(self,basename = None):
		print 'WallClock::update()'
		dec = decimal.Decimal
		
		self.time = datetime.now()
		
		self.minute = self.get_minute()
		self.hour = self.get_hour()
		self.day = self.get_day()
		self.month = self.get_month()
		self.year = self.get_year()
		
		self.hour24 = self.get_hour24()
		self.weekday = self.get_weekday()
		
		pos = self.position()
		self.moon = int(((float(pos))*100)/3.333333) +1
		self.moon = str(self.moon)
		phasename = self.phase(pos)
		self.zodiac = self.get_zodiac(int(self.day),int(self.month))
		
		config = ConfigParser.RawConfigParser()
		config.read(basename+'/clock.ini')
		refreshhourinterval = config.getint('Settings', 'refreshhourinterval')
		hourimages = config.getint('Settings', 'hourimages')
		ampmenabled = config.getint('Settings', 'ampmenabled')
		if ampmenabled == 0:
			self.hour = str(((int(self.hour24) * 60 + int(self.minute)) / refreshhourinterval) % hourimages)
		elif ampmenabled == 1 and self.hour_format == '12':
			self.hour = str(((int(self.hour) * 60 + int(self.minute)) / refreshhourinterval) % hourimages)

		if self.month[0] == '0': 
			self.month = self.month[1]
		
		if self.day[0] == '0': 
			self.day = self.day[1]

		if self.hour[0] == '0':
			if len(str(self.hour)) == 2:
				self.hour = self.hour[1]
			if len(str(self.hour)) == 1:
				self.hour = self.hour[0]
		if int(self.hour)>60:
			self.hour = str(int(self.hour)-60)
		
		if self.minute[0] == '0':
			self.minute = self.minute[1]

		if self.weekday == '0': 
			self.weekday = '7'

		self.set_image (basename)
		self.parent.wall_engine.set_wallpaper('file://' + self.parent.config_engine.slidewall_live_dir + '/slidewall.png')
		self.parent.wall_engine.set_picture_options('stretched')
		return True

			
