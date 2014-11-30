from module.plugins.Hook import Hook 
import feedparser, re, urllib, httplib, codecs
from module.network.RequestFactory import getURL 
from BeautifulSoup import BeautifulSoup
import smtplib

def getSeriesList(file):
    titles = []
    f = codecs.open(file, "rb", "utf-8")
    for title in f.read().splitlines():
        title = title.replace(" ", ".")
        titles.append(title)
    f.close()
    return titles 
    
def notify(title, message, api):
    data = {"token":"aBGPe78hyxBKfRawhuGbzttrEaQ9rW","user":api,"message":message,"title":title}
    conn = httplib.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json", urllib.urlencode(data), { "Content-type": "application/x-www-form-urlencoded" })
    result = conn.getresponse()
    
def send_mail(text):
    """Tested with googlemail.com and bitmessage.ch. It should work with all mailservices which provide SSL access.""" 
    serveraddr = ''
    serverport = '465'
    username = ''
    password = ''
    fromaddr = ''
    toaddrs  = ''
    
    if toaddrs == "":
        return

    subject = "pyLoad: Package added!"
    msg = "\n".join(text)

    header = "To: %s\nFrom:%s\nSubject:%s\n" %(toaddrs,fromaddr,subject)
    msg = header + "\n" + msg

    server = smtplib.SMTP_SSL(serveraddr,serverport)
    server.ehlo()
    server.login(username,password)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit() 

class SJ(Hook):
    __name__ = "SJ"
    __version__ = "1.04"
    __description__ = "Findet und fuegt neue Episoden von SJ.org pyLoad hinzu"
    __config__ = [("activated", "bool", "Aktiviert", "False"),
                  ("regex","bool","Eintraege aus der Suchdatei als regulaere Ausdruecke behandeln", "False"),
                  ("quality", """480p;720p;1080p""", "480p, 720p oder 1080p", "720p"),
                  ("file", "file", "Datei mit Seriennamen", "SJ.txt"),
                  ("rejectlist", "str", "Titel ablehnen mit (; getrennt)", "dd51;itunes"),
                  ("language", """DEUTSCH;ENGLISCH""", "Sprache", "DEUTSCH"),
                  ("interval", "int", "Interval", "60"),
                  ("hoster", """ul;so;fm;cz""", "ul.to, filemonkey, cloudzer oder share-online", "ul"),
                  ("pushover", "str", "deine pushover api", ""),
                  ("queue", "bool", "Direkt in die Warteschlange?", "False")]
    __author_name__ = ("gutz-pilz","zapp-brannigan")
    __author_mail__ = ("unwichtig@gmail.com","")

    def setup(self):
        self.interval = self.getConfig("interval") * 60

    def periodical(self):
        feed = feedparser.parse('http://serienjunkies.org/xml/feeds/episoden.xml')
        
        pattern = "|".join(getSeriesList(self.getConfig("file"))).lower()
        reject = self.getConfig("rejectlist").replace(";","|").lower() if len(self.getConfig("rejectlist")) > 0 else "^unmatchable$"
        self.added_items = []
        
        for post in feed.entries:
            link = post.link
            title = post.title
            
            if self.getConfig("regex"):
                m = re.search(pattern,title.lower())
                if not m and not "720p" in title and not "1080p" in title:
                    m = re.search(pattern.replace("480p","."),title.lower())
                    
                if m:
                    m = re.search(reject,title.lower())
                    if m:
                        self.core.log.debug("SJFetcher - Abgelehnt: " + title)
                        continue
                    title = re.sub('\[.*\] ', '', post.title)
                    self.range_checkr(link,title)
                                
            else:

                if self.getConfig("quality") != '480p':
                    if (self.getConfig("language") in title) and any (word.lower() in title.lower() for word in getSeriesList(self.getConfig("file"))) and not any (word2.lower() in title.lower() for word2 in self.getConfig("rejectlist").split(";")):
                        if self.getConfig("quality") in title:
                            title = re.sub('\[.*\] ', '', post.title)
                            self.range_checkr(link,title)
        
                else:
                    if (self.getConfig("language") in title) and any (word.lower() in title.lower() for word in getSeriesList(self.getConfig("file"))) and not any (word2.lower() in title.lower() for word2 in self.getConfig("rejectlist").split(";")) and not ('720p' in title) and not ('1080p' in title):
                        title = re.sub('\[.*\] ', '', post.title)
                        self.range_checkr(link,title)
                        
        send_mail(self.added_items) if len(self.added_items) > 0 else True
            
                    
    def range_checkr(self, link, title):
        pattern = re.match(".*S\d{2}E\d{2}-\d{2}.*", title)
        if pattern is not None:
            range0 = re.sub(r".*S\d{2}E(\d{2}-\d{2}).*",r"\1", title)
            number1 = re.sub(r"(\d{2})-\d{2}",r"\1", range0)
            number2 = re.sub(r"\d{2}-(\d{2})",r"\1", range0)
            title_cut = re.sub(r"(.*S\d{2}E).*",r"\1",title)
            for count in range(int(number1),(int(number2)+1)):
                NR = re.match("d\{2}", str(count))
                if NR is not None:
                    title1 = title_cut + str(count)
                    self.range_parse(link, title1)
                else:
                    title1 = title_cut +"0"+ str(count)
                    self.range_parse(link, title1)
        else:
            self.parse_download(link, title)


    def range_parse(self,series_url, search_title):
        req_page = getURL(series_url)
        soup = BeautifulSoup(req_page)
        titles = soup.findAll(text=re.compile(search_title))
        for title in titles:
           if (self.getConfig("quality") !='480p') and (self.getConfig("quality") in title):
               self.parse_download(series_url, title)
           if (self.getConfig("quality") =='480p') and not (('.720p.' in post.title) or ('.1080p.' in post.title)):            
               self.parse_download(series_url, title)

    def parse_download(self,series_url, search_title):
        req_page = getURL(series_url)
        soup = BeautifulSoup(req_page)
        title = soup.find(text=re.compile(search_title))
        if title:
            links = title.parent.parent.findAll('a')
            for link in links:
                url = link['href']
                pattern = '.*%s_.*' % self.getConfig("hoster")
                if re.match(pattern, url):
                    self.send_package(title, url)
                 
    def send_package(self, title, link):
        storage = self.getStorage(title)
        if storage == 'downloaded':
            self.core.log.debug("SJFetcher - " + title + " already downloaded")
        else:
            self.core.log.info("SJFetcher - NEW EPISODE: " + title)
            self.setStorage(title, 'downloaded')
            if self.getConfig('pushover'):
                notify("SJ: Added package",title.encode("utf-8"),self.getConfig("pushover"))
            self.core.api.addPackage(title.encode("utf-8"), link.split('"'), 1 if self.getConfig("queue") else 0)
            self.added_items.append(title.encode("utf-8"))
