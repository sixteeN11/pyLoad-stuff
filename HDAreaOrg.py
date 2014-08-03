from module.plugins.Hook import Hook 
import feedparser, re, urllib2, urllib, httplib
from BeautifulSoup import BeautifulSoup 
from module.network.RequestFactory import getURL

def notify(title, message, api):
    data = {"token":"aHjfpv2HPi6CnGxbharCnFqpfzPHpe","user":api,"message":message,"title":title}
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json", urllib.urlencode(data), { "Content-type": "application/x-www-form-urlencoded" })
    result = conn.getresponse()
def replaceUmlauts(title):
    title = title.replace(unichr(228), "ae").replace(unichr(196), "Ae")
    title = title.replace(unichr(252), "ue").replace(unichr(220), "Ue")
    title = title.replace(unichr(246), "oe").replace(unichr(214), "Oe")
    title = title.replace(unichr(223), "ss")
    title = title.replace('&amp;', "&")
    return titlepsu

class HDAreaOrg(Hook):
    __name__ = "HDAreaOrg"
    __version__ = "1.0"
    __description__ = "Get new movies from HD-area"
    __config__ = [("activated", "bool", "Aktiviert", "False"),
                  ("quality", """720p;1080p""", "720p oder 1080p", "1080p"),
                  ("rejectList", "str", "reject (seperated by ;)", "dd51;itunes;doku;avc;remux"),
                  ("conf_rating_collector","float","Collector Rating","6.1"),
                  ("conf_rating_queue","float","Queue Rating","7.1"),
                  ("interval", "int", "Check interval in minutes", "60"),
                  ("conf_year","long","Min Year","1990"),
                  ("rej_genre","str","Reject Genre (seperated by ;)","Family;Anime;Documentary"),
                  ("pushover", "str", "deine pushover api", "uGpi5jzHhj3tLozqRMHsebfUPwmi2a"),
                  ("hoster", "str", "Preferred Hoster (seperated by ;)","uploaded;uplaoded;oboom;cloudzer;filemonkey")]
    __author_name__ = ("gutz-pilz")
    __author_mail__ = ("unwichtig@gmail.com")

    def setup(self):
        self.interval = self.getConfig("interval") * 60

    def periodical(self):
        for site in ('top-rls','movies','Cinedubs','msd','Old_Stuff'):
            address = ('http://hd-area.org/index.php?s=' + site)
            req_page = getURL(address)
            soup = BeautifulSoup(req_page)
            self.get_title(soup)

    def get_title(self,soup1):
        for all in soup1.findAll("div", {"class" : "topbox"}):
            for title in all.findAll("div", {"class" : "title"}):
                 self.filter(all, title.getText())
  
    def filter(self, all, title):
        season = re.compile('.*S\d|\Sd{2}|eason\d|eason\d{2}.*')
        if (self.getConfig("quality") in title) and not any (word.lower() in title.lower() for word in self.getConfig("rejectList").split(";")) and not season.match(title):
            self.get_download(all, title)
         
    def get_download(self, soup1, title):
        for title in soup1.findAll("div", {"class" : "title"}):
             hda_url = title.a["href"]
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
                self.core.log.debug("HDaFetcher:\t"+title+" ("+year+"): to OLD")

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
            self.core.log.debug("HDaFetcher:\t" + title + " ("+year+"): matches rejected GENRE")

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
                    self.core.log.debug("HDaFetcher:\t"+title+" ("+year+") IMDb: "+rating+": rating to LOW")
                if (storage == 'downloaded') and not (rating < self.getConfig("conf_rating_collector")):
                    self.core.log.debug("HDaFetcher:\t"+title+" ("+year+")" + ": downloaded already")
                else:
                    self.setStorage(title, 'downloaded')
                    if (rating < self.getConfig("conf_rating_queue")) and (rating > self.getConfig("conf_rating_collector")):
                        self.core.log.info("HDaFetcher:\tCOLLECTOR: "+title.decode("utf-8")+" ("+year+") IMDb: "+rating)
                        notify("Added to Collector", title.decode("utf-8")+" ("+year+") \n\tIMDb_rating: "+rating+"\n\tIMDb_URL: "+imdb_url, self.getConfig("pushover"))
                        self.core.api.addPackage(title.decode("utf-8")+" ("+year+") IMDb: "+rating, dlLink.split('"'), 0)
                        if self.getConfig('pushover'):
                            notify("Added to Collector", title.decode("utf-8")+" ("+year+") \n\tIMDb_rating: "+rating+"\n\tIMDb_URL: "+imdb_url, self.getConfig("pushover"))
                    elif rating > self.getConfig("conf_rating_queue"):
                        self.core.log.info("HDaFetcher:\tQUEUE: "+title.decode("utf-8")+" ("+year+") IMDb: "+rating)
                        notify("Added to Queue", title.decode("utf-8")+" ("+year+") \n\tIMDb_rating: "+rating+"\n\tIMDb_URL: "+imdb_url, self.getConfig("pushover"))
                        self.core.api.addPackage(title.decode("utf-8")+" ("+year+") IMDb: "+rating, dlLink.split('"'), 1)
                        if self.getConfig('pushover'):
                            notify("Added to Collector", title.decode("utf-8")+" ("+year+") \n\tIMDb_rating: "+rating+"\n\tIMDb_URL: "+imdb_url, self.getConfig("pushover"))
