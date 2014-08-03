[[Hook] HDAreaOrg.py](HDAreaOrg.py)
==============
 - standalone Moviefetcher
 - gets all Movies from HD-AR** and grab rating, title and genre from IMDb
 - gets a clean title from imdb (year)
 - gets only your preferred hoster
 - 2 factor rating - one for directly adding it to the Queue and one for later decision to the Collector
 - decide which genre you'd not want to download
 - pushover notifications

[[Hook] SJ.py](SJ.py)
==============
 - uses the serienjunk**s episode rss to fetch the latest episodes
 - decide which quality, language and hoster you prefer
 - create a SJ.txt in your pyload folder with all the seriesnames (each a new line)
 - pushover notifications

[[Hook] FileBot.py](FileBot.py)
==============
This Hook uses the FileBot program from rednoah to have downloaded Movies/Series/Animes automatically renamed and sorted.

download FileBot.py and copy it into your pyload/hooks folder.
restart pyload and configure it.


[FileBot.sh](filebot.sh)
==============
Some additional stuff happening to the moved File
 - modify creation date (to have it stored "recently added" in XBMC)
 - update XBMC LIbrary
 - make it read / writeable for everyone (something i need to do)
 - send email with location of the file and changed filesize (nice to have)

Have fun
Gutz-Pilz
