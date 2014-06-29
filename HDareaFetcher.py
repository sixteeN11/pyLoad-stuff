# -*- coding: utf-8 -*-
from module.plugins.Hook import Hook
import urllib2 
from BeautifulSoup import BeautifulSoup 
import re 

class HDareaFetcher(Hook):
    __name__ = "HDareaFetcher"
    __version__ = "0.1"
    __description__ = "Checks HD-AREA.org for new Movies. "
    __config__ = [("activated", "bool", "Activated", "False"),
                  ("interval", "int", "Check interval in minutes", "60"),
                  ("quality", "str", "720p or 1080p", "720p"),
                  ("rating","float","Collector Rating","6.1"),
                  ("rating2","float","Queue Rating","8.0"),
                  ("rating3","float","Cinedubs Queue Rating","5.5"),
                  ("min_year","long","Min Year","1990"),
                  ("hoster", "str", "Preferred Hoster (seperated by ;)","uploaded;cloudzer")]
    __author_name__ = ("Gutz-Pilz")
    __author_mail__ = ("")

    def setup(self):
        self.interval = self.getConfig("interval") * 60 
    def periodical(self):
        for site in ('top-rls','movies','Cinedubs','msd','Old_Stuff'):
            address = ('http://hd-area.org/index.php?s=' + site)
            page = urllib2.urlopen(address).read()
            soup = BeautifulSoup(page)
            movieTit = []
            movieLink = []
            movieRating = []
            movieYear = []

            try:
                for title in soup.findAll("div", {"class" : "topbox"}):
                    for title2 in title.findAll("div", {"class" : "boxlinks"}):
                        for title3 in title2.findAll("div", {"class" : "title"}):
                            movieTit.append(title3.getText())
                    for imdb in title.findAll("div", {"class" : "boxrechts"}):
                        if 'IMDb' in imdb.getText():
                            #for aref in imdb.findAll('a'):
                            movieRating.append(imdb.getText())
                        if not 'IMDb' in imdb.getText():
                            movieRating.append('IMDb 0.1/10')
                    for year in soup.findAll("div", {"class":"download"}):
                        for year1 in year.findAll("div", {"class":"beschreibung"}):
                            if 'Jahr' in year1.getText():
                                movieYear.append(year1.getText())
                        if not 'Jahr' in year1.getText():
                            movieYear.append('JahrJahr:1950')
                            #for year2 in year1.findAll("strong", {"class":"main"}):

            except:
                pass

            for download in soup.findAll("div", {"class":"download"}):
                for descr in download.findAll("div", {"class":"beschreibung"}):
                    links = descr.findAll("span", {"style":"display:inline;"})
                    for link in links:
                        url = link.a["href"]
                        hoster = link.text
                        for prefhoster in self.getConfig("hoster").split(";"):
                            if prefhoster.lower() in hoster.lower():
                                movieLink.append(url)
                                break
                        else:
                            continue
                        break

            f = open("hdarea.txt", "a")            
#            print len(movieTit)
#            print len(movieLink)
#            print len(movieRating)
#            print len(movieYear) 
            if (len(movieLink) == len(movieTit) == len(movieRating)) :
                for i in range(len(movieTit)):                 
                    #print movieYear[i]
                    link = movieLink[i]
                    title = movieTit[i]
                    title = title.lower()
                    title = title.replace('.german','')
                    title = title.replace('.bluray','')
                    title = re.sub(".(h|x)264(-|.)\S+", "", title)
                    title = re.sub(".complete-\S+", "", title)
                    title = re.sub(".remux-\S+", "", title)
                    title = re.sub(".web\S+", "", title)
                    title = re.sub(".nfo(-\S+|)", "", title)
                    title = title.replace('.unrated','')
                    title = title.replace('.directors','')
                    title = title.replace('.cut','')
                    title = title.replace('.dual','')
                    title = title.replace('.avc','')
                    title = title.replace('.dl','')
                    title = title.replace('.ac3ld','')
                    title = title.replace('.ac3d','')
                    title = title.replace('.ac3','')
                    title = title.replace('.dtshd','')
                    title = title.replace('.dtsd','')
                    title = title.replace('.dts','')
                    title = title.replace('.dd5.1','')
                    title = title.replace('.dtsd','')
                    title = title.replace('.5.1','')
                    title = title.replace('.hddvd','')
                    title = title.replace('.md','')
                    title = title.replace('.bluray','')
                    title = title.replace('.multi','')
                    title = title.replace('.disc1+2','')
                    title = title.replace('.extended','')
                    title = title.replace('.dubbed','')
                    title = title.replace('.ml','')
                    title = title.replace('.flac','')
                    title = title.replace('.read',' ')
                    s = open("hdarea.txt").read()    
                    if title in s:
                        self.core.log.debug("HDArea: Already been added:\t\t" +title)
                    else:
                        rating_txt = movieRating[i]
                        rating_float = rating_txt[5:8]
                        rating = rating_float.replace(',','.')    
                        rating = rating.replace('-/','0.')
                        year = movieYear[i]
                        year = year[9:13]
#                        print year
                        list = [self.getConfig("quality")]
                        list2 = ['S0','s0','season','Season','DOKU','doku','Doku','s1','s2','s3','s4']

                        if any(word in title for word in list) and rating > self.getConfig("rating"):
                            if any (word in title for word in list2):
                                self.core.log.debug("HDArea: REJECTED! not a Movie:\t\t" +title)
                            else:
                                #if year < self.getConfig("min_year"):
                                    #self.core.log.debug("HDArea: REJECTED! Movie older than "+self.getConfig("min_year")+":\t\t" +title)
                                if rating > self.getConfig("rating2"): 
                                    f.write(title+"\n")                      
                                    f.write(link+"\n\n")
                                    self.core.api.addPackage(title.encode("utf-8")+" IMDB: "+rating, link.split('"'), 1)               
                                    self.core.log.info("HDArea: !!! JACKPOT !!!:\t\t" +title+"... with rating:\t"+rating)
                                else:
                                    if year > self.getConfig("min_year"):
                                        f.write(title+"\n")
                                        f.write(link+"\n\n")
                                        self.core.api.addPackage(title.encode("utf-8")+" IMDB: "+rating, link.split('"'), 0)
                                        self.core.log.info("HDArea: !!! ACCEPTED !!!:\t\t" +title+"... with rating:\t"+rating)
                                    else: 
                                        self.core.log.debug("HDArea: REJECTED! Movie older than "+self.getConfig("min_year")+":\t" +title)
                        else:
                            if rating < self.getConfig("rating"):
                                self.core.log.debug("HDArea: IMDB-Rating ("+rating+") to low:\t\t" +title)
                            if not any(word in title for word in list):
                                self.core.log.debug("HDArea: Quality ("+self.getConfig("quality")+") mismatch:\t\t" +title)
                        if any(word in title for word in list) and site == 'Cinedubs' and rating > self.getConfig("rating3"):
                            f.write(title+"\n")                      
                            f.write(link+"\n\n")
                            self.core.api.addPackage(title.encode("utf-8")+" IMDB: "+rating, link.split('"'), 1)               
                            self.core.log.info("HDArea: ! CinedubJackpot !:\t\t" +title+"... with rating:\t"+rating)
                        else:
                            if rating < self.getConfig("rating3"):
                                f.write(title+"\n")
                                f.write(link+"\n\n")
                                self.core.api.addPackage(title.encode("utf-8")+" IMDB: "+rating, link.split('"'), 0)               
                                self.core.log.info("HDArea: !!! ACCEPTED !!!:\t\t" +title+"... with rating:\t"+rating)
                            if not any(word in title for word in list):
                                self.core.log.debug("HDArea: Quality ("+self.getConfig("quality")+") mismatch:\t\t" +title)
               
            else:
                self.core.log.debug("ERROR: Array length mismatch!!!")         

            f.close()
