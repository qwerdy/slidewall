
import threading
import os
from shutil import copytree
from slidewall_engine import ConfEngine

class CopyThread ( threading.Thread ):
    def __init__(self, parent):
        self.parent = parent
        threading.Thread.__init__(self)
        

    def run ( self ):
        self.config_engine = ConfEngine.ConfigEngine()
        if(not os.path.isdir(self.config_engine.slidewall_live_dir + '/lcd_blue')):
            copytree(self.config_engine.find_data_folder() + '/media/lcd_blue',self.config_engine.slidewall_live_dir + '/lcd_blue')
        if(not os.path.isdir(self.config_engine.slidewall_live_dir + '/goldflame')):
            copytree(self.config_engine.find_data_folder() + '/media/goldflame',self.config_engine.slidewall_live_dir + '/goldflame')
        if(not os.path.isdir(self.config_engine.slidewall_live_dir + '/soundwave')):
            copytree(self.config_engine.find_data_folder() + '/media/soundwave',self.config_engine.slidewall_live_dir + '/soundwave')
        if(not os.path.isdir(self.config_engine.slidewall_live_dir + '/radarblue')):
            copytree(self.config_engine.find_data_folder() + '/media/radarblue',self.config_engine.slidewall_live_dir + '/radarblue')
        #update slidewall
        self.parent.load_livemode_wall()
