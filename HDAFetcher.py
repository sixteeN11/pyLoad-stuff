# -*- coding: utf-8 -*-
"""
    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 3 of the License,
    or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
    See the GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, see <http://www.gnu.org/licenses/>.

    @author: wongdong  thanks to mkaay for Ev0-fetcher
"""

from module.plugins.Hook import Hook
from module.lib import feedparser
from time import mktime, time


class HDAFetcher(Hook):
    __name__ = "HDAFetcher"
    __version__ = "1.0"
    __description__ = "Checks your HDarea YahooRSS pipe for new movies. "
    __config__ = [("activated", "bool", "Activated", "True"),
                  ("rssnumber", "str", "Your personal RSS identifier", "5bb58xxbccbb38923a19e3152ccf5364"),
                  ("interval", "int", "Check interval in minutes", "60"),    
                  ("queue", "bool", "Move new shows directly to Queue", "True")]
    __author_name__ = ("gutz-pilz")
    __author_mail__ = ("unwichtig@gmail.com")

    def setup(self):
        self.interval = self.getConfig("interval") * 60
    
    def periodical(self):
        self.interval = self.getConfig("interval") * 60                                                # Re-set the interval if it has changed (need to restart pyload otherwise)
        feed = feedparser.parse("http://pipes.yahoo.com/pipes/pipe.run?_id="+self.getConfig("rssnumber")+"&_render=rss")           # This is your personal feed Number from Directxxxxxxxx.tv
        
        for item in feed['entries']:
            link = str(item['summary'])
            title = str(item['title'])                                                                                # Thats a single Episode item in the feed                                                               # Take only those not already parsed                                                                            
            f = open("HDAFetcher_DB.txt", "a")
            s = open("HDAFetcher_DB.txt").read()
            if title in s:
                self.core.log.debug("HDAFetcher: Already been added:\t\t" +title)
            else:
                self.core.log.info("HDAFetcher: New Episode found: %s" % (title))
                self.core.api.addPackage(title.encode("utf-8"), link.split('"'), 1 if self.getConfig("queue") else 0) 
                f.write(title+"\n")                      
                f.write(link+"\n\n")
