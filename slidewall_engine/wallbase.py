import urllib
import re
class WallBase:
    def __init__(self):
        self.wallbase_url = 'http://wallbase.cc/search/'

        self.wallbase_newest_url = 'http://wallbase.cc/search/'

        self.wallbase_random_url = 'http://wallbase.cc/random/2/eqeq/0x0/0x0/000/20'

        self.wallbase_search_url = '/0/213/eqeq/0x0/0/1/1/0/60/relevance/desc/wallpapers'
        self.new_returnlist = {}
        self.ran_returnlist = {}
        self.sea_returnlist = {}

    def wtf_wallbase(self,a):
        b = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
        k = 0
        n = []
        a_len = len(a)
        while(k < a_len):
            f = b.find(a[k])
            k += 1
            g = b.find(a[k])
            k += 1
            h = b.find(a[k])
            k += 1
            i = b.find(a[k])
            k += 1
            j = f << 18 | g << 12 | h << 6 | i
            c = j >> 16 & 255
            d = j >> 8 & 255
            e = j & 255
            if h == 64:
                n.append(chr(c))
            elif i == 64:
                n.append(chr(c) + chr(d))
            else:
                n.append(chr(c) + chr(d) + chr(e))
        return ''.join(n)

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
                    ff = urllib.urlopen(value)
                    ss = ff.read()
                    bb = ss.find("+B('")
                    if bb:
                        counter += 1
                        real_url = self.wtf_wallbase(ss[bb+4 : ss.find("'", bb+4)])
                        #print real_url
                        self.ran_returnlist[str(counter)] = real_url
            #print self.sea_returnlist
            return self.sea_returnlist
        else:
            return self.sea_returnlist

    def get_newest_url(self, force=False):
        print "get_newest_url :: forcing: %s" % force
        if(force or len(self.new_returnlist) <= 0 ):
            self.final_url = self.wallbase_newest_url
            f = urllib.urlopen(self.final_url)
            s = f.read()
            counter = -1;
            for line in s.split('\n'):
                if('http://wallbase.cc/wallpaper/' in line):
                    value = line[line.find("http://wallbase.cc/wallpaper/"):line.find('" id="')]
                    ff = urllib.urlopen(value)
                    ss = ff.read()
                    bb = ss.find("+B('")
                    if bb:
                        counter += 1
                        real_url = self.wtf_wallbase(ss[bb+4 : ss.find("'", bb+4)])
                        #print real_url
                        self.ran_returnlist[str(counter)] = real_url
            #print self.new_returnlist
            return self.new_returnlist
        else:
            return self.new_returnlist 

    def get_random_url(self, force=False):
        print "get_random_url :: forcing: %s" % force
        if( force or len(self.ran_returnlist) <= 0 ):
            self.final_url = self.wallbase_random_url
            f = urllib.urlopen(self.final_url)
            s = f.read()
            counter = -1;
            #p =re.compile("http://[^[:space:]]*")
            for line in s.split('\n'):
                if('http://wallbase.cc/wallpaper/' in line):
                    value = line[line.find("http://wallbase.cc/wallpaper/"):line.find('" id="')]
                    ff = urllib.urlopen(value)
                    ss = ff.read()
                    bb = ss.find("+B('")
                    if bb:
                        counter += 1
                        real_url = self.wtf_wallbase(ss[bb+4 : ss.find("'", bb+4)])
                        #print real_url
                        self.ran_returnlist[str(counter)] = real_url
            return self.ran_returnlist
        else:
            return self.ran_returnlist