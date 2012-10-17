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
import os
import logging
import shelve
class ConfigEngine:
    '''This class is will help to load/store
        user preferences'''

    def __init__(self):
        self.home_dir = os.environ['HOME']
        self.share_dir = '.local/share'
        self.app_dir = 'slidewall'
        self.config_dir = 'config'
        self.slide_dir = 'slideshow'
        self.live_dir = 'live'
        self.conf_file = "slidewall"
        self.logger = logging.getLogger('slidewall_engine')
        #check if slidewall_dir exist if not then create it
        self.slidewall_dir = self.home_dir + '/' + self.share_dir + '/' + self.app_dir
        self.make_dir(self.slidewall_dir)
        #check if config folder exist else create it
        self.slidewall_config_dir = self.slidewall_dir + '/' + self.config_dir
        self.make_dir(self.slidewall_config_dir)
        #check if slideshow folder exist else create it
        self.slidewall_slide_dir = self.slidewall_dir + '/' + self.slide_dir
        self.make_dir(self.slidewall_slide_dir)
        #check if live folder exist else create it
        self.slidewall_live_dir = self.slidewall_dir + '/' + self.live_dir
        self.make_dir(self.slidewall_live_dir)
        #check if slidewall.conf exist
        self.slidewall_conf_file = self.slidewall_config_dir + '/' + self.conf_file
        self.slidemode_conf_file = self.slidewall_config_dir + '/slidemode'
        self.livemode_conf_file = self.slidewall_config_dir + '/livemode'
        #self.make_file(self.slidewall_conf_file)

        self.slidewall_data = self.find_data_folder()
        
    def make_dir(self,folder):
        '''This method check for the specified folder
            and if it not exist than create it'''
        if not os.path.exists(folder):
            os.mkdir(folder)
            self.logger.debug('Creating dir:' + folder)

    def make_file(self,conf_file):
        '''This method check if a file exist and if not it will create it'''
        print('make_file:' + conf_file)
        if not (os.path.exists(conf_file) and os.path.isfile(conf_file)):
            fo = open(conf_file, "w")
            fo.close()
            self.logger.debug('Creating file:' +conf_file )

    def write_config(self,config_dict):
        '''This method will write a dictionary in a shelve file
        '''
        conf_file = shelve.open(self.slidewall_conf_file)
        for key, value in config_dict.items():
            conf_file[key]=value
        conf_file.close()
    def write_config_in_file(self,config_dict,shelve_path):
        '''This method will write a dictionary in specified  shelve file
        '''
        #print 'write_config_in_file::' 
        #print config_dict
        #remove the old shelve 
        if os.path.exists(shelve_path):
            os.remove(shelve_path)
            #print 'write_config_in_file removed::' + shelve_path
        conf_file = shelve.open(shelve_path)
        for key, value in config_dict.items():
            conf_file[key]=value
        conf_file.close()
        
    def read_config(self,config_dict):
        '''This method will read and return a dictionary stored in shelve file'''
        if(os.path.exists(config_dict)):    
            data=shelve.open(config_dict)
            return data
        else:   
            data={}
            return data
        

    def print_dict(self,data):
        '''Just for debugging purpose.It will print out a dictionary'''
        print("dictionary...")
        for key,value in data.items():
            print(key + ":" + str(value) + "\n")
            
    def print_shelve(self,shelve_file):
        '''Just for debugging purpose.It will print out a shelve'''
        data = shelve.open(shelve_file)
        print("shelve...")
        for key,value in data.items():
            print(key + ":" + str(value) + "\n")
    
    def find_data_folder(self):
        if(os.path.exists('/opt/extras.ubuntu.com/slidewall/share/')):
            return '/opt/extras.ubuntu.com/slidewall/share/slidewall'
        elif(os.path.exists('/usr/share/slidewall/')):
            return '/usr/share/slidewall'
        elif(os.path.exists('/usr/local/share/slidewall')):
            return '/usr/share/local/share/slidewall'
        elif(os.path.exists(os.getcwd() + '/data')):
            return os.getcwd() + '/data'
        else:
            return ''
        
