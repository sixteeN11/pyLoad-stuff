# !/usr/bin/python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License,published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import subprocess, re, os, sys, subprocess
from os import listdir, access, X_OK, makedirs
from os.path import join, exists, basename

from module.plugins.Hook import Hook
from module.utils import save_join


class FileBot(Hook):
    __name__ = "FileBot"
    __version__ = "0.6"
    __config__ = [("activated", "bool", "Activated", "False"),

                  ("destination", "folder", "destination folder", ""),

                  ("conflict", """skip;override""", "conflict handling", "override"),

                  ("action", """move;copy;test""", "copy, move or test(dry run)", "move"),

                  ("lang", "str", "language (en, de, fr, es, etc)", "de"),

                  ("subtitles", "str", "subtitles language (en, de, fr, es, etc)", "de"),

                  ("ignore", "str", "ignore files (regex)", ""),

                  ("artwork", """y;n""", "download artwork", "y"),

                  ("clean", """y;n""", "clean folder from clutter thats left behind", "y"),
                  
                  ("storeReport", """y;n""", "save reports to local filesystem", "n"),

                  ("movie", "str", "movie destination (relative to destination or absolute)", ""),

                  ("series", "str", "series destination (relative to destination or absolute)", ""),

                  ("excludeList", "str", "exclude list file", "pyload-amc.txt"),

                  ("reperror", """y;n""", "Report Error via Email", "n"),

                  ("filebot", "str", "filebot executable", "filebot"),

                  ("exec", "str", "additional exec script", ""),

                  ("no-xattr", "bool", "no-xattr", "False"),

                  ("xbmc", "str", "xbmc hostname", ""),

                  ("plex", "str", "plex hostname", ""),

                  ("plextoken", "str", "plex token (only needed with external plex servers)", ""),

                  ("extras", """y;n""", "create .url with all available backdrops", "n"),
                  
                  ("pushover", "str", "pushover user-key", ""),

                  ("pushbullet", "str", "pushbullet api-key", ""),

                  ("cleanfolder", "bool", "remove DownloadFolder after moving", "False"),
                  
                  ("output_to_log", "bool", "write FileBot Output to pyLoad Logfile", "True")]

    __description__ = "Automated renaming and sorting for tv episodes movies, music and animes"
    __author_name__ = ("Branko Wilhelm", "Kotaro", "Gutz-Pilz")
    __author_mail__ = ("branko.wilhelm@gmail.com", "screver@gmail.com", "unwichtig@gmail.com")

    event_list = ["package_extracted", "packageFinished"]
    
    def coreReady(self):
        self.core.api.setConfigValue("ExtractArchive", "delete", "True", section='plugin')
        self.core.api.setConfigValue("ExtractArchive", "deltotrash", "False", section='plugin')
        self.core.api.setConfigValue("general", "folder_per_package", "True", section='core')
        self.core.api.setConfigValue("FileBot", "exec", 'cd / && ./filebot.sh "{file}"', section='plugin')

    def packageFinished(self, pypack):
        x = False
        download_folder = self.config['general']['download_folder']
        folder = save_join(download_folder, pypack.folder)
        self.core.log.debug("FileBot: MKV-Checkup (packageFinished)")
        for root, dirs, files in os.walk(folder):
            for name in files:
                if name.endswith((".rar", ".r0", ".r12")):
                    self.core.log.debug("FileBot: Hier sind noch Archive")
                    x = True
                break
            break
        if x == False:
            self.core.log.debug("FileBot: Hier sind keine Archive")
            self.Finished(folder)


    def package_extracted(self, pypack):
        x = False

        download_folder = self.config['general']['download_folder']
        extract_destination = self.core.api.getConfigValue("ExtractArchive", "destination", section='plugin')
        extract_subfolder = self.core.api.getConfigValue("ExtractArchive", "subfolder", section='plugin')
        
        # determine output folder
        folder = save_join(download_folder, pypack.folder, extract_destination, "")  #: force trailing slash

        if extract_subfolder is True:
            folder = save_join(folder, pypack.folder)

        self.core.log.debug("FileBot: MKV-Checkup (package_extracted)")
        for root, dirs, files in os.walk(folder):
            for name in files:
                if name.endswith((".rar", ".r0", ".r12")):
                    self.core.log.debug("FileBot: Hier sind noch Archive")
                    x = True
                break
            break
        if x == False:
            self.core.log.debug("FileBot: Hier sind keine Archive")
            self.Finished(folder)


    def Finished(self, folder):
        args = []

        if self.getConfig('filebot'):
            args.append(self.getConfig('filebot'))
        else:
            args.append('filebot')

        args.append('-script')
        args.append('fn:amc')

        args.append('-non-strict')

        args.append('--log-file')
        args.append('amc.log')

        args.append('-r')

        args.append('--conflict')
        args.append(self.getConfig('conflict'))

        args.append('--action')
        args.append(self.getConfig('action'))

        if self.getConfig('destination'):
            args.append('--output')
            args.append(self.getConfig('destination'))
        else:
            args.append('--output')
            args.append(folder)

        if self.getConfig('lang'):
            args.append('--lang')
            args.append(self.getConfig('lang'))

        # start with all definitions:
        args.append('--def')

        if self.getConfig('exec'):
            args.append('exec=' + self.getConfig('exec'))

        if self.getConfig('clean'):
            args.append('clean=' + self.getConfig('clean'))

        args.append('skipExtract=y')

        if self.getConfig('excludeList'):
            args.append('excludeList=' + self.getConfig('excludeList'))

        if self.getConfig('reperror'):
            args.append('reportError=' + self.getConfig('reperror'))
        
        if self.getConfig('storeReport'):
            args.append('storeReport=' + self.getConfig('storeReport'))

        if self.getConfig('artwork'):
            args.append('artwork=' + self.getConfig('artwork'))

        if self.getConfig('subtitles'):
            args.append('subtitles=' + self.getConfig('subtitles'))

        if self.getConfig('ignore'):
            args.append('ignore=' + self.getConfig('ignore'))

        if self.getConfig('movie'):
            args.append('movieFormat=' + self.getConfig('movie'))

        if self.getConfig('series'):
            args.append('seriesFormat=' + self.getConfig('series'))

        if self.getConfig('no-xattr') is True:
            args.append(" -no-xattr")

        if self.getConfig('xbmc'):
            args.append('xbmc=' + self.getConfig('xbmc'))
            
        if self.getConfig('pushover'):
            args.append('pushover=' + self.getConfig('pushover'))

        if self.getConfig('pushbullet'):
            args.append('pushbullet=' + self.getConfig('pushbullet'))

        if self.getConfig('plex'):
            if self.getConfig('plextoken'):
                plexToken = ":" + self.getConfig('plextoken')
            else:
                plexToken = ""

            args.append('plex=' + self.getConfig('plex') + plexToken)
            self.logInfo('plex refreshed at ' + self.getConfig('plex') + plexToken)


        if self.getConfig('extras'):
            args.append('extras='+ self.getConfig('extras'))

        args.append(folder)

        try:
            if self.getConfig('output_to_log') is True:
                self.logInfo('executed')
                proc=subprocess.Popen(args, stdout=subprocess.PIPE)
                for line in proc.stdout:
                    self.logInfo(line.decode('utf-8').rstrip('\r|\n'))
                proc.wait()
            else:
                self.logInfo('executed')
                subprocess.Popen(args, bufsize=-1)
            if (self.getConfig('cleanfolder') is True) and (self.getConfig('output_to_log') is True):
                self.logInfo('cleaning')
                proc=subprocess.Popen(['filebot -script fn:cleaner --def root=y ', folder], stdout=subprocess.PIPE)
                for line in proc.stdout:
                    self.logInfo(line.decode('utf-8').rstrip('\r|\n'))
                proc.wait()
            if (self.getConfig('cleanfolder') is True) and (self.getConfig('output_to_log') is False):
                self.logInfo('cleaning')
                subprocess.Popen(['filebot -script fn:cleaner --def root=y ', folder], bufsize=-1)
        except Exception, e:
            self.logError(str(e))
