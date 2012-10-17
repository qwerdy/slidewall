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
from gi.repository import Gio

class WallEngine:
    """
        Allow you to set wallpaper for the unity desktop
    """
    #path in gsettings registry for background
    __background_path = "org.gnome.desktop.background" 

    def __init__(self):
        self.settings = Gio.Settings.new(self.__background_path)

    def get_wallpaper(self):
        """
            Return the path of the current wallpaper
        """
        value = self.settings.get_string("picture-uri")
        return value

    def get_picture_options(self):
        """
            Return how the background wallpaper is rendered.
            Values : none,wallpaper,centered,scaled,
            stretched,zoom,spanned
        """
        value = self.settings.get_string("picture-options")
        return value

    def set_wallpaper(self,image_uri=""):
        """
            Set a wallpaper for the background.The parameter
            is uri so it should be like:
                file:///home/user/Picture/some_picture.png
        """
        if image_uri.find("file:///"):
            raise Exception('Path ' +image_uri + ' does not follow this format: file:///path_to_image') 
        else:                  
            self.settings.set_string("picture-uri",image_uri)

    def set_picture_options(self,option="stretch"):
        """
            Set how the background wallpaper is rendered.
            Values : none,wallpaper,centered,scaled,
            stretched,zoom,spanned
        """
        if option not in ["none","wallpaper","centered","scaled","stretched","zoom","spanned"]:
            raise Exception("Option " + option +" is not in this list:none,wallpaper,centered,scaled,stretched,zoom,spanned")
        else:
            self.settings.set_string("picture-options",option)
            
                
