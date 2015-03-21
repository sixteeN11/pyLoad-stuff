#!/usr/bin/env python
import re, fileinput
confFile = open('/root/.pyload/plugin.conf').read()
#Sollzustand
filebotexec = 'str exec : "additional exec script" = cd / && ./filebot.sh "{file}"'
extractarchive = 'bool delete : "Delete archive after extraction" = True'


item1=re.findall('str exec : "additional exec script" =.*$',confFile,re.MULTILINE)
for x in item1:
    if filebotexec != x:
        for line in fileinput.FileInput("/root/.pyload/plugin.conf", inplace=1):
            line=line.replace(x,filebotexec)
            print line,
        #print "changed line1"

item2=re.findall('bool delete : "Delete archive after extraction" =.*$',confFile,re.MULTILINE)
for x in item2:
    if extractarchive != x:
        for line in fileinput.FileInput("/root/.pyload/plugin.conf", inplace=1):
            line=line.replace(x,extractarchive)
            print line,
        #print "changed line2"