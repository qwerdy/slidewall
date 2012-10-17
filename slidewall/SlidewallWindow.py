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

import gettext
from gettext import gettext as _
gettext.textdomain('slidewall')

from gi.repository import Gtk # pylint: disable=E0611
import logging
logger = logging.getLogger('slidewall')

from slidewall_lib import Window
from slidewall.AboutSlidewallDialog import AboutSlidewallDialog

# See slidewall_lib.Window.py for more details about how this class works
class SlidewallWindow(Window):
    __gtype_name__ = "SlidewallWindow"
    
    def finish_initializing(self, builder): # pylint: disable=E1002
        """Set up the main window"""
        super(SlidewallWindow, self).finish_initializing(builder)

        self.AboutDialog = AboutSlidewallDialog
        # Code for other initialization actions should be added here.
    
   
        
