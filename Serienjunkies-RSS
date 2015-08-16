#!/usr/bin/env python
# -- coding: utf-8 --
import feedparser, re, requests, codecs, os, sys
from BeautifulSoup import BeautifulSoup

### Anpassen
file = "SJ.txt"             # Dateiname für die gewünschte Serien
rejectlist = "itunes;xxx"   # was darf nicht im titel vorkommen
hoster = "ul"               # ul, filemonkey, cloudzer, share-online oder alle
outputFilename = "rss.xml"  # wo soll die rss-datei gespeichert werden ?

### Nur anpassen wenn Regex auf False
regex = True                # Eintraege aus der Suchdatei als regulaere Ausdruecke behandeln
debug = False               # Sehen was abgelehnt wird
language = "DEUTSCH"        # welche sprache "DEUTSCH" oder "ENGLISCH" - spielt nur eine Rolle wenn regex auf False
quality= "720p"             # 480p;720p;1080p - spielt nur eine Rolle wenn regex auf False


def getSeriesList(file):
    try:
        titles = []
        f = codecs.open(file, "rb", "utf-8")
        for title in f.read().splitlines():
            if len(title) == 0:
                continue
            title = title.replace(" ", ".")
            titles.append(title)
        f.close()
        return titles
    except UnicodeError:
        print("Abbruch, es befinden sich ungueltige Zeichen in der Suchdatei!")
    except IOError:
        print("Abbruch, Suchdatei wurde nicht gefunden!")
    except Exception, e:
        print("Unbekannter Fehler: %s" %e) 


def range_checkr(link, title):
    pattern = re.match(".*S\d{2}E\d{2}-\w?\d{2}.*", title)
    if pattern is not None:
        range0 = re.sub(r".*S\d{2}E(\d{2}-\w?\d{2}).*",r"\1", title).replace("E","")
        number1 = re.sub(r"(\d{2})-\d{2}",r"\1", range0)
        number2 = re.sub(r"\d{2}-(\d{2})",r"\1", range0)
        title_cut = re.findall(r"(.*S\d{2}E)(\d{2}-\w?\d{2})(.*)",title)
        for count in range(int(number1),(int(number2)+1)):
            NR = re.match("d\{2}", str(count))
            if NR is not None:
                title1 = title_cut[0][0] + str(count) + ".*" + title_cut[0][-1]
                range_parse(link, title1)
            else:
                title1 = title_cut[0][0] + "0" + str(count) + ".*" + title_cut[0][-1]
                range_parse(link, title1)
    else:
        parse_download(link, title) 

def range_parse(series_url, search_title):
    req_page = requests.get(series_url).text
    soup = BeautifulSoup(req_page)
    titles = soup.findAll(text=re.compile(search_title))
    for title in titles:
       if quality !='480p' and quality in title:
           print title
           parse_download(series_url, title)
       if quality =='480p' and not (('.720p.' in title) or ('.1080p.' in title)):
           print title
           parse_download(series_url, title)

def parse_download(series_url, search_title):
    req_page = requests.get(series_url).text
    soup = BeautifulSoup(req_page)
    title = soup.find(text=re.compile(search_title))
    if title:
        links = title.parent.parent.findAll('a')
        for link in links:
            url = link['href']
            pattern = '.*%s_.*' % hoster
            if re.match(pattern, url):
                print title
                print url
                make_rss(title,url)

def make_rss(title, link):
    outputFile.write("<item>\n")
    outputFile.write("<title>"+title+"</title>\n")
    outputFile.write("<link>"+link+"</link>\n")
    outputFile.write("</item>\n")




feed = feedparser.parse('http://serienjunkies.org/xml/feeds/episoden.xml')
pattern = "|".join(getSeriesList(file)).lower()
reject = rejectlist.replace(";","|").lower() if len(rejectlist) > 0 else "^unmatchable$"
if hoster == "alle":
	hoster = "."
added_items = []

## Schreibe RSS
outputFile = open(outputFilename, "w")
# Schreibe RSS
outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\" ?>\n")
outputFile.write("<rss version=\"2.0\">\n")
outputFile.write("<channel>\n")
outputFile.write("<title>SerienJunkies-RSS Generator</title>\n")
outputFile.write("<description>Serienjunkies.org RSS Generator for Flexget</description>\n")
outputFile.write("<link>theres no link</link>\n")
outputFile.write("<ttl> </ttl>\n")


for post in feed.entries:
	link = post.link
	title = post.title
	
	if regex:
		m = re.search(pattern,title.lower())
		if not m and not "720p" in title and not "1080p" in title:
			m = re.search(pattern.replace("480p","."),title.lower())
			quality = "480p"
		if m:
			if "720p" in title.lower(): quality = "720p"
			if "1080p" in title.lower(): quality = "1080p"
			m = re.search(reject,title.lower())
			if m and debug:
				print("Abgelehnt: " + title)
				continue
			title = re.sub('\[.*\] ', '', post.title)
			range_checkr(link,title)
						
	else:
		if quality != '480p':
			m = re.search(pattern,title.lower())
			if m:
				if language in title:
					mm = re.search(quality,title.lower())
					if mm:
						mmm = re.search(reject,title.lower())
						if mmm and debug:
							print("Abgelehnt: " + title)
							continue
						title = re.sub('\[.*\] ', '', post.title)
						range_checkr(link,title)

		else:
			m = re.search(pattern,title.lower())
			if m:
				if language in title:
					if "720p" in title.lower() or "1080p" in title.lower():
						continue
					mm = re.search(reject,title.lower())
					if mm and debug:
						print("Abgelehnt: " + title)
						continue
					title = re.sub('\[.*\] ', '', post.title) 

# Schreibe RSS footer
outputFile.write("</channel>\n")
outputFile.write("</rss>")
outputFile.close()





