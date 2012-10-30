import urllib
import re
class WallBase:
    def __init__(self):

        self.wallbase_url = 'http://wallbase.cc/search/'

        self.wallbase_newest_url = 'http://wallbase.cc/search/'
        self.wallbase_random_url = 'http://wallbase.cc/random/2/eqeq/0x0/0/110/20'
        self.wallbase_search_url = '/0/213/eqeq/0x0/0/1/1/0/60/relevance/desc/wallpapers'

        self.return_list = []

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

    def get_url(self, opt, force=False, tag=None):
        print "wallbase : %s :: forcing: %s" % (opt, force)
        if( force or len(self.return_list) <= 0 ):
            self.return_list = []
            if opt == 'new wallbase':
                final_url = self.wallbase_newest_url
            elif opt == 'search wallbase' and tag:
                final_url = self.wallbase_url + str(tag) + self.wallbase_search_url
            else: #opt == 'random':
                final_url = self.wallbase_random_url
            try:
                f = urllib.urlopen(final_url)
                s = f.read()
                for line in s.split('\n'):
                    if('http://wallbase.cc/wallpaper/' in line):
                        value = line[line.find("http://wallbase.cc/wallpaper/"):line.find('" id="')]
                        ff = urllib.urlopen(value)
                        ss = ff.read()
                        bb = ss.find("+B('")
                        if bb:
                            real_url = self.wtf_wallbase(ss[bb+4 : ss.find("'", bb+4)])
                            if real_url.find('http://'):
                                continue
                            self.return_list.append(real_url)
            except IOError: #urllib
                print "wallbase :: Failed fetching a wallbase url!"
        
        return self.return_list 
