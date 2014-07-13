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


class SJFetcher(Hook):
    __name__ = "SJFetcher"
    __version__ = "1.0"
    __description__ = "Checks your  SJ YahooRSS pipe for new episodes. "
    __config__ = [("activated", "bool", "Activated", "False"),
                  ("rssnumber", "str", "Your personal RSS identifier", "02abxxe991fadaa183c0fa57892b8302"),
                  ("interval", "int", "Check interval in minutes", "60"),    
                  ("queue", "bool", "Move new shows directly to Queue", "False")]
    __author_name__ = ("gutz-pilz")
    __author_mail__ = ("unwichtig@gmail.com")

    def setup(self):
        self.interval = self.getConfig("interval") * 60
    
    def periodical(self):
        self.interval = self.getConfig("interval") * 60                                                # Re-set the interval if it has changed (need to restart pyload otherwise)
        feed = feedparser.parse("http://pipes.yahoo.com/pipes/pipe.run?_id="+self.getConfig("rssnumber")+"&_render=rss")           # This is your personal feed Number from Directxxxxxxxx.tv
        
        lastupdate = 0                  # The last timestamp of a downloaded file
        try:
            lastupdate = int(self.getStorage("lastupdate", 0))  # Try to load the last updated timestamp   
        except:
            pass
        
        
        maxtime =lastupdate 
        for item in feed['entries']:                                                                                # Thats a single Episode item in the feed
            currenttime = int(mktime(item['updated_parsed']))                          
            if ( currenttime > lastupdate):                                                                         # Take only those not already parsed                                                                            
                link = str(item['summary'])
                title = str(item['title'])
                #links = filter (lambda x:x.startswith("http://") , links)                                           # remove all non-links (Empty lines, and whatnot)
                self.core.log.info("SJFetcher: New Episode found: %s" % (title))
                self.core.api.addPackage(title.encode("utf-8"), link.split('"'), 1 if self.getConfig("queue") else 0) 
                maxtime = max(maxtime, currenttime)                                                             # no links found. Try again next time.

        if (maxtime == lastupdate):
            self.core.log.debug("SJFetcher: No new Episodes found")
        else:
            self.setStorage("lastupdate",int(maxtime))
