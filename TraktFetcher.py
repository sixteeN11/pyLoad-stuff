from module.plugins.internal.Addon import Addon
import re, urllib2, urllib, httplib, base64, contextlib, HTMLParser
from BeautifulSoup import BeautifulSoup 
from module.network.RequestFactory import getURL 
from module.plugins.internal.utils import json

def replaceUmlauts(title):
    title = title.replace(unichr(228), "ae").replace(unichr(196), "Ae")
    title = title.replace(unichr(252), "ue").replace(unichr(220), "Ue")
    title = title.replace(unichr(246), "oe").replace(unichr(214), "Oe")
    title = title.replace(unichr(223), "ss")
    title = title.replace('&amp;', "&")
    title = title.replace("'", "")
    title = title.replace(",", "")
    title = title.replace("?", "")
    title = title.replace("!", "")
    title = title.replace("&", " ")
    title = title.replace(" -", "")
    title = title.replace(".", " ")
    title = title.replace(":", " ")
    title = title.replace("  ", " ")
    title = "".join(i for i in title if ord(i)<128)
    return title

def notifyPushover(api ='', msg=''):
    data = urllib.urlencode({
        'user': api,
        'token': 'aBGPe78hyxBKfRawhuGbzttrEaQ9rW',
        'title': 'pyLoad: TraktFetcher added Package',
        'message': "\n".join(msg)
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

def notifyPushbullet(api='', msg=''):
    data = urllib.urlencode({
        'type': 'note',
        'title': 'pyLoad: TraktFetcher added Package',
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

class TraktFetcher(Addon):
    __name__ = "TraktFetcher"
    __version__ = "0.3"
    __type__    = "hook"
    __status__  = "testing"
    __description__ = "Searches HDArea for Trakt Watchlist Titles"
    __config__ = [("activated", "bool", "Aktiviert", "False"),
                  ("traktuser", "str", "Dein Trakt Benutzername", "username"),
                  ("quality", """720p;1080p""", "720p oder 1080p", "720p"),
                  ("rejectList", "str", "ablehnen (; getrennt)", "dd51;itunes;doku"),
                  ("interval", "int", "Intervall", "60"),
                  ("pushoverapi", "str", "Dein Pushover-API-Key", ""),
                  ("hoster", "str", "Hoster (durch ; getrennt)","uploaded;uplaoded"),
                  ("pushbulletapi","str","Dein Pushbullet-API-Key","")]
    __author_name__ = ("gutz-pilz")
    __author_mail__ = ("unwichtig@gmail.com")

    def activate(self):
        self.start_periodical(self.get_config('interval') * 60)
    def periodical(self):
        html_parser = HTMLParser.HTMLParser()
        self.items_to_pyload = []
        address = ('https://trakt.tv/users/%s/watchlist' %self.get_config("traktuser"))
        page = getURL(address)
        soup = BeautifulSoup(page)
        trakttitles = []
        # Get Trakt Watchlist Titles
        for all in soup.findAll("div", {"class" : "titles"}):
            for title in all.findAll("h3"):
                title = title.getText()
                title = replaceUmlauts(html_parser.unescape(title))
                storage = self.retrieve(title)
                if (storage == 'downloaded'):
                    self.log_debug(title+": already found and downloaded")
                else:
                    trakttitles.append(title)
        self.search(trakttitles)

        #Pushnotification
        if len(self.get_config('pushoverapi')) > 2:
            notifyPushover(self.get_config("pushoverapi"),self.items_to_pyload) if len(self.items_to_pyload) > 0 else True
        if len(self.get_config('pushbulletapi')) > 2:
            notifyPushbullet(self.get_config("pushbulletapi"),self.items_to_pyload) if len(self.items_to_pyload) > 0 else True

    def search(self, trakttitles):
        for title in trakttitles:
            tmdb_link = "https://api.themoviedb.org/3/search/movie?api_key=4e33dc1073b5ad87851d8a4f506dc096&query=" + urllib2.quote(title.encode('utf-8')) +"&language=de"
            #print tmdb_link
            json_data = self.load("https://api.themoviedb.org/3/search/movie?api_key=4e33dc1073b5ad87851d8a4f506dc096&query="+ urllib2.quote(title.encode('utf-8')) +"&language=de")
            json_data = json.loads(json_data)
            #r = getURL(tmdb_link)
            #config = r.json()
            if len(json_data["results"]) > 0:
                orig_tmdb_title = replaceUmlauts(json_data["results"][0]["original_title"])
                german_tmdb_title = replaceUmlauts(json_data["results"][0]["title"])
            else:
                continue
            searchLink_orig = "http://www.hd-area.org/?s=search&q=" + urllib2.quote(orig_tmdb_title.encode('utf-8'))
            searchLink_german = "http://www.hd-area.org/?s=search&q=" + urllib2.quote(german_tmdb_title.encode('utf-8'))
            page_orig = getURL(searchLink_orig)
            page_german = getURL(searchLink_german)
            soup_orig = BeautifulSoup(page_orig)
            soup_german = BeautifulSoup(page_german)
            self.log_debug('Suche "%s" auf HDArea' %german_tmdb_title)
            for content_german in soup_german.findAll("div", {"class":"whitecontent contentheight"}):
                searchLinks_german = content_german.findAll("a")
                if len(searchLinks_german) > 0:
                    for link in searchLinks_german:
                        href = link["href"]
                        releaseName = link.getText()
                        season = re.compile('.*S\d|\Sd{2}|eason\d|eason\d{2}.*')
                        if (self.get_config("quality") in releaseName) and not any (word.lower() in releaseName.lower() for word in self.get_config("rejectList").split(";")) and not season.match(releaseName):
                            req_page = href.getText()
                            soup_ = BeautifulSoup(req_page)
                            links = soup_.findAll("span", {"style":"display:inline;"})
                            for link in links:
                                url = link.a["href"]
                                for hoster in self.get_config("hoster").split(";"):
                                    if hoster.lower() in link.text.lower():
                                        self.log_info('ADDED: "'+title+'" Releasename: '+releaseName)
                                        self.pyload.api.addPackage(title, url.split('"'), 0)
                                        self.items_to_pyload.append(title+"  ||  Link: "+href) 
                                        self.store(title, 'downloaded')
                            break
                else:
                    self.log_debug('keine Suchergebnisse mit deutschem Titel gefunden: "%s"' %german_tmdb_title)
                    self.log_debug("suche mit englischem Titel: %s" %orig_tmdb_title)
                    for content_orig in soup_orig.findAll("div", {"class":"whitecontent contentheight"}):
                        searchLinks_orig = content_orig.findAll("a")
                        for link in searchLinks_orig:
                            href = link["href"]
                            releaseName = link.getText()
                            season = re.compile('.*S\d|\Sd{2}|eason\d|eason\d{2}.*')
                            if (self.get_config("quality") in releaseName) and not any (word.lower() in releaseName.lower() for word in self.get_config("rejectList").split(";")) and not season.match(releaseName):
                                req_page = href.getText()
                                soup_ = BeautifulSoup(req_page)
                                links = soup_.findAll("span", {"style":"display:inline;"})
                                for link in links:
                                    url = link.a["href"]
                                    for hoster in self.get_config("hoster").split(";"):
                                        if hoster.lower() in link.text.lower():
                                            self.log_info('ADDED: "'+title+'" Releasename: '+releaseName)
                                            self.pyload.api.addPackage(title, url.split('"'), 0)
                                            self.items_to_pyload.append(title+"  ||  Link: "+href) 
                                            self.store(title, 'downloaded')
                                break

