import os
import logging
from shutil import copytree
from shutil import rmtree
from gi.repository import Gtk,GdkPixbuf,GObject

logger = logging.getLogger('slidewall_lib')

class LiveEngine():
    def __init__(self,parent = None):
        self.parent = parent
        if(not os.path.isdir(self.parent.config_engine.slidewall_live_dir + '/lcd_blue')):
            copytree(self.parent.config_engine.find_data_folder() + '/media/lcd_blue',self.parent.config_engine.slidewall_live_dir + '/lcd_blue')
        if(not os.path.isdir(self.parent.config_engine.slidewall_live_dir + '/goldflame')):
            copytree(self.parent.config_engine.find_data_folder() + '/media/goldflame',self.parent.config_engine.slidewall_live_dir + '/goldflame')
        if(not os.path.isdir(self.parent.config_engine.slidewall_live_dir + '/soundwave')):
            copytree(self.parent.config_engine.find_data_folder() + '/media/soundwave',self.parent.config_engine.slidewall_live_dir + '/soundwave')
        if(not os.path.isdir(self.parent.config_engine.slidewall_live_dir + '/radarblue')):
            copytree(self.parent.config_engine.find_data_folder() + '/media/radarblue',self.parent.config_engine.slidewall_live_dir + '/radarblue')
        

    def load_livemode_wall(self):
        '''Load default livewall's for slidewall at startup'''
        sc = self.parent.config_engine.slidewall_data
        print '\n\n\n\n\n\tLoading...\n\n\n'
        #we must load the default ones and then search the local share folder for the wallclock's
        self.storee={'live earth': sc + '/media/map.png','new wallbase': sc + '/media/new.png','random wallbase': sc + '/media/random.png'}
        print str(self.storee)  + ' \n\n\t with keys:' + str(self.storee.keys())
        for image in self.storee.keys():
            try:
                print "Loading::" + self.storee[str(image)]
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.storee[image],100,100)
                self.parent.liststore3.append([pixbuf,image])
            except Exception:
                logger.debug(image + ' is not a image type')

        #load other clocks from loca share
        path = self.parent.config_engine.slidewall_live_dir 
        lists = os.listdir(path)
        print 'liveengine::lists of clocks' + str(lists)
        for clock in lists:
            if(os.path.isdir(path + '/' + clock)):
                try:
                    #print "Loading::" + storee['clock lcd_blue']
                    image = 'clock ' + clock
                    self.storee[image] = path + '/' + clock
                    print "Loading::" + self.storee[image]
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(self.storee[image]+'/preview200x150.jpg',100,100);
                    self.parent.liststore3.append([pixbuf,image])
                except Exception:
                    logger.debug(image + ' is not a image type')      

        self.parent.ui.live_view.set_model(self.parent.liststore3)
        self.parent.ui.live_view.thaw_child_notify()
        self.parent.ui.live_view.set_pixbuf_column(0)
        self.parent.ui.live_view.set_text_column(1)

    def remove_bin(self,widget,data=None):
        '''Remove selected items from liveview and from storee.It will return true if the user is trying to remove
        default bins.It will help if you  want to notify him'''
        #this one should be moved in on_bt_delete
        if('timer_id' in vars(self.parent) or 'timer_id' in globals()) and(self.parent.ui.r_bt_live.get_active()):
           GObject.source_remove(self.parent.timer_id)
           self.parent.last_position = 'live earth'
           self.parent.timer_id = -1
           print('Removed timer id')
           logger.debug('on_bt_delete_clicked::timer removed')

        selects = self.parent.ui.live_view.get_selected_items()
        for select in selects:
            iterr  = self.parent.liststore3.get_iter(select)
            datas = self.parent.liststore3.get(iterr,0,1)
            if(not datas[1] in ['live earth', 'new wallbase', 'random wallbase', 'clock radarblue', 'clock goldflame', 'clock soundwave']):
                del self.storee[str(datas[1])]
                self.parent.liststore3.remove(iterr)
                #remove from local store
                name = datas[1][6:]
                path = self.parent.config_engine.slidewall_live_dir
                fullpath = path + '/' + name
                print("Going to remove "  + fullpath)
                rmtree(fullpath) 
                return False
            else:
               return True

    def get_selected(self):
        '''Return the text from livew_view'''

        selects = self.parent.ui.live_view.get_selected_items()
        for select in selects:
            iterr  = self.parent.liststore3.get_iter(select)
            datas = self.parent.liststore3.get(iterr,0,1)
            print 'liveengine::get_selected()::selected item:' + str(datas[1])
            return datas[1]

