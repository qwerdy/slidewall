import urllib
import re
class WallBase:
    def __init__(self):
        self.wallbase_url = 'http://wallbase.cc/search/'

        self.wallbase_newest_url = 'http://wallbase.cc/search/'

        self.wallbase_random_url = 'http://wallbase.cc/random/'

        self.wallbase_search_url = '/0/213/eqeq/0x0/0/1/1/0/60/relevance/desc/wallpapers'
        self.new_returnlist = {}
        self.ran_returnlist = {}
        self.sea_returnlist = {}

    def get_searched_url(self,tag):
        self.final_url = self.wallbase_url + tag + self.wallbase_search_url
        if(len(self.sea_returnlist) <= 0 ):
            self.final_url = self.wallbase_newest_url
            f = urllib.urlopen(self.final_url)
            s = f.read()
            counter = -1;
            for line in s.split('\n'):
                if('http://wallbase.cc/wallpaper/' in line):
                    value = line[line.find("http://wallbase.cc/wallpaper/"):line.find('" id="')]
                    #print value
                    ff = urllib.urlopen(value)
                    ss = ff.read()
                    for lline in ss.split('\n'):
                        if('<img src="http://' in lline) and ('.jpg' in lline) and (' alt='  in lline):
                            vvalue = lline[lline.find('<img src="http://')+10 :lline.find('" alt="')]
                            #print "::::::::::::::::::" + vvalue
                            counter = counter + 1
                            self.sea_returnlist[str(counter)]= vvalue
            #print self.sea_returnlist
            return self.sea_returnlist
        else:
            return self.sea_returnlist

    def get_newest_url(self):
        if(len(self.new_returnlist) <= 0 ):
            self.final_url = self.wallbase_newest_url
            f = urllib.urlopen(self.final_url)
            s = f.read()
            counter = -1;
            for line in s.split('\n'):
                if('http://wallbase.cc/wallpaper/' in line):
                    value = line[line.find("http://wallbase.cc/wallpaper/"):line.find('" id="')]
                    #print value
                    ff = urllib.urlopen(value)
                    ss = ff.read()
                    for lline in ss.split('\n'):
                        if('<img src="http://' in lline) and ('.jpg' in lline) and (' alt='  in lline):
                            vvalue = lline[lline.find('<img src="http://')+10 :lline.find('" alt="')]
                            #print "::::::::::::::::::" + vvalue
                            counter = counter + 1
                            self.new_returnlist[str(counter)]= vvalue
            #print self.new_returnlist
            return self.new_returnlist
        else:
            return self.new_returnlist
                
            
        
        

    def get_random_url(self):
        if(len(self.ran_returnlist) <= 0 ):
            self.final_url = self.wallbase_random_url
            f = urllib.urlopen(self.final_url)
            s = f.read()
            counter = -1;
            #p =re.compile("http://[^[:space:]]*")
            for line in s.split('\n'):
                if('http://wallbase.cc/wallpaper/' in line):
                    value = line[line.find("http://wallbase.cc/wallpaper/"):line.find('" id="')]
                    #print value
                    ff = urllib.urlopen(value)
                    ss = ff.read()
                    for lline in ss.split('\n'):
                        if('<img src="http://' in lline) and ('.jpg' in lline) and (' alt='  in lline):
                            vvalue = lline[lline.find('<img src="http://')+10 :lline.find('" alt="')]
                            #print "::::::::::::::::::" + vvalue
                            counter = counter + 1
                            self.ran_returnlist[str(counter)]= vvalue
            #print self.ran_returnlist
            return self.ran_returnlist
        else:
            return self.ran_returnlist

         
