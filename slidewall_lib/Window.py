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

from gi.repository import Gio, Gtk,Gdk,GdkPixbuf,GObject # pylint: disable=E0611
from gi.repository import AppIndicator3 as appindicator
from slidewall_engine import ConfEngine
from slidewall_engine import SlideWallEngine
from slidewall_engine import NotifyEngine
from slidewall_engine import wallbase
from slidewall_engine import liveengine
from slidewall_engine import wallclock
import logging
import os
import urllib
logger = logging.getLogger('slidewall_lib')

from . helpers import get_builder, show_uri, get_help_uri

# This class is meant to be subclassed by SlidewallWindow.  It provides
# common functions and some boilerplate.
class Window(Gtk.Window):
    __gtype_name__ = "Window"
   
    # To construct a new instance of this method, the following notable 
    # methods are called in this order:
    # __new__(cls)
    # __init__(self)
    # finish_initializing(self, builder)
    # __init__(self)
    #
    # For this reason, it's recommended you leave __init__ empty and put
    # your initialization code in finish_initializing
    
    def __new__(cls):
        """Special static method that's automatically called by Python when 
        constructing a new instance of this class.
        
        Returns a fully instantiated BaseSlidewallWindow object.
        """
        builder = get_builder('SlidewallWindow')
        new_object = builder.get_object("slidewall_window")
        new_object.finish_initializing(builder)
        return new_object

    def finish_initializing(self, builder):
        """Called while initializing this instance in __new__

        finish_initializing should be called after parsing the UI definition
        and creating a SlidewallWindow object with it in order to finish
        initializing the start of the new SlidewallWindow instance.
        """
        #copy first the data
        self.config_engine = ConfEngine.ConfigEngine()
        self.live_engine = liveengine.LiveEngine(parent = self)
        # Get a reference to the builder and set up the signals.
        self.builder = builder
        self.ui = builder.get_ui(self, True)
        
        self.AboutDialog = None # class

        self.settings = Gio.Settings("net.launchpad.slidewall")

        self.first_start = True
        if(os.path.exists(os.environ['HOME'] + '/.local/share/slidewall')):
            self.first_start = False
        #enable buttons with images on them
        bt_settings = Gtk.Settings.get_default()
        bt_settings.props.gtk_button_images = True
        bt_settings.props.gtk_menu_images = True
        
        self.wall_engine = SlideWallEngine.WallEngine()
        self.notify_engine = NotifyEngine.NotifyServer('Slidewall')
        self.wall_base = wallbase.WallBase()
        self.slide_link={}
        self.livemode_position = 'live earth'
        self.ui.cb_options.set_active(0)
        self.slide_options = {'0':'zoom','1':'scaled','2':'centered','3':'spanned','4':'stretched','5':'wallpaper'}


        # Optional Launchpad integration
        # This shouldn't crash if not found as it is simply used for bug reporting.
        # See https://wiki.ubuntu.com/UbuntuDevelopment/Internationalisation/Coding
        # for more information about Launchpad integration.
        try:
            from gi.repository import LaunchpadIntegration # pylint: disable=E0611
            LaunchpadIntegration.add_items(self.ui.helpMenu, 1, True, True)
            LaunchpadIntegration.set_sourcepackagename('slidewall')
        except ImportError:
            pass

        # Optional application indicator support
        # Run 'quickly add indicator' to get started.
        # More information:
        #  http://owaislone.org/quickly-add-indicator
        #  https://wiki.ubuntu.com/DesktopExperienceTeam/ApplicationIndicators
        #try:
            #from slidewall import indicator
            # self is passed so methods of this class can be called from indicator.py
            # Comment this next line out to disable appindicator
            #self.indicator = indicator.new_application_indicator(self)
        #except ImportError:
            #pass
        self.position = 0
        self.livemode_last = 0

        self.timer_id = 1
        self.liststore2 = Gtk.ListStore(GdkPixbuf.Pixbuf,str)
        self.liststore3 = Gtk.ListStore(GdkPixbuf.Pixbuf,str)

        self.live_engine.load_livemode_wall()
        self.wallclock_engine = wallclock.WallClock(parent = self)
        #force write config file
        if(self.first_start):
            self.on_bt_save_clicked(None)

        self.load_config_file()
        self.ui.wall_view.set_pixbuf_column(0)
        self.ui.wall_view.set_text_column(1)
        print(str(self.first_start))
        if(self.ui.r_bt_slide.get_active() and (not self.first_start) ):
            print("Going to autostart slideshow")
            #initialize timer_id but won't run now since 1 billion seconds it's quite a time
            self.timer_id = GObject.timeout_add_seconds(1000000000,self.on_slidechange_time,None)
            #now force running in the background
            self.on_bt_start_clicked(self.ui.bt_start)

            
        elif(not self.first_start) :
            print("Going to autostart live")
            self.timer_id = GObject.timeout_add_seconds(1000000000,self.on_livechange_time,None)
            #now force autostart in livemode
            self.on_bt_apply_clicked(self.ui.bt_apply, data = [self.livemode_position])
                
        #force starting in system tray if check_tray is active    
        if(self.ui.check_tray.get_active() and not self.first_start):
            #self.ui.slidewall_window.hide()
            self.ui.slidewall_window.iconify()
            self.build_tray()
            self.build_tray_first = 1

    def on_mnu_contents_activate(self, widget, data=None):
        show_uri(self, "ghelp:%s" % get_help_uri())

    def on_mnu_about_activate(self, widget, data=None):
        """Display the about box for slidewall."""
        if self.AboutDialog is not None:
            about = self.AboutDialog() # pylint: disable=E1102
            response = about.run()
            about.destroy()

    def on_mnu_close_activate(self, widget, data=None):
        """Signal handler for closing the SlidewallWindow."""
        print("menu close activated")
        self.on_bt_close_clicked(widget)
    def on_delete_event(self,widget,data=None):
        ret = self.on_bt_close_clicked(widget)
        return ret

    def on_destroy(self, widget, data=None):
        """Called when the SlidewallWindow is closed."""
        self.on_bt_close_clicked(None)
        

    def on_preferences_changed(self, settings, key, data=None):
        logger.debug('preference changedpython check if is file: %s = %s' % (key, str(settings.get_value(key))))

    def on_preferences_dialog_destroyed(self, widget, data=None):
        '''only affects gui
        
        logically there is no difference between the user closing,
        minimising or ignoring the preferences dialog'''
        logger.debug('on_preferences_dialog_destroyed')
        # to determine whether to create or present preferences_dialog
        self.preferences_dialog = None
    def slide_togled(self,widget,data=None):
        ''' when slideshow mode is togled than
            activate the timing_box'''
        logger.debug("SlideShow Mode activated")
        if(self.ui.r_bt_slide.get_active()):
            self.ui.timing_box.set_sensitive(True)
        elif(self.ui.r_bt_live.get_active()):
            self.ui.timing_box.set_sensitive(False)

    def on_bt_quit_clicked(self,widget,data=None):
        '''when this button is clicked we should save all 
           the app info and call gtk_main_quit
           '''
        #save data
        logger.debug("Going to quit the app")
        self.save_data_on_quit()
        Gtk.main_quit()
    
    def tray_view(self,widget,data=None):
        logger.debug("Showing SlideWall")
        print('tray_view::running tray_view')   
        if(self.build_tray_first):
            self.build_tray_first = False
            self.ui.slidewall_window.show()
        else:
            self.ui.slidewall_window.show()
            self.ui.slidewall_window.deiconify()
            self.ui.bt_close.set_sensitive(True)
        print('tray_view::running tray_view')   

        
        if(os.path.exists('/usr/share/icons/hicolor/48x48/apps/slidewall.png')):
            self.icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file('/usr/share/icons/hicolor/48x48/apps/slidewall.png')
        else:
            self.icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.config_engine.slidewall_data + '/media/slidewall.png')
        self.ui.slidewall_window.set_icon(self.icon_pixbuf)

    def tray_exit(self,widget,data=None):
        logger.debug("Going to close SlideWall")
        self.save_data_on_quit()
        Gtk.main_quit()
    
    def tray_icon_activated(self,widget,data=None):
        self.ui.slidewall_window.hide()
        self.ui.slidewall_window.iconify()
    
    def tray_icon_popup(self,menu):
        menu.popup()
    
    def build_tray(self):
        '''This method build the system try indicator for slidewalls'''
        print('Build_tray:::called()')
        self.tray_indicator = appindicator.Indicator.new ("slidewall",'',appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.tray_indicator.set_status (appindicator.IndicatorStatus.ACTIVE)
        
        self.tray_indicator.set_icon (self.config_engine.slidewall_data + '/media/slidewall.png')
        #agr = GtkAccelGroup().new()
        #self.ui.slidewall_window.add_accel_group(agr)

        self.__menu_tray = Gtk.Menu()

        self.menu_item_view = Gtk.ImageMenuItem("View SlideWall")
        self.menu_item_view.set_image(self.ui.img_view)
        self.menu_item_view.connect("activate",self.tray_view,self.ui)
        self.menu_item_view.show()
        self.__menu_tray.append(self.menu_item_view)

        self.menu_item_prev = Gtk.ImageMenuItem("Previous")
        self.menu_item_prev.set_image(self.ui.img_prev)
        self.menu_item_prev.connect("activate",self.on_menu_prev,self.ui)
        self.menu_item_prev.show()
        self.__menu_tray.append(self.menu_item_prev)

        self.menu_item_next = Gtk.ImageMenuItem("Next")
        self.menu_item_next.set_image(self.ui.img_next)
        self.menu_item_next.connect("activate",self.on_menu_next,self.ui)
        self.menu_item_next.show()
        self.__menu_tray.append(self.menu_item_next)

        self.menu_item_exit = Gtk.ImageMenuItem("Exit SlideWall")
        self.menu_item_exit.set_image(self.ui.img_quit)
        self.menu_item_exit.connect("activate",self.tray_exit,self.ui)
        self.menu_item_exit.show()
        self.__menu_tray.append(self.menu_item_exit)


        
    

        
        self.__menu_tray.show()
        self.tray_indicator.set_menu(self.__menu_tray)
 
             
    def on_bt_close_clicked(self,widget,data=None):
        '''Define actions to do when button Close to Tray/system Close is pressed'''
        print('on_bt_close_clicked')
        if(self.ui.check_tray.get_active()):
            self.ui.bt_close.set_sensitive(False)
            self.ui.slidewall_window.hide()
            self.ui.slidewall_window.iconify()
            self.build_tray()
            return True
        else:
           self.save_data_on_quit()
           Gtk.main_quit()
           return False
    
    def on_bt_reset_clicked(self,widget,data=None):
        '''Reset user preferences to default'''
        logger.debug("Reset user preferences to default")    
        self.ui.r_bt_slide.set_active(True)
        self.ui.r_bt_live.set_active(False)
        self.ui.adjustment3.set_value(2.5)
        self.ui.check_tray.set_active(True)
        self.ui.check_notify.set_active(True)

    def load_config_file(self):
        '''Load user preferences.Must be called in constructor'''
        logger.debug('Loading user preferences')
        # read preferences config file
        data = self.config_engine.read_config(self.config_engine.slidewall_conf_file)
        if (len(data) >0):
            self.ui.r_bt_slide.set_active(data['r_bt_slide'])
            self.ui.r_bt_live.set_active(data['r_bt_live'])
            self.ui.adjustment3.set_value(data['adjustment3']) #minutes
            self.ui.adjustment2.set_value(data['adjustment2']) #seconds
            self.ui.check_tray.set_active(data['check_tray'])
            self.ui.check_notify.set_active(data['check_notify'])
        #read slideshow mode config file    
        image_list = []
        self.slide_config = self.config_engine.read_config(self.config_engine.slidemode_conf_file)
        for iterr in self.slide_config:
             if not(iterr =='position') and not(iterr=='option'):       
                image_list =image_list + [self.slide_config[iterr] ]
        self.ui.wall_view.freeze_child_notify()
        self.ui.wall_view.set_model(None)    

        self.fill_store_from_image_list(image_list)

        self.ui.wall_view.set_model(self.liststore2)  
        self.ui.wall_view.thaw_child_notify()
        if len(self.slide_config)>0:
            self.ui.cb_options.set_active(self.slide_config['option'])
            self.position = self.slide_config['position']
        #read live mode config file    
        self.live_config = self.config_engine.read_config(self.config_engine.livemode_conf_file)
        if(len(self.live_config) > 0):
            self.livemode_position = self.live_config['position']
        else:
            self.livemode_position = "live earth"

    def on_bt_save_clicked(self,widget,data=None):
        '''Save user preferences'''
        logger.debug('Saving user preferences')
        config_dict={}
        
        config_dict['r_bt_slide'] = self.ui.r_bt_slide.get_active()
        config_dict['r_bt_live'] = self.ui.r_bt_live.get_active()
        #minutes
        config_dict['adjustment3'] = self.ui.adjustment3.get_value()
        #seconds        
        config_dict['adjustment2'] = self.ui.adjustment2.get_value()
        config_dict['check_tray'] = self.ui.check_tray.get_active()
        config_dict['check_notify'] = self.ui.check_notify.get_active()
        
        self.config_engine.write_config(config_dict)
        if(self.ui.check_autostart.get_active() ):
            self.set_autostart()
        elif(os.path.exists(self.config_engine.home_dir + '/.config/autostart/slidewall.desktop')):
            os.remove(self.config_engine.home_dir + '/.config/autostart/slidewall.desktop')


    def fill_store_from_dir(self,folder_path):
        '''Fill up wall_view with image thumbnails from folder_path''' 
        
        if not (folder_path[len(folder_path) - 1] == '/'):            
            folder_path = folder_path + '/'

        image_list = os.listdir(folder_path)
        for image in image_list:
            if os.path.isfile(folder_path + image):
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(folder_path+image,64,64)
                   
                    self.liststore2.append([pixbuf,str(image)])
                    self.slide_link[str(image)] = folder_path + image
                except Exception:
                    logger.debug(image + ' is not a image type')
            else: 
                print("Can't add:" + folder_path+image)
    
    def fill_store_from_image_list(self,image_list):
        '''Fill up wall_view with image thumbnails from image_list''' 
        for image in image_list:
            if os.path.isfile(image):
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(image,64,64)
                    basename = os.path.basename(image)
                    self.liststore2.append([pixbuf,str(basename)])
                    self.slide_link[basename] = image
                except Exception:
                    logger.debug(image + ' is not a image type')
            else: 
                print("Can't add:" + image)

    def on_bt_select_files_clicked(self,widget,data=None):
        '''Get a list with selected files and call fill_store_from_list'''
        dialog = Gtk.FileChooserDialog("Please select one or more image files", self,Gtk.FileChooserAction.OPEN,(Gtk.STOCK_CANCEL,          Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_select_multiple(True)
        filter = Gtk.FileFilter()
        filter.set_name("Images")
        filter.add_mime_type("image/png")
        filter.add_mime_type("image/jpeg")
        filter.add_mime_type("image/jpg")
        filter.add_mime_type("image/bmp")
        filter.add_mime_type("image/gif")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")     
        filter.add_pattern("*.jpeg")
        filter.add_pattern("*.bmp")
        filter.add_pattern("*.gif")   
        filter.add_pattern("*.tif")
        filter.add_pattern("*.xpm")
        dialog.add_filter(filter)
        response = dialog.run()
        img_list = []
        if response == Gtk.ResponseType.OK:
            img_list=dialog.get_filenames()
        dialog.destroy()
        self.ui.wall_view.freeze_child_notify()
        self.ui.wall_view.set_model(None)   

        self.fill_store_from_image_list(img_list)

        self.ui.wall_view.set_model(self.liststore2)  
        self.ui.wall_view.thaw_child_notify()

    def on_bt_select_folder_clicked(self,widget,data=None):
        '''Get a list with selected folder and call fill_store_from_dir'''
        dialog = Gtk.FileChooserDialog("Please select a folder wich contains image files", self,Gtk.FileChooserAction.SELECT_FOLDER,(Gtk.STOCK_CANCEL,          Gtk.ResponseType.CANCEL,Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        response = dialog.run()
        folder_list=''
        if response == Gtk.ResponseType.OK:
            folder_list=dialog.get_filename()
            print('Selected folder:' + folder_list)
        dialog.destroy()
        self.ui.wall_view.freeze_child_notify()
        self.ui.wall_view.set_model(None)    
        self.fill_store_from_dir(folder_list)
        self.ui.wall_view.set_model(self.liststore2)  
        self.ui.wall_view.thaw_child_notify()
    
    def on_bt_delete_clicked(self,widget,data=None):
        '''Remove selected items from iconview and from slide_link'''
        if('timer_id' in vars(self) or 'timer_id' in globals()) and(self.ui.r_bt_slide.get_active()):
           GObject.source_remove(self.timer_id)
           self.timer_id = 1
           logger.debug('on_bt_delete_clicked::timer removed')
        selects = self.ui.wall_view.get_selected_items()
        for select in selects:
            iterr  = self.liststore2.get_iter(select)
            datas = self.liststore2.get(iterr,0,1)
            del self.slide_link[str(datas[1])]
            self.liststore2.remove(iterr)

    def on_cb_options_changed(self,widget,data=None):
       '''Select wallpaper options '''
       tree_iter = self.ui.cb_options.get_active_iter()
       if tree_iter != None:
           model = self.ui.cb_options.get_model()
           option = model[tree_iter][0]
           #set the image for image6 object
           file_icon = self.config_engine.slidewall_data + '/media/monitor/monitor_' + option.lower() + '.png'
           self.ui.image6.set_from_pixbuf( GdkPixbuf.Pixbuf.new_from_file(file_icon))

    def on_menu_next(self,widget,data =None):
        #next wallpaper
        if(self.ui.r_bt_slide.get_active()):
            #check if position is not greatear than len(self.slide_link)
            if(self.position == (len(self.slide_link) - 1)):
                self.position = 0;
            else:
                self.position = self.position +1
            #get the wallpaper path
            key = self.wall_dict[str(self.position)]
            wallpaper = self.slide_link[key]
            #print 'position::' + str(self.position) + ' new wallpaper::' + wallpaper + ' number of photos::' + str(len(self.slide_link))
            self.wall_engine.set_wallpaper('file://' + wallpaper)
            index = self.ui.cb_options.get_active()
            self.wall_engine.set_picture_options(self.slide_options[str(index)])
            #send notification
            if(self.ui.check_notify.get_active()):
                self.notify_engine.wall_notify('Slidewall',key + ' is your new wallpaper!',self.config_engine.slidewall_data+'/media/slidewall.png')
        else:
            self.on_livechange_time()

    def on_menu_prev(self,widget,data=None):
        #previous wallpaper
        if(self.ui.r_bt_slide.get_active()):
            #check if position is not greatear than len(self.slide_link)
            if(self.position == 0):
                self.position = (len(self.slide_link) - 1)
            else:
                self.position = self.position -1
            #get the wallpaper path
            key = self.wall_dict[str(self.position)]
            wallpaper = self.slide_link[key]
            #print 'position::' + str(self.position) + ' new wallpaper::' + wallpaper + ' number of photos::' + str(len(self.slide_link))
            self.wall_engine.set_wallpaper('file://' + wallpaper)
            index = self.ui.cb_options.get_active()
            self.wall_engine.set_picture_options(self.slide_options[str(index)])
            #send notification
            if(self.ui.check_notify.get_active()):
                self.notify_engine.wall_notify('Slidewall',key + ' is your new wallpaper!',self.config_engine.slidewall_data+'/media/slidewall.png')
        else:
            self.on_livechange_time(prev=True)


   
    def on_slidechange_time(self,user_data=None):
        '''Change the wallpaper for slideshow mode'''
        #print('position::' + str(self.position))
        #check if position is not greatear than len(self.slide_link)
        if(self.position == (len(self.slide_link) - 1)):
            self.position = 0;
        else:
            self.position = self.position +1
        #get the wallpaper path
        key = self.wall_dict[str(self.position)]
        wallpaper = self.slide_link[key]
        print 'position::' + str(self.position) + ' new wallpaper::' + wallpaper + ' number of photos::' + str(len(self.slide_link))
        self.wall_engine.set_wallpaper('file://' + wallpaper)
        index = self.ui.cb_options.get_active()
        print str(index)
        if(index ==-1):
            index = 0;
            self.ui.cb_options.set_active(index)
        self.wall_engine.set_picture_options(self.slide_options[str(index)])
        #send notification
        if(self.ui.check_notify.get_active()):
            self.notify_engine.wall_notify('Slidewall',key + ' is your new wallpaper!',self.config_engine.slidewall_data+'/media/slidewall.png')
        return True

    def on_livechange_time(self,force=False,prev=False):
        '''Change the wallpaper for the live mode'''
        opt = self.livemode_position
        if(str(opt).isdigit() or (opt == None)):
            opt = 'live earth'
            self.livemode_position = 'live earth'

        if(opt == 'live earth'):
            self.download_and_set_wallpaper('http://www.opentopia.com/images/data/sunlight/world_sunlight_map_rectangular.jpg')

        elif opt == 'new wallbase' or opt == 'random wallbase':
            livemode_list = self.wall_base.get_url(opt, force)
            if not livemode_list:
                print "on_livechange_time : wallbase returned a zero length list!"
                return True
            if(self.livemode_last == len(livemode_list) - 1) and not force:
                self.livemode_last = 0
                print("on_livechange_time : wallbase ::All pictures have been used, fetching new list!")
                return self.on_livechange_time(force=True)
            
            if prev and self.livemode_last > 1:
                self.livemode_last -= 2
            self.livemode_last += 1

            if not self.download_and_set_wallpaper(livemode_list[self.livemode_last-1]) and not force:
                self.livemode_last = 0
                return self.on_livechange_time(force=True)

        else:
            print 'Window::livechange()::called'
            self.wallclock_engine.update(basename = self.live_engine.storee[opt])
        #Return True so gobject keep going
        return True


    def download_and_set_wallpaper(self, url):
        '''download wallpaper and save it on /home/user/.local/share/slidewall/live/slidewallslidemode.jpg'''

        livemode_path = self.config_engine.home_dir + '/' + self.config_engine.share_dir + '/slidewall/live/slidewall.jpg'
        print "download_and_set_wallpaper ::" ,self.livemode_last, url
        try:
            site = urllib.urlopen(url)
            if site.getcode() != 200:
                print("write_url_to_target :: url failed(code!=200)")
                return False
            buff = site.read()
            stream = open(livemode_path,'w')
            stream.write(buff)
            #set wallpaper
            self.wall_engine.set_wallpaper('file://' + livemode_path)
            self.wall_engine.set_picture_options('zoom')
            return True
        except:
            print 'download_and_set_wallpaper :: ERROR on url: ', url
            self.notify_engine.wall_notify('Slidewall','Please check your internet connection!\nOr maybe wallbase.cc is down!',self.config_engine.slidewall_data+'/media/slidewall.png')
            return False


    def on_bt_start_clicked(self,widget,data=None):
        '''start the slideshow'''
        self.ui.r_bt_slide.set_active(True)
        if(len(self.slide_link) <=0):
            # dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.OK, "SlideWall Error")
            # dialog.format_secondary_text("You need at least one image!")
            # dialog.run()
            # dialog.destroy() 
            return None   
        if('timer_id' in vars(self) or 'timer_id' in globals()):
           GObject.source_remove(self.timer_id)
           self.timer_id = 1

        #compute seconds
        seconds = self.ui.adjustment3.get_value() * 60
        seconds = seconds + self.ui.adjustment2.get_value()
        #build position iterator
        count = -1
        self.wall_dict = {}
        for key in self.slide_link:
            count = count + 1
            self.wall_dict[str(count)] = key    
        print('Going to change wallpaper at every::' + str(seconds)  + ' seconds'  + ' position::' + str(self.position))
        #force on_slidechange_time first
        if(int(seconds)< 40):
            dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.WARNING,Gtk.ButtonsType.OK, "SlideWall Warning")
            dialog.format_secondary_text("Because of performance reasons SlideShow Mode can't have a timer below 40 seconds")
            dialog.run()
            dialog.destroy()
            seconds = 40
            self.ui.adjustment3.set_value(0)
            self.ui.adjustment2.set_value(40)

         
        self.on_slidechange_time(None)  
        self.timer_id = GObject.timeout_add_seconds(int(seconds),self.on_slidechange_time,None)

    
    def save_data_on_quit(self):
        self.on_bt_save_clicked(None)
        #remove timer if it is running
        if('timer_id' in vars(self) or 'timer_id' in globals()):
            GObject.source_remove(self.timer_id)
            self.timer_id = 1
        #save self.slide_config
        self.slide_config={}
        self.slide_config['position'] = self.position
        self.slide_config['option'] = self.ui.cb_options.get_active()
        self.slide_config = dict(self.slide_config.items() + self.slide_link.items() )
        self.config_engine.write_config_in_file(self.slide_config,self.config_engine.slidemode_conf_file)

        #save live mode
        self.live_config = {}
        #get the selected option
        self.live_config['position'] = self.livemode_position
        self.config_engine.write_config_in_file(self.live_config,self.config_engine.livemode_conf_file)


    def on_live_view_clicked(self,widget,data=None):
        datas = self.live_engine.get_selected()
        textbuffer = self.ui.text_info.get_buffer()
        if(datas == 'live earth'):
            textbuffer.set_text("This option check every 20 minutes www.opentopia.com for the sunlight map.")
        elif(datas == 'new wallbase'):
            textbuffer.set_text("This option check every 15 minutes www.wallbase.cc for the newest wallpapers.")
        elif(datas =='random wallbase'):
            textbuffer.set_text("This option check every 15 minutes www.wallbase.cc for random wallpapers.")
        else:
            textbuffer.set_text("This wallpaper clock will be changing every minute.")

    def on_bt_apply_clicked(self,widget,data=None):
        self.ui.r_bt_live.set_active(True)
        if( data != None ):
            self.livemode_position = data[0]
        else :
            self.livemode_position = self.live_engine.get_selected()
        opt = self.livemode_position
        print(opt)
        if(opt == 'live earth'):
            #send notification
            if(self.ui.check_notify.get_active()):
                print("Sending notification 0!")
                self.notify_engine.wall_notify('Slidewall','Slidewall will update every 20 minutes your sunlight map',self.config_engine.slidewall_data+'/media/slidewall.png')
            if('timer_id' in vars(self) or 'timer_id' in globals()):
                GObject.source_remove(self.timer_id)
                self.timer_id = 1

            self.on_livechange_time()  
            self.timer_id = GObject.timeout_add_seconds(1200,self.on_livechange_time) #20 minutes
                
        elif(opt == 'new wallbase'):
            print("Sending notification 1!")
            #send notification
            if(self.ui.check_notify.get_active()):
                self.notify_engine.wall_notify('Slidewall','Slidewall will set every 15 minutes the newest wallpaper from wallbase.cc\nIf it is the first time you run this option on this session please be patient,it will take a while!',self.config_engine.slidewall_data+'/media/slidewall.png')
            if('timer_id' in vars(self) or 'timer_id' in globals()):
                GObject.source_remove(self.timer_id)
                self.timer_id = 1
            self.on_livechange_time()  
            self.timer_id = GObject.timeout_add_seconds(900,self.on_livechange_time) #15 minutes
        elif(opt == 'random wallbase'):
            print("Sending notification 2!")
            #send notification
            if(self.ui.check_notify.get_active()):
                self.notify_engine.wall_notify('Slidewall','Slidewall will set every 15 minutes a random wallpaper from wallbase.cc\nIf it is the first time you run this option on this session please be patient,it will take a while!',self.config_engine.slidewall_data+'/media/slidewall.png')
            if('timer_id' in vars(self) or 'timer_id' in globals()):
                GObject.source_remove(self.timer_id)
                self.timer_id = 1
            self.on_livechange_time()  
            self.timer_id = GObject.timeout_add_seconds(900,self.on_livechange_time) #15 minutes
        else:
            print("Sending notification 3!")
            #send notification
            if(self.ui.check_notify.get_active()):
                self.notify_engine.wall_notify('Slidewall','Slidewall will will update your clock every minute!',self.config_engine.slidewall_data+'/media/slidewall.png')
            if('timer_id' in vars(self) or 'timer_id' in globals()):
                GObject.source_remove(self.timer_id)
                self.timer_id = 1
            self.on_livechange_time()
            #call sync  
            import time
            sync = 60 - int(time.strftime("%S"))
            print 'Window::on_bt_apply_clicked()::going live in ' + str(sync) + ' seconds'
            self.timer_id = GObject.timeout_add_seconds(sync,self.sync_clock) #remaining seconds till the next minute


    def sync_clock(self,user_data = None):
        '''When you run a wallclock for the first time you need to make a sync.For example you start a wall clock
        at 12:15 AM but the problem is you didn't start at 12:15:00 maybe you start at 12:15:30 or something else.So it will be
        a bad thing to update the clock at 12:16:30.That's why you make this sync so that the next time it update exactly at 
        XX:XX:00 every time.'''
        if('timer_id' in vars(self) or 'timer_id' in globals()):
            GObject.source_remove(self.timer_id)
            self.timer_id = 1
        print('Window::sync_clock()::called')
        self.on_livechange_time()
        self.timer_id = GObject.timeout_add_seconds(60,self.on_livechange_time) #1 minute      
        #don't get back here
        return False
    def set_autostart(self):
        '''Enable Slidewall to start when Ubuntu starts.Just copy slidewall.desktop
        in /home/user/.config/autostart and Slidewall will autostart.'''
        desktop = '[Desktop Entry]\nName=Slidewall\nComment=Slidewall application\nCategories=GNOME;Utility;\nExec=/opt/extras.ubuntu.com/slidewall/bin/slidewall\nIcon=/opt/extras.ubuntu.com/slidewall/share/slidewall/media/slidewall.svg\nTerminal=false\nType=Application\n'
        autostart = open(self.config_engine.home_dir + '/.config/autostart/slidewall.desktop','w')
        autostart.write(desktop)
        autostart.close()

    def on_bt_add_clock_clicked(self, widget, data = None):
        '''Import wallclock's '''
        self.wallclock_engine.import_wallclock_dialog(parent = self)

    def on_bt_del_clock_clicked(self,widget, data = None ):
        '''Remove selected bins from LiveMode but except live eart,new wallbase, random wallbase, clock radarblue and
        clock goldflame'''
        ret = self.live_engine.remove_bin(widget,data)
        if(ret == True):
            self.notify_engine.wall_notify('Slidewall','Slidwall would not work as expected without this widget!',self.config_engine.slidewall_data+'/media/slidewall.png')