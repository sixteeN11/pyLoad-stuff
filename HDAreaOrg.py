from module.plugins.Hook import Hook 
import feedparser, re, urllib2, urllib, httplib, base64, json
from BeautifulSoup import BeautifulSoup 
from module.network.RequestFactory import getURL 

def replaceUmlauts(title):
    title = title.replace(unichr(228), "ae").replace(unichr(196), "Ae")
    title = title.replace(unichr(252), "ue").replace(unichr(220), "Ue")
    title = title.replace(unichr(246), "oe").replace(unichr(214), "Oe")
    title = title.replace(unichr(223), "ss")
    title = title.replace('&amp;', "&")
    return title

def notifyPushover(api ='', msg='',location=''):
    data = urllib.urlencode({
        'user': api,
        'token': 'aBGPe78hyxBKfRawhuGbzttrEaQ9rW',
        'title': 'pyLoad: HDAreaHook added Package to %s' %location,
        'message': "\n\n".join(msg)
    })
    try:
        req = urllib2.Request('https://api.pushover.net/1/messages.json', data)
        response = urllib2.urlopen(req)
    except urllib2.HTTPError:
        print 'Failed much'
        return False
    res = json.load(response)
    if res['status'] == 1:
        print 'Pushover Success'
    else:
        print 'Pushover Fail' 

def notifyPushbullet(api='', msg='',location=''):
    data = urllib.urlencode({
        'type': 'note',
        'title': 'pyLoad: HDAreaHook added Package to %s' %location,
        'body': "\n\n".join(msg)
    })
    auth = base64.encodestring('%s:' %api).replace('\n', '')
    try:
        req = urllib2.Request('https://api.pushbullet.com/v2/pushes', data)
        req.add_header('Authorization', 'Basic %s' % auth)
        response = urllib2.urlopen(req)
    except urllib2.HTTPError:
        print 'Failed much'
        return False
    res = json.load(response)
    if res['sender_name']:
        print 'Pushbullet Success'
    else:
        print 'Pushbullet Fail'

class HDAreaOrg(Hook):
    __name__ = "HDAreaOrg"
    __version__ = "1.6"
    __description__ = "Get new movies from HD-area"
    __config__ = [("activated", "bool", "Aktiviert", "False"),
                  ("quality", """720p;1080p""", "720p oder 1080p", "720p"),
                  ("rejectList", "str", "ablehnen (; getrennt)", "dd51;itunes"),
                  ("cinedubs", "bool", "Cinedubs einbeziehen ?", "False"),
                  ("conf_rating_collector","float","Collector Bewertung","6.1"),
                  ("conf_rating_queue","float","Queue Bewertung","7.1"),
                  ("interval", "int", "Intervall", "60"),
                  ("conf_year","long","Maximales Alter","1990"),
                  ("rej_genre","str","Genre ablehnen","Family;Anime;Documentary"),
                  ("pushoverapi", "str", "Dein Pushover-API-Key", ""),
                  ("hoster", "str", "Bevorzugte Hoster (durch ; getrennt)","uploaded;uplaoded;oboom;cloudzer;filemonkey"),
                  ("pushbulletapi","str","Dein Pushbullet-API-Key","")]
    __author_name__ = ("gutz-pilz")
    __author_mail__ = ("unwichtig@gmail.com")

    def setup(self):
        self.interval = self.getConfig("interval") * 60
    def periodical(self):
        self.items_to_queue = []
        self.items_to_collector = []
        for site in ('top-rls','movies','Old_Stuff'):
            address = ('http://hd-area.org/index.php?s=' + site)
            req_page = getURL(address)
            soup = BeautifulSoup(req_page)
            self.get_title(soup)
        if self.getConfig("cinedubs") == True:
            address = ('http://hd-area.org/index.php?s=Cinedubs')
            req_page = getURL(address)
            soup = BeautifulSoup(req_page)
            self.get_title(soup)
        if len(self.getConfig('pushoverapi')) > 2:
            notifyPushover(self.getConfig("pushoverapi"),self.items_to_queue,"QUEUE") if len(self.items_to_queue) > 0 else True
            notifyPushover(self.getConfig("pushoverapi"),self.items_to_collector,"COLLECTOR") if len(self.items_to_collector) > 0 else True
        if len(self.getConfig('pushbulletapi')) > 2:
            notifyPushbullet(self.getConfig("pushbulletapi"),self.items_to_queue,"QUEUE") if len(self.items_to_queue) > 0 else True
            notifyPushbullet(self.getConfig("pushbulletapi"),self.items_to_collector,"COLLECTOR") if len(self.items_to_collector) > 0 else True  
    def get_title(self,soup1):
        for all in soup1.findAll("div", {"class" : "topbox"}):
            for title in all.findAll("div", {"class" : "title"}):
                fetched = self.getStorage(title.getText())
                if fetched == 'fetched':
                    self.core.log.debug("HDaFetcher:\t"+title.getText()+ " already fetched")
                else:
                    self.filter(all, title.getText())
                    self.setStorage(title.getText(), 'fetched')
    def filter(self, all, title):
        season = re.compile('.*S\d|\Sd{2}|eason\d|eason\d{2}.*')
        if (self.getConfig("quality") in title) and not any (word.lower() in title.lower() for word in self.getConfig("rejectList").split(";")) and not season.match(title):
            self.get_download(all, title)
    def get_download(self, soup1, title):
        for title in soup1.findAll("div", {"class" : "title"}):
            hda_url = title.a["href"].replace("https","http")
            req_page = getURL(hda_url)
            soup_ = BeautifulSoup(req_page)
            links = soup_.findAll("span", {"style":"display:inline;"})
            for link in links:
                url = link.a["href"]
                for pref_hoster in self.getConfig("hoster"):
                    if pref_hoster.lower() in link.text.lower():
                        self.get_year(soup1, title, url)
                    break
    def get_year(self, soup1, title, dlLink):
        imdb_url = soup1.find("div", {"class" : "boxrechts"})
        imdb_url = unicode.join(u'',map(unicode,imdb_url))
        imdb_url = re.sub(r'.*(imdb.*)"\starget.*', r'http://\1', imdb_url)
        if "http" in imdb_url:
            page = urllib2.urlopen(imdb_url).read()
            imdb_site = BeautifulSoup(page)
            year_pattern = re.compile(r'[0-9]{4}')
            year = imdb_site.find("span", {"class" : "nobr"})
            year = unicode.join(u'',map(unicode,year))
            year = re.sub(r".*([0-9]{4}).*", r"\1", year)
            orig_title = imdb_site.find("span", {"class" : "itemprop"}).getText()
            title = replaceUmlauts(orig_title)
            if year > self.getConfig("conf_year"):
                self.get_genre(soup1, title, dlLink , year, imdb_url)
            else:
                self.core.log.debug("HDaFetcher:\t"+title+" ("+year+"): zu ALT")
    def get_genre(self, soup1, title, dlLink, year, imdb_url):
        page = urllib2.urlopen(imdb_url).read()
        imdb_site = BeautifulSoup(page)
        genres = []
        get_genre = imdb_site.findAll("span", {"itemprop" : "genre"})
        for genre in get_genre:
            genre = genre.getText().encode("utf-8")
            genres.append(genre)
        if not any (word in genres for word in self.getConfig("rej_genre").split(";")):
            self.get_rating(soup1, title, dlLink , year, imdb_url)
        else:
            self.core.log.debug("HDaFetcher:\t" + title + " ("+year+"): GENRE passt nicht")
    def get_rating(self, soup1, title, dlLink, year, imdb_url):
        for rating in soup1.findAll("div", {"class" : "boxrechts"}):
            if 'IMDb' in rating.getText():
                rating = unicode.join(u'',map(unicode,rating))
                rating = re.sub(r".*(\d\.\d|\d\,\d).*", r"\1", rating)
                rating = rating.replace(',','.')
                rating = re.sub(r'(.*\s-/10)',r'0.1', rating)
                rating = "".join(rating.split('\n'))
                title = replaceUmlauts(title)
                storage = self.getStorage(title)
                if rating < self.getConfig("conf_rating_collector"):
                    self.core.log.debug("HDaFetcher:\t"+title+" ("+year+") IMDb: "+rating+": zu SCHLECHT")
                if (storage == 'downloaded') and not (rating < self.getConfig("conf_rating_collector")):
                    self.core.log.debug("HDaFetcher:\t"+title+" ("+year+")" + " already downloaded")
                else:
                    self.setStorage(title, 'downloaded')
                    if (rating < self.getConfig("conf_rating_queue")) and (rating > self.getConfig("conf_rating_collector")):
                        self.core.log.info("HDaFetcher:\tCOLLECTOR: "+title.decode("utf-8")+" ("+year+") IMDb: "+rating)
                        self.core.api.addPackage(title.decode("utf-8")+" ("+year+") IMDb: "+rating, dlLink.split('"'), 0)
                        self.items_to_collector.append(title.encode("utf-8")+" ("+year+") IMDb: "+rating) 
                    elif rating > self.getConfig("conf_rating_queue"):
                        self.core.log.info("HDaFetcher:\tQUEUE: "+title.decode("utf-8")+" ("+year+") IMDb: "+rating)
                        self.core.api.addPackage(title.decode("utf-8")+" ("+year+") IMDb: "+rating, dlLink.split('"'), 1)
                        self.items_to_queue.append(title.encode("utf-8")+" ("+year+") IMDb: "+rating)

